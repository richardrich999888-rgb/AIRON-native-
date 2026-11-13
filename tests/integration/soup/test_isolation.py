from unittest.mock import patch, MagicMock
import socket
import pytest
from airon_adaptation.worker import isolation_probe
from airon_adaptation.integrity import Rejected


@pytest.mark.parametrize("routes", ["", "Iface Destination Gateway Flags RefCnt Use Metric Mask MTU Window IRTT\n"])
def test_empty_namespace_route_representations_accepted_only_with_failed_connectivity(routes):
    sock = MagicMock()
    sock.__enter__.return_value = sock
    sock.connect_ex.return_value = 101
    with patch("airon_adaptation.worker.os.readlink", return_value="net:[2]"), \
         patch("airon_adaptation.worker.Path.read_text", return_value=routes), \
         patch("airon_adaptation.worker.Path.exists", return_value=False), \
         patch("airon_adaptation.worker.socket.socket", return_value=sock), \
         patch("airon_adaptation.worker.socket.getaddrinfo", side_effect=socket.gaierror(-2, "fixture")):
        assert isolation_probe("net:[1]")["route_count"] == 0


def test_same_network_namespace_rejected():
    with patch("airon_adaptation.worker._trace_probe_marker"), \
         patch("airon_adaptation.worker.os.readlink", return_value="net:[1]"), \
         patch("airon_adaptation.worker.Path.read_text", return_value=""):
        with pytest.raises(Rejected):
            isolation_probe("net:[1]")


def test_external_route_rejected():
    with patch("airon_adaptation.worker._trace_probe_marker"), \
         patch("airon_adaptation.worker.os.readlink", return_value="net:[2]"), \
         patch("airon_adaptation.worker.Path.read_text", return_value="Iface Destination\neth0 00000000\n"):
        with pytest.raises(Rejected):
            isolation_probe("net:[1]")


def test_connected_socket_rejected_even_when_route_file_empty():
    sock = MagicMock()
    sock.__enter__.return_value = sock
    sock.connect_ex.return_value = 0
    with patch("airon_adaptation.worker.os.readlink", return_value="net:[2]"), \
         patch("airon_adaptation.worker.Path.read_text", return_value=""), \
         patch("airon_adaptation.worker.socket.socket", return_value=sock):
        with pytest.raises(Rejected):
            isolation_probe("net:[1]")
