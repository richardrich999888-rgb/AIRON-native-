"""Bundle integrity tests use tiny data fixtures, never pretrained weights."""
import io
import json
import tarfile
from pathlib import Path
from unittest.mock import patch
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from airon_adaptation.bundle import build_bundle, verify_archive
from airon_adaptation.evidence import seal
from airon_adaptation.integrity import Rejected, file_hash, write_json


def make_archive(tmp_path, entries, key):
    path = tmp_path/"bad.tar"
    with tarfile.open(path, "w") as tar:
        for name, contents, kind in entries:
            member = tarfile.TarInfo(name)
            member.type = kind
            if kind == tarfile.SYMTYPE:
                member.linkname = "/etc/passwd"
                tar.addfile(member)
            else:
                raw = contents.encode()
                member.size = len(raw)
                tar.addfile(member, io.BytesIO(raw))
    return path, seal({"schema": "airon-offline-bundle/v1", "archive_sha256": file_hash(path)}, key)


@pytest.mark.parametrize("name,kind", [("../escape", tarfile.REGTYPE), ("/absolute", tarfile.REGTYPE),
                                       ("link", tarfile.SYMTYPE), ("windows\\escape", tarfile.REGTYPE)])
def test_signed_but_unsafe_archive_rejected(tmp_path, name, kind):
    key = Ed25519PrivateKey.generate()
    path, signature = make_archive(tmp_path, [(name, "unsafe", kind)], key)
    with pytest.raises(Rejected):
        verify_archive(path, signature, key.public_key().public_bytes_raw())


def test_signed_manifest_cannot_hide_undeclared_bytes(tmp_path):
    key = Ed25519PrivateKey.generate()
    path, signature = make_archive(tmp_path, [
        ("manifest.json", json.dumps({"files": []}), tarfile.REGTYPE),
        ("unexpected.txt", "payload", tarfile.REGTYPE)], key)
    with pytest.raises(Rejected):
        verify_archive(path, signature, key.public_key().public_bytes_raw())


def test_real_soup_bundle_roundtrip_and_tamper(tmp_path, monkeypatch):
    pytest.importorskip("soup_cli")
    monkeypatch.chdir(tmp_path)
    for folder in ("model", "dataset", "wheels"):
        (tmp_path/folder).mkdir()
    write_json(tmp_path/"model/config.json", {"model_type": "llama"})
    (tmp_path/"model/model.safetensors").write_bytes(b"FIXTURE-NOT-MODEL")
    (tmp_path/"dataset/records.json").write_text("[]")
    (tmp_path/"wheels/fixture.whl").write_bytes(b"FIXTURE-NOT-WHEEL")
    (tmp_path/"wheels/requirements.lock").write_text("# Fixture; no closure claim\n")
    key = Ed25519PrivateKey.generate()
    result = build_bundle(tmp_path/"model", [tmp_path/"dataset"], tmp_path/"wheels", tmp_path/"bundle.tar", key)
    assert result["valid"] and result["dependency_closure"] == "REQUIRES_FRESH_OFFLINE_INSTALL_TEST"
    signature = json.loads((tmp_path/"bundle.attestation.json").read_text())
    path = tmp_path/"bundle.tar"
    with path.open("ab") as stream:
        stream.write(b"tamper")
    with pytest.raises(Rejected):
        verify_archive(path, signature, key.public_key().public_bytes_raw())
