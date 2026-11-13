# P0-052 work ledger

Updated 13 November 2026. Status applies to the exact cited evidence, not every later commit.

| Work item | Status | Code reference | Test evidence | Blocker / next action |
|---|---|---|---|---|
| Inspect existing sources | DONE, scoped | UPSTREAM_AUDIT.md | Exact AIRON/Soup/AIP/model pins, source/manifests/history inspection | No claim of exhaustive upstream security audit |
| Bounded control plane | PASS | controller.py, sandbox.py, server.py | 93 checks at 7b964cd, local and CI | Trusted single OS account; aggregate quotas and enterprise identity open |
| Existing demonstrations | PASS | website/offline; website | 15 gateway tests, 8 website cases and build at 7b964cd | Original runtime unchanged |
| Genuine training | PASS, recorded source | worker.py | a297332: 45 optimizer steps, 120 tensors, separately inspected real adapter | Stronger 102-record candidate under test |
| Model-quality gate | IMPLEMENTED, v3 trial pending | controller.evaluate_candidate | Actual rejected retention candidates; current minimum 50% routing | Need a v3 passing candidate |
| Candidate lifecycle | PASS under v2 | registry, approval, activation, rollback | a297332 complete real workflow and restored predictions | Scripted reviewer is not independent human identity |
| Knowledge controls | PASS, recorded source | knowledge.py, query_knowledge | Actual full-source generation, denial and abstention at a297332 | Synthetic exact-question corpus only |
| Offline dependencies | PASS on tested platform | prepare_wheelhouse.py | 63-wheel hash-locked fresh isolated installation; all notices retained | Full OS/native redistribution review before shipping runtime |
| Complete offline operation | PASS under v2 | offline_acceptance.py, audit_network.py | a297332 full lifecycle; 11 probe windows, no violations | New v3 candidate requires complete rerun; customer hardware separate |
| Evidence | PASS at application level | evidence.py, EVIDENCE_INDEX.json | Signed chains, source-reviewed anchors and downloaded artifact checks | Independent identity/key custody and external anchoring open |
| Actual fault checks | PASS | run_fault_acceptance.py | a297332: optimizer-progress cancellation -9; malformed safetensors parser rejection | Broader recovery/resource faults remain unqualified |
| Guided console | PASS, recorded source | ui/, check_console.py | Actual workspace, raw downloaded chain, reviewer denial, mobile/desktop | Quality claim limited to displayed benchmark |
| Diagnostic crash | FOLLOW-UP RUNNING | worker.main | 0f46ef0 SIGSEGV during periodic stack dump; 7b964cd removes only that diagnostic | Await controlled rerun; no unproven root-cause claim |
| Review delivery | DRAFT PR #2 | Target main | Pinned commits, source/evidence/history retained | Do not merge without review |

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

Complete the unchanged-evaluation 102-record trial under the current v3 gate, then repeat its fresh offline lifecycle and artifact verification. Preserve every rejection and runtime failure. The earlier v2 workflow remains reproducible but its weak routing score is insufficient for the current gate.

## Controlled retention iteration (pending real results)

The routing-only adapter abstained on the real document query. The next candidate adds twelve explicitly synthetic source-copy training examples alongside the original eighteen routing records. Frozen routing/factual questions and the existing knowledge corpus are unchanged and absent from training records. The evaluation now requires an actual full-source candidate quote before deployment approval. The release validator can discard model-added framing but only returns the complete approved source, with whitespace differences ignored during matching. It never releases additional generated text. Exact dependency versions from the executed CPU stack are now constrained in source.

The first retention-data trial (921f111, run 43349342064) produced a genuine adapter and reproduced the full approved document, but factual regression fell from 3/6 to 0/6 while routing increased from 1/6 to 3/6. The candidate was rejected before deployment. Its complete signed report is retained in evidence/rejected-retention-921f111.json. The next trial changes only the learning rate from 0.001 to 0.0003; training examples and all evaluation material remain unchanged. This is explicit development-set experimentation, not evidence from an untouched independent holdout.

The 0.0003 trial (fe2046d, run 43350750912) completed 45 optimizer steps and changed 120 tensors. Routing increased from 1/6 to 2/6 and factual scores from 3/6 to 6/6, but candidate source-copy generation failed. The unchanged gate rejected it before deployment. Retained evidence: rejected-retention-fe2046d.json. Real optimizer-progress cancellation and malformed safetensors rejection passed separately (faults-fe2046d.json). The next trial reduces only the learning rate to 0.0001. The fault harness now requires the actual safetensors parser error so an unrelated worker failure cannot satisfy that check.

Local execution became available again. The pinned CPU stack installed successfully. The first local fixture run exposed two tests that opened real AF_UNIX sockets before reaching their mocked namespace conditions; the workspace denies those sockets. Those two tests now mock only the trace marker, leaving the production isolation checks unchanged. The installed-environment rerun passed all 67 tests; Python compilation and diff whitespace checks passed. Local connected model provisioning failed before download because the workspace proxy needs socksio. Full real execution continues on the already validated GitHub Actions runner; no local training pass is claimed.

