import io
import json
import tempfile
import unittest
from email.message import Message
from pathlib import Path
from types import SimpleNamespace
from local_api import Handler
from store import initialize


class Pairing(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        database = Path(directory.name) / "knowledge.sqlite"
        initialize(database)
        self.server = SimpleNamespace(
            ui="http://127.0.0.1:8787", server_port=8766, path=database, demo=False,
            keys={"Dev": "unit-test-employee", "Mira": "unit-test-admin"}, model=""
        )

    def post(self, op, body, token="", origin="http://127.0.0.1:8787", host="127.0.0.1:8766"):
        request = object.__new__(Handler)
        request.server = self.server
        request.headers = Message()
        content = json.dumps(body).encode()
        for name, value in {"Host": host, "Origin": origin, "Authorization": "Bearer " + token,
                            "Content-Type": "application/json", "Content-Length": str(len(content))}.items():
            request.headers[name] = value
        request.path = "/knowledge/" + op
        request.rfile = io.BytesIO(content)
        output = []
        request.respond = lambda payload, status=200: output.append((status, payload))
        request.do_POST()
        return output[0]

    def test_private_pairing_and_origin(self):
        self.assertEqual(self.post("pair", {"actor":"Mira"})[0],401)
        self.assertEqual(self.post("state",{},token="unit-test-admin",origin="https://example.invalid")[0],403)
        self.assertEqual(self.post("state",{},token="unit-test-admin",host="elsewhere.invalid")[0],403)
        self.assertEqual(self.post("state",{},token="unit-test-admin")[1]["actor"],"Mira")

    def test_bearer_owns_role(self):
        self.assertEqual(self.post("import-sample",{"actor":"Mira","role":"Administrator"},token="unit-test-employee")[0],403)
        self.assertEqual(self.post("import-sample",{},token="unit-test-admin")[0],200)

    def test_demo_pairing_is_explicit(self):
        self.server.demo=True
        self.assertEqual(self.post("pair",{"actor":"Dev"}),(200,{"token":"unit-test-employee"}))
