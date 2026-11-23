import base64
import hashlib
from pathlib import Path
import unittest
from contextlib import closing

import test_access
from store import connect, initialize

PDF = Path(__file__).resolve().parents[1] / "tests/fixtures/workshop-note.pdf"


class Infrastructure(unittest.TestCase):
    setUp = test_access.Pairing.setUp
    post = test_access.Pairing.post

    def upload(self, filename="workshop-note.pdf", raw=None):
        return self.post("upload", {"title": filename, "filename": filename,
            "content": base64.b64encode(PDF.read_bytes() if raw is None else raw).decode()}, "unit-test-admin")

    def test_pdf_index_citations_restart_and_duplicate(self):
        self.assertEqual(self.upload()[0], 200)
        self.assertEqual(self.upload()[0], 409)
        initialize(self.server.path)
        question = {"question": "What is the amber spindle interval?"}
        for _ in range(2):
            answer = self.post("ask", question, "unit-test-employee")[1]
            self.assertEqual((answer["answer"], answer["citation"]["page"], answer["citation"]["chunk"]),
                             ("The amber spindle interval is 72 hours.", 2, 2))
        meta = self.post("state", {}, "unit-test-employee")[1]["documents"][0]
        self.assertEqual(meta["file_sha256"], hashlib.sha256(PDF.read_bytes()).hexdigest())
        self.assertEqual(self.post("ask", {"question": "Where is the amber spindle invoice?"}, "unit-test-employee")[1]["outcome"], "Abstained")
        self.assertEqual(self.post("search", {"query": "spindle"}, "unit-test-employee")[1]["documents"], [{"id":1}])
        with closing(connect(self.server.path)) as db:
            self.assertEqual(db.execute("SELECT original FROM source_files").fetchone()[0],PDF.read_bytes())

    def test_rejected_uploads_leave_no_content(self):
        for name,raw,status in [("../test.txt",b"abc",422),("binary.md",bytes([255]),422),("photo.png",b"abc",415),
                                ("empty.txt",b"",413),("bad.pdf",b"%PDF-invalid",422),("wrong.pdf",b"data",422),
                                ("archive.md", b"a" * 160001, 422)]:
            with self.subTest(name=name):
                self.assertEqual(self.upload(name,raw)[0],status)
        self.assertFalse(self.post("state",{}, "unit-test-admin")[1]["documents"])
        self.assertEqual(self.post("measurements",{}, "unit-test-admin")[1]["summary"]["unsuccessful"],7)

    def test_scoped_metrics_have_no_document_body_or_prompt(self):
        self.assertEqual(self.upload("memory.md",b"Amber spindle cradle turns slowly.")[0],200)
        self.post("ask",{"question":"amber spindle cradle?"},"unit-test-employee")
        result=self.post("measurements",{}, "unit-test-employee")[1]
        self.assertEqual({r["operation"] for r in result["rows"]},{"retrieval","workspace.ask"})
        self.assertEqual(len({r["traceId"] for r in result["rows"]}),1)
        self.assertNotIn("spindle",str(result))
        self.assertIsNone(result["summary"]["inputTokens"])
        self.assertEqual(self.post("restart",{},"unit-test-admin")[0],403)
        self.assertEqual(self.post("verify-archive",{},"unit-test-employee")[0],403)

    def test_migration_backfills_legacy_sources_once(self):
        self.upload("legacy.txt",b"Legacy copper valve records.")
        with closing(connect(self.server.path)) as db,db:
            db.executescript("DROP TRIGGER index_chunk; DROP TABLE chunk_index; DROP TABLE chunks; DROP TABLE source_files;")
        initialize(self.server.path)
        initialize(self.server.path)
        answer=self.post("ask",{"question":"legacy copper valve?"},"unit-test-employee")[1]
        self.assertEqual(answer["citation"]["chunk"],1)
        self.assertEqual(self.post("state",{},"unit-test-admin")[1]["documents"][0]["chunks"],1)
