# P0-052 work ledger

Updated 13 November 2026. Status applies to the exact cited evidence, not every later commit.

| Work item | Status | Code reference | Test evidence | Blocker / next action |
|---|---|---|---|---|
| Inspect current AIRON | DONE | Base 04a84e6 | Clone, branch/history/manifests/source inspection | No adaptation existed at base |
| Pin/audit Soup | DONE, scoped | UPSTREAM_AUDIT.md; requirements-training.txt | af2f5d5; source-tree digest checked by real worker | Full native redistribution review |
| Inspect AIP | DONE, no runtime dependency | ARCHITECTURE.md | 872dbf3 raw crypto/README; P0-048 reference | Ownership decision and executed bridge contract |
| Controller/API/adversarial suite | PASS | tests/integration/soup | 63 tests at 34d150c; equivalent suite at 53976dc passed | Production identity/key custody remain outside demo |
| Existing demonstrations | PASS | website/offline; website | 15 gateway tests, 8 website cases and build | Original hosted/Ollama behavior unchanged |
| Real Soup operation/training | PASS | worker.py | 53976dc: 27 steps, 120 tensors, FP32 measured | One small CPU model only |
| Candidate lifecycle | PASS, scoped | controller.py | Real evaluation, export, activation, rollback | Scripted reviewer is not independent human approval |
| Knowledge access integration | CONTROLS PASS | knowledge.py; query_knowledge | Denial, unknown-question abstention, local generation | Real source-copy answers currently abstain |
| Offline wheelhouse | PARTIAL | prepare_wheelhouse.py | 63 wheels; fresh isolated install at 3444026 | Correct top-level metadata selection; rerun full workflow |
| Complete offline operation | INCOMPLETE | offline_acceptance.py; audit_network.py | Individual workers isolated; full fresh-runtime run failed previously | Require full lifecycle plus classified syscall trace |
| Evidence verification | PASS, application level | evidence.py; verify_evidence.py | Real retained 15-event chain externally anchored in CI | Independent observer/anchor custody not integrated |
| Real process fault checks | IMPLEMENTED, PENDING | run_fault_acceptance.py | Upcoming actual in-flight cancellation and malformed safetensors load | No fixture substitution |
| Guided console | IMPLEMENTED, PENDING browser check | ui/; check_console.py | Upcoming browser check against real completed workspace | Document answer quality open |
| Review delivery | DRAFT PR #2 | Target main | Commits and branch preserved via GitHub API | Do not merge without review |

## Observed failures and fixes

- Local workspace execution became unavailable after training-stack imports/install attempts exited 137. No kernel OOM diagnosis was available. Implementation and actual execution continued through GitHub and Actions.
- 53453da: package discovery included fixtures as a top-level package. Fixed explicit package discovery.
- dd8f3b9 through 658d4f6: isolated procfs returned an empty route file. Accept an empty or header-only zero-route table only with a distinct namespace and failed live probes.
- bfd00de: real training completed, but the artifact allowlist rejected tokenizer chat_template.jinja. Allow only this exact standard template filename; arbitrary model code remains forbidden.
- Initial arithmetic regression suite scored 0/4 at baseline. Reject a vacuous preservation claim; use a documented fixed factual suite. Routing test prompts were not changed.
- 3444026: fresh offline install succeeded, then training failed while dependencies were exposed at both /app and /env. Narrow the app mount to airon_adaptation only.
- e71de2e: training slowed to about 20 seconds/step and exited 137 near step 25. 34d150c diagnostics showed backward computation and the bounded worker stopped at 300 seconds. No OOM diagnosis is asserted.
- 53976dc: explicitly checked FP32 training completed in 42.9 seconds on the AMD runner, with unchanged passing frozen scores.
- b1b88a6: knowledge registry used a singleton identifier rejected by generic ID validation. Fixed explicit singleton handling; all five new knowledge tests pass.
- 53976dc: offline notice inventory saw nested vendored METADATA files as multiple distribution metadata records. Select only the wheel's top-level dist-info/METADATA and keep vendored notices.
- Failed/skipped downstream stages remain incomplete. Full failed reports are retained where available.

## Next highest-value task

Complete the fresh offline workflow with full syscall classification and browser inspection; then execute real cancellation/corrupt-model checks. Preserve the observed document abstention as an open quality result rather than weakening the release validation.
