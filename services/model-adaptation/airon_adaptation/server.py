"""Loopback API for a single-machine experiment. No enterprise identity claim."""
import argparse
import json
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from .controller import Controller
from .integrity import Rejected

UI = Path(__file__).with_name("ui")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _host(self):
        port = self.server.server_port
        return self.headers.get("Host") in (f"127.0.0.1:{port}", f"localhost:{port}")

    def _reply(self, value, status=200, mime="application/json"):
        raw = json.dumps(value, allow_nan=False).encode() if mime == "application/json" else value
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; "
                         "img-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if not self._host():
            return self._reply({"error": "Invalid host"}, 403)
        files = {"/": ("index.html", "text/html; charset=utf-8"),
                 "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                 "/style.css": ("style.css", "text/css; charset=utf-8"),
                 "/syntriass-logo.jpeg": ("syntriass-logo.jpeg", "image/jpeg")}
        if self.path not in files:
            return self._reply({"error": "Not found"}, 404)
        name, mime = files[self.path]
        self._reply((UI/name).read_bytes(), mime=mime)

    def do_POST(self):
        port = self.server.server_port
        origin = self.headers.get("Origin")
        if not self._host() or (origin and origin not in (f"http://127.0.0.1:{port}", f"http://localhost:{port}")):
            return self._reply({"error": "Host or origin rejected"}, 403)
        supplied = self.headers.get("Authorization", "")
        principal = next((p for token, p in self.server.sessions.items()
                          if secrets.compare_digest(supplied, "Bearer "+token)), None)
        if not principal:
            return self._reply({"error": "Invalid session token"}, 401)
        if self.path != "/api/operation":
            return self._reply({"error": "Not found"}, 404)
        try:
            if self.headers.get("Transfer-Encoding"):
                raise Rejected("Chunked requests are unsupported")
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                raise Rejected("JSON required")
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 1024*1024:
                raise Rejected("Invalid request size")
            self.connection.settimeout(15)
            body = json.loads(self.rfile.read(size))
            if not isinstance(body, dict) or set(body) != {"operation", "params"}:
                raise Rejected("Invalid operation envelope")
            result = self.server.controller.call(body["operation"], body["params"], **principal)
            self._reply(result)
        except (Rejected, ValueError, KeyError, TypeError) as exc:
            self._reply({"error": str(exc)}, 400)
        except Exception:
            self._reply({"error": "Operation failed closed; inspect local job logs"}, 500)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    controller = Controller(args.root)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    server.controller = controller
    server.sessions = {}
    print(f"AIRON Native experimental adaptation: http://127.0.0.1:{server.server_port}")
    for role in ("operator", "reviewer"):
        token = secrets.token_urlsafe(32)
        server.sessions[token] = {"actor": "local-"+role, "role": role}
        print(f"{role} token: {token}", flush=True)
    print("Tokens are local demonstration roles, not independent enterprise identities.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        controller.close()


if __name__ == "__main__":
    main()
