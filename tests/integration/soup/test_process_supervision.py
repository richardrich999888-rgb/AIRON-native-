"""Real subprocess lifetime tests; no training or model qualification claims."""
import subprocess
import sys
import pytest
from airon_adaptation import sandbox
from airon_adaptation.integrity import Rejected


def test_callback_failure_kills_launched_process(tmp_path):
    observed = []
    def fail(proc):
        observed.append(proc)
        raise RuntimeError("registration failed")
    with pytest.raises(RuntimeError, match="registration failed"):
        sandbox.run([sys.executable, "-c", "import time; time.sleep(30)"],
                    tmp_path/"callback.log", on_start=fail)
    assert observed[0].poll() is not None


def test_wall_timeout_kills_launched_process(tmp_path):
    observed = []
    with pytest.raises(Rejected, match="wall-clock"):
        sandbox.run([sys.executable, "-c", "import time; time.sleep(30)"],
                    tmp_path/"timeout.log", on_start=observed.append, timeout=0.1)
    assert observed[0].poll() is not None
