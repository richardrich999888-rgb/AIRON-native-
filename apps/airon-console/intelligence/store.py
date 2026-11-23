"""Local, single-organization knowledge ledger. A database corresponds to one workspace."""
import http.client
import hashlib
import accountability
import documents
import inference
import measurements
from documents import Problem
import json
import re
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "website/offline"))
import server as airon_local  # the existing Ollama adapter and source validator

SAMPLE = next(d for d in airon_local.DOCS if d["id"] == "OPS-001")
PEOPLE = {"Mira": "Administrator", "Dev": "Employee", "Leela": "Expert",
          "Ravi": "Reviewer", "Nila": "Employee"}
Q1 = SAMPLE["questions"][0]
Q2 = "Which register records the cooling assembly handover?"
CORRECTION = "Record the cooling assembly handover in the fictional shift register MH-04."
LIMIT = 32000



def now():
    return datetime.now(timezone.utc).isoformat()


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def field(data, name, limit=500):
    val = data.get(name)
    if not isinstance(val, str) or not val.strip() or len(val) > limit:
        raise Problem(422, f"Provide a valid {name} (up to {limit} characters).")
    return val.strip()


def key(question):
    return airon_local.normalized(question)


def require(actor, *roles):
    if PEOPLE.get(actor) not in roles:
        raise Problem(403, "This identity has no authority for that action.")


def connect(path):
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db


def initialize(path):
    with connect(path) as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.executescript("""
          CREATE TABLE IF NOT EXISTS documents(id INTEGER PRIMARY KEY,title TEXT NOT NULL,body TEXT NOT NULL,
              hash TEXT UNIQUE NOT NULL,actor TEXT NOT NULL,origin TEXT NOT NULL,at TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS sources(question TEXT NOT NULL,doc INTEGER NOT NULL REFERENCES documents(id),
              PRIMARY KEY(question,doc));
          CREATE TABLE IF NOT EXISTS teachings(id INTEGER PRIMARY KEY,question TEXT NOT NULL,qkey TEXT NOT NULL,
              answer TEXT NOT NULL,doc INTEGER NOT NULL REFERENCES documents(id),note TEXT NOT NULL,
              actor TEXT NOT NULL,at TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'Pending',
              reviewer TEXT,reviewed TEXT,version INTEGER,UNIQUE(qkey,version));
          CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,at TEXT NOT NULL,actor TEXT NOT NULL,
              action TEXT NOT NULL,detail TEXT NOT NULL);
          CREATE VIRTUAL TABLE IF NOT EXISTS vault_index USING fts5(title,body,content='documents',content_rowid='id');
          CREATE TRIGGER IF NOT EXISTS index_import AFTER INSERT ON documents BEGIN
              INSERT INTO vault_index(rowid,title,body) VALUES(new.id,new.title,new.body);
          END;
        """)


        accountability.install(db)
        measurements.install(db)
        documents.install(db)


def event(db, actor, action, detail):
    db.execute("INSERT INTO events(at,actor,action,detail) VALUES(?,?,?,?)",
               (now(), actor, action, json.dumps(detail, ensure_ascii=False)))


def rows(db, sql, args=()):
    return [dict(row) for row in db.execute(sql, args)]


def inventory(db, actor):
    docs = rows(db, """SELECT d.*, f.filename,f.format,f.file_sha256,f.pages,
        (SELECT count(*) FROM chunks c WHERE c.doc=d.id) AS chunks
        FROM documents d LEFT JOIN source_files f ON f.doc=d.id ORDER BY d.id DESC""")
    teaches = rows(db, "SELECT t.*,d.title AS source,d.hash AS source_hash FROM teachings t JOIN documents d ON d.id=t.doc ORDER BY t.id DESC")
    if PEOPLE[actor] not in ("Reviewer", "Administrator"):
        teaches = [t for t in teaches if t["status"] == "Approved" or t["actor"] == actor]
    events = rows(db, "SELECT * FROM events ORDER BY id DESC LIMIT 200") if PEOPLE[actor] in ("Administrator","Reviewer") else rows(db,"SELECT * FROM events WHERE actor=? ORDER BY id DESC LIMIT 200",(actor,))
    memory = [{**t,"reuse":db.execute("SELECT count(*) FROM events WHERE action='Answer released' AND json_extract(detail,'$.teaching')=?",(t["id"],)).fetchone()[0]} for t in teaches if t["status"]=="Approved"]
    return dict(actor=actor,role=PEOPLE[actor],documents=docs,teachings=teaches,memory=memory,events=events,asOf=now())


