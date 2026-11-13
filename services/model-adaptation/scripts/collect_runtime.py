"""Inventory trusted host prerequisites; does not redistribute OS binaries."""
import argparse
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from airon_adaptation.integrity import file_hash, write_json

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", required=True)
args = parser.parse_args()
executables = {"python": sys.executable}
for name in ("bwrap", "unshare", "strace"):
    executables[name] = shutil.which(name)
    if not executables[name]:
        raise RuntimeError("Missing runtime prerequisite: "+name)
items = {}
for name, executable in executables.items():
    path = Path(executable).resolve(strict=True)
    linked = subprocess.run(["ldd", str(path)], capture_output=True, text=True, check=True)
    if "not found" in linked.stdout:
        raise RuntimeError("Unresolved native dependency: "+name)
    items[name] = {"path": str(path), "sha256": file_hash(path), "bytes": path.stat().st_size,
                   "dynamic_linker_inventory": linked.stdout.splitlines()}
packages = subprocess.run(["dpkg-query", "-W", "-f=${binary:Package}\t${Version}\n",
                           "bubblewrap", "util-linux", "strace", "libc6"],
                          capture_output=True, text=True, check=False)
report = {"schema": "airon-host-prerequisites/v1", "platform": platform.platform(),
          "python": sys.version, "os_release": Path("/etc/os-release").read_text(),
          "executables": items, "os_packages": packages.stdout.splitlines(),
          "os_package_inventory_complete": packages.returncode == 0,
          "os_package_inventory_errors": packages.stderr.splitlines(),
          "scope": "Trusted host prerequisite binaries and linker output; wheel-native libraries and a complete OS SBOM are not claimed"}
write_json(args.output, report)
print("RUNTIME_PREREQUISITES="+json.dumps(report))
