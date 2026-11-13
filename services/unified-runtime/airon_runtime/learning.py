"""Deterministic research policy. Recommendations confer no authority."""
from dataclasses import dataclass
from airon_adaptation.integrity import Rejected

@dataclass(frozen=True)
class Opportunity:
    verified: bool
    source_available: bool = False
    factual_change: bool = False
    typed_rule: bool = False
    existing_capability: bool = False
    approved_training_rows: int = 0
    language_error: bool = False

def decide(o: Opportunity):
    if any(type(getattr(o, k)) is not bool for k in (
        "verified","source_available","factual_change","typed_rule","existing_capability","language_error")):
        raise Rejected("Learning flags must be booleans")
    if type(o.approved_training_rows) is not int or not 0 <= o.approved_training_rows <= 1000:
        raise Rejected("Learning sample count outside policy")
    if not o.verified:
        route, reason = "EXPERT", "Unverified output cannot become trusted memory"
    elif o.factual_change and o.source_available:
        route, reason = "RETRIEVAL", "Version the approved source"
    elif o.typed_rule and o.source_available:
        route = "UPDATE_CAPABILITY" if o.existing_capability else "PROPOSE_CAPABILITY"
        reason = "Typed rule requires signed independent tests and separate approval"
    elif o.language_error and o.approved_training_rows >= 32:
        route, reason = "ADAPTER", "Isolated training; evaluation and approval remain mandatory"
    else:
        route, reason = "EXPERT", "Insufficient verified evidence for an automated route"
    return {"policy":"airon-learning-rules/v1","route":route,"reason":reason,
            "automatically_authorized":False}
