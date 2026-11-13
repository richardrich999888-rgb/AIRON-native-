# P0-052 work ledger

Updated 13 November 2026. Test statuses are scoped to the cited commit/run.

| Work item | Status | Code reference | Executed evidence | Blocker / next action |
|---|---|---|---|---|
| Inspect current AIRON | DONE | Base 04a84e6, website/offline/server.py | Clone, branches, log and source reads | None |
| Pin/audit Soup | SOURCE REVIEW DONE | requirements-training.txt; UPSTREAM_AUDIT.md | af2f5d5 source clone and focused reads | Full dependency redistribution review |
| Inspect AIP boundary | DONE, no runtime import | ARCHITECTURE.md | Main 872dbf3 raw crypto and README; P0-048 reference/README | Ownership/licence decision and cross-language tests |
| Controller and HTTP boundary | FIXTURE TESTS PASS | controller.py, server.py | 36 tests at 6202242, Actions 43337077363 | Production identity and key custody |
| Preserve current demos | REGRESSION PASS | Existing website/offline and website/tests | 15 gateway + 8 website tests and build at 6202242 | Real Ollama integration remains separate |
| Package AIRON service | FIXED AFTER FAILURE | pyproject.toml | Run 43337381647 failed on ambiguous package discovery | Explicit package list; rerun queued |
| Genuine Soup data operation | PENDING | worker.py probe | Remote CPU workflow | Await actual result |
| Real LoRA training | NOT YET QUALIFIED | worker.py train | Local import/install exit 137; remote acceptance queued | Actual changed tensors and loadable adapter |
| Evaluation and regression | IMPLEMENTED, real result pending | worker.py evaluation; controller gate | Synthetic fixture gate tests | Actual model scores |
| Approval and rollback | FIXTURE TESTS PASS | controller.py | Role, integrity, replay, rollback tests | Actual adapted inference and restoration |
| Offline operation | NOT QUALIFIED | sandbox.py; OFFLINE_INSTALL.md | Basic namespace probes only before outage | Complete workflow isolation and syscall review |
| Offline distribution | OPEN | OFFLINE_INSTALL.md | Source analysis of Soup bundle | Wheel closure, provenance bridge, full member verifier, fresh install |
| Ed25519 records | FIXTURE TESTS PASS | evidence.py | Tamper, chain order and anchored truncation tests | External trust anchor/custody deployment |
| Guided console | IMPLEMENTED, visual QA pending | airon_adaptation/ui/ | Static source only | Browser inspection and real rehearsal |
| Draft delivery | OPEN PR | PR #2, target main | GitHub API commit/ref/PR verified | Do not merge without review |

## Failure record

- Local training-stack install and PyTorch import attempts exited 137. The workspace then became unavailable. No kernel OOM diagnosis or real training success was observed.
- Initial remote CPU job at 53453da failed during editable AIRON package installation: setuptools found fixtures and airon_adaptation as multiple top-level packages. The fix explicitly discovers only airon_adaptation*. A package-install check was added to the fast CI job.
- Unexecuted downstream steps are skipped/pending, never passed.

## Current highest-value task

Complete the real CPU worker run and investigate its first actual failure. Do not expand to GPU training or autonomous feedback ingestion before the first governed experiment is supported by evidence.
