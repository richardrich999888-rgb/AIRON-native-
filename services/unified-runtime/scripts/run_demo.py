"""Execute the synthetic vertical slice and preserve every observed gate."""
import argparse
import copy
import json
import os
import platform
import subprocess
import time
from pathlib import Path
from airon_runtime.core import Core
from airon_adaptation.integrity import digest, write_json
from airon_adaptation.evidence import verify_chain

FIXTURES=Path(__file__).resolve().parents[1]/"fixtures"

def signed_suite(core):
    cases=core.root/"synthetic-suite-cases.jsonl"
    rows=json.loads((FIXTURES/"development-cases.json").read_text())
    cases.write_text(''.join(json.dumps({**row,"label":row["expected"]})+'\n' for row in rows))
    target=core.root/"synthetic-suite.json"
    subprocess.run([core.config["native"]["cli"]["path"],"suite-sign","--key",core.config["suite_key"],
        "--cases",str(cases),"--suite-id","p056-frozen-development","--tenant","synthetic-plant",
        "--task","cooling maintenance","--out",str(target)],check=True,capture_output=True)
    return json.loads(target.read_text())

def run_demo(root,report_path,backend):
    report_path=Path(report_path)
    report={"schema":"airon-p056-demo/v1","source_revision":os.environ.get("AIRON_SOURCE_COMMIT"),
        "hardware":{"platform":platform.platform(),"cpus":os.cpu_count(),"affinity":sorted(os.sched_getaffinity(0)),
            "meminfo":Path('/proc/meminfo').read_text().splitlines()[0],"gpu":False},
        "gates":{},"overall":"INCOMPLETE","independent_execution":"CANNOT_PROVE",
        "approval_scope":"Scripted synthetic test with distinct signer roles; same administrator and test author",
        "evaluation_scope":"Frozen development cases; not an untouched independent holdout"}
    core=Core(root);operator=core.principal("operator");reviewer=core.principal("reviewer")
    def call(op,**params):return core.call(operator,op,params)
    def review(op,**params):return core.call(reviewer,op,params)
    def step(name,fn,requires=()):
        if any(report["gates"][x]["status"]!="PASS" for x in requires):
            report["gates"][name]={"status":"BLOCKED","requires":list(requires)};write_json(report_path,report);return None
        print("P056_STEP="+name,flush=True);start=time.monotonic()
        try:
            result=fn()
            report["gates"][name]={"status":"PASS","result":result,"wall_s":time.monotonic()-start}
            return result
        except Exception as e:
            report["gates"][name]={"status":"FAIL","error":str(e),"wall_s":time.monotonic()-start}
            return None
        finally:write_json(report_path,report)
    def check(value,predicate,message):
        if not predicate(value):raise RuntimeError(message+": "+json.dumps(value))
        return value
    try:
        step("01_docling_import",lambda:call("ingest",text=(FIXTURES/"maintenance.md").read_text().strip(),
            doc_id="maintenance",title="Synthetic maintenance manual",classification="restricted"))
        step("02_local_index",lambda:check(call("search",question="cooling inspection"),lambda x:len(x["result"]["hits"])==1,"Missing index"),("01_docling_import",))
        def access():
            out={}
            for actor in ("viewer","foreign"):
                out[actor]=core.call(core.principal(actor),"ask",{"question":"When should we inspect the cooling assembly?","backend":backend})
                if out[actor]["model_calls"]!=0 or out[actor]["outcome"]!="ABSTAINED":raise RuntimeError("Unauthorized model context")
            return out
        step("03_access_control",access,("02_local_index",))
        step("04_grounded_local_answer",lambda:check(call("ask",question="When should we inspect the cooling assembly?",backend=backend),
            lambda x:x["outcome"]=="ANSWERED" and x["model_calls"]==1,"Grounded answer unavailable"),("03_access_control",))
        step("05_learning_route",lambda:review("learn",verified=True,source_available=True,typed_rule=True))
        cap=json.loads((FIXTURES/"cooling-capability.json").read_text())
        proposed=step("06_propose",lambda:call("capability",action="propose",payload={"capability":cap}),("02_local_index",))
        h=proposed[0]["hash"] if proposed else None
        suite=signed_suite(core)
        step("07_signed_validation",lambda:check(call("capability",action="validate",payload={"hash":h,"suite":suite}),
            lambda x:x[0]["passed"],"Native suite rejected"),("06_propose",))
        step("08_expert_approval",lambda:review("capability",action="approve",payload={"hash":h}),("07_signed_validation",))
        step("09_activate_capability",lambda:review("capability",action="activate",payload={"hash":h}),("08_expert_approval",))
        step("10_deterministic_execution",lambda:check(call("execute",capability_id=cap["id"],text="cooling hours 210 vibration 2"),
            lambda x:x["result"]["outcome"].get("label")=="INSPECT" and x["result"]["cost"]["model_calls"]==0,
            "Deterministic task did not pass"),("09_activate_capability",))
        step("11_outcome_memory",lambda:check(core.control._all("outcome"),lambda x:bool(x) and not x[-1]["trusted_fact"],"Outcome memory absent"),("10_deterministic_execution",))
        step("12_adapter_route",lambda:review("learn",verified=True,language_error=True,approved_training_rows=102))
        before=step("13a_baseline_model",lambda:call("adapt",operation="infer",params={"dataset_id":core.config["dataset_id"]}))
        def train():
            value=call("adapt",operation="start_training",params={"job_id":core.config["job_id"]})
            deadline=time.monotonic()+960
            while time.monotonic()<deadline:
                value=call("adapt",operation="get_training_status",params={"job_id":core.config["job_id"]})
                if value["status"] not in {"RUNNING","CREATED"}:break
                time.sleep(.5)
            return check(value,lambda x:x["status"]=="SUCCEEDED","Training gate failed")
        step("13b_real_soup_training",train,("13a_baseline_model",))
        candidate=step("13c_register_adapter",lambda:call("adapt",operation="register_checkpoint",params={"job_id":core.config["job_id"]}),("13b_real_soup_training",))
        ev=step("14_evaluate",lambda:check(call("adapt",operation="evaluate_candidate",params={"candidate_id":candidate["id"]}),lambda x:x["passed"],"Candidate rejected"),("13c_register_adapter",))
        def approve():
            a=call("adapt",operation="request_deployment",params={"candidate_id":candidate["id"],"evaluation_id":ev["id"]})
            review("adapt",operation="approve_deployment",params={"approval_id":a["id"],"decision":"APPROVED"})
            return a
        approval=step("15_model_review",approve,("14_evaluate",))
        activated=step("16_activate_model",lambda:review("adapt",operation="activate_model",params={"approval_id":approval["id"]}),("15_model_review",))
        try:
            step("17_adapted_task",lambda:call("adapt",operation="infer",params={"dataset_id":core.config["dataset_id"]}),("16_activate_model",))
        finally:
            step("18_restore_model",lambda:review("adapt",operation="rollback_model",params={}),("16_activate_model",))
        def restored():
            result=call("adapt",operation="infer",params={"dataset_id":core.config["dataset_id"]})
            preds=lambda x:[(r["prompt_sha256"],r["predicted"]) for r in x["result"]["rows"]]
            return check(result,lambda x:preds(x)==preds(before),"Restored predictions changed")
        step("18b_verify_restored_model",restored,("18_restore_model",))
        def rollback_cap():
            v2=copy.deepcopy(cap);v2["version"]=2
            h2=call("capability",action="propose",payload={"capability":v2})[0]["hash"]
            check(call("capability",action="validate",payload={"hash":h2,"suite":suite}),lambda x:x[0]["passed"],"Second capability rejected")
            review("capability",action="approve",payload={"hash":h2})
            review("capability",action="activate",payload={"hash":h2})
            review("capability",action="rollback",payload={"hash":h})
            return check(call("execute",capability_id=cap["id"],text="cooling hours 210 vibration 2"),
                         lambda x:x["result"]["capability_hash"]==h,"Wrong restored capability")
        step("18c_capability_rollback",rollback_cap,("10_deterministic_execution",))
        evidence=review("evidence")
        report["evidence"]=evidence
        def verify():
            return {k:verify_chain(v["records"],bytes.fromhex(v["public_key_hex"]),v["verification"]["head"]) for k,v in evidence.items()}
        step("19_offline_evidence",verify)
        report["overall"]="PASS_SYNTHETIC_VERTICAL_SLICE" if all(g["status"]=="PASS" for g in report["gates"].values()) else "INCOMPLETE"
    finally:
        write_json(report_path,report);core.close()
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--report",required=True)
    p.add_argument("--backend",choices=("adaptation","llama"),default="adaptation")
    p.add_argument("--approve-synthetic-test-deployment",action="store_true",required=True)
    a=p.parse_args();r=run_demo(a.root,a.report,a.backend)
    print(json.dumps({"overall":r["overall"],"gates":{k:v["status"] for k,v in r["gates"].items()}}))
    raise SystemExit(0 if r["overall"].startswith("PASS") else 2)
