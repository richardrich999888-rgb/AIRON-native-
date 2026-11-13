"""Application attestations, not AIP EvidencePackets or observed execution."""
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from .integrity import canonical, digest, Rejected

DOMAIN = b"AIRON-MODEL-LIFECYCLE-v1\x00"


def seal(payload, key):
    return {"payload": payload, "sha256": digest(payload),
            "signature": base64.b64encode(key.sign(DOMAIN + canonical(payload))).decode()}


def verify(record, trusted_public_key):
    try:
        if set(record) != {"payload", "sha256", "signature"}:
            raise ValueError("Unknown envelope")
        if digest(record["payload"]) != record["sha256"]:
            raise ValueError("Digest mismatch")
        Ed25519PublicKey.from_public_bytes(trusted_public_key).verify(
            base64.b64decode(record["signature"], validate=True), DOMAIN + canonical(record["payload"]))
        return record["payload"]
    except Exception as exc:
        raise Rejected("Invalid application signature or digest") from exc


def verify_chain(records, trusted_public_key, expected_head=None):
    previous = "GENESIS"
    for index, record in enumerate(records, 1):
        payload = verify(record, trusted_public_key)
        if payload["sequence"] != index or payload["previous"] != previous:
            raise Rejected("Broken event chain")
        previous = digest(record)
    if expected_head is not None and previous != expected_head:
        raise Rejected("Event head differs from external anchor")
    return {"valid": True, "events": len(records), "head": previous,
            "level": "APPLICATION_SIGNED", "independent_execution": "CANNOT_PROVE",
            "truncation_checked": expected_head is not None}
