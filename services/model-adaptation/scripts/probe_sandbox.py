"""Genuine isolated Soup dataset operation; no training capability claim."""
import argparse
import json
from airon_adaptation.controller import Controller

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--root", required=True)
args = parser.parse_args()
ctl = Controller(args.root)
try:
    job = ctl.call("status", {}, actor="probe", role="operator")["job"][-1]
    path, result = ctl._execute(job, "probe")
    print(json.dumps({"result": result, "path": str(path)}))
finally:
    ctl.close()
