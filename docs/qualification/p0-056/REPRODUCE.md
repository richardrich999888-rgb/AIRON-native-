# Reproduce P0-056 evidence

Tested source: AIRON initial lifecycle `16c6bd745edacaa4ad7b435cc52de935e1d1802f`; final qualification target `0f4cd7e20f4c19577b5a73b9d1dacdc221f3085a`; native interface `f1ba9fc2072dac1431543fd4961baaa2762b8ea9`. See `BENCHMARKS.json` and `evidence/local/PROVENANCE.json` for per-run revisions. Local hardware: Linux 6.18.57, AMD EPYC 9V74, 9 visible CPUs, 10,206,472 KiB RAM, no GPU; inference comparisons restricted to CPUs 0–1. Hosted hardware: Ubuntu 22.04, Linux 6.8 Azure, 4 visible CPUs, 16,371,436 KiB RAM; the corrected two-CPU run enforced an 8 GiB cgroup limit but training timed out; separate four-CPU training and two-CPU serving qualification is in progress. No claim of independent administration.

Follow BUILD_AND_INSTALL with the exact AIRON and native revisions. The primary workflow records the source commit, platform, affinity and local model artifacts. Two-phase provisioning/install keeps online acquisition outside serving.

Commands from the AIRON root after qualified dependencies/native artifacts are provisioned:

```bash
PYTHONPATH=services/model-adaptation:services/unified-runtime python -m pytest -q tests/integration/soup tests/integration/unified
python -m unittest discover -s website/offline -p test_server.py
python services/unified-runtime/scripts/run_demo.py --root /absolute/state --report demo.json --backend llama --approve-synthetic-test-deployment
python docs/qualification/p0-056/helpers/audit_egress.py --prefix /absolute/network --expected-probes 7 --report network-audit.json
python docs/qualification/p0-056/helpers/export_public_snapshot.py --root /absolute/state --demo demo.json --output public-snapshot.json
python docs/qualification/p0-056/helpers/verify_snapshot.py --snapshot public-snapshot.json --report snapshot-verification.json
```

The first command additionally requires `P056_ASSETS`, `P056_AIP_SOURCE` and `P056_AIP_BIN`. The original native suite runs with `cargo +1.99.1 test --locked -p syntriass-runtime` in AIP. Tests deliberately fail rather than mock a missing native binary or Docling.

`services/unified-runtime/scripts/benchmark.py` takes a new `--root`, `--report`, local `--assets`, `--aip-dir`, `--bin-dir`, `--llama`, `--gguf` and the explicit synthetic-deployment flag. It verifies the frozen protocol hash, creates distinct development suites and then runs the untouched 30-case set twice. Model baselines are strict label generation; B3/B5 execute actual approved procedures. Do not compare B4's different routing-task accuracy directly with these values.

`qualify_scale.py` uses only previously approved local GGUF files from `scale-models.lock.json`; it never downloads. Optional `provision_scale.py --approve-download` is an online acquisition tool, excluded from serving. The 3B model is not approved by this lock.

Install pinned LM Evaluation Harness / MLflow source only in a separate qualification environment. `qualify_harness.py` executes actual local generation on the frozen custom task; `track_experiment.py` verifies signed evidence before logging it to local SQLite and checks the recovered artifact hash. Set telemetry-disable flags before importing MLflow. No public standard-benchmark equivalence is asserted.

Cosign requires a local key and an explicit empty signing service configuration. `sign-blob --signing-config offline-signing.json --key ... --bundle ...` and `verify-blob --key ... --bundle ... --insecure-ignore-tlog=true` implement the tested offline key-based policy. The transparency-log exemption is intentional and documented, not a substitute for signature checks. Wrong-key and altered-artifact tests must fail.

Raw results compressed with gzip are byte-preserving (`gzip -dc`). Compare their hashes and provenance before aggregating results. Retain failed iterations. Local Git commit `853fd413...` and published `bb87ca5...` have the same tree; the provenance sidecar explains base-labelled optional-tool runs rather than silently rewriting their raw source labels.

For recipient-held evidence anchors, decompress the retained public-snapshot JSON and run:

```bash
python docs/qualification/p0-056/helpers/verify_snapshot.py --snapshot public-snapshot.json --trust-pins trust-pins.json --report checked.json
```

Retain the pins through a trusted separate channel before comparing later copies. For the destructive-copy qualification (the original is unchanged):

```bash
python docs/qualification/p0-056/helpers/qualify_snapshot.py --snapshot public-snapshot.json --output snapshot-checks
```

The output pins from this test are same-administrator fixtures, not an independent approval.
