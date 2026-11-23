"""Pair a browser with a loopback-only AIRON knowledge repository."""
import argparse
from contextlib import nullcontext
import inference
import measurements
import json
import os
import secrets
import sys
import sqlite3
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from store import PEOPLE, Problem, connect, initialize, perform


class Handler(BaseHTTPRequestHandler):
    timeout = 20

    def log_message(self, *args):
        pass

    def respond(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(body)))
        self.send_header("Cache-Control","no-store")
        if self.headers.get("Origin") == self.server.ui:
            self.send_header("Access-Control-Allow-Origin",self.server.ui)
            self.send_header("Vary","Origin")
            self.send_header("Access-Control-Allow-Headers","Authorization, Content-Type")
            self.send_header("Access-Control-Allow-Methods","POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def allowed(self):
        return (self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}" and
                self.headers.get("Origin") in (None,self.server.ui))

    def do_OPTIONS(self):
        self.respond({},200 if self.allowed() else 403)

    def do_POST(self):
        try:
            if not self.allowed():
                raise Problem(403,"Unrecognized local origin.")
            if self.headers.get_content_type() != "application/json":
                raise Problem(415,"JSON required.")
            length = int(self.headers.get("Content-Length",0))
            limit = 2_850_000 if self.path == "/knowledge/upload" else 200000
            if not 0 < length <= limit:
                raise Problem(413,"Invalid request size.")
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict):
                raise Problem(422,"Expected an object.")
            op = self.path.removeprefix("/knowledge/")
            if not self.path.startswith("/knowledge/"):
                raise Problem(404,"Unknown path.")
            if op == "info":
                return self.respond({"demo":self.server.demo,"people":PEOPLE,"model":self.server.model,"instance":self.server.instance})
            if op == "pair" and self.server.demo:
                actor=data.get("actor")
                if actor not in PEOPLE:
                    raise Problem(400,"Unknown sample workspace profile.")
                return self.respond({"token":self.server.keys[actor]})
            auth = self.headers.get("Authorization","")
            actor = next((a for a,k in self.server.keys.items() if secrets.compare_digest("Bearer "+k,auth)),None)
            if not actor:
                raise Problem(401,"Pair an authorized identity in this browser.")
            if op == "restart":
                if not self.server.demo or PEOPLE[actor] != "Administrator":
                    raise Problem(403, "Only the sample workspace administrator can restart this service from the console.")
                self.server.restarting = True
                self.respond({"status": "Restarting"}, 202)
                self.server.shutdown()
                return
            if op == "cancel":
                return self.respond(inference.stop(actor, data.get("requestId")))
            measured = {"ask":"workspace.ask", "search":"vault.search", "import":"document.ingest",
                        "upload":"document.ingest", "import-sample":"document.ingest", "propose":"knowledge.propose",
                        "review":"knowledge.review", "runtime":"runtime.probe", "export":"knowledge.export",
                        "verify-archive":"tool.verify_archive"}
            with closing(connect(self.server.path)) as db:
                if op in measured:
                    records = []
                    try:
                        with db:
                            with measurements.trace(measured[op], actor) as (records, root):
                                if op in ("review", "propose", "export"):
                                    db.execute("BEGIN IMMEDIATE")
                                slot = (inference.request_slot(actor, data.get("requestId"))
                                        if op == "ask" and data.get("engine") == "ollama" else nullcontext())
                                with slot as cancel:
                                    result = perform(db, actor, op, data, self.server.model, cancel)
                                root["outcome"] = result.get("outcome", result.get("status", "Completed"))
                                root["document"] = result.get("document") or (result.get("citation") or {}).get("document")
                                root["model"] = result.get("model")
                            measurements.save(db, records)
                    except Exception:
                        with db:
                            measurements.save(db, records)
                        raise
                else:
                    with db:
                        result = perform(db, actor, op, data, self.server.model)
            self.respond(result)
        except Problem as exc:
            self.respond({"error":str(exc)},exc.status)
        except (ValueError,UnicodeError,TypeError):
            self.respond({"error":"Malformed request."},400)
        except sqlite3.Error:
            self.respond({"error":"The local repository could not complete this operation."},503)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-personas",action="store_true",help="Allow local viewers to select sample workspace profiles.")
    parser.add_argument("--directory",type=Path,default=Path.home()/".airon-native")
    parser.add_argument("--model",default="",help="Existing local Ollama model tag")
    args=parser.parse_args()
    if "cloud" in args.model.lower():
        parser.error("Select a local model tag.")
    os.umask(0o077)
    workspace=args.directory/("ciic-fictional" if args.demo_personas else "enterprise")
    workspace.mkdir(mode=0o700,parents=True,exist_ok=True)
    path=workspace/"knowledge.sqlite"
    initialize(path)
    server=ThreadingHTTPServer(("127.0.0.1",8766),Handler)
    # Drain bounded in-flight work before re-executing and rotating pairing keys.
    server.daemon_threads = False
    server.restarting = False
    server.instance = secrets.token_hex(12)
    server.keys={person:secrets.token_urlsafe(32) for person in PEOPLE}
    server.ui="http://127.0.0.1:8787"
    server.demo,server.path,server.model=args.demo_personas,str(path),args.model
    print(f"Local knowledge store: {path}\nConsole: {server.ui}",flush=True)
    if not args.demo_personas:
        for actor,token in server.keys.items():
            print(f"{actor} ({PEOPLE[actor]}) pairing key: {token}",flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    if server.restarting:
        os.execv(sys.executable, [sys.executable, *sys.argv])

if __name__=="__main__":
    main()
