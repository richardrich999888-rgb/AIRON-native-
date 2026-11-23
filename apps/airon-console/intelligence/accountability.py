"""Operator-authorized, fixed archive verifier. Local run observations are application records."""
import json
from pathlib import Path
import subprocess
from threading import BoundedSemaphore
from uuid import uuid4

from documents import Problem

slots = BoundedSemaphore(1)
TOOL = Path(__file__).resolve().parents[1] / "scripts/local-archive-tool.mjs"


def install(db):
    db.execute("""CREATE TABLE IF NOT EXISTS tool_runs(
        id TEXT PRIMARY KEY, at TEXT NOT NULL, actor TEXT NOT NULL,
        agent TEXT NOT NULL, tool TEXT NOT NULL, report TEXT NOT NULL)""")


def run(db, actor, at):
    if not slots.acquire(blocking=False):
        raise Problem(429, "An archive check is already running.")
    try:
        process = subprocess.run(["node", str(TOOL)], capture_output=True, timeout=30, check=True)
        report = json.loads(process.stdout)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise Problem(503, "The bundled verifier could not complete. Check the Node runtime and replay assets.") from exc
    finally:
        slots.release()
    ident = str(uuid4())
    db.execute("INSERT INTO tool_runs VALUES(?,?,?,?,?,?)",
               (ident, at, actor, "airon.archive-reviewer", "verify.packaged-archives", json.dumps(report)))
    return {"run": ident, "status": "Completed"}


def records(db):
    return [{**dict(row), "report": json.loads(row["report"])} for row in
            db.execute("SELECT * FROM tool_runs ORDER BY rowid DESC LIMIT 100")]
