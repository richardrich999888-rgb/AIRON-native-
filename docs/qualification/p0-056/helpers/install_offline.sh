#!/usr/bin/env bash
set -euo pipefail
# Run from the extracted AIRON_P0_056 folder. Provisioning requires the
# separately licensed AIP checkout and its compiled native interface.
bundle_dir=$(cd -- "$(dirname -- "$0")" && pwd)
: "${AIRON_NATIVE_SOURCE:?Set the approved AIP checkout path}"
: "${AIRON_NATIVE_BIN:?Set the directory containing syntriass and airon-bridge}"
: "${AIRON_WORKSPACE:?Set a new absolute workspace path}"
test "${AIRON_WORKSPACE:0:1}" = /
test "$(git -C "$AIRON_NATIVE_SOURCE" rev-parse HEAD)" = f1ba9fc2072dac1431543fd4961baaa2762b8ea9
test ! -e "$AIRON_WORKSPACE"
cd "$bundle_dir"
sha256sum -c MANIFEST.sha256 > installation-hashes.log
for command in python3.12 unshare prlimit bwrap; do command -v "$command" > /dev/null; done
test ! -e "$bundle_dir/runtime"
unshare --user --map-root-user --net env -u PYTHONPATH python3.12 -m venv runtime
unshare --user --map-root-user --net env -u PYTHONPATH runtime/bin/python -m pip install --no-index --find-links wheelhouse --require-hashes -r wheelhouse/requirements.lock
unshare --user --map-root-user --net env -u PYTHONPATH runtime/bin/python -m pip check
unshare --user --map-root-user --net env -u PYTHONPATH runtime/bin/python source/services/unified-runtime/scripts/provision.py \
  --root "$AIRON_WORKSPACE" --assets "$bundle_dir/models/hf135" \
  --aip-dir "$AIRON_NATIVE_SOURCE" --bin-dir "$AIRON_NATIVE_BIN" \
  --llama "$bundle_dir/llama/bin/llama-completion" --gguf "$bundle_dir/models/135m.gguf" --approve-synthetic-data
printf '%s\n' 'Installed and provisioned. Run the documented synthetic acceptance before deployment.'
