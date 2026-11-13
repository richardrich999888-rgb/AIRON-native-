"""Verify exported records using separately supplied trusted anchors."""
import argparse
import json
from pathlib import Path
from airon_adaptation.evidence import verify_chain

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("report")
parser.add_argument("--trusted-public-key", required=True)
parser.add_argument("--expected-head", required=True)
args = parser.parse_args()
payload = json.loads(Path(args.report).read_text())
evidence = payload.get("evidence", payload)
key = bytes.fromhex(args.trusted_public_key)
if len(key) != 32 or len(args.expected_head) != 64:
    parser.error("A 32-byte public key and SHA-256 chain head are required")
# Never take the trust anchor from the file being verified.
result = verify_chain(evidence["records"], key, args.expected_head)
print(json.dumps(result))
