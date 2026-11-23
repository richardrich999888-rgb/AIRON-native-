"""Workspace-scoped operation records. No network exporter or prompt payloads."""
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

try:
    from opentelemetry.sdk.trace import TracerProvider
    tracer = TracerProvider().get_tracer("syntriass.airon.local")
except ImportError:
    tracer = None

current = ContextVar("airon_measurements", default=None)


@contextmanager
def trace(operation, actor):
    records = []
    token = current.set(records)
    try:
        with span(operation, actor) as root:
            yield records, root
    finally:
        current.reset(token)


@contextmanager
def span(operation, actor):
    start = perf_counter()
    record = dict(operation=operation, actor=actor, at=datetime.now(timezone.utc).isoformat(),
                  outcome="Completed", model=None, inputTokens=None, outputTokens=None, document=None)
    records = current.get()
    if records is not None:
        records.append(record)
    try:
        if tracer:
            with tracer.start_as_current_span(operation, record_exception=False, set_status_on_exception=False) as active:
                ctx = active.get_span_context()
                record.update(traceId=format(ctx.trace_id, "032x"), spanId=format(ctx.span_id, "016x"))
                yield record
                for key in ("outcome", "model", "inputTokens", "outputTokens", "document"):
                    if record[key] is not None:
                        active.set_attribute("airon." + key, record[key])
        else:
            record.update(traceId=records[0].get("traceId") if records else None, spanId=uuid4().hex[:16])
            record["traceId"] = record["traceId"] or uuid4().hex
            yield record
    except Exception:
        record["outcome"] = "Failed"
        raise
    finally:
        record["durationMs"] = round((perf_counter() - start) * 1000, 3)


def install(db):
    db.executescript("""
      CREATE TABLE IF NOT EXISTS operations(id INTEGER PRIMARY KEY,at TEXT NOT NULL,
       actor TEXT NOT NULL,operation TEXT NOT NULL,outcome TEXT NOT NULL,durationMs REAL NOT NULL,
       model TEXT,inputTokens INTEGER,outputTokens INTEGER,document INTEGER,traceId TEXT NOT NULL,spanId TEXT NOT NULL);
      CREATE INDEX IF NOT EXISTS operations_actor ON operations(actor,id);
      CREATE INDEX IF NOT EXISTS operations_kind ON operations(operation,id);
    """)


def save(db, records):
    db.executemany("""INSERT INTO operations(at,actor,operation,outcome,durationMs,model,inputTokens,
        outputTokens,document,traceId,spanId) VALUES(:at,:actor,:operation,:outcome,:durationMs,:model,
        :inputTokens,:outputTokens,:document,:traceId,:spanId)""", records)


def read(db, actor, workspace_wide, kind=None):
    conditions, params = [], []
    if not workspace_wide:
        conditions.append("actor=?")
        params.append(actor)
    if kind:
        conditions.append("operation=?")
        params.append(kind)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    records = [dict(row) for row in db.execute("SELECT * FROM operations" + where + " ORDER BY id DESC LIMIT 100", params)]
    summary = dict(db.execute("""SELECT count(*) AS operations,
        count(CASE WHEN operation='model.inference' THEN 1 END) AS modelRequests,
        sum(inputTokens) AS inputTokens,sum(outputTokens) AS outputTokens,
        count(CASE WHEN operation='model.inference' AND outputTokens IS NOT NULL THEN 1 END) AS metered,
        avg(CASE WHEN operation='model.inference' THEN durationMs END) AS modelLatencyMs,
        count(CASE WHEN outcome IN ('Failed','Withheld','Unavailable') THEN 1 END) AS unsuccessful
        FROM operations""" + where, params).fetchone())
    models = []
    if kind == "model.inference":
        models = [dict(row) for row in db.execute("""SELECT model,count(*) AS requests,
            sum(inputTokens) AS inputTokens,sum(outputTokens) AS outputTokens,
            avg(durationMs) AS latencyMs FROM operations""" + where +
            " GROUP BY model ORDER BY requests DESC,model", params)]
    return dict(models=models, source="Local Runtime", scope="Workspace" if workspace_wide else "Your activity",
                instrumentation="OpenTelemetry SDK" if tracer else "Local timer", rows=records, summary=summary)
