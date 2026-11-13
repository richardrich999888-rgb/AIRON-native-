"""Test the exact signing-byte boundary; no AIP authority or execution claim."""
import argparse
import base64
import hashlib
import json
import subprocess
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from airon_adaptation.evidence import DOMAIN, verify_chain
from airon_adaptation.integrity import canonical, write_json
from airon_adaptation.worker import isolation_probe

AIP_REVISION = "872dbf375838cff464eb019488c63d948015e9b8"


def prepare(root, report, index):
    approved = next(x for x in json.loads(index.read_text())["reports"] if x["path"] == report.name)
    raw = report.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == approved["sha256"]
    payload = json.loads(raw)
    evidence = payload["evidence"]
    key = bytes.fromhex(approved["public_key_hex"])
    verification = verify_chain(evidence["records"], key, approved["verification"]["head"])
    root.mkdir(parents=True, exist_ok=False)
    (root/"public.key").write_bytes(key)
    (root/"count.txt").write_text(str(len(evidence["records"])))
    for i, record in enumerate(evidence["records"]):
        (root/f"record-{i}.bytes").write_bytes(DOMAIN + canonical(record["payload"]))
        (root/f"record-{i}.sig").write_bytes(base64.b64decode(record["signature"], validate=True))
    # Explicitly public test seed, unrelated to the real report's signer.
    test_key = Ed25519PrivateKey.from_private_bytes(bytes([52])*32)
    (root/"roundtrip-public.key").write_bytes(test_key.public_key().public_bytes_raw())
    (root/"roundtrip.bytes").write_bytes(DOMAIN + canonical({"purpose": "public interop vector", "score": 1.0}))
    write_json(root/"input.json", {"source": payload["source"], "report_sha256": approved["sha256"],
        "public_key_hex": key.hex(), "expected_head": approved["verification"]["head"],
        "verification": verification})


def finish(root, binary, aip, parent_netns, output):
    assert subprocess.check_output(["git", "-C", str(aip), "rev-parse", "HEAD"], text=True).strip() == AIP_REVISION
    subprocess.run(["git", "-C", str(aip), "diff", "--exit-code"], check=True)
    isolation = isolation_probe(parent_netns, require_private_mounts=False)
    result = subprocess.run([str(binary), str(root)], check=True, capture_output=True, text=True)
    observed = json.loads(result.stdout)
    count = int((root/"count.txt").read_text())
    assert observed == {"real_records_verified": count, "tamper_rejections": count*3, "aip_roundtrip_signed": True}
    test_key = Ed25519PrivateKey.from_private_bytes(bytes([52])*32).public_key()
    test_key.verify((root/"roundtrip-aip.sig").read_bytes(), (root/"roundtrip.bytes").read_bytes())
    report = {"schema": "airon-aip-raw-signature-contract/v1", "passed": True,
        "aip_revision": AIP_REVISION, "aip_source_unmodified": True,
        "rustc": subprocess.check_output(["rustup", "run", "1.90.0", "rustc", "--version"], text=True).strip(),
        "aip_cargo_lock_sha256": hashlib.sha256((aip/"aip-standalone/Cargo.lock").read_bytes()).hexdigest(),
        "contract_binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "input": json.loads((root/"input.json").read_text()), **observed,
        "python_verified_aip_signature": True, "isolation": isolation,
        "assurance": "APPLICATION_SIGNED", "independent_execution": "CANNOT_PROVE",
        "scope": "Raw byte interoperability only; Python prepares canonical bytes. No Rust JSON canonicalization, AIP EvidencePacket, delegation, signer custody, Sniffer Dog or production integration qualification.",
        "licensing": "Test-only separate proprietary AIP checkout; no AIP source/binary redistribution or production dependency."}
    write_json(output, report)
    print("AIP_SIGNATURE_CONTRACT="+json.dumps(report))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--root", type=Path, required=True)
    prep.add_argument("--report", type=Path, required=True)
    prep.add_argument("--index", type=Path, required=True)
    done = sub.add_parser("finish")
    for name in ("root", "binary", "aip", "output"):
        done.add_argument("--"+name, type=Path, required=True)
    done.add_argument("--parent-netns", required=True)
    args = vars(parser.parse_args())
    operation = args.pop("operation")
    (prepare if operation == "prepare" else finish)(**args)


if __name__ == "__main__":
    main()
