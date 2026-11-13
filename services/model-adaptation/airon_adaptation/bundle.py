"""Reuse Soup's bundle assembler; independently verify every member before use.

No extraction is performed. The caller must supply an externally trusted key and
signed whole-archive digest; a self-supplied key is not a trust anchor.
"""
import hashlib
import json
import re
import tarfile
from pathlib import Path, PurePosixPath
from .evidence import seal, verify
from .integrity import Rejected, file_hash, manifest, write_json
from .worker import upstream_identity

MAX_BYTES = 4 * 1024**3
MAX_FILES = 10000


def verify_archive(path, attestation, trusted_public_key):
    path = Path(path)
    payload = verify(attestation, trusted_public_key)
    if payload.get("schema") != "airon-offline-bundle/v1":
        raise Rejected("Unknown bundle attestation")
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise Rejected("Invalid bundle file")
    if file_hash(path) != payload.get("archive_sha256"):
        raise Rejected("Archive digest mismatch")
    seen, observed, expected, total = set(), {}, None, 0
    with tarfile.open(path, mode="r:") as archive:
        for member in archive:
            name = member.name
            parts = PurePosixPath(name)
            if (not member.isfile() or name in seen or parts.is_absolute()
                    or ".." in parts.parts or "\\" in name or ":" in name
                    or not name or len(name) > 1024):
                raise Rejected("Unsafe or duplicate archive member")
            seen.add(name)
            if len(seen) > MAX_FILES or member.size < 0:
                raise Rejected("Archive member limit")
            total += member.size
            if total > MAX_BYTES:
                raise Rejected("Archive size limit")
            stream = archive.extractfile(member)
            if stream is None:
                raise Rejected("Unreadable member")
            with stream:
                if name == "manifest.json":
                    if member.size > 4 * 1024 * 1024:
                        raise Rejected("Manifest too large")
                    raw = json.loads(stream.read())
                    entries = raw.get("files")
                    if not isinstance(entries, list):
                        raise Rejected("Invalid manifest")
                    expected = {}
                    for entry in entries:
                        if (not isinstance(entry, dict) or set(entry) != {"name", "size", "sha256"}
                                or not isinstance(entry["name"], str) or entry["name"] in expected
                                or type(entry["size"]) is not int or entry["size"] < 0
                                or not isinstance(entry["sha256"], str)
                                or not re.fullmatch("[a-f0-9]{64}", entry["sha256"])):
                            raise Rejected("Invalid manifest entry")
                        expected[entry["name"]] = {"size": entry["size"], "sha256": entry["sha256"]}
                else:
                    h = hashlib.sha256()
                    count = 0
                    for chunk in iter(lambda: stream.read(1024*1024), b""):
                        count += len(chunk)
                        h.update(chunk)
                    observed[name] = {"size": count, "sha256": h.hexdigest()}
    if expected is None or not observed or observed != expected:
        raise Rejected("Bundle members differ from declared complete inventory")
    return {"valid": True, "members": len(observed), "bytes": sum(v["size"] for v in observed.values()),
            "archive_sha256": payload["archive_sha256"], "level": "APPLICATION_SIGNED_BUNDLE",
            "dependency_closure": "REQUIRES_FRESH_OFFLINE_INSTALL_TEST"}


def build_bundle(model, datasets, wheelhouse, output, signer):
    from soup_cli.utils.airgap_bundle import AirgapBundlePlan, build_airgap_bundle
    source = upstream_identity()
    manifest(model, model=True)
    for dataset in datasets:
        manifest(dataset)
    wheels = manifest(wheelhouse)
    if not any(name.endswith(".whl") for name in wheels):
        raise Rejected("A nonempty prepared wheelhouse is required")
    if "requirements.lock" not in wheels:
        raise Rejected("Hash-locked offline requirements are required")
    output = Path(output)
    if output.exists() or output.with_suffix(".attestation.json").exists():
        raise Rejected("Bundle output already exists")
    plan = AirgapBundlePlan(output=str(output), model_dir=str(model),
        dataset_dirs=tuple(str(p) for p in datasets), wheel_dirs=(str(wheelhouse),),
        kernel_dirs=(), bundle_size_cap_bytes=MAX_BYTES,
        repro_receipt={"schema": "airon-preparation/v1", "soup": source,
                       "os_prerequisites": ["matching Linux/Python ABI", "bubblewrap", "util-linux unshare"],
                       "dependency_closure": "NOT_YET_TESTED"})
    build_airgap_bundle(plan)
    attestation = seal({"schema": "airon-offline-bundle/v1", "archive_sha256": file_hash(output),
                        "soup": source, "claim": "byte integrity, not successful offline installation"}, signer)
    result = verify_archive(output, attestation, signer.public_key().public_bytes_raw())
    write_json(output.with_suffix(".attestation.json"), attestation)
    return result
