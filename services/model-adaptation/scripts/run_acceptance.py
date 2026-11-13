"""Real acceptance driver. No mocked results and no automatic production promotion."""
import argparse
import json
import time
from pathlib import Path
from airon_adaptation.controller import Controller
from airon_adaptation.integrity import write_json

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--approve-synthetic-test-deployment", action="store_true")
    args = parser.parse_args()
    report_path = Path(args.report).absolute()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = {"schema": "airon-p0-052-acceptance/v1", "overall": "INCOMPLETE", "fixture": False,
              "gates": {}, "limitations": [
                  "CPU synthetic classification only; no enterprise model quality claim",
                  "Application signatures are not independent execution attestations",
                  "This driver does not prove isolated controller or complete wheelhouse installation",
                  "No GPU, GGUF, Ollama adapter deployment or AIP integration qualification"]}
    ctl = Controller(args.root)
    def invoke(operation, **params):
        return ctl.call(operation, params, actor="local-operator", role="operator")
    def review(operation, **params):
        return ctl.call(operation, params, actor="synthetic-test-reviewer", role="reviewer")
    code = 2
    try:
        state = invoke("status")
        job = state["job"][-1]
        report["baseline"] = invoke("infer", dataset_id=job["dataset_id"])
        report["gates"]["baseline_inference"] = "PASS"
        invoke("start_training", job_id=job["id"])
        deadline = time.monotonic()+960
        while time.monotonic() < deadline:
            job = invoke("get_training_status", job_id=job["id"])
            if job["status"] not in {"RUNNING", "CREATED"}:
                break
            time.sleep(.5)
        report["training"] = job
        if job["status"] != "SUCCEEDED":
            raise RuntimeError("Training did not succeed: "+job["status"])
        report["gates"]["real_training"] = "PASS"
        candidate = invoke("register_checkpoint", job_id=job["id"])
        report["candidate"] = candidate
        evaluation = invoke("evaluate_candidate", candidate_id=candidate["id"])
        report["evaluation"] = evaluation
        report["gates"]["improvement_without_regression"] = "PASS" if evaluation["passed"] else "FAIL"
        if not evaluation["passed"]:
            raise RuntimeError("Strict improvement/regression gate failed; deployment remains blocked")
        report["export"] = invoke("export_model", candidate_id=candidate["id"])
        report["gates"]["export"] = "PASS"
        approval = invoke("request_deployment", candidate_id=candidate["id"], evaluation_id=evaluation["id"])
        if not args.approve_synthetic_test_deployment:
            raise RuntimeError("Awaiting human approval; use console for review or explicit synthetic-test flag")
        review("approve_deployment", approval_id=approval["id"], decision="APPROVED")
        report["deployment"] = review("activate_model", approval_id=approval["id"])
        try:
            report["adapted_inference"] = invoke("infer", dataset_id=job["dataset_id"])
        finally:
            report["rollback"] = review("rollback_model")
        report["restored_inference"] = invoke("infer", dataset_id=job["dataset_id"])
        before = report["baseline"]["result"]["rows"]
        restored = report["restored_inference"]["result"]["rows"]
        if [(r["prompt_sha256"], r["predicted"]) for r in before] != [(r["prompt_sha256"], r["predicted"]) for r in restored]:
            raise RuntimeError("Restored predictions do not match baseline")
        report["gates"]["activation_and_rollback"] = "PASS"
        report["overall"] = "PASS_SCOPED_CPU_EXPERIMENT"
        code = 0
    except Exception as exc:
        report["failure"] = str(exc)
    finally:
        report["evidence"] = invoke("evidence")
        write_json(report_path, report)
        ctl.close()
    print(json.dumps({"overall": report["overall"], "report": str(report_path), "gates": report["gates"]}))
    raise SystemExit(code)


if __name__ == "__main__":
    main()
