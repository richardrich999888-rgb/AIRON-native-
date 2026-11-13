"""Bind retained real reports to source-reviewed hashes, signer keys and chain heads.

These anchors are maintained with the PR, not an independent identity authority.
"""
import json
from pathlib import Path
import pytest
from airon_adaptation.evidence import verify_chain
from airon_adaptation.integrity import file_hash

ROOT = Path(__file__).resolve().parents[3]/"docs/qualification/p0-052"
INDEX = json.loads((ROOT/"EVIDENCE_INDEX.json").read_text())["reports"]


@pytest.mark.parametrize("item", INDEX, ids=[item["path"] for item in INDEX])
def test_retained_report_matches_reviewed_bytes_and_signed_head(item):
    path = ROOT/"evidence"/item["path"]
    assert file_hash(path) == item["sha256"]
    if item["verification"] is not None:
        report = json.loads(path.read_text())
        result = verify_chain(report["evidence"]["records"], bytes.fromhex(item["public_key_hex"]),
                              item["verification"]["head"])
        assert result["valid"] and result["truncation_checked"]
