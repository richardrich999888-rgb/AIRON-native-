"""Real acceptance driver. No mocked results and no automatic production promotion."""
import argparse
import json
import os
import platform
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
    cpu_info = Path("/proc/cpuinfo").read_text()
    report["hardware"] = {"platform": platform.platform(), "python": platform.python_version(),
        "cpu_model": next((line.split(":", 1)[1].strip() for line in cpu_info.splitlines()
                           if line.startswith("model name")), "unknown"),
        "logical_cpus": os.cpu_count(), "allowed_cpus": sorted(os.sched_getaffinity(0)),
        "mem_total": next((line for line in Path("/proc/meminfo").read_text().splitlines()
                           if line.startswith("MemTotal:")), "unknown"),
        "worker_threads": 2, "gpu_used": False}
    report["source"] = {"head": os.environ.get("AIRON_SOURCE_COMMIT"),
                        "actions_checkout": os.environ.get("GITHUB_SHA")}
    ctl = Controller(args.root)
    def invoke(operation, **params):
        print("ACCEPTANCE_STEP="+operation, flush=True)
        value = ctl.call(operation, params, actor="local-operator", role="operator")
        write_json(report_path.with_suffix(".progress.json"), {"last_completed": operation, "gates": report["gates"]})
        return value
    def review(operation, **params):
        return ctl.call(operation, params, actor="synthetic-test-reviewer", role="reviewer")
    code = 2
    try:
        state = invoke("status")
        job = state["job"][-1]
        report["baseline"] = invoke("infer", dataset_id=job["dataset_id"])
        report["gates"]["baseline_inference"] = "PASS"
        report["knowledge_baseline"] = invoke("query_knowledge",
            question="When should we inspect the cooling assembly?", enabled=["OPS-001"])
        report["knowledge_denied"] = invoke("query_knowledge",
            question="Who approves large supplier payments?", enabled=["FIN-001"])
        report["knowledge_abstained"] = invoke("query_knowledge",
            question="What will revenue be?", enabled=["OPS-001"])
        if not report["knowledge_baseline"]["model_called"]:
            raise RuntimeError("Authorized knowledge query did not invoke the local model")
        if (report["knowledge_denied"]["outcome"] != "DENIED" or report["knowledge_denied"]["model_called"]
                or report["knowledge_abstained"]["outcome"] != "ABSTAINED" or report["knowledge_abstained"]["model_called"]):
            raise RuntimeError("Knowledge access or abstention gate failed")
        report["gates"]["private_knowledge_controls"] = "PASS"
        report["knowledge_answer_quality"] = report["knowledge_baseline"]["outcome"]
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
            report["knowledge_adapted"] = invoke("query_knowledge",
                question="When should we inspect the cooling assembly?", enabled=["OPS-001"])
            if report["knowledge_adapted"]["outcome"] != "ANSWERED":
                raise RuntimeError("Adapted knowledge response regressed; restore original model")
        finally:
            report["rollback"] = review("rollback_model")
        report["restored_inference"] = invoke("infer", dataset_id=job["dataset_id"])
        before = report["baseline"]["result"]["rows"]
        restored = report["restored_inference"]["result"]["rows"]
        if [(r["prompt_sha256"], r["predicted"]) for r in before] != [(r["prompt_sha256"], r["predicted"]) for r in restored]:
            raise RuntimeError("Restored predictions do not match baseline")
        report["gates"]["activation_and_rollback"] = "PASS"
        report["gates"]["adapted_private_knowledge_answer"] = "PASS"
        report["overall"] = "PASS_SCOPED_CPU_EXPERIMENT"
        code = 0
    except Exception as exc:
        report["failure"] = str(exc)
    finally:
        report["evidence"] = invoke("evidence")
        write_json(report_path, report)
        ctl.close()
    print("ACCEPTANCE_REPORT=" + json.dumps(report))
    raise SystemExit(code)


if __name__ == "__main__":
    main()
