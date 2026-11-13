"""Bounded synthetic corpus retrieval. Authorization precedes model execution."""
import re
from .integrity import Rejected


def normalized(value):
    return re.sub("[^a-z0-9]", "", value.lower())


def validate_documents(docs):
    if not isinstance(docs, list) or not 1 <= len(docs) <= 4:
        raise Rejected("Only the bounded synthetic demonstration corpus is supported")
    ids = set()
    for doc in docs:
        if not isinstance(doc, dict) or set(doc) != {"id", "title", "category", "version", "roles", "body", "questions"}:
            raise Rejected("Invalid document schema")
        if not isinstance(doc["id"], str) or not re.fullmatch("[A-Z]{2,4}-[0-9]{3}", doc["id"]) or doc["id"] in ids:
            raise Rejected("Invalid or duplicate document identity")
        ids.add(doc["id"])
        for field in ("title", "category", "version", "body"):
            if not isinstance(doc[field], str) or not 1 <= len(doc[field]) <= 1000:
                raise Rejected("Invalid document text")
        if not isinstance(doc["roles"], list) or not doc["roles"] or any(
                role not in {"analyst", "operator", "admin"} for role in doc["roles"]):
            raise Rejected("Invalid document roles")
        if not isinstance(doc["questions"], list) or not 1 <= len(doc["questions"]) <= 8 or any(
                not isinstance(q, str) or not 1 <= len(q) <= 500 for q in doc["questions"]):
            raise Rejected("Invalid supported questions")


def retrieve(docs, question, enabled, access_role):
    validate_documents(docs)
    if not isinstance(question, str) or not 1 <= len(question.strip()) <= 500:
        raise Rejected("Question must contain 1–500 characters")
    if (not isinstance(enabled, list) or len(enabled) > 4 or
            any(not isinstance(x, str) or x not in {d["id"] for d in docs} for x in enabled)):
        raise Rejected("Invalid document selection")
    if access_role not in {"analyst", "operator", "admin"}:
        raise Rejected("Unrecognized document role")
    source = next((d for d in docs if d["id"] in enabled and
                   any(normalized(q) == normalized(question) for q in d["questions"])), None)
    if source is None:
        return {"outcome": "ABSTAINED", "answer": "The approved documents do not support that question.",
                "sources": [], "model_called": False}
    if access_role not in source["roles"]:
        return {"outcome": "DENIED", "answer": "Your session cannot access this document.",
                "sources": [], "model_called": False}
    return {"outcome": "SOURCE_FOUND", "source": source}


def approved_quote(text, source):
    """Release only the full approved text; discard any model-added framing."""
    if not isinstance(text, str):
        return None
    # Formatting changes cannot add facts: output is the original approved bytes.
    expected = " ".join(source.split())
    return source if expected in " ".join(text.split()) else None
