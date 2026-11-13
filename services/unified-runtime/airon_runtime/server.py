"""Owner-local console. Random role-bound sessions, no identity from payloads."""
import argparse
import hmac
import json
import secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from airon_adaptation.integrity import Rejected
from .core import Core

class Server(HTTPServer):
    request_queue_size=2

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",required=True)
    parser.add_argument("--port",type=int,default=8767)
    args=parser.parse_args()
    core=Core(args.root)
    tokens={secrets.token_urlsafe(32):actor for actor in core.identities}
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup();self.connection.settimeout(10)
        def log_message(self,*args): pass
        def reply(self,code,body,ctype="application/json"):
            raw=body if isinstance(body,bytes) else json.dumps(body,allow_nan=False).encode()
            self.send_response(code)
            for k,v in {"Content-Type":ctype,"Content-Length":str(len(raw)),"Cache-Control":"no-store",
                        "X-Content-Type-Options":"nosniff","Referrer-Policy":"no-referrer",
                        "Content-Security-Policy":"default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'"}.items():self.send_header(k,v)
            self.end_headers();self.wfile.write(raw)
        def do_GET(self):
            name={"/":"index.html","/app.js":"app.js","/style.css":"style.css"}.get(self.path)
            if name is None:return self.reply(404,{"error":"Not found"})
            mime={"index.html":"text/html; charset=utf-8","app.js":"text/javascript","style.css":"text/css"}[name]
            self.reply(200,(Path(__file__).parent/"ui"/name).read_bytes(),mime)
        def do_POST(self):
            try:
                if self.path!="/api":raise Rejected("Unknown endpoint")
                host=f"127.0.0.1:{args.port}"
                if self.headers.get("Host") not in {host,f"localhost:{args.port}"}:raise Rejected("Host refused")
                if self.headers.get("Origin") not in {None,"http://"+host,f"http://localhost:{args.port}"}:raise Rejected("Origin refused")
                token=self.headers.get("Authorization","").removeprefix("Bearer ")
                actor=next((actor for key,actor in tokens.items() if hmac.compare_digest(key,token)),None)
                if actor is None:raise Rejected("Session token required")
                if self.headers.get("Content-Type")!="application/json" or self.headers.get("Transfer-Encoding"):
                    raise Rejected("JSON with fixed content length required")
                n=int(self.headers.get("Content-Length","0"))
                if not 0<n<=1100000:raise Rejected("Request size refused")
                raw=self.rfile.read(n)
                if len(raw)!=n:raise Rejected("Incomplete request")
                req=json.loads(raw)
                if set(req)!={"operation","params"}:raise Rejected("Invalid request envelope")
                self.reply(200,core.call(core.principal(actor),req["operation"],req["params"]))
            except (Rejected,ValueError,TypeError,KeyError) as e:self.reply(400,{"error":str(e)})
            except Exception:self.reply(500,{"error":"Operation failed; inspect local evidence"})
    try:
        server=Server(("127.0.0.1",args.port),Handler)
        print(f"AIR​ON local console: http://127.0.0.1:{args.port}",flush=True)
        for token,actor in tokens.items():print(actor+" token: "+token,flush=True)
        server.serve_forever()
    finally:core.close()

if __name__=="__main__":main()
