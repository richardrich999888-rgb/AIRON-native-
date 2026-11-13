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

Provisioning writes a runtime/dependency inventory and pip freeze. Source-declared ranges are not a reproducible offline lock. Build a wheelhouse on a matching connected staging host, record its hashes and install it into a *fresh* environment with --no-index --find-links and --require-hashes. Do not treat a successful online install or an already populated cache as evidence that dependency closure is complete.

The present worker accepts Soup's immutable VCS-install provenance. Installing Soup from a generic wheel loses that provenance and will fail its check; a reviewed wheel-provenance bridge is still required for a clean offline installation. Do not bypass the pin check. A preprovisioned runtime whose package metadata and code remain intact can be used to test offline operation now.

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

Soup's utils/airgap_bundle.py contains a reusable model/dataset/wheel/kernel tar assembler and per-member SHA-256 manifest. Its inspected build path does not sign that manifest, despite the module-level description referring to a signed manifest. inspect_airgap_bundle reads metadata; it does not hash-check every payload member. Before relying on an upstream bundle, AIRON needs complete member verification plus a separately trusted archive/manifest signature and tested safe extraction. This remains a named packaging gap; no counterfeit “air-gap-ready bundle” is shipped.
