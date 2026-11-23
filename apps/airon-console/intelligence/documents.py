"""Bounded source conversion and page-aware SQLite FTS5 retrieval."""
import base64
import binascii
import hashlib
import io
import json
from pathlib import Path
import re
from threading import BoundedSemaphore
import subprocess
import sys

MAX_FILE = 2 * 1024 * 1024
MAX_TEXT = 160_000
PDF_SLOTS = BoundedSemaphore(2)
CHUNK = 1000
STOP = set("a an the what which when where how why is are was were be does do did should shall must can could would we i our in on of to for and from with at by please tell me about my according document file protocol".split())


class Problem(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parse_pdf(raw):
    import resource
    resource.setrlimit(resource.RLIMIT_CPU, (8, 9))
    resource.setrlimit(resource.RLIMIT_AS, (512 << 20, 512 << 20))
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(raw), strict=True)
    if reader.is_encrypted or len(reader.pages) > 64:
        raise ValueError("Encrypted PDFs and files over 64 pages are unsupported.")
    pages = []
    length = 0
    for page in reader.pages:
        text = page.extract_text()
        length += len(text)
        if length > MAX_TEXT:
            raise ValueError("Extracted text exceeds 160,000 characters.")
        pages.append(text)
    return pages


def decode_upload(name, encoded):
    if not isinstance(name, str) or not 1 <= len(name) <= 160 or re.search(r"[/\\:\x00-\x1f]", name) or name in (".", ".."):
        raise Problem(422, "Choose a plain filename without a directory.")
    kind = Path(name).suffix.lower()
    if kind not in (".txt", ".md", ".pdf"):
        raise Problem(415, "Choose a TXT, Markdown or text-based PDF file.")
    try:
        if not isinstance(encoded, str) or len(encoded) > 4 * ((MAX_FILE + 2) // 3):
            raise ValueError()
        raw = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise Problem(422, "Invalid file encoding or size.") from exc
    if not 0 < len(raw) <= MAX_FILE:
        raise Problem(413, "Choose a nonempty file of at most 2 MiB.")
    if kind == ".pdf":
        if not raw.startswith(b"%PDF-"):
            raise Problem(422, "This file has no PDF header.")
        if not PDF_SLOTS.acquire(blocking=False):
            raise Problem(429, "The PDF parser is busy. Try again shortly.")
        try:
            process = subprocess.run([sys.executable, __file__, "--pdf"], input=raw,
                                     capture_output=True, timeout=12, check=False)
        except subprocess.TimeoutExpired as exc:
            raise Problem(422, "PDF conversion exceeded its time limit.") from exc
        finally:
            PDF_SLOTS.release()
        if process.returncode == 3:
            raise Problem(503, "Install the pinned PDF parser on a supported Linux host.")
        if process.returncode:
            raise Problem(422, "PDF could not be read within the page, text or resource limits.")
        pages = json.loads(process.stdout)
    else:
        try:
            pages = [raw.decode("utf-8-sig")]
        except UnicodeDecodeError as exc:
            raise Problem(422, "Text and Markdown must use UTF-8.") from exc
    text = "\n\n".join(pages).strip()
    if not text or "\x00" in text or len(text) > MAX_TEXT:
        raise Problem(422, "No usable text or text exceeds 160,000 characters. Scanned PDFs require OCR.")
    return raw, kind[1:], pages, text


def install(db):
    db.executescript("""
      CREATE TABLE IF NOT EXISTS source_files(
        doc INTEGER PRIMARY KEY REFERENCES documents(id), filename TEXT, format TEXT NOT NULL,
        file_sha256 TEXT, original BLOB, pages INTEGER NOT NULL);
      CREATE TABLE IF NOT EXISTS chunks(
        id INTEGER PRIMARY KEY, doc INTEGER NOT NULL REFERENCES documents(id), ordinal INTEGER NOT NULL,
        page INTEGER, text TEXT NOT NULL, UNIQUE(doc,ordinal));
      CREATE VIRTUAL TABLE IF NOT EXISTS chunk_index USING fts5(
        text,content='chunks',content_rowid='id',tokenize='porter unicode61');
      CREATE TRIGGER IF NOT EXISTS index_chunk AFTER INSERT ON chunks BEGIN
        INSERT INTO chunk_index(rowid,text) VALUES(new.id,new.text);
      END;
    """)
    # Existing records retain their original hashes and IDs across upgrades.
    db.execute("BEGIN IMMEDIATE")
    for row in db.execute("SELECT id,body FROM documents WHERE id NOT IN (SELECT doc FROM source_files)"):
        index(db, row["id"], [row["body"]], "text")


def index(db, doc, pages, kind, name=None, raw=None):
    db.execute("INSERT INTO source_files VALUES(?,?,?,?,?,?)",
               (doc, name, kind, sha(raw) if raw is not None else None, raw, len(pages)))
    ordinal = 0
    for number, page in enumerate(pages, 1):
        rest = page.strip()
        while rest:
            end = len(rest)
            if end > CHUNK:
                end = max(rest.rfind("\n", CHUNK // 2, CHUNK), rest.rfind(" ", CHUNK // 2, CHUNK))
                if end < 0:
                    end = CHUNK
            ordinal += 1
            db.execute("INSERT INTO chunks(doc,ordinal,page,text) VALUES(?,?,?,?)",
                       (doc, ordinal, number if kind == "pdf" else None, rest[:end].strip()))
            rest = rest[end:].lstrip()


def retrieve(db, normalized_question, question):
    approved = db.execute("""SELECT t.id,t.answer,t.version,t.doc,d.title,d.hash
        FROM teachings t JOIN documents d ON d.id=t.doc WHERE t.qkey=? AND t.status='Approved'
        ORDER BY t.version DESC LIMIT 1""", (normalized_question,)).fetchone()
    if approved:
        return dict(approved)
    known = db.execute("""SELECT d.id AS doc,d.title,d.hash,d.body AS answer FROM sources s
        JOIN documents d ON d.id=s.doc WHERE s.question=? LIMIT 2""", (normalized_question,)).fetchall()
    if len(known) > 1:
        return None
    if known:
        chunk = db.execute("SELECT ordinal,page,text FROM chunks WHERE doc=? ORDER BY ordinal LIMIT 2",
                           (known[0]["doc"],)).fetchall()
        if len(chunk) == 1:
            return {**dict(known[0]), "id": None, "version": 1, "chunk": 1, "page": chunk[0]["page"]}
        # Long, legacy excerpts were explicitly bound to the complete source.
        if len(known[0]["answer"]) <= 32000:
            return {**dict(known[0]), "id": None, "version": 1}
    terms = [t for t in re.findall(r"[^\W_]+", question.casefold()) if t not in STOP]
    if len(set(terms)) < 2 or len(terms) > 32:
        return None
    query = " AND ".join('"' + t + '"' for t in dict.fromkeys(terms))
    matches = db.execute("""SELECT c.doc,d.title,d.hash,c.ordinal AS chunk,c.page,c.text AS answer
        FROM chunk_index JOIN chunks c ON c.id=chunk_index.rowid JOIN documents d ON d.id=c.doc
        WHERE chunk_index MATCH ? ORDER BY rank LIMIT 2""", (query,)).fetchall()
    if len(matches) != 1 or (known and matches[0]["doc"] != known[0]["doc"]):
        return None
    return {**dict(matches[0]), "id": None, "version": 1}


if __name__ == "__main__":
    try:
        print(json.dumps(parse_pdf(sys.stdin.buffer.read(MAX_FILE + 1))))
    except ImportError:
        sys.exit(3)
    except Exception:
        sys.exit(2)
