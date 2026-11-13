import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
import pytest
from airon_adaptation.controller import Controller
from airon_adaptation.server import Handler


@pytest.fixture
def server(tmp_path):
    ctl = Controller(tmp_path/"state")
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    srv.controller = ctl
    srv.sessions = {"test-token": {"actor": "tester", "role": "operator"}}
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    yield srv
    srv.shutdown()
    srv.server_close()
    thread.join()
    ctl.close()


@pytest.mark.parametrize("headers,status", [
    ({}, 401), ({"Authorization": "Bearer wrong"}, 401),
    ({"Authorization": "Bearer test-token", "Origin": "https://attacker.example"}, 403),
    ({"Authorization": "Bearer test-token", "Host": "attacker.example"}, 403)])
def test_api_auth_and_origin_fail_closed(server, headers, status):
    req = urllib.request.Request(f"http://127.0.0.1:{server.server_port}/api/operation",
                                 data=b'{"operation":"status","params":{}}',
                                 headers={"Content-Type": "application/json", **headers})
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(req)
    assert exc.value.code == status


def test_api_role_comes_from_session(server):
    req = urllib.request.Request(f"http://127.0.0.1:{server.server_port}/api/operation",
                                 data=json.dumps({"operation": "activate_model", "params": {
                                     "approval_id": "approval-"+"a"*16}}).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer test-token"})
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(req)
    assert exc.value.code == 400
