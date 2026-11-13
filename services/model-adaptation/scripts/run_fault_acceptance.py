"""Real cancellation and malformed-model probes, restricted to synthetic inputs."""
import argparse
import json
import re
import shutil
import time
from pathlib import Path
from airon_adaptation.controller import Controller
from airon_adaptation.integrity import Rejected, write_json

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--source-root", required=True)
parser.add_argument("--root", required=True)
parser.add_argument("--report", required=True)
parser.add_argument("--authorize-synthetic-fault-tests", required=True, action="store_true")
args = parser.parse_args()
source = Controller(args.source_root)
ctl = Controller(args.root)
report = {"schema": "airon-real-fault-check/v1", "fixture": False, "checks": {}, "passed": False}
try:
    state = source.call("status", {}, actor="fault-reviewer", role="reviewer")
    original = state["model"][0]
    dataset = state["dataset"][0]
    if dataset["authorization"] != {"synthetic": True, "approved_for_training": True, "license": "CC0-1.0"}:
        raise RuntimeError("Fault tests require explicit synthetic authorization")
    base = ctl.import_base(source.root/"models"/original["id"],
                           identifier=original["identifier"], revision=original["revision"],
                           license_id=original["license"])
    rows = json.loads((source.root/"datasets"/dataset["id"]/"records.json").read_text())
    source.close()
    source = None
    def invoke(operation, **params):
        return ctl.call(operation, params, actor="synthetic-fault-operator", role="operator")
    ds = invoke("prepare_dataset", rows=rows, authorization=dataset["authorization"])
    cfg = {"epochs": 12, "lr": .001, "rank": 8, "seed": 52}
    job = invoke("create_training_job", base_id=base["id"], dataset_id=ds["id"], config=cfg)
    invoke("start_training", job_id=job["id"])
    total_steps = ((ds["counts"]["train"]+1)//2)*cfg["epochs"]
    deadline, observed_step = time.monotonic()+120, False
    while time.monotonic() < deadline:
        if invoke("get_training_status", job_id=job["id"])["status"] != "RUNNING":
            break
        logs = list((ctl.root/"jobs").glob("*/worker.log"))
        if any(re.search(rf"\b[1-9][0-9]*/{total_steps}\b", p.read_text(errors="replace")) for p in logs):
            observed_step = True
            break
        time.sleep(.1)
    if not observed_step:
        raise RuntimeError("No genuine optimizer-step progress observed before cancellation")
    with ctl.mutex:
        process = ctl.processes[job["id"]]
    cancelled = invoke("cancel_training", job_id=job["id"])
    if cancelled["status"] != "CANCELLED" or process.poll() is None:
        raise RuntimeError("Cancellation did not stop the real process")
    try:
        invoke("register_checkpoint", job_id=job["id"])
    except Rejected:
        pass
    else:
        raise RuntimeError("Cancelled job registered a candidate")
    report["checks"]["real_training_cancellation"] = {"passed": True, "observed_optimizer_progress": True,
                                                     "process_returncode": process.returncode}
    for thread in ctl.threads:
        thread.join(timeout=15)
    malformed = ctl.root/"malformed-input"
    shutil.copytree(ctl.root/"models"/base["id"], malformed)
    (malformed/"model.safetensors").write_bytes(b"INTENTIONALLY-MALFORMED-SYNTHETIC-FAULT")
    broken = ctl.import_base(malformed, identifier="synthetic-malformed-test",
                              license_id="Apache-2.0", revision="intentional-corruption")
    badjob = invoke("create_training_job", base_id=broken["id"], dataset_id=ds["id"],
                    config={**cfg, "epochs": 1})
    invoke("start_training", job_id=badjob["id"])
    deadline = time.monotonic()+60
    while time.monotonic() < deadline:
        failed = invoke("get_training_status", job_id=badjob["id"])
        if failed["status"] != "RUNNING":
            break
        time.sleep(.2)
    if failed["status"] != "FAILED":
        raise RuntimeError("Malformed model did not fail in the actual loader")
    if invoke("status")["candidate"] or invoke("status")["deployment"][0]["active"] is not None:
        raise RuntimeError("Fault test affected candidate/deployment state")
    report["checks"]["real_malformed_model_rejection"] = {"passed": True, "status": failed["status"],
                                                        "error": failed.get("error")}
    report["passed"] = True
except Exception as exc:
    report["failure"] = str(exc)
finally:
    report["evidence"] = ctl.call("evidence", {}, actor="fault-reviewer", role="reviewer")
    write_json(args.report, report)
    ctl.close()
    if source is not None:
        source.close()
print("REAL_FAULT_REPORT="+json.dumps(report))
raise SystemExit(0 if report["passed"] else 2)
