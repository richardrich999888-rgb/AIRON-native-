"""Bounded, measured child processes. No shell and no network fallback."""
import json
import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path
import psutil
from airon_adaptation.integrity import Rejected, file_hash


def checked_file(record):
    p = Path(record["path"])
    if p.is_symlink() or not p.is_file() or file_hash(p) != record["sha256"]:
        raise Rejected("Provisioned artifact hash mismatch: " + p.name)
    return p


def run(args, *, data=None, timeout=60, max_ram=6*1024**3, isolated=True, env_extra=None):
    """Serialized by Core; measure sum RSS of the live process tree every 20ms.

    Summed RSS is conservative for shared pages and can miss sub-20ms peaks.
    This is not a cgroup hard memory limit. RLIMIT_AS/CPU/FSIZE are additional
    per-process bounds. The kernel network namespace is mandatory by default.
    """
    command = [str(x) for x in args]
    if isolated:
        command = ["unshare", "--user", "--map-root-user", "--net", *command]
    # prlimit applies before exec without unsafe preexec_fn in a threaded server.
    command = ["prlimit", "--as="+str(8*1024**3), "--cpu="+str(timeout+10),
               "--fsize="+str(8*1024**2), "--nofile=256", "--", *command]
    env = {"PATH":"/usr/bin:/bin", "LANG":"C.UTF-8", "HF_HUB_OFFLINE":"1",
           "HF_DATASETS_OFFLINE":"1", "TRANSFORMERS_OFFLINE":"1", "HF_HUB_DISABLE_TELEMETRY":"1",
           "DO_NOT_TRACK":"1", "WANDB_DISABLED":"true", "TOKENIZERS_PARALLELISM":"false",
           "OMP_NUM_THREADS":"2", "MKL_NUM_THREADS":"2", "OPENBLAS_NUM_THREADS":"2",
           "CUDA_VISIBLE_DEVICES":"", **(env_extra or {})}
    start = time.monotonic()
    peak = 0
    cpu = {}
    with tempfile.TemporaryFile() as inp, tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        if data is not None:
            inp.write(json.dumps(data, allow_nan=False).encode())
        inp.seek(0)
        p = subprocess.Popen(command, stdin=inp, stdout=out, stderr=err, env=env,
                             start_new_session=True, close_fds=True)
        try:
            root = psutil.Process(p.pid)
            while p.poll() is None:
                # Include the calling controller as well as all worker children.
                rss = psutil.Process().memory_info().rss
                try:
                    procs = [root, *root.children(recursive=True)]
                except psutil.Error:
                    procs = []
                for proc in procs:
                    try:
                        rss += proc.memory_info().rss
                        t = proc.cpu_times()
                        cpu[(proc.pid,proc.create_time())] = t.user+t.system
                    except psutil.Error:
                        pass
                peak = max(peak,rss)
                if rss > max_ram:
                    raise Rejected("Aggregate child memory policy exceeded")
                if time.monotonic()-start > timeout:
                    err.seek(0)
                    raise Rejected("Child deadline exceeded: "+err.read(8*1024**2).decode(errors="replace")[-2048:])
                time.sleep(.02)
            out.seek(0); err.seek(0)
            stdout, stderr = out.read(8*1024**2), err.read(8*1024**2)
            if p.returncode:
                raise Rejected(f"Child failed ({p.returncode}): "+stderr.decode(errors="replace")[-2048:])
            return {"stdout":stdout.decode(), "stderr":stderr.decode(errors="replace"),
                    "measurement":{"wall_s":time.monotonic()-start,"peak_aggregate_rss_bytes":peak,
                                   "sampled_cpu_s":sum(cpu.values()),"sampling_ms":20}}
        finally:
            if p.poll() is None:
                os.killpg(p.pid, signal.SIGKILL)
            p.wait()
