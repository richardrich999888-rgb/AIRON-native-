# Offline preparation and qualification

## Current implementation

Every worker is launched through unshare --user --map-root-user --net followed by bubblewrap with separate PID/IPC/UTS namespaces. Only an explicit filesystem allowlist is mounted. The worker environment disables Hugging Face downloads/telemetry, has no proxy variables or credentials, and uses preinstalled local models. Remote model code and pickle-format model imports are rejected.

The worker checks for a route-free IPv4 namespace, attempts a connection to an RFC 5737 test address and to host Ollama's usual loopback port, and attempts resolution of an invalid DNS name. Successful connectivity is an error. These deliberate probes are labelled in the report. strace -ff -e trace=network around the acceptance driver independently records syscall attempts from the runner's process tree. Review attempts beyond the deliberate probes; merely seeing failed connections does not prove that no code attempted egress.

This demonstrates only the observed runner and workflow. No physical disconnection, customer network or IAF testbed qualification is implied.

## Before moving to a disconnected host

Use the exact tested Linux/Python/CPU ABI. Prepare and independently approve:

- AIRON source or wheel and its repository licence.
- Soup at the audited commit, including LICENSE and NOTICE.
- Every resolved Python wheel, with SHA-256 and declared licence evidence.
- Python, bubblewrap, unshare, dynamic libraries and required OS packages.
- Pinned pretrained weights, tokenizer, config and model card.
- Authorized dataset, fixed held-out test/regression splits and configuration.
- Baseline rollback artifacts.
- Verifier source, trusted signer public key and independently retained expected chain head.
- Installation commands, qualification scripts and previously observed results.

Provisioning writes a runtime/dependency inventory and pip freeze. requirements-training.txt uses constraints-cpu.txt for the observed CPU package versions. prepare_wheelhouse.py builds a platform-specific wheelhouse, records every wheel SHA-256 and writes requirements.lock, wheelhouse.json, licences.json and packaged notices. Install into a *fresh* environment with --no-index, --no-cache-dir, --find-links and --require-hashes. A source version constraint alone is not an artifact hash lock. Do not treat a successful online install or an already populated cache as evidence that dependency closure is complete.

The worker checks Soup 0.77.2, any declared VCS revision, and the installed Python-source tree digest d87ec3624378b062095b71d68baa820bf88da5e641c623c6b9ead7a1e6a4a6b4. This permits the locally built pinned wheel after offline installation, without relying on direct_url.json surviving wheel packaging. Different Soup code is rejected before import. Wheel hashes separately bind the approved installation artifacts.

A complete fresh offline lifecycle was observed at c1f9ad7b92ebc7574d41c707b9f2fde21899e8e2 in Actions run 43347812566: 63 wheels installed without networking; real inference, training, evaluation, export, scripted test approval, activation and rollback succeeded. The external syscall audit recorded nine complete probe windows across 141 trace files and zero unexpected IP/DNS violations. That historical candidate used the earlier routing-only corpus and abstained on document answers. Later source adds a mandatory adapted-document quality gate and two extra evaluation workers; it requires a new run with at least eleven probe windows. Consult STATUS.md and the exact evidence revision for the current result.

## Acceptance procedure

1. Preprovision and hash the approved artifacts.
2. Record OS/Python/runtime versions, CPU topology and actual resource constraints.
3. Disable external connectivity for the complete runtime, not only the browser.
4. Trace DNS/socket syscalls while running baseline inference, genuine training, evaluation, export, approval, activation, adapted inference and rollback.
5. Confirm no runtime fetch succeeds and classify all attempted connections.
6. Reverify all approved artifact digests and application signatures with the externally supplied public key.
7. Recreate the installation in a new empty environment from the wheelhouse and repeat.

Do not mark M5 complete while only individual workers, fixture lifecycle tests or application environment flags have been exercised.

## Upstream bundle finding

Soup's utils/airgap_bundle.py contains a reusable model/dataset/wheel/kernel tar assembler and per-member SHA-256 manifest. Its inspected build path does not sign that manifest, despite the module-level description referring to a signed manifest. inspect_airgap_bundle reads metadata; it does not hash-check every payload member. AIRON's bundle.py reuses the assembler and adds a detached Ed25519 whole-archive attestation, complete member inventory/hash checking, and rejection of links, traversal, duplicate members and undeclared bytes. It deliberately performs no extraction. Bundle API tests use tiny fixtures; they do not qualify a real installation or a safe extraction utility. The actual fresh wheelhouse installation and isolated workflow have their own evidence, separately from these archive tests.


## Bundle API

In a trusted preparation process whose current directory contains all input/output paths:

    from airon_adaptation.bundle import build_bundle, verify_archive
    result = build_bundle(model_dir, [dataset_dir], wheelhouse_dir, output_tar, signer_key)
    verify_archive(output_tar, detached_attestation, externally_trusted_public_key)

The wheelhouse must include wheel files and requirements.lock. File presence does not prove that the wheel files are valid or that the lock covers every dependency; the verifier explicitly reports REQUIRES_FRESH_OFFLINE_INSTALL_TEST. Retain the archive, detached attestation, trusted public key, exact preparation/runtime versions and qualification results separately. Never include the controller's signing.key or state database in a redistribution bundle.

A reviewer must trust the public key independently of the archive. An archive and a matching attacker-supplied key establish no provenance.
