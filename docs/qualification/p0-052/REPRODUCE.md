# Reproduce the governed local adaptation experiment

Use the current PR source checkout, Linux x86-64 and Python 3.12. The measured reference runner uses Ubuntu 22.04. Python, git, bubblewrap, util-linux/unshare, strace and their native libraries must be provisioned before isolation. A Python wheelhouse does not contain the operating system.

## Connected preparation

Run from the AIRON repository root. Use fresh paths for each independent experiment.

```sh
python -m venv .venv
.venv/bin/python -m pip install --index-url https://download.pytorch.org/whl/cpu 'torch==2.9.1'
.venv/bin/python -m pip install -r services/model-adaptation/requirements-training.txt
.venv/bin/python -m pip install -e services/model-adaptation
.venv/bin/python services/model-adaptation/scripts/provision.py \
  --root /absolute/path/airon-preparation-state \
  --assets /absolute/path/airon-model-assets --approve-synthetic-data
.venv/bin/python services/model-adaptation/scripts/prepare_wheelhouse.py \
  --output /absolute/path/airon-wheels --source services/model-adaptation
```

Provisioning verifies every model/tokenizer file against model.lock.json. The source includes the approved synthetic routing/training corpus and the existing synthetic enterprise documents. Keep the source checkout, wheels, requirements.lock, wheelhouse.json, licences.json, packaged notices, model assets and OS/runtime inventory together. Inspect and independently approve these artifacts before transfer.

Soup is installed separately at af2f5d5000f7baec6386a72a6d16e82383eb5303. Workers verify its version and the measured Python-source tree digest before importing it. Generic unreviewed Soup wheels fail this check. No Soup source changes are required.

## Fresh installation with networking unavailable

```sh
python -m venv /absolute/path/airon-offline-runtime
unshare --user --map-root-user --net \
  /absolute/path/airon-offline-runtime/bin/python -m pip install \
  --no-cache-dir --no-index --find-links /absolute/path/airon-wheels \
  --require-hashes -r /absolute/path/airon-wheels/requirements.lock
```

This test creates an empty Python environment, then installs only the exact local wheels. It must fail if a required wheel is absent or altered. Do not replace a failure with a network-enabled install and call that offline qualification.

## Isolate the complete controller and run the real experiment

```sh
mkdir -p acceptance-evidence
AIRON_HOST_NETNS=$(readlink /proc/self/ns/net)
strace -ff -e trace=network -o acceptance-evidence/offline-network \
  unshare --user --map-root-user --net \
  /absolute/path/airon-offline-runtime/bin/python \
  services/model-adaptation/scripts/offline_acceptance.py \
  --root /absolute/path/fresh-airon-offline-state \
  --assets /absolute/path/airon-model-assets \
  --report acceptance-evidence/offline-acceptance.json \
  --parent-netns "$AIRON_HOST_NETNS"
.venv/bin/python services/model-adaptation/scripts/audit_network.py \
  --prefix acceptance-evidence/offline-network \
  --report acceptance-evidence/network-audit.json
```

The offline driver uses local assets, checks dependency consistency, provisions a fresh private workspace and runs actual baseline inference, authorised knowledge queries, training, evaluation, export, scripted test approval, adapted inference and rollback. Its explicit synthetic-test authorization is not proof of an independent human approval.

Both the controller and individual workers receive new network namespaces. Workers also receive restricted filesystem mounts, a clean environment and resource limits. Deliberate failed IP/DNS probes are labelled in the syscall trace. The classifier rejects other IP activity and incomplete probe coverage. Its markers are application labels, not independent agent identities.

A nonzero exit, missing report, failed gate, unexpected network activity or skipped stage is a failure/incomplete result. Read STATUS.md for the latest observed result; commands alone are not acceptance evidence.

## Interactive demonstration

On an independently isolated workstation with local loopback available:

```sh
/absolute/path/airon-offline-runtime/bin/airon-adaptation \
  --root /absolute/path/fresh-provisioned-demo-state
```

Open http://127.0.0.1:8766 and use the terminal's operator token. A fresh prepared state is required to demonstrate training again; a completed job cannot be silently restarted. Review results, request deployment, switch to the reviewer token, approve, activate and roll back. The two local tokens are demonstration roles under one trusted OS account.

The console shows measured training and evaluation values, document responses and exact record details. It never claims that localhost or cloud hosting establishes physical disconnection. The original Ollama and hosted demonstrations are unchanged.

## Verify evidence independently of the running controller

```sh
python services/model-adaptation/scripts/verify_evidence.py \
  /absolute/path/acceptance.json \
  --trusted-public-key APPROVED_32_BYTE_PUBLIC_KEY_HEX \
  --expected-head INDEPENDENTLY_RETAINED_CHAIN_HEAD
```

Supply both anchors from a separate trusted record. Never trust a key merely because it accompanies the evidence. Verification proves the signed record chain under that key; it does not prove truthful execution or compromise resistance of the signer.

## Tests and measurements

```sh
python -m pytest -q tests/integration/soup
python -m unittest discover -s website/offline -p test_server.py
npm --prefix website ci
npm test
npm run build
```

The unit/adversarial suite uses explicit model fixtures. Real training results are separately produced by the acceptance driver. Preserve both positive and failed reports, exact source revision, installed dependency inventory and complete raw syscall traces.