def perform(db, actor, op, data, configured_model="", cancel=None):
    if actor not in PEOPLE:
        raise Problem(401,"Pair a workspace identity.")
    if op == "state":
        return inventory(db, actor)
    if op == "tool-runs":
        require(actor, "Administrator", "Reviewer")
        return {"runs": accountability.records(db)}
    if op == "verify-archive":
        require(actor, "Administrator", "Reviewer")
        result = accountability.run(db, actor, now())
        event(db, actor, "Archive tool completed", result)
        return result
    if op == "measurements":
        kind = data.get("kind")
        if kind is not None and (not isinstance(kind, str) or len(kind) > 64):
            raise Problem(422, "Invalid operation filter.")
        return measurements.read(db, actor, PEOPLE[actor] in ("Administrator", "Reviewer"), kind)
    if op == "search":
        words = re.findall(r"\w+", field(data,"query",200))
        if not words:
            return {"documents":[]}
        return {"documents":rows(db,"SELECT rowid AS id FROM vault_index WHERE vault_index MATCH ? ORDER BY rank",
                                 (" AND ".join('"'+word+'"' for word in words),))}
    if op in ("import-sample", "import", "upload"):
        require(actor, "Administrator")
        raw, filename, kind = None, None, "text"
        if op == "import-sample":
            title, body, questions, origin = SAMPLE["title"], SAMPLE["body"], SAMPLE["questions"], "Fictional maintenance fixture"
            pages = [body]
        else:
            title = field(data, "title", 160)
            questions = [field(data, "question")] if data.get("question") else []
            if op == "upload":
                filename = data.get("filename")
                raw, kind, pages, body = documents.decode_upload(filename, data.get("content"))
                origin = "Local file upload"
            else:
                body = field(data, "body", LIMIT)
                pages, origin = [body], "Operator import"
        if not all(key(q) for q in questions):
            raise Problem(422, "Use a question with searchable characters.")
        content_hash = digest(body)
        try:
            doc = db.execute("INSERT INTO documents(title,body,hash,actor,origin,at) VALUES(?,?,?,?,?,?)",
                             (title, body, content_hash, actor, origin, now())).lastrowid
        except sqlite3.IntegrityError as exc:
            raise Problem(409, "This document is already in the vault.") from exc
        documents.index(db, doc, pages, kind, filename, raw)
        db.executemany("INSERT INTO sources VALUES(?,?)", [(q, doc) for q in set(map(key, questions))])
        event(db, actor, "Source imported", {"document": doc, "sha256": content_hash, "origin": origin})
        return {"document": doc, "status": "Indexed"}
    if op == "propose":
        require(actor,"Expert")
        question, answer, note = field(data,"question"),field(data,"answer",3000),field(data,"note",2000)
        if not key(question):
            raise Problem(422,"Use a question with searchable characters.")
        doc = data.get("document")
        if type(doc) is not int or not db.execute("SELECT 1 FROM documents WHERE id=?",(doc,)).fetchone():
            raise Problem(422,"Select an existing source.")
        ident = db.execute("INSERT INTO teachings(question,qkey,answer,doc,note,actor,at) VALUES(?,?,?,?,?,?,?)",
                           (question,key(question),answer,doc,note,actor,now())).lastrowid
        event(db,actor,"Correction submitted",{"teaching":ident,"document":doc})
        return {"teaching":ident}
    if op == "review":
        require(actor,"Reviewer")
        status = data.get("decision")
        if status not in ("Approved","Rejected"):
            raise Problem(422,"Choose an approval decision.")
        ident = data.get("teaching")
        item = db.execute("SELECT * FROM teachings WHERE id=?",(ident,)).fetchone() if type(ident) is int else None
        if not item or item["status"] != "Pending" or item["actor"] == actor:
            raise Problem(409,"Only another person's pending correction can be reviewed.")
        version = (db.execute("SELECT coalesce(max(version),0)+1 FROM teachings WHERE qkey=?",(item["qkey"],)).fetchone()[0]
                   if status == "Approved" else None)
        db.execute("UPDATE teachings SET status=?,version=?,reviewer=?,reviewed=? WHERE id=?",(status,version,actor,now(),ident))
        event(db,actor,"Correction "+status.lower(),{"teaching":ident,"version":version})
        return {"version":version}
    if op == "runtime":
        try:
            models = inference.discover(airon_local)
            status = "Ready" if models else "No local models installed"
        except (OSError,ValueError,KeyError):
            models,status = [],"Ollama unavailable"
        return dict(models=models,status=status,configured=configured_model,at=now(),cpuSeconds=time.process_time(),
                    databaseBytes=db.execute("PRAGMA page_count").fetchone()[0]*db.execute("PRAGMA page_size").fetchone()[0])
    if op == "ask":
        question, engine = field(data,"question"), data.get("engine","extract")
        if engine not in ("extract","ollama"):
            raise Problem(422,"Unknown engine.")
        if not isinstance(engine, str):
            raise Problem(422, "Invalid answer engine.")
        model = data.get("model") or configured_model
        if not isinstance(model, str) or len(model) > 180:
            raise Problem(422, "Invalid model name.")
        with measurements.span("retrieval", actor) as retrieval:
            match = documents.retrieve(db, key(question), question)
            retrieval["outcome"] = "Matched" if match else "Abstained"
            retrieval["document"] = match["doc"] if match else None
        if not match:
            event(db,actor,"Abstained",{"question":question,"modelCalls":0})
            return {"outcome":"Abstained","answer":"No unambiguous approved source supports this question.","engine":"No model called"}
        citation = dict(document=match["doc"],title=match["title"],sha256=match["hash"],version=match["version"],
                        teaching=match["id"],page=match.get("page"),chunk=match.get("chunk"),excerpt=match["answer"])
        answer = match["answer"]
        usage = None
        if engine == "ollama":
            with measurements.span("model.inference", actor) as measurement:
                measurement.update(model=model or None, document=match["doc"])
                try:
                    answer, grounded, counts = inference.generate(airon_local, model, question, answer, cancel)
                    measurement.update(counts)
                    if not grounded:
                        raise ValueError("Unverified excerpt")
                except (OSError, ValueError, KeyError, TypeError, http.client.HTTPException):
                    outcome = "Cancelled" if cancel and cancel.stopped else "Withheld"
                    measurement["outcome"] = outcome
                    event(db, actor, "Model response " + outcome.lower(), {"model": model})
                    return {"outcome":outcome,"answer":"No model answer released. Check local model availability and source validation.",
                            "engine":"Ollama","model":model}
            usage = {k:measurement[k] for k in ("durationMs","inputTokens","outputTokens")}
        event(db,actor,"Answer released",{k:v for k,v in {**citation,"question":question,"engine":engine}.items() if k!="excerpt"})
        return {"outcome":"Answered","answer":answer,"citation":citation,
                "engine":"Ollama · source-constrained generation" if engine=="ollama" else "Deterministic source excerpt",
                "model":model if engine=="ollama" else None, "usage":usage}
    if op == "export":
        require(actor,"Administrator")
        event(db,actor,"Knowledge exported",{"format":"airon-knowledge/v1"})
        state=inventory(db,actor)
        return dict(schema="airon-knowledge/v1",exportedAt=state["asOf"],documents=state["documents"],
                    approved=state["memory"],events=rows(db,"SELECT * FROM events ORDER BY id"),assurance="Unsigned local application records")
    raise Problem(404,"Unknown operation.")
