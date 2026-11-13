# AIRON Native — Private AI That Learns Locally

Experimental Linux adaptation service. It adds a governed Soup training experiment beside the existing AIRON demonstrations. It is not a production release. Read the current qualification record before presenting any capability as validated.

## Preparation (connected, explicitly before isolation)

From the repository root, with Python 3.12, git, bubblewrap and util-linux/unshare installed:

    python -m venv .venv
    .venv/bin/python -m pip install --index-url https://download.pytorch.org/whl/cpu 'torch==2.9.1'
    .venv/bin/python -m pip install -r services/model-adaptation/requirements-training.txt
    .venv/bin/python -m pip install -e services/model-adaptation
    .venv/bin/python services/model-adaptation/scripts/provision.py \
      --root /absolute/path/airon-state \
      --assets /absolute/path/new-model-assets \
      --approve-synthetic-data

Use fresh asset and state directories for independent experiments. Provisioning downloads only the enumerated model/tokenizer files at a fixed revision, verifies the model card's declared licence, preserves the card, creates a synthetic approved dataset with fixed splits, and prepares a bounded training job. Never put customer material into this demonstration.

The requirements file selects an audited Soup VCS revision and core ML versions. Transitive versions must be frozen and their licences reviewed for the deployment. Provisioning records actual installed distributions, licence metadata and pip freeze. The preparation script additionally builds a hash-locked platform-specific wheelhouse and inventories packaged notices. See ../../docs/qualification/p0-052/REPRODUCE.md for the fresh offline installation and full isolation procedure. Runtime redistribution still requires reviewing the exact dependency/native-platform terms.

## Guided local console

    .venv/bin/airon-adaptation --root /absolute/path/airon-state

Open http://127.0.0.1:8766. Paste the operator token printed in the local terminal. Tokens remain in page memory only.

1. Deploy: refresh status and inspect the preinstalled base and prepared data.
2. Understand: ask the approved synthetic document; inspect an answer or explicit abstention. Run the frozen benchmark separately.
3. Identify limitations: inspect expected answers and baseline predictions.
4. Adapt: start training. Refresh status until SUCCEEDED or FAILED.
5. Verify: register the checkpoint, then compare baseline/candidate scores.
6. Authorise: request review. Switch to the separately printed reviewer token, inspect the evaluation and approve.
7. Activate: activate the approved candidate in this experimental runtime, then run inference.
8. Inspect isolation: read the namespace/connectivity probes in worker results and the acceptance syscall trace. Do not call a browser on localhost a physical air gap.
9. Inspect evidence: export/verify signed application records; retain an externally trusted public key and chain head.
10. Roll back: restore the previous experimental model and run inference again.

The console does not automatically poll, promote, harvest conversations, modify model weights or change Ollama. Operations requiring missing input, insufficient authority or failed evaluation fail closed. The model-selection test is a closed-choice synthetic routing task, not general enterprise answer quality.

The adaptation runtime imports the existing synthetic document corpus during explicit provisioning. Its query_knowledge operation enforces server-bound document roles before sending an approved source to the same active base/adapter used by the experiment. Unknown questions abstain; restricted documents never reach the model. Generated text is released only when it exactly reproduces the approved source. An abstention is a valid safety outcome, not a successful answer-quality result. No conversation is automatically added to training data.

The original Ollama gateway remains unchanged and separate from this model backend. No Ollama adapter installation or production enterprise identity integration is implied.

## Reproducible experiment

A provisioned job can be exercised without the UI:

    .venv/bin/python services/model-adaptation/scripts/probe_sandbox.py --root /absolute/path/airon-state
    .venv/bin/python services/model-adaptation/scripts/run_acceptance.py \
      --root /absolute/path/airon-state --report /absolute/path/acceptance.json

Without the explicit synthetic-test approval flag, the driver stops awaiting review. For an authorized synthetic test only:

    .venv/bin/python services/model-adaptation/scripts/run_acceptance.py \
      --root /absolute/path/fresh-airon-state --report /absolute/path/acceptance.json \
      --approve-synthetic-test-deployment

This flag is scripted test authorization, not proof of independent human review. The controller's actual UI approval path requires a reviewer session and a different actor. Improvement and regression gates are enforced in both paths. A failed candidate is recorded and never activated.

The script returns nonzero when a gate is incomplete or fails. It writes the observed report and signed evidence even on failure. It restores the prior model in a finally block after activated-model inference. CPU/RAM and latency values come from worker measurements; no GPU performance is inferred.

## Tests

    python -m pip install cryptography pytest ./services/model-adaptation 'soup-cli @ git+https://github.com/MakazhanAlpamys/Soup.git@af2f5d5000f7baec6386a72a6d16e82383eb5303'
    python -m pytest -q tests/integration/soup
    cd website/offline
    python -m unittest test_server.py

The controller tests deliberately use fixture bytes in place of models. They test governance, integrity and failure behavior; they are not training evidence. CI runs them separately from the real CPU experiment. Existing website tests/build are also retained.

## Files and assurance

- controller.py: signed state, job supervision, registry, approval and rollback.
- worker.py: pinned Soup SFT, local inference/evaluation and merge helper.
- sandbox.py: explicit mounts, no inherited credentials, fresh network namespace.
- integrity.py: canonical encoding, data-only imports and hash verification.
- evidence.py: Ed25519 application signatures and externally anchored chain verification.
- server.py and ui/: local reviewer/operator console.
- scripts/: connected preparation and actual acceptance driver.
- fixtures/: synthetic data with a CC0 declaration.

AIP and Sniffer Dog are not runtime dependencies. Application records remain APPLICATION_SIGNED / independent execution CANNOT_PROVE. See docs/integrations/soup/ARCHITECTURE.md for exact API parameters and trust boundaries.

## Qualified scope

Read [the qualification status](../../docs/qualification/p0-052/STATUS.md) and [the full reproduction procedure](../../docs/qualification/p0-052/REPRODUCE.md). Passing fixture tests, importing a package and completing a genuine model adaptation are separate evidence classes. Signed application evidence does not replace independent execution observation.
