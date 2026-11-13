# P0-052 — actual offline adaptation and controlled model changes

Updated 13 November 2026. Draft [PR #2](https://github.com/richardrich999888-rgb/AIRON-native-/pull/2); inspected main 04a84e64fc2be36fe03fc73006c9a42285617a02 is unchanged. This is an experimental CPU qualification, not a production release.

## Current result

Runtime source **6077c9a104c42e024ae343aafdc2cc4a91181663** passed every stage of [Actions run 43373086529](https://github.com/richardrich999888-rgb/AIRON-native-/actions/runs/43373086529). Genuine Soup training completed twice. The second experiment installed 63 exact wheels into a fresh environment without networking, then repeated baseline inference, authorized knowledge access, training, evaluation, export, explicit synthetic review, activation, adapted inference and rollback with the complete controller and workers isolated. Actual browser checks and real cancellation/corrupt-model tests also passed.

Routing improved from 1/6 to 5/6, factual retention from 3/6 to 6/6, and both models reproduced the complete approved source for the document question. Denied and unsupported queries stopped before model execution. Evaluation questions and factual evaluation answer strings were excluded from rehearsal. These are small development-set results, not general enterprise accuracy or an untouched scientific holdout.

The final evidence/documentation commit retains these observations without changing the tested runtime, fixtures, tests or workflows. Actions tested the runtime revision above (PR merge checkout f9ca8ba54070182d43760a235fef7cdb03aca315); it did not rerun training for the subsequent documentation-only commit. Historical failed and rejected experiments remain in EXPERIMENTS.md and evidence/.

## Latest measured offline workflow

| Observation | Actual result at 6077c9a |
|---|---|
| Base model | Pinned pretrained SmolLM2-135M-Instruct; Apache-2.0 model terms retained |
| Training input | 102 approved primary records plus 24 disjoint authorized rehearsal records, mixed by native Soup |
| Adaptation | Rank-8 LoRA on seven attention/MLP projections; 3 epochs, LR .0003, seed 52 |
| Real training | 189 optimizer steps; 420 changed tensors; floating training parameters checked FP32 |
| Training plus save | 437.544 seconds; worker wall time 452.429 seconds |
| Peak worker RSS | 2,004,656 KiB; per-process measurement, not host total or aggregate peak |
| Hardware | AMD EPYC 7763 runner; 4 logical CPUs, 2 torch threads, 16,372,448 KiB host RAM; Python 3.12.16 |
| GPU | Not used |
| Routing | 1/6 → 5/6; closed-choice likelihood over the fixed answer set |
| Factual retention | 3/6 → 6/6 on the unchanged six questions |
| Approved document | Baseline and candidate reproduced the full approved source; extra framing is discarded |
| Routing mean evaluation latency | Baseline 3.181 s; candidate 4.463 s per prompt, including all choice scoring |
| Factual mean evaluation latency | Baseline 2.577 s; candidate 3.660 s per prompt |
| Document generation latency | Baseline 4.035 s; candidate 3.282 s |
| Base / adapter weights | 269,060,552 / 9,823,216 bytes |
| Adapter / HF export with tokenizer | 13,353,221 / 272,585,007 bytes; merged-export numerical parity not qualified |
| Deployment and rollback | Experimental version 2 activated; version 3 restored the baseline and its predictions |
| Offline dependencies | 63 exact wheels installed with --no-index, --no-cache-dir and --require-hashes in an isolated namespace |
| Network observations | Eleven probe windows; all 163 downloaded raw trace files rehashed and reclassified; zero unexpected IP/DNS activity |
| Real interruption | Cancel after optimizer step 1/756; process stopped with -9, registration denied, baseline inference then succeeded over 12 rows |
| Actual malformed model | Safetensors parser rejected the malformed header; no candidate or activation |
| Adapter inspection | Primary/offline weight hashes identical; 420 FP32 tensors and 210 nonzero LoRA-B tensors |
| Evidence | 20 signed lifecycle records; source-reviewed key/head; APPLICATION_SIGNED / independent execution CANNOT_PROVE |
| Console | Actual workspace/scores, reviewer training denial, desktop/mobile checks and raw signed download passed |

Latency excludes cold model loading and HTTP overhead. Training/save and worker wall time are separate measurements. CPU runners differ across trials: scores reproduced across observed hosts, but weight bytes are not claimed identical across hardware. Within this run, primary/offline adapter SHA-256 is 4875ff6d50e45f51cab5b5148790518c2234dd3977466b825ee06a2b6d3a53ec.

## Qualification milestones

| Milestone | Observed status | Scope / open gate |
|---|---|---|
| M1 source qualification | Scoped review completed | Pinned source/model terms, licences/notices and actual Python wheel inventory; full OS/native redistribution review open |
| M2 working adapter | Passed | Actual Soup data loading, replay mixing, SFT and merge helper; separately packaged upstream |
| M3 training qualification | Passed | Genuine changed adapter, saved/reloaded and separately inspected artifact |
| M4 model lifecycle | Passed v3 | Current quality gate, explicit role/review, activation, adapted inference and rollback; synthetic test reviewer |
| M5 offline qualification | Passed on tested runner | Fresh dependency installation and entire workflow without external networking; no physical/customer-site accreditation |
| M6 assurance qualification | Passed at application level | Signature chains and trace/artifact checks; actual AIP raw-byte compatibility; independent-execution gate OPEN |
| M7 guided demonstration | Implemented and rehearsed | Local SYNTRIASS console, ten-scene guide, browser/fault checks and reproduction commands |

At the tested runtime revision, CI passed 111 adaptation checks (80 controller/adversarial/transport/harness checks and 31 retained-report checks), 15 original gateway tests, eight website cases and the build. The documentation commit adds ten retained reports; the unchanged suite passed 121 checks locally, including all 41 retained reports. Counts overlap across runs and must not be summed as independent tests. Separate [AIP contract run 43373086477](https://github.com/richardrich999888-rgb/AIRON-native-/actions/runs/43373086477) also passed; it is a byte-signature contract, not a full identity/observation integration.

## Delivered evidence and remaining gates

Original signed reports, failures and source-reviewed anchors are retained in evidence/ and EVIDENCE_INDEX.json. BENCHMARKS.json contains machine-readable measurements. The actual adapters, raw traces and packaged notices are in [artifact 14015340252](https://github.com/richardrich999888-rgb/AIRON-native-/actions/runs/43373086529/artifacts/14015340252): ZIP SHA-256 d0998f7b453bf1e647159f50578b89bbdb45800b37205bc1aba4c569795da975, 20,020,945 bytes, recorded expiry 11 February 2027. Retain an approved copy before expiry or reproduce. Separate reinspection verified adapter manifests, signatures, all traces, 139 notices and the 63-wheel hash lock. It does not establish independent signer custody.

A larger independently prepared benchmark, authorized real-data ingestion and poisoning/drift review, independent approver identity/key custody/external anchors, a licensed full AIP/observer contract, separately administered customer hardware and physical isolation, aggregate cgroup limits/multi-user isolation, incremental adapter recovery, merged-export numerical parity and GGUF/llama.cpp/Ollama deployment remain open. INDEPENDENT_OBSERVATION.md records the actual source/capability investigation; no Sniffer Dog execution is claimed.

The original Ollama and hosted demos are preserved. Activation affects only the new experimental HF/PEFT runtime. No conversation harvesting, automatic promotion, uncontrolled self-modification or production readiness is claimed. The feasible experimental slice is delivered for review; broader enterprise qualification is incomplete.

Read REPRODUCE.md, COMMANDS.md, CHANGED_FILES.md, DEMO_SCRIPT.md, ADVERSARIAL_MATRIX.md and LEDGER.md for setup, executed commands, changed files, demonstration, negative-test scope and outstanding work.
