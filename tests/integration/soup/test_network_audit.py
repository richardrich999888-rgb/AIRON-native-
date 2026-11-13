import importlib.util
from pathlib import Path

source = Path(__file__).resolve().parents[3]/"services/model-adaptation/scripts/audit_network.py"
spec = importlib.util.spec_from_file_location("audit_network", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_unexpected_egress_fails_even_when_connection_blocked(tmp_path):
    path = tmp_path/"trace.1"
    path.write_text('connect(3, {sa_family=AF_INET, sin_port=htons(443), sin_addr=inet_addr("8.8.8.8")}, 16) = -1 ENETUNREACH (Network unreachable)\n')
    result = module.classify([path])
    assert not result["passed"]
    assert any(v.get("reason") == "unclassified IP activity" for v in result["violations"])


def test_only_failed_expected_connections_in_marked_windows_pass(tmp_path):
    path = tmp_path/"trace.1"
    lines = [
        'connect(3, {sa_family=AF_UNIX, sun_path="/tmp/airon-isolation-probe-begin"}, 42) = -1 ENOENT',
        'connect(3, {sa_family=AF_INET, sin_port=htons(443), sin_addr=inet_addr("198.51.100.1")}, 16) = -1 ENETUNREACH',
        'connect(3, {sa_family=AF_UNIX, sun_path="/tmp/airon-isolation-probe-end"}, 40) = -1 ENOENT',
    ]
    path.write_text("\n".join(lines*11)+"\n")
    assert module.classify([path])["passed"]
    path.write_text(path.read_text().replace("= -1 ENETUNREACH", "= 0"))
    assert not module.classify([path])["passed"]