Release-evidence review found that JSON reserialization had changed integer-valued float spelling in two retained rejection reports, breaking their signatures. Restored exact raw report JSON from the corresponding Actions logs; all eight retained chains then verified with their recorded heads. Added a source-reviewed evidence index and regression checks. The console now offers a raw-response download so its formatted JavaScript detail view cannot accidentally become an invalid signed export. Browser verification of the downloaded record chain is part of the next rehearsal.

Local verification after these changes: 77 controller, adversarial, transport and retained-evidence checks passed; JavaScript syntax, Python compilation and git diff whitespace checks passed. The b4b9505 real experiment is still running; no outcome is inferred from this local result.

The b4b9505 primary real lifecycle passed all gates, including the full adapted document answer, and advanced to fresh offline preparation. Review of the tightened fault harness exposed a diagnostic gap: run_path was previously recorded only on successful training. The controller now signs/persists that path before launch, so a failed or cancelled job retains an unambiguous worker-log location; inference and evaluation cannot overwrite it. Added a failure-injection check that registration remains denied and the correct log/config remain available. The forthcoming real malformed-model test exercises this path without mocks.

Evidence delivery now retains actual trained adapter safetensors in the CI artifact, bound to the existing manifests, without exporting the signing key or state database. A prerequisite collector records Python/bubblewrap/unshare/strace binary hashes, actual linker output and selected OS package versions. This adds concrete reproducibility evidence while leaving full native redistribution review open. The 78-test suite passed after the failed-job diagnostic fix.

The prerequisite collector executed locally and identified all four binaries with resolved linker dependencies. The workspace has no matching Debian package records, so that separate inventory is explicitly partial; it is not converted to a pass. The Ubuntu CI execution will record its own package result. Candidate artifacts also retain the approved base model card, Apache-2.0 terms and synthetic-data licence.

## Model-quality iteration after the first offline slice

b4b9505 completed the full isolated workflow and browser check: 45 steps, 120 changed tensors, 95.782 s offline training/save, 1,704,472 KiB peak worker RSS, routing 1/6→2/6, factual 3/6→3/6 and a full approved-source answer. The downloaded artifact SHA-256 matched GitHub metadata. All 173 raw network traces rehashed and the syscall classifier passed again locally; its 20 signed events verified against the retained head. All 63 wheels had packaged or supplemental notices. The real fault harness exposed the missing failed-job run_path, now fixed in 3f54825. The browser raw-download signature check subsequently passed at 170e4db.

Although the lifecycle worked, 2/6 routing is only the constant-label reference score for the balanced three-class suite. It is not an adequate investor quality claim. Policy v3 now additionally requires at least 50% routing accuracy and rejects prior-policy approvals. The next trial retains the original evaluation questions and knowledge corpus, expands authorised routing training from 18 to 90 distinct records, retains the twelve disjoint copy records, and aligns their system instruction with runtime generation. Total training records: 102; 153 expected steps at three epochs, rank 8, LR .0003, seed 52. No passing result is assumed. The local suite passed 85 checks, including all newly retained signed reports.

The 102-row trial at 0f46ef0 (run 43358210167) reached step 92/153 and exited 139 during the periodic 120-second faulthandler traceback. The external strace recorded SIGSEGV in that diagnostic thread, and the log ends mid-stack. This is observed correlation, not an established CPython/root-cause diagnosis. No adapter registered or activated. The next controlled trial removes only the asynchronous periodic stack walk; fatal-signal reporting, the 300-second external wall timeout and all OS limits remain. Dataset, training configuration and quality gates are unchanged. Complete failure report and hashed diagnostic excerpt retained.

The 7b964cd diagnostic ablation reached 149/153 optimizer steps on an AMD EPYC runner, then the 300-second external wall limit killed it. No candidate registered or activated; the complete signed failure report is retained. The previous segmentation fault did not recur in this run, but a root-cause proof is not claimed. The larger, authorised dataset now receives a bounded 480-second training-only wall limit and 900 CPU-seconds; other operations retain 300/600 seconds and every operation retains the 6 GiB address-space limit. Worker reports record the applied OS CPU/address-space limits. Dataset, model, learning rate, epochs and quality gates remain unchanged.

A test-only AIP raw-signature experiment is now prepared under tests/integration/aip-signature. It links the separately checked-out, unmodified pinned aip-crypto crate against its original Cargo.lock; no proprietary code or binary is added to AIRON runtime/distribution. Local Python preparation verified the retained 20-event offline report and emitted exact signing bytes. Local Rust execution is unavailable (cargo absent). A separate CI job will verify actual AIRON signatures with AIP, reject altered messages/signatures/keys, and verify a public-seed AIP signature with Python in a network-isolated stage. No result is claimed before execution.
