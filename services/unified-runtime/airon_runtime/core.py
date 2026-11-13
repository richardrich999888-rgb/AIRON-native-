"""One orchestration boundary for knowledge, native capabilities and Soup.

P0-052 is reused unchanged at a pinned revision. Private adapter calls below
are version-pinned, tested contracts, not a promise of upstream public API.
"""
import dataclasses
import hashlib
import json
import re
import sys
import threading
from pathlib import Path
from airon_adaptation.controller import Controller
from airon_adaptation.integrity import Rejected, digest, file_hash, write_json
from airon_adaptation.knowledge import approved_quote, SOURCE_COPY_INSTRUCTION
from .learning import Opportunity, decide
from .native import Native
from .process import run, checked_file

RANK = {"public":0,"internal":1,"restricted":2}

@dataclasses.dataclass(frozen=True)
class Principal:
    actor: str
    tenant: str
    clearance: str
    role: str

class Core:
    def __init__(self, root):
        if Path(root).is_symlink(): raise Rejected("Workspace cannot be a symlink")
        self.root = Path(root).resolve()
        self.config = json.loads((self.root/"provision.json").read_text())
        if self.config["schema"] != "airon-provision/v1":
            raise Rejected("Unknown provisioning contract")
        self.control = Controller(self.root/"control")
        self.adaptation = Controller(self.root/"adaptation")
        self.native = Native(self.config["native"])
        self.slot = threading.Lock() # capacity 1, no unbounded request queue
        self.identities = {k:Principal(actor=k,**v) for k,v in self.config["principals"].items()}
        self._verify_native_state()

    def close(self):
        self.adaptation.close()
        self.control.close()

    def principal(self, actor):
        try: return self.identities[actor]
        except KeyError as e: raise Rejected("Unknown provisioned actor") from e

    def _who(self, principal):
        if not isinstance(principal, Principal) or self.identities.get(principal.actor) != principal:
            raise Rejected("Principal differs from provisioned authority")

    def _require(self, p, roles):
        self._who(p)
        if p.role not in roles:
            raise Rejected("Operation outside session authority")

    def _record(self, p, action, detail):
        with self.control.mutex, self.control.db:
            self.control._event(p.actor,action,{"tenant":p.tenant,**detail})

    def _put(self, kind, record, ident=None):
        ident = ident or self.control._new(kind)
        record = {"id":ident,**record}
        with self.control.mutex, self.control.db:
            self.control._put(ident,kind,record)
        return record

    def _audit_path(self):
        return Path(self.config["native_state"])/"audit.jsonl"

    def _verify_native_state(self):
        records = self.control._all("anchor")
        if records:
            path = self._audit_path()
            if not path.is_file() or file_hash(path) != records[-1]["sha256"]:
                raise Rejected("Native execution audit is missing, truncated or modified")
        caps = self.control._all("capanchor")
        if caps and self._cap_manifest() != caps[-1]["manifest"]:
            raise Rejected("Native capability state differs from the signed lifecycle anchor")

    def _cap_manifest(self):
        folder = Path(self.config["native_state"])/"capabilities"
        return {p.name:file_hash(p) for p in sorted(folder.glob("*.json"))}

    def _documents(self, p):
        return [r for r in self.control._all("document") if r["tenant"] == p.tenant
                and RANK[r["classification"]] <= RANK[p.clearance] and not r.get("deleted")]

    def _ready(self):
        if self.adaptation.running:
            raise Rejected("Training owns the heavy-worker slot; retry after completion")

    def ingest(self, principal, *, text, doc_id, title, classification):
        p = principal
        self._require(p,{"operator"})
        self._ready()
        if (not re.fullmatch(r"[A-Za-z0-9._-]{1,128}",doc_id) or not isinstance(text,str)
                or not 1 <= len(text.encode()) <= 1024**2 or len(title)>512
                or classification not in RANK or RANK[classification]>RANK[p.clearance]):
            raise Rejected("Document outside ingestion policy")
        raw_hash = hashlib.sha256(text.encode()).hexdigest()
        folder = self.root/"documents"/p.tenant/raw_hash
        folder.mkdir(parents=True,exist_ok=True,mode=0o700)
        path = folder/"source.md"
        if path.exists() and file_hash(path) != raw_hash:
            raise Rejected("Existing source artifact corrupted")
        path.write_text(text)
        result = run([sys.executable,Path(__file__).with_name("docling_worker.py")],
                     data={"path":str(path)},timeout=120)
        extracted = json.loads(result["stdout"])
        write_json(folder/"structure.json",extracted["structure"])
        prior = next((r for r in self.control._all("document") if r["tenant"]==p.tenant and r["doc_id"]==doc_id),None)
        # Persist intent before crossing the database boundary. Incomplete writes
        # cannot pass the source-digest check in search().
        self._record(p,"document_ingest_intent",{"doc_id":doc_id,"source_sha256":raw_hash})
        outcome = self.native.call("ingest",{"doc_id":doc_id,"title":title,
            "classification":classification,"body":extracted["text"]},p.actor)
        record = self._put("document",{"tenant":p.tenant,"doc_id":doc_id,"title":title,
            "classification":classification,"source_sha256":raw_hash,
            "body_sha256":hashlib.sha256(extracted["text"].encode()).hexdigest(),
            "structure_sha256":file_hash(folder/"structure.json"),"version":1 if not prior else prior["version"]+1,
            "previous":digest(prior) if prior else None,"engine":"docling","format":"markdown",
            "native_outcome":outcome["result"]["outcome"]}, prior["id"] if prior else None)
        self._record(p,"document_indexed",{"record_digest":digest(record),"measurement":result["measurement"]})
        return record

    def search(self, principal, *, question):
        self._who(principal)
        if not isinstance(question,str) or not 1 <= len(question) <= 500:
            raise Rejected("Question outside bounds")
        response = self.native.call("search",{"query":question,"limit":3},principal.actor)
        documents = {d["doc_id"]:d for d in self._documents(principal)}
        for hit in response["result"]["hits"]:
            doc = documents.get(hit["doc_id"])
            if not doc or doc["body_sha256"] != hit["body_sha256"]:
                raise Rejected("Native source lacks a matching committed document version")
            hit["citation"] = {k:doc[k] for k in ("doc_id","version","source_sha256","structure_sha256")}
        return response

    def delete(self, principal, *, doc_id):
        self._require(principal,{"operator"})
        self._ready()
        record = next((r for r in self._documents(principal) if r["doc_id"]==doc_id),None)
        if record is None: raise Rejected("Document unavailable")
        self._record(principal,"document_delete_intent",{"doc_id":doc_id})
        result = self.native.call("delete",{"doc_id":doc_id},principal.actor)
        self._put("document",{**record,"deleted":True},record["id"])
        self._record(principal,"document_deleted",{"doc_id":doc_id,"result":result["result"]})
        return result

    def ask(self, principal, *, question, backend="adaptation"):
        self._who(principal); self._ready()
        found = self.search(principal,question=question)
        hits = found["result"]["hits"]
        if not hits:
            result = {"outcome":"ABSTAINED","reason":"No authorized source","model_calls":0,"sources":[]}
        else:
            hit = hits[0]
            # One bounded approved passage. Source contents are data, never tool
            # instructions; only an exact source quote can be released.
            source = hit["text"]
            if backend == "adaptation":
                dep = self.adaptation._get("deployment","deployment")
                jobs = [j for j in self.adaptation._all("job") if j["base_id"]==dep["base"]]
                if not jobs: raise Rejected("No approved local model/dataset binding")
                adapter = self.adaptation._candidate(dep["active"])[1] if dep["active"] else None
                _, generated = self.adaptation._execute(jobs[-1],"knowledge",adapter,
                    knowledge_request={"question":question,"source_text":source})
                model = {"backend":"p0-052-transformers","deployment":dep}
            elif backend == "llama":
                from .inference import llama_generate
                generated = llama_generate(self.config["llama"],question,source)
                model = {"backend":"llama.cpp","model_sha256":self.config["llama"]["model"]["sha256"]}
            else: raise Rejected("Unknown inference backend")
            matched = approved_quote(generated.get("text"),source) is not None
            result = {"outcome":"ANSWERED" if matched else "ABSTAINED","model_calls":1,
                      "answer":source if matched else None,"sources":[hit["citation"]] if matched else [],
                      "model":model,"generation":generated,"route":"authorized_retrieval_then_neural_inference"}
        self._record(principal,"answer",{"question_sha256":digest(question),"result_sha256":digest(result),
                     "outcome":result["outcome"],"model_calls":result["model_calls"]})
        return result

    def execute(self, principal, *, capability_id, text):
        self._who(principal); self._verify_native_state()
        response = self.native.call("execute",{"capability_id":capability_id,"text":text},principal.actor)
        self._put("anchor",{"sha256":file_hash(self._audit_path())})
        self._put("outcome",{"tenant":principal.tenant,"task_sha256":digest(text),
            "capability_id":capability_id,"response":response,"trusted_fact":False})
        self._record(principal,"capability_execution",{"result_sha256":digest(response),"route":"deterministic"})
        return response

    def capability(self, principal, *, action, payload):
        role = "reviewer" if action in {"approve","activate","rollback"} else "operator"
        self._require(principal,{role}); self._ready(); self._verify_native_state()
        staging = self.root/"requests"; staging.mkdir(exist_ok=True,mode=0o700)
        if action == "propose":
            cap = payload["capability"]
            if cap["required"]["tenant"] != principal.tenant or cap["proposed_by"] != principal.actor:
                raise Rejected("Capability tenant/proposer must match session")
            path = staging/(digest(cap)+".json"); write_json(path,cap)
            args = ["--file",str(path)]
        elif action == "validate":
            suite = payload["suite"]
            path = staging/(digest(suite)+".json"); write_json(path,suite)
            args = ["--hash",payload["hash"],"--suite",str(path)]
        elif action == "approve":
            key = checked_file(self.config["approver_keys"][principal.actor])
            args = ["--hash",payload["hash"],"--key",str(key)]
        elif action == "activate":
            args = ["--hash",payload["hash"],"--actor",principal.actor,"--reason","explicit local review","--supersede"]
        elif action == "rollback":
            args = ["--to",payload["hash"],"--actor",principal.actor,"--reason","explicit local rollback"]
        else: raise Rejected("Unknown capability action")
        # Scope lifecycle requests by looking up the actual stored capability.
        if action != "propose":
            stored = Path(self.config["native_state"])/"capabilities"
            records = [json.loads(x.read_text()) for x in stored.glob("*.json")]
            matching = [r for r in records if r.get("capability_hash")==payload["hash"]]
            if len(matching)!=1 or matching[0]["capability"]["required"]["tenant"] != principal.tenant:
                raise Rejected("Lifecycle capability outside tenant scope")
        self._record(principal,"capability_intent",{"action":action,"request_sha256":digest(payload)})
        result = self.native.lifecycle("cap-"+action,args)
        self._put("capanchor",{"manifest":self._cap_manifest()})
        self._put("procedure",{"tenant":principal.tenant,"action":action,"result":result})
        self._record(principal,"capability_"+action,{"result_sha256":digest(result)})
        return result

    def learn(self, principal, **fields):
        self._require(principal,{"operator","reviewer"})
        if fields.get("verified") and principal.role != "reviewer":
            raise Rejected("Only a reviewer may attest a learning opportunity")
        recommendation = decide(Opportunity(**fields))
        self._put("learning",{"tenant":principal.tenant,"opportunity":fields,"recommendation":recommendation})
        self._record(principal,"learning_recommendation",recommendation)
        return recommendation

    def adapt(self, principal, *, operation, params):
        self._who(principal)
        # P0-052 is a single-tenant workspace. Reject other tenants before its API.
        if principal.tenant != self.config["adaptation_tenant"]:
            raise Rejected("Adaptation workspace outside tenant scope")
        if operation in {"start_training","infer","evaluate_candidate","export_model","query_knowledge"}:
            self._ready()
        result = self.adaptation.call(operation,params,actor=principal.actor,role=principal.role)
        self._record(principal,"adaptation_"+operation,{"result_sha256":digest(result)})
        return result

    def status(self, principal):
        self._who(principal)
        caps = self.native.lifecycle("cap-list",[])
        # Native cap-list lacks tenant information; expose only capabilities
        # with records in this tenant, without exposing foreign hashes.
        records = [json.loads(x.read_text()) for x in (Path(self.config["native_state"])/"capabilities").glob("*.json")]
        allowed = {r["capability_hash"] for r in records if r["capability"]["required"]["tenant"]==principal.tenant}
        return {"schema":"airon-status/v1","principal":dataclasses.asdict(principal),
            "documents":self._documents(principal),"capabilities":[r for r in caps if r["hash"] in allowed],
            "adaptation":self.adaptation.status(principal.actor) if principal.tenant==self.config["adaptation_tenant"] else {},
            "learning":[r for r in self.control._all("learning") if r["tenant"]==principal.tenant],
            "assurance":"APPLICATION_SIGNED","independent_execution":"CANNOT_PROVE",
            "issues":["Synthetic local roles; no independently administered signer custody",
                      "PDF/OCR and simultaneous training/serving not qualified",
                      "Consequential capabilities remain disabled until AIP authorization is integrated"]}

    def evidence(self, principal):
        self._require(principal,{"reviewer"})
        if principal.tenant != self.config["adaptation_tenant"]:
            raise Rejected("Workspace evidence outside tenant scope")
        self._verify_native_state()
        return {"core":self.control.evidence(principal.actor),"adaptation":self.adaptation.evidence(principal.actor)}

    def call(self, principal, operation, params):
        if operation not in {"ingest","search","delete","ask","execute","capability","learn","adapt","status","evidence"}:
            raise Rejected("Unknown operation")
        if not isinstance(params,dict) or any(k in params for k in ("principal","actor","role","tenant","clearance")):
            raise Rejected("Session identity cannot be supplied in request parameters")
        if not self.slot.acquire(blocking=False): raise Rejected("Runtime busy; bounded queue is full")
        try:
            return getattr(self,operation)(principal,**params)
        finally:
            self.slot.release()
