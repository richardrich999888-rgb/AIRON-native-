"""Extend the unchanged P0-052 wheelhouse with a hash-locked AIRON wheel.

Use a qualification venv with airon-adaptation installed and unified-runtime
on PYTHONPATH, not installed from PyPI. Every installed third-party wheel is
inventoried by the original packager. Network use occurs only in this step.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from airon_adaptation.integrity import file_hash, write_json

p=argparse.ArgumentParser();p.add_argument("--output",required=True);a=p.parse_args()
repo=Path(__file__).resolve().parents[3];out=Path(a.output).absolute()
subprocess.run([sys.executable,repo/"services/model-adaptation/scripts/prepare_wheelhouse.py",
                "--output",out,"--source",repo/"services/model-adaptation"],check=True)
subprocess.run([sys.executable,"-m","pip","wheel","--no-deps","--no-build-isolation",
                "-w",out,repo/"services/unified-runtime"],check=True)
wheels=list(out.glob("airon_runtime-*.whl"))
if len(wheels)!=1:raise RuntimeError("Ambiguous AIRON wheel")
w=wheels[0];sha=file_hash(w)
with (out/"requirements.lock").open("a") as f:f.write("airon-runtime==0.1.0 --hash=sha256:"+sha+"\n")
index=json.loads((out/"wheelhouse.json").read_text());index["files"][w.name]={"sha256":sha,"bytes":w.stat().st_size}
write_json(out/"wheelhouse.json",index)
licences=json.loads((out/"licences.json").read_text())
licences["airon-runtime==0.1.0"]={"license_expression":"MIT","notice_sha256":file_hash(repo/"LICENSE"),
    "scope":"New AIRON code only; AIP proprietary binaries are separately provisioned and not included"}
write_json(out/"licences.json",licences)
