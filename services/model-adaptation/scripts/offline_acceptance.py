"""Run provisioning and acceptance in an already isolated controller namespace."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from airon_adaptation.integrity import write_json
from airon_adaptation.worker import isolation_probe, upstream_identity

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--root", required=True)
parser.add_argument("--assets", required=True)
parser.add_argument("--report", required=True)
parser.add_argument("--parent-netns", required=True)
args = parser.parse_args()
report_path = Path(args.report)
scripts = Path(__file__).resolve().parent
isolation = isolation_probe(args.parent_netns, require_private_mounts=False)
upstream = upstream_identity()
subprocess.run([sys.executable, "-m", "pip", "check"], check=True)
subprocess.run([sys.executable, str(scripts/"provision.py"), "--root", args.root, "--assets", args.assets,
                "--local-assets", "--approve-synthetic-data"], check=True)
result = subprocess.run([sys.executable, str(scripts/"run_acceptance.py"), "--root", args.root,
                         "--report", args.report, "--approve-synthetic-test-deployment"])
report = json.loads(report_path.read_text())
report["controller_isolation"] = isolation
report["offline_installed_soup"] = upstream
report["runtime_prefix"] = sys.prefix
report["offline_install_evidence"] = "See fresh venv and --require-hashes install step in the same CI run"
report["limitations"] = [x for x in report["limitations"] if "does not prove isolated controller" not in x]
report["limitations"].append("Namespace isolation on this runner; not physical/customer-site air-gap accreditation")
write_json(report_path, report)
print("OFFLINE_ACCEPTANCE_REPORT="+json.dumps(report))
raise SystemExit(result.returncode)
