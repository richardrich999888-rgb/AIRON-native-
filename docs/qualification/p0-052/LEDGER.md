# P0-052 work ledger

Updated 13 November 2026. Results apply to the exact source/run cited. Runtime 6077c9a104c42e024ae343aafdc2cc4a91181663 passed full run 43373086529. Original failures remain in EXPERIMENTS.md and evidence/.

| Work item | Status | Code reference | Test evidence | Blocker / next action |
|---|---|---|---|---|
| Source and licence qualification | DONE, scoped | UPSTREAM_AUDIT.md, LICENCE_REPORT.md | Immutable source/model pins, declared and actual wheel inventory; 139 notice hashes rechecked | Complete native/OS redistribution review before shipping a runtime |
| Bounded control plane | PASS | controller.py, sandbox.py, server.py | 111 CI checks at 6077c9a; original demo tests passed | Trusted OS account; aggregate quotas and enterprise identity remain open |
| Genuine model adaptation | PASS | worker.py, dataset.py | 6077c9a: 189 steps, 420 changed tensors; 102 primary + 24 native Soup replay rows | CPU-only selected model; no GPU/streaming/QLoRA claim |
| Contamination and authorization | PASS, narrow | Controller._validate_rows, prepare_dataset | Actual loader, authorization/duplicate/quarantine/manifest tests; frozen evaluation digest | Semantic poisoning and independent real-data review remain open |
| Model-quality gate | PASS v3 | evaluate_candidate | Routing 1/6→5/6, facts 3/6→6/6, complete approved-source answer | Six cases per classification split; reused development set, not scientific holdout |
| Governed activation and rollback | PASS v3 | approval/deployment registry | Primary and offline workflows; version 2 activated, version 3 restored original predictions | Test reviewer scripted; enterprise human identity not qualified |
| Knowledge access | PASS, synthetic corpus | knowledge.py, query_knowledge | Actual full-source answer; denied and unsupported queries stop before model | Exact-question retrieval; arbitrary document ingestion open |
| Offline dependencies | PASS on tested ABI | prepare_wheelhouse.py | Fresh 63-wheel hash-locked installation with networking unavailable | Native OS prerequisites must be preinstalled and approved |
| Complete offline operation | PASS v3, tested runner | offline_acceptance.py, audit_network.py | Entire lifecycle; eleven probe windows, 163 raw traces rechecked, zero unexpected IP/DNS violations | Customer hardware/physical disconnection separately required |
| Adapter artifact delivery | PASS | artifact 14015340252; adapter-artifact-6077c9a.json | ZIP hash, both real adapters, 420 FP32 tensors, 210 nonzero B tensors; primary/offline weights equal | Retain finite-lifetime artifact or reproduce |
| Application provenance | PASS, scoped | evidence.py, EVIDENCE_INDEX.json | 20-event chains and original browser-download bytes verified; source-reviewed anchors | Independent custody and external anchoring open |
| AIP compatibility | PASS, raw bytes only | tests/integration/aip-signature | Actual pinned Rust crate: 20 signatures, 60 tamper rejections and cross-implementation signing; run 43373086477 passed | No full AIP protocol, identity or production dependency |
| Independent execution | OPEN | INDEPENDENT_OBSERVATION.md | Observer source inspected; local capability/tool limitations recorded | Compatible separately administered observer/testbed and licensed contract |
| Real fault acceptance | PASS | run_fault_acceptance.py; faults-6077c9a.json | Actual optimizer cancellation, no registration, real baseline inference after cancellation, actual malformed-model parser rejection | No unsafe optimizer recovery or hostile-admin resistance claim |
| Cancellation scope fix | PASS | Controller._execute; CANCELLATION_FIX.md | Reproduced failing regression; fixed training-only callback, preserved launch-race stop; actual inference after cancel passed | None for the reproduced defect |
| Guided local console | PASS, experimental | ui/, check_console.py | Real workspace, scores, role denial, raw signed download, desktop/mobile | No physical-air-gap or general-quality claim from UI alone |
| Existing product preservation | PASS | original website and Ollama gateway | No runtime diff from main; 15 gateway tests, 8 website cases and build at 6077c9a | Adapted HF/PEFT runtime is separate |
| Review delivery | DRAFT PR #2 | codex/p0-052-airon-soup-offline-adaptation | Immutable source and retained reports/failures; final commit records evidence only | Review required; main unchanged and no automatic merge |

## Latest completed engineering iteration

Inspected source: Controller._execute and its process-start/cancellation callback, sandbox supervision, fault acceptance harness, original failed logs and pinned Soup training/replay behavior. Found and reproduced a bug: cancelled training status also stopped later baseline inference. Changed the callback to apply the cancellation race guard only to training; the cancelled-training launch race remains rejected. Added genuine baseline inference after actual cancellation to the fault acceptance driver. Learning inputs, frozen evaluation and approval gates remain unchanged.

Executed: local regression first failed as expected, then passed after the fix; CI passed 111 checks and the original website/gateway suites. Full run 43373086529 completed two real trainings, fresh offline installation and the complete isolated lifecycle, browser checks, actual cancellation at step 1/756, 12-row baseline inference while the job remained cancelled, and the malformed safetensors parser rejection. Every stage passed. Actual AIP raw-byte contract run 43373086477 also passed.

Evidence: original signed reports and measured resource/quality values; externally traced syscalls within the same runner administration boundary; separate downloaded-artifact reinspection outside the training runner. All 163 traces reclassified with no unexpected IP/DNS violations, both adapter manifests and 420 FP32 tensors checked, 139 notices and 63-wheel lock checked. These checks do not constitute independent signer identity or independently administered execution observation. The final documentation commit changes no tested runtime/test/workflow files.

## Preserved failures

EXPERIMENTS.md retains rejected candidates, interrupted/failed workers and failed harness reports. These include vacuous baseline evaluation replaced explicitly during development; package/mount and precision issues; diagnostic-thread SIGSEGV without an asserted root cause; wall timeout; inadequate routing; factual forgetting; lost source-copy behavior; and a rehearsal-omitting cancellation progress counter. The latter was fixed at 3ce3cfe and its complete rerun passed before the subsequent cancellation-scope fix. Rejected candidates were not activated. Later passes do not erase earlier failures.

## Next highest-value task and exact constraints

The next qualification task is a larger independently prepared evaluation suite on customer-controlled hardware, followed by separately administered execution observation and enterprise approval identity. No authorized customer dataset, independent evaluator/signer, compatible separately administered observer host or physical disconnected site is available in this session. Local CapEff is zero; required audit/BPF tools and capabilities are absent (INDEPENDENT_OBSERVATION.md). Generating more synthetic prompts here would not supply independence. Continue those gates when the actual testbed, ownership/licensing contract and data/identity authorization are supplied.

Optional engineering extensions remain incremental recovery, aggregate cgroup controls, broader ingestion, merged-export numerical parity and additional inference formats. They are outside the qualified vertical slice and must retain its approval and rollback boundaries. The current experimental workflow and reproducible evidence are ready for PR review, not production rollout.
