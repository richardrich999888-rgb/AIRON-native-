"""Transactional local lifecycle; the OS account is the administrative trust root."""
import fcntl
import json
import math
import os
import re
import secrets
import shutil
import sqlite3
import threading
import time
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from . import sandbox
from .evidence import seal, verify, verify_chain
from .integrity import Rejected, canonical, digest, manifest, safe_path, verify_tree, write_json

POLICY = {
    "operator": {"prepare_dataset", "validate_dataset", "create_training_job", "start_training",
                 "get_training_status", "cancel_training", "register_checkpoint", "evaluate_candidate",
                 "export_model", "request_deployment", "infer", "status", "evidence"},
    "reviewer": {"approve_deployment", "activate_model", "rollback_model", "infer", "status", "evidence"}}
ID = re.compile(r"[a-z]+-[a-f0-9]{16}\Z")


class Controller:
    def __init__(self, root):
        self.root = Path(root).absolute()
        if self.root.is_symlink():
            raise Rejected("Controller root cannot be a symlink")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        safe_path(self.root, "state.db", exists=False)
        if self.root.stat().st_mode & 0o077:
            raise Rejected("Controller root must have mode 0700")
        fd = os.open(self.root / "controller.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        self.lock_file = os.fdopen(fd, "w")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            self.lock_file.close()
            raise Rejected("Another controller owns this workspace") from exc
        self.mutex = threading.RLock()
        self.processes, self.running, self.threads = {}, set(), []
        key_path = safe_path(self.root, "signing.key", exists=False)
        if not key_path.exists():
            if (self.root / "state.db").exists():
                raise Rejected("Signing key missing; do not replace an existing trust root")
            fd = os.open(key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            with os.fdopen(fd, "wb") as stream:
                stream.write(Ed25519PrivateKey.generate().private_bytes_raw())
        if key_path.stat().st_mode & 0o077:
            raise Rejected("Signing key must have mode 0600")
        self.key = Ed25519PrivateKey.from_private_bytes(key_path.read_bytes())
        self.public_key = self.key.public_key().public_bytes_raw()
        for name in ("state.db", "state.db-wal", "state.db-shm"):
            safe_path(self.root, name, exists=False)
        self.db = sqlite3.connect(self.root / "state.db", check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript("CREATE TABLE IF NOT EXISTS objects(id TEXT PRIMARY KEY, kind TEXT, record TEXT);"
                             "CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY, record TEXT);")
        self.db.commit()
        for folder in ("models", "datasets", "jobs", "candidates", "exports"):
            safe_path(self.root, folder, exists=False).mkdir(exist_ok=True, mode=0o700)
        with self.mutex, self.db:
            for job in self._all("job"):
                if job["status"] == "RUNNING":
                    job.update(status="INTERRUPTED", error="Controller restarted; create a new job")
                    self._put(job["id"], "job", job)
                    self._event("controller", "interrupted", {"job_id": job["id"]})

    def close(self):
        with self.mutex:
            for proc in list(self.processes.values()):
                sandbox.stop(proc)
        for thread in self.threads:
            thread.join(timeout=15)
        self.db.close()
        self.lock_file.close()

    def _new(self, prefix):
        return prefix + "-" + secrets.token_hex(8)

    def _put(self, ident, kind, value):
        self.db.execute("INSERT OR REPLACE INTO objects VALUES(?,?,?)",
                        (ident, kind, canonical(seal(value, self.key)).decode()))

    def _get(self, ident, kind):
        if ident != "deployment" and (not isinstance(ident, str) or not ID.fullmatch(ident)):
            raise Rejected("Invalid object identifier")
        row = self.db.execute("SELECT record FROM objects WHERE id=? AND kind=?", (ident, kind)).fetchone()
        if row is None:
            raise Rejected("Unknown " + kind)
        return verify(json.loads(row[0]), self.public_key)

    def _all(self, kind):
        return [verify(json.loads(row[0]), self.public_key) for row in
                self.db.execute("SELECT record FROM objects WHERE kind=? ORDER BY rowid", (kind,))]

    def _event(self, actor, action, details):
        row = self.db.execute("SELECT seq,record FROM events ORDER BY seq DESC LIMIT 1").fetchone()
        payload = {"schema": "airon-model-change/v1", "sequence": row[0]+1 if row else 1,
                   "previous": digest(json.loads(row[1])) if row else "GENESIS",
                   "at_unix": time.time(), "actor": actor, "action": action,
                   "policy": "local-two-role-v1", "details": details,
                   "assurance": "APPLICATION_SIGNED", "independent_execution": "CANNOT_PROVE"}
        self.db.execute("INSERT INTO events VALUES(?,?)",
                        (payload["sequence"], canonical(seal(payload, self.key)).decode()))

    def call(self, operation, params, *, actor, role):
        if operation not in POLICY.get(role, set()):
            raise Rejected("Operation not permitted for this session role")
        if not isinstance(params, dict) or len(canonical(params)) > 1024*1024:
            raise Rejected("Invalid request")
        if any(k in params for k in ("actor", "role")):
            raise Rejected("Client cannot set actor or role")
        with self.mutex, self.db:
            try:
                return getattr(self, operation)(actor=actor, **params)
            except TypeError as exc:
                raise Rejected("Invalid operation arguments") from exc

    def import_base(self, source, *, identifier, license_id, revision):
        """Administrative provisioning only; absent from network API."""
        with self.mutex, self.db:
            if not all(isinstance(v, str) and v.strip() for v in (identifier, license_id, revision)):
                raise Rejected("Model identifier, revision and licence required")
            files = manifest(source, model=True)
            cfg = json.loads((Path(source)/"config.json").read_text())
            if cfg.get("model_type") not in {"llama", "gpt2"}:
                raise Rejected("Only reviewed llama/gpt2 architectures supported")
            ident = self._new("model")
            target = self.root/"models"/ident
            shutil.copytree(source, target)
            verify_tree(target, files, model=True)
            obj = {"id": ident, "identifier": identifier, "revision": revision, "license": license_id,
                   "manifest": files, "digest": digest(files)}
            self._put(ident, "model", obj)
            if not self._all("deployment"):
                self._put("deployment", "deployment", {"version": 1, "base": ident, "active": None, "history": []})
            self._event("provisioner", "base_registered", obj)
            return obj

    @staticmethod
    def _validate_rows(rows):
        if not isinstance(rows, list) or not 4 <= len(rows) <= 1000:
            raise Rejected("Supply 4–1000 approved synthetic records")
        seen = set()
        for row in rows:
            if not isinstance(row, dict) or set(row) != {"prompt", "answer", "split"}:
                raise Rejected("Unknown dataset fields")
            if row["split"] not in {"train", "test", "regression"}:
                raise Rejected("Unknown split")
            for key in ("prompt", "answer"):
                value = row[key]
                if not isinstance(value, str) or not 1 <= len(value.strip()) <= 2000:
                    raise Rejected("Invalid dataset text")
                if any(ord(c) < 32 and c not in "\n\t" for c in value):
                    raise Rejected("Control characters in dataset")
                if re.search(r"ignore.{0,30}(instructions|policy)|system\s*:|<\|.*?\|>|private.key|api.key|https?://", value, re.I):
                    raise Rejected("Dataset quarantine: instruction/control/secret pattern")
            normalized = " ".join(row["prompt"].lower().split())
            if normalized in seen:
                raise Rejected("Duplicate prompt or split contamination")
            seen.add(normalized)
        counts = {s: sum(r["split"] == s for r in rows) for s in ("train", "test", "regression")}
        if not all(counts.values()):
            raise Rejected("Training, held-out test and regression splits mandatory")
        return counts

    def prepare_dataset(self, rows, authorization, actor):
        counts = self._validate_rows(rows)
        if (not isinstance(authorization, dict)
                or set(authorization) != {"synthetic", "approved_for_training", "license"}
                or authorization["synthetic"] is not True
                or authorization["approved_for_training"] is not True
                or authorization["license"] != "CC0-1.0"):
            raise Rejected("Only explicitly approved CC0 synthetic data accepted")
        ident = self._new("dataset")
        path = self.root/"datasets"/ident
        path.mkdir(mode=0o700)
        write_json(path/"records.json", rows)
        with (path/"train.jsonl").open("x") as stream:
            for row in rows:
                if row["split"] == "train":
                    stream.write(canonical({"messages": [{"role": "user", "content": row["prompt"]},
                                                          {"role": "assistant", "content": row["answer"]}]}).decode()+"\n")
        files = manifest(path)
        obj = {"id": ident, "counts": counts, "manifest": files, "digest": digest(files),
               "authorized_by": actor, "authorization": authorization}
        self._put(ident, "dataset", obj)
        self._event(actor, "dataset_authorized", obj)
        return obj

    def validate_dataset(self, dataset_id, actor):
        ds = self._get(dataset_id, "dataset")
        path = safe_path(self.root, "datasets/"+dataset_id)
        verify_tree(path, ds["manifest"])
        return {"valid": True, "digest": ds["digest"],
                "counts": self._validate_rows(json.loads((path/"records.json").read_text())),
                "poisoning_review": "HEURISTICS_ONLY; human authorization required"}

    def create_training_job(self, base_id, dataset_id, config, actor):
        self._get(base_id, "model")
        self.validate_dataset(dataset_id, actor)
        if not isinstance(config, dict) or set(config) != {"epochs", "lr", "rank", "seed"}:
            raise Rejected("Only epochs, lr, rank and seed accepted")
        for key, lo, hi in (("epochs", 1, 12), ("rank", 2, 16), ("seed", 0, 2**31-1)):
            if type(config[key]) is not int or not lo <= config[key] <= hi:
                raise Rejected("Training config outside resource policy")
        if type(config["lr"]) not in (int, float) or not math.isfinite(config["lr"]) or not 0 < config["lr"] <= 0.005:
            raise Rejected("Invalid learning rate")
        ident = self._new("job")
        job = {"id": ident, "base_id": base_id, "dataset_id": dataset_id, "config": config,
               "config_digest": digest(config), "status": "CREATED", "authorized_by": actor}
        self._put(ident, "job", job)
        self._event(actor, "training_authorized", job)
        return job

    def _inputs(self, job):
        base = self._get(job["base_id"], "model")
        ds = self._get(job["dataset_id"], "dataset")
        model = safe_path(self.root, "models/"+base["id"])
        data = safe_path(self.root, "datasets/"+ds["id"])
        verify_tree(model, base["manifest"], model=True)
        verify_tree(data, ds["manifest"])
        return model, data

    def start_training(self, job_id, actor):
        job = self._get(job_id, "job")
        if job["status"] != "CREATED" or self.running:
            raise Rejected("Job cannot start or another worker is running")
        self._inputs(job)
        job.update(status="RUNNING", started_at=time.time())
        self._put(job_id, "job", job)
        self._event(actor, "training_started", {"job_id": job_id})
        self.running.add(job_id)
        thread = threading.Thread(target=self._train, args=(job, actor), daemon=True)
        self.threads.append(thread)
        thread.start()
        return job

    def _execute(self, job, operation, adapter=None):
        with self.mutex:
            model, data = self._inputs(job)
            path = self.root/"jobs"/self._new("run")
            path.mkdir(mode=0o700)
            (path/"output").mkdir(mode=0o700)
            write_json(path/"request.json", {"operation": operation, "config": job["config"],
                                            "has_adapter": adapter is not None,
                                            "parent_netns": os.readlink("/proc/self/ns/net")})
        def started(proc):
            with self.mutex:
                self.processes[job["id"]] = proc
                if self._get(job["id"], "job")["status"] == "CANCELLED":
                    sandbox.stop(proc)
        try:
            sandbox.run(sandbox.command(path, model, data, adapter), path/"worker.log", on_start=started)
            result = json.loads(safe_path(path, "output/result.json").read_text())
            return path, result
        finally:
            with self.mutex:
                self.processes.pop(job["id"], None)

    def _train(self, job, actor):
        try:
            path, result = self._execute(job, "train")
            with self.mutex, self.db:
                current = self._get(job["id"], "job")
                if current["status"] == "CANCELLED":
                    return
                if result.get("changed_parameters", 0) <= 0 or result.get("steps", 0) <= 0:
                    raise Rejected("No measured parameter update")
                files = manifest(path/"output"/"adapter", model=True)
                current.update(status="SUCCEEDED", result=result, run_path=path.relative_to(self.root).as_posix(),
                               checkpoint_manifest=files, completed_at=time.time())
                self._put(job["id"], "job", current)
                self._event(actor, "training_completed", {"job_id": job["id"], "result": result,
                                                         "checkpoint_digest": digest(files)})
        except Exception as exc:
            with self.mutex, self.db:
                current = self._get(job["id"], "job")
                if current["status"] != "CANCELLED":
                    current.update(status="FAILED", error=str(exc), completed_at=time.time())
                    self._put(job["id"], "job", current)
                    self._event(actor, "training_failed", {"job_id": job["id"], "error": str(exc)})
        finally:
            with self.mutex:
                self.running.discard(job["id"])

    def get_training_status(self, job_id, actor):
        return self._get(job_id, "job")

    def cancel_training(self, job_id, actor):
        job = self._get(job_id, "job")
        if job["status"] not in {"CREATED", "RUNNING"}:
            raise Rejected("Job is not cancellable")
        job["status"] = "CANCELLED"
        self._put(job_id, "job", job)
        if job_id in self.processes:
            sandbox.stop(self.processes[job_id])
        self._event(actor, "training_cancelled", {"job_id": job_id})
        return job

    def register_checkpoint(self, job_id, actor):
        job = self._get(job_id, "job")
        if job["status"] != "SUCCEEDED":
            raise Rejected("Only completed training may register a candidate")
        source = safe_path(self.root, job["run_path"]+"/output/adapter")
        verify_tree(source, job["checkpoint_manifest"], model=True)
        cfg = json.loads((source/"adapter_config.json").read_text())
        if cfg.get("base_model_name_or_path") != "/model" or cfg.get("peft_type") != "LORA":
            raise Rejected("Adapter must bind to the isolated local base and LoRA")
        ident = self._new("candidate")
        target = self.root/"candidates"/ident
        shutil.copytree(source, target)
        verify_tree(target, job["checkpoint_manifest"], model=True)
        obj = {"id": ident, "job_id": job_id, "base_id": job["base_id"], "dataset_id": job["dataset_id"],
               "manifest": job["checkpoint_manifest"], "digest": digest(job["checkpoint_manifest"])}
        self._put(ident, "candidate", obj)
        self._event(actor, "candidate_registered", obj)
        return obj

    def _candidate(self, candidate_id):
        candidate = self._get(candidate_id, "candidate")
        path = safe_path(self.root, "candidates/"+candidate_id)
        verify_tree(path, candidate["manifest"], model=True)
        job = self._get(candidate["job_id"], "job")
        self._inputs(job)
        return candidate, path, job

    def evaluate_candidate(self, candidate_id, actor):
        if self.running:
            raise Rejected("Another worker is running")
        candidate, path, job = self._candidate(candidate_id)
        run, metrics = self._execute(job, "evaluate", path)
        for split in ("test", "regression"):
            scores = metrics.get(split, {})
            for key in ("baseline_accuracy", "candidate_accuracy"):
                v = scores.get(key)
                if type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1:
                    raise Rejected("Invalid evaluation metrics")
            if scores.get("count") != self._get(job["dataset_id"], "dataset")["counts"][split]:
                raise Rejected("Evaluation did not cover frozen split")
        passed = (metrics["test"]["candidate_accuracy"] > metrics["test"]["baseline_accuracy"]
                  and metrics["regression"]["candidate_accuracy"] >= metrics["regression"]["baseline_accuracy"])
        ident = self._new("evaluation")
        report = {"id": ident, "candidate_id": candidate_id, "candidate_digest": candidate["digest"],
                  "dataset_digest": self._get(job["dataset_id"], "dataset")["digest"],
                  "base_digest": self._get(job["base_id"], "model")["digest"], "config_digest": job["config_digest"],
                  "metrics": metrics, "passed": passed, "run_path": run.relative_to(self.root).as_posix(),
                  "policy": "strict-improvement-no-regression-v1"}
        self._put(ident, "evaluation", report)
        self._event(actor, "candidate_evaluated", report)
        return report

    def export_model(self, candidate_id, actor):
        if self.running:
            raise Rejected("Another worker is running")
        _, path, job = self._candidate(candidate_id)
        run, result = self._execute(job, "export", path)
        source = run/"output"/"export"
        files = manifest(source, model=True)
        ident = self._new("export")
        shutil.copytree(source, self.root/"exports"/ident)
        verify_tree(self.root/"exports"/ident, files, model=True)
        obj = {"id": ident, "candidate_id": candidate_id, "format": "hf-safetensors",
               "manifest": files, "digest": digest(files), "result": result}
        self._put(ident, "export", obj)
        self._event(actor, "model_exported", obj)
        return obj

    def request_deployment(self, candidate_id, evaluation_id, actor):
        candidate, _, _ = self._candidate(candidate_id)
        evaluation = self._get(evaluation_id, "evaluation")
        if not evaluation["passed"] or evaluation["candidate_id"] != candidate_id or evaluation["candidate_digest"] != candidate["digest"]:
            raise Rejected("Matching passing evaluation required")
        ident = self._new("approval")
        obj = {"id": ident, "candidate_id": candidate_id, "evaluation_id": evaluation_id,
               "evaluation_digest": digest(evaluation), "requested_by": actor, "decision": "PENDING",
               "expected_version": self._get("deployment", "deployment")["version"]}
        self._put(ident, "approval", obj)
        self._event(actor, "deployment_requested", obj)
        return obj

    def approve_deployment(self, approval_id, decision, actor):
        approval = self._get(approval_id, "approval")
        if decision not in {"APPROVED", "REJECTED"} or approval["decision"] != "PENDING":
            raise Rejected("Invalid or already decided approval")
        if actor == approval["requested_by"]:
            raise Rejected("Requester cannot approve their deployment")
        approval.update(decision=decision, decided_by=actor)
        self._put(approval_id, "approval", approval)
        self._event(actor, "approval_decision", approval)
        return approval

    def activate_model(self, approval_id, actor):
        approval = self._get(approval_id, "approval")
        deployment = self._get("deployment", "deployment")
        if approval["decision"] != "APPROVED" or approval["expected_version"] != deployment["version"]:
            raise Rejected("Missing, consumed or stale approval")
        candidate, _, _ = self._candidate(approval["candidate_id"])
        evaluation = self._get(approval["evaluation_id"], "evaluation")
        if digest(evaluation) != approval["evaluation_digest"] or not evaluation["passed"]:
            raise Rejected("Evaluation changed after approval")
        if candidate["base_id"] != deployment["base"]:
            raise Rejected("Candidate belongs to another base")
        deployment["history"].append(deployment["active"])
        deployment.update(active=candidate["id"], version=deployment["version"]+1)
        approval["decision"] = "CONSUMED"
        self._put("deployment", "deployment", deployment)
        self._put(approval_id, "approval", approval)
        self._event(actor, "model_activated", {"approval_id": approval_id, **deployment})
        return deployment

    def rollback_model(self, actor):
        deployment = self._get("deployment", "deployment")
        if not deployment["history"]:
            raise Rejected("No deployment to restore")
        target = deployment["history"][-1]
        base = self._get(deployment["base"], "model")
        verify_tree(self.root/"models"/base["id"], base["manifest"], model=True)
        if target:
            self._candidate(target)
        deployment["history"].pop()
        deployment.update(active=target, version=deployment["version"]+1)
        self._put("deployment", "deployment", deployment)
        self._event(actor, "model_rolled_back", deployment)
        return deployment

    def infer(self, dataset_id, actor):
        if self.running:
            raise Rejected("Another worker is running")
        deployment = self._get("deployment", "deployment")
        jobs = [j for j in self._all("job") if j["base_id"] == deployment["base"] and j["dataset_id"] == dataset_id]
        if not jobs:
            raise Rejected("Prepare a job binding the approved dataset first")
        adapter = self._candidate(deployment["active"])[1] if deployment["active"] else None
        _, result = self._execute(jobs[-1], "infer", adapter)
        self._event(actor, "local_inference", {"deployment_version": deployment["version"],
                                              "active": deployment["active"], "result_digest": digest(result)})
        return {"deployment": deployment, "result": result}

    def status(self, actor):
        return {kind: self._all(kind) for kind in ("model", "dataset", "job", "candidate", "evaluation", "approval", "deployment", "export")}

    def evidence(self, actor):
        records = [json.loads(r[0]) for r in self.db.execute("SELECT record FROM events ORDER BY seq")]
        return {"public_key_hex": self.public_key.hex(), "records": records,
                "verification": verify_chain(records, self.public_key),
                "aip_integration": "CONTRACT_ONLY", "sniffer_dog": "NOT_INTEGRATED"}
