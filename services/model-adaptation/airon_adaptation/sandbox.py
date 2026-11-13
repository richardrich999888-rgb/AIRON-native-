"""No shell. Linux namespaces plus explicit read-only mounts; fail if unavailable."""
import os
import signal
import subprocess
import sys
from pathlib import Path
from .integrity import Rejected


def command(job, model, data, adapter=None):
    app = Path(__file__).resolve().parent.parent
    env_root = Path(sys.prefix).resolve()
    runtime_root = Path(sys.base_prefix).resolve()
    args = ["unshare", "--user", "--map-root-user", "--net", "bwrap",
            "--unshare-pid", "--unshare-ipc", "--unshare-uts", "--die-with-parent",
            "--new-session", "--cap-drop", "ALL", "--clearenv"]
    for source in ("/usr", "/lib", "/lib64", str(runtime_root)):
        if Path(source).exists():
            args += ["--ro-bind", source, source]
    args += ["--ro-bind", str(env_root), "/env", "--ro-bind", str(app), "/app",
             "--ro-bind", str(model), "/model", "--ro-bind", str(data), "/data",
             "--ro-bind", str(job / "request.json"), "/request.json",
             "--bind", str(job / "output"), "/output", "--proc", "/proc",
             "--dev", "/dev", "--tmpfs", "/tmp", "--dir", "/home",
             "--dir", "/home/worker", "--chdir", "/tmp"]
    if adapter:
        args += ["--ro-bind", str(adapter), "/adapter"]
    environment = {
        "PATH": "/env/bin:/usr/bin:/bin", "HOME": "/home/worker", "PYTHONPATH": "/app",
        "HF_HOME": "/tmp/hf", "HF_HUB_OFFLINE": "1", "HF_DATASETS_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1", "HF_HUB_DISABLE_TELEMETRY": "1",
        "SOUP_TELEMETRY": "0", "WANDB_DISABLED": "true", "TOKENIZERS_PARALLELISM": "false",
        "OMP_NUM_THREADS": "2", "MKL_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2",
        "PYTHONHASHSEED": "52", "CUDA_VISIBLE_DEVICES": "", "LANG": "C.UTF-8"}
    for key, value in environment.items():
        args += ["--setenv", key, value]
    args += ["/env/bin/python", "-m", "airon_adaptation.worker"]
    return args


def run(args, logfile, *, on_start=lambda process: None, timeout=900):
    with open(logfile, "xb", buffering=0) as log:
        proc = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                start_new_session=True, close_fds=True,
                                env={"PATH": "/usr/bin:/bin"})
        on_start(proc)
        try:
            code = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            stop(proc)
            raise Rejected("Worker exceeded wall-clock limit") from exc
        if code != 0:
            raise Rejected(f"Isolated worker failed with exit {code}; inspect job log")


def stop(proc):
    if proc.poll() is None:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait(timeout=10)
