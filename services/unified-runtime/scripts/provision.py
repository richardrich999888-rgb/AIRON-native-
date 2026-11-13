"""Explicit synthetic provisioning. No download code is part of the runtime."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from airon_adaptation.controller import Controller
from airon_adaptation.integrity import file_hash, manifest, write_json

ROOT = Path(__file__).resolve().parents[3]
CAPABILITY = "airon.cooling.inspection"

def pin(path):
    p=Path(path).absolute()
    return {"path":str(p),"sha256":file_hash(p)}

def private_json(path,value):
    write_json(path,value)
    path.chmod(0o600)

def provision(root,assets,aip_dir,bin_dir,llama=None,gguf=None):
    root=Path(root).absolute(); root.mkdir(mode=0o700)
    native=root/"native"; native.mkdir(mode=0o700)
    bin_dir=Path(bin_dir).absolute(); aip_dir=Path(aip_dir).absolute()
    cli=bin_dir/"syntriass"
    keys=root/"keys";keys.mkdir(mode=0o700)
    for name in ("suite-expert","reviewer"):
        subprocess.run([cli,"keygen","--id",name,"--out",str(keys/(name+".json"))],check=True,capture_output=True)
    expert=json.loads((keys/"suite-expert.json").read_text())
    reviewer=json.loads((keys/"reviewer.json").read_text())
    principals={
        "operator":{"tenant":"synthetic-plant","clearance":"restricted","role":"operator"},
        "reviewer":{"tenant":"synthetic-plant","clearance":"restricted","role":"reviewer"},
        "viewer":{"tenant":"synthetic-plant","clearance":"public","role":"viewer"},
        "foreign":{"tenant":"other-plant","clearance":"restricted","role":"viewer"}}
    identities={}
    for actor,p in principals.items():
        path=root/(actor+".identity.json")
        private_json(path,{"tenant":p["tenant"],"clearance":p["clearance"],"can_ingest":p["role"]=="operator"})
        identities[actor]=pin(path)
    now=int(time.time()*1000)
    config={"state":str(native),"policy_version":"airon-maintenance-v1","security_domain":"airon-local",
        "rag_k":3,"approvers":{"reviewer":reviewer["public_hex"]},"experts":{"suite-expert":expert["public_hex"]},
        "approval_policy":{"authorities":{"reviewer":{
            "expert_id":"reviewer","public_key_sha256":hashlib.sha256(bytes.fromhex(reviewer["public_hex"])).hexdigest(),
            "tenant":"synthetic-plant","security_domain":"airon-local","capability_ids":[CAPABILITY],
            "min_version":1,"max_version":100,"max_clearance":"restricted",
            "valid_from_ms":now-1000,"expires_at_ms":now+86400*1000,"revoked":False}}},
        "profile":"none","python":"/UNAVAILABLE_IN_LIFECYCLE","sidecar_script":"/UNAVAILABLE_IN_LIFECYCLE",
        "llama_server":"/UNAVAILABLE_IN_LIFECYCLE","q4":{"path":"/UNAVAILABLE","sha256":"0"*64},
        "q8":{"path":"/UNAVAILABLE","sha256":"0"*64},"port":18080}
    cfg=root/"native-config.json"; private_json(cfg,config)
    ctl=Controller(root/"adaptation")
    try:
        assets=Path(assets).absolute()
        lock=json.loads((ROOT/"services/model-adaptation/model.lock.json").read_text())
        if manifest(assets,model=True)!=lock["manifest"]: raise RuntimeError("Unapproved model assets")
        model=ctl.import_base(assets,identifier="HuggingFaceTB/SmolLM2-135M-Instruct",
            revision="12fd25f77366fa6b3b4b768ec3050bf629380bac",license_id="Apache-2.0")
        ctl.import_knowledge(ROOT/"website/offline/documents.json")
        rows=json.loads((ROOT/"services/model-adaptation/fixtures/enterprise-routing.json").read_text())
        ds=ctl.call("prepare_dataset",{"rows":rows,"authorization":{"synthetic":True,
            "approved_for_training":True,"license":"CC0-1.0"}},actor="operator",role="operator")
        job=ctl.call("create_training_job",{"base_id":model["id"],"dataset_id":ds["id"],
            "config":{"epochs":3,"lr":.0003,"rank":8,"seed":52}},actor="operator",role="operator")
    finally:ctl.close()
    provision={"schema":"airon-provision/v1","principals":principals,"native_state":str(native),
        "native":{"bridge":pin(bin_dir/"airon-bridge"),"cli":pin(cli),"config":pin(cfg),"identities":identities,
            "source_revision":subprocess.check_output(["git","-C",aip_dir,"rev-parse","HEAD"],text=True).strip()},
        "adaptation_tenant":"synthetic-plant","approver_keys":{"reviewer":pin(keys/"reviewer.json")},
        "dataset_id":ds["id"],"job_id":job["id"],"synthetic_test_authorization":True,
        "suite_key":str(keys/"suite-expert.json")}
    if llama and gguf: provision["llama"]={"binary":pin(llama),"model":pin(gguf)}
    private_json(root/"provision.json",provision)
    return provision

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("root","assets","aip-dir","bin-dir"):p.add_argument("--"+name,required=True)
    p.add_argument("--llama");p.add_argument("--gguf")
    p.add_argument("--approve-synthetic-data",action="store_true",required=True)
    a=p.parse_args();provision(a.root,a.assets,a.aip_dir,a.bin_dir,a.llama,a.gguf)
    print(json.dumps({"root":a.root,"provisioned":True,"synthetic_only":True}))
