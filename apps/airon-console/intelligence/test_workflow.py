import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from unittest.mock import patch
from store import CORRECTION, Q1, Q2, Problem, SAMPLE, connect, digest, initialize, perform


class Ownership(unittest.TestCase):
    def setUp(self):
        self.space=tempfile.TemporaryDirectory()
        self.addCleanup(self.space.cleanup)
        self.path=Path(self.space.name)/"knowledge.sqlite"
        initialize(self.path)

    def run_as(self,actor,op,**data):
        with closing(connect(self.path)) as db,db:
            db.execute("BEGIN IMMEDIATE")
            return perform(db,actor,op,data)

    def propose(self,answer=CORRECTION,question=Q2):
        return self.run_as("Leela","propose",question=question,answer=answer,
                           note="Fictional maintenance addendum MH-04, reviewed copy",document=1)["teaching"]

    def test_ownership_through_restart_and_export(self):
        self.run_as("Mira","import-sample")
        found=self.run_as("Dev","ask",question=Q1)
        self.assertEqual(found["answer"],SAMPLE["body"])
        self.assertEqual(found["citation"]["sha256"],digest(found["answer"]))
        self.assertEqual(self.run_as("Dev","ask",question=Q2)["outcome"],"Abstained")
        teaching=self.propose()
        self.assertEqual(self.run_as("Nila","ask",question=Q2)["outcome"],"Abstained")
        self.run_as("Ravi","review",teaching=teaching,decision="Approved")
        # Reinitialize the existing on-disk workspace as the launcher does after restart.
        initialize(self.path)
        self.assertEqual(self.run_as("Nila","ask",question=Q2)["answer"],CORRECTION)
        export=self.run_as("Mira","export")
        self.assertEqual(export["documents"][0]["body"],SAMPLE["body"])
        item=export["approved"][0]
        self.assertEqual((item["actor"],item["reviewer"],item["version"],item["reuse"]),("Leela","Ravi",1,1))
        self.assertIn("Correction approved",[e["action"] for e in export["events"]])

    def test_permissions_rejection_and_revision(self):
        self.run_as("Mira","import-sample")
        t=self.propose()
        for actor,op,params in [("Nila","export",{}),("Leela","review",dict(teaching=t,decision="Approved")),
                                ("Ravi","import-sample",{}),("invalid","state",{})]:
            with self.assertRaises(Problem):self.run_as(actor,op,**params)
        self.run_as("Ravi","review",teaching=t,decision="Rejected")
        self.assertEqual(self.run_as("Dev","ask",question=Q2)["outcome"],"Abstained")
        for version in (1,2):
            update=self.propose(answer=f"Fictional revision {version}")
            self.assertEqual(self.run_as("Ravi","review",teaching=update,decision="Approved")["version"],version)
        self.assertEqual(self.run_as("Dev","ask",question=Q2)["answer"],"Fictional revision 2")
        self.assertEqual(len(self.run_as("Mira","export")["approved"]),2)

    def test_one_decision_under_concurrent_review(self):
        self.run_as("Mira","import-sample")
        t=self.propose()
        def review(_):
            try:return self.run_as("Ravi","review",teaching=t,decision="Approved")["version"]
            except Problem as exc:return exc.status
        with ThreadPoolExecutor(2) as pool:self.assertEqual(sorted(pool.map(review,range(2))),[1,409])
        self.assertEqual(sum(e["action"]=="Correction approved" for e in self.run_as("Mira","export")["events"]),1)

    def test_upload_search_and_ambiguous_question(self):
        fields=dict(title="Cooling checklist",body="Fictional checklist A.",question=Q1)
        self.run_as("Mira","import",**fields)
        with self.assertRaises(Problem):self.run_as("Mira","import",**fields)
        self.assertEqual(len(self.run_as("Dev","search",query="Cooling")["documents"]),1)
        self.assertEqual(self.run_as("Dev","ask",question=Q1)["answer"],fields["body"])
        self.run_as("Mira","import-sample")
        self.assertEqual(self.run_as("Dev","ask",question=Q1)["outcome"],"Abstained")

    def test_unavailable_model_withholds_answer(self):
        self.run_as("Mira","import-sample")
        with patch("store.airon_local.ollama",side_effect=OSError("offline")):
            self.assertEqual(self.run_as("Dev","ask",question=Q1,engine="ollama")["outcome"],"Withheld")
            self.assertEqual(self.run_as("Dev","runtime")["status"],"Ollama unavailable")
