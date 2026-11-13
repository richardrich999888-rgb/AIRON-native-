"""Browser checks against the real completed experiment, not mocked API responses."""
import argparse
import base64
import json
import secrets
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from airon_adaptation.controller import Controller
from airon_adaptation.server import Handler
from airon_adaptation.integrity import write_json

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--root", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()
output = Path(args.output)
output.mkdir(parents=True, exist_ok=True)
ctl = Controller(args.root)
server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
server.controller = ctl
operator, reviewer = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
server.sessions = {operator: {"actor": "console-check-operator", "role": "operator"},
                   reviewer: {"actor": "console-check-reviewer", "role": "reviewer"}}
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
errors, external = [], []
try:
    with sync_playwright() as browser_tool:
        browser = browser_tool.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 1000})
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: external.append(request.url)
                if not request.url.startswith("http://127.0.0.1:"+str(server.server_port)+"/") else None)
        page.goto("http://127.0.0.1:"+str(server.server_port))
        page.locator("#token").fill(operator)
        page.locator("#connect").click()
        expect(page.locator("#training-state")).to_have_text("SUCCEEDED")
        observed = {key: page.locator("#"+key).inner_text()
                    for key in ("training-state", "routing-score", "regression-score", "active-model")}
        assert observed["active-model"] == "Original model", observed
        page.locator("#token").fill("")  # Never capture a credential, including masked input.
        desktop = page.screenshot(path=str(output/"console-desktop.jpeg"), type="jpeg", quality=55)
        page.set_viewport_size({"width": 390, "height": 844})
        page.screenshot(path=str(output/"console-mobile.jpeg"), type="jpeg", quality=55)
        assert page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth"), "Mobile overflow"
        page.locator("#token").fill(reviewer)
        page.locator('[data-action="start_training"]').click()
        expect(page.locator("#message")).to_contain_text("not permitted")
        page.locator('[data-action="evidence"]').click()
        expect(page.locator("#result")).to_contain_text("APPLICATION_SIGNED")
        assert not errors and not external, (errors, external)
        result = {"passed": True, "real_workspace": True, "observed": observed,
                  "browser_errors": errors, "external_page_requests": external,
                  "checks": ["load measured state", "reviewer training denied", "signed evidence display", "mobile width"]}
        write_json(output/"console-check.json", result)
        print("CONSOLE_CHECK="+json.dumps(result))
        print("CONSOLE_SCREENSHOT_BASE64="+base64.b64encode(desktop).decode())
        browser.close()
finally:
    server.shutdown()
    server.server_close()
    thread.join()
    ctl.close()
