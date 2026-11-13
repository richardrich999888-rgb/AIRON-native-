"""Connected preparation: create a platform-specific, hash-locked wheelhouse."""
import argparse
import importlib.metadata as metadata
import json
import subprocess
import sys
from pathlib import Path
from packaging.utils import canonicalize_name, parse_wheel_filename
from airon_adaptation.integrity import file_hash, write_json
from airon_adaptation.worker import upstream_identity, SOUP_REVISION

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", required=True)
parser.add_argument("--source", required=True)
args = parser.parse_args()
output = Path(args.output).absolute()
output.mkdir(parents=True, exist_ok=False)
upstream_identity()
requirements = sorted({dist.metadata["Name"]+"=="+dist.version for dist in metadata.distributions()
                       if canonicalize_name(dist.metadata["Name"]) not in {"soup-cli", "airon-adaptation"}})
subprocess.run([sys.executable, "-m", "pip", "download", "--no-deps", "--only-binary=:all:",
                "--dest", str(output), "--extra-index-url", "https://download.pytorch.org/whl/cpu",
                *requirements], check=True)
subprocess.run([sys.executable, "-m", "pip", "wheel", "--no-deps", "--wheel-dir", str(output),
                "soup-cli @ git+https://github.com/MakazhanAlpamys/Soup.git@"+SOUP_REVISION,
                str(Path(args.source).absolute())], check=True)
locked, files = {}, {}
for wheel in sorted(output.glob("*.whl")):
    name, version, _, _ = parse_wheel_filename(wheel.name)
    key = str(name)+"=="+str(version)
    if key in locked:
        raise RuntimeError("Multiple wheels for one locked distribution")
    sha = file_hash(wheel)
    locked[key] = sha
    files[wheel.name] = {"sha256": sha, "bytes": wheel.stat().st_size}
(output/"requirements.lock").write_text("\n".join(
    key+" --hash=sha256:"+sha for key, sha in sorted(locked.items()))+"\n")
write_json(output/"wheelhouse.json", {"schema": "airon-wheelhouse/v1", "soup": upstream_identity(),
                                     "python": sys.version, "files": files,
                                     "dependency_closure": "REQUIRES_FRESH_OFFLINE_INSTALL_TEST"})
print("WHEELHOUSE_MANIFEST="+json.dumps({"files": files, "distributions": len(locked)}))
