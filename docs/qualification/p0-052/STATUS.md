# P0-052 — measured offline adaptation and current quality gate

Updated 13 November 2026. Draft [PR #2](https://github.com/richardrich999888-rgb/AIRON-native-/pull/2); main is unchanged. This is an experimental qualification, not a production release.

## Completed vertical slice

Source a29733297c0d022b700ffa260750ed40a4d2e48a completed [Actions run 43356140596](https://github.com/richardrich999888-rgb/AIRON-native-/actions/runs/43356140596) successfully, including both jobs and every real CPU step. It demonstrated baseline inference, approved private-document access, genuine Soup training, evaluation, scripted test approval, experimental activation, adapted inference, export, rollback, a fresh hash-locked offline installation, complete namespace isolation and syscall classification, browser evidence download, real cancellation and corrupt-model rejection.

Its task score remains weak: 2/6 equals the constant-label reference for the balanced three-class routing set. That run qualifies the implemented lifecycle and isolation, not useful enterprise routing quality. The current policy v3 now requires at least 50% routing accuracy as well as strict improvement, factual preservation and the full-source document answer. The 102-record trial at 14ef5317954d3ed38df87ea3bd5d5d4f0bc123eb completed 153 genuine steps but routing remained 1/6; factual 4/6 and the full-source answer passed. The current v3 gate correctly rejected deployment. A controlled follow-up broadens rank-8 LoRA from q/v to seven attention/MLP projections with all data, learning parameters and evaluation unchanged. No pass is inferred.

| Observation at a297332 | Actual offline result |
|---|---|
| Base / adapter | SmolLM2-135M-Instruct; genuine rank-8 CPU LoRA |
| Training | 45 optimizer steps; 120 changed tensors |
| Precision / threads | All floating training parameters FP32; 2 observed torch CPU threads |
| Training plus save | 99.931 seconds |
| Worker wall time | 114.532 seconds |
| Peak worker RSS | 1,726,268 KiB |
| Hardware | AMD EPYC 7763 runner; 4 logical CPUs; 16,372,448 KiB host RAM |
| GPU | Not used |
| Routing | 1/6 → 2/6; insufficient under current v3 minimum |
| Factual regression | 3/6 → 3/6 |
| Approved document | Baseline and adapted answer reproduced the full approved source |
| Restricted / unsupported documents | Denied / abstained before model execution |
| Adapter weights | 1,858,776 bytes; safetensors |
| Deployment / rollback | Experimental version 2 activated; version 3 restored original; predictions restored |
| Offline install | 63 exact wheels installed into an empty environment with networking unavailable |
| Network audit | Eleven controller/worker probe windows; no unexpected IP/DNS activity |
| Evidence | 20 signed events; APPLICATION_SIGNED; independent execution CANNOT_PROVE |
| Browser | Actual workspace, reviewer training denial, mobile width, evidence download and signatures passed |
| Real faults | Optimizer-progress cancellation stopped process (-9); malformed safetensors parser rejected model |
| Delivery | Actual primary/offline adapter files retained in the Actions evidence artifact |

Full original reports are in evidence/. The base, tokenizer, dataset, configuration, candidate, evaluation and approval digests remain attached to actual signed events. Source-reviewed report hashes/keys/heads are in EVIDENCE_INDEX.json; these are not independent enterprise identities.

## Qualification milestones

| Gate | Status | Scope |
|---|---|---|
| M1 source qualification | Scoped review completed | Immutable Soup/AIRON/AIP/model references, source licences/notices and actual wheel inventory; full OS/native redistribution review remains open |
| M2 working adapter | Passed on recorded source | Actual local Soup data loading, training and merge helper |
| M3 genuine training | Passed on recorded source | Real changed parameters, saved/reloaded adapter; separate downloaded artifact inspection |
| M4 model lifecycle | Passed under v2; v3 quality trial pending | Explicit role/approval gate and rollback work; current stricter task-quality requirement needs a new passing candidate |
| M5 offline qualification | Passed for recorded v2 workflow; new trial pending | Fresh installation and complete namespace-isolated workflow; no physical/customer-site accreditation |
| M6 assurance | Passed at application level | Signed chain, reviewed anchors, separately inspected syscall traces; AIP raw-byte interoperability passed separately; no production AIP or Sniffer Dog integration |
| M7 demonstration | UI and reproducibility passed; stronger quality pending | Guided local console and downloadable evidence; weak routing score must remain visible |

The pre-expansion suite passed 78 tests plus the 15 existing gateway tests and eight existing website cases/build. Current source passed 85 local/controller/adversarial/retained-evidence checks, and its CI contracts job passed. Counts overlap across runs; they are not independent test totals.

## Remaining work and limits

The immediate engineering task is a v3-qualified candidate from the unchanged-evaluation, 102-record corpus. The q/v-only adapter failed routing despite genuine training; the next trial broadens the fixed LoRA target coverage. Evaluation answers are not added to training.

Enterprise qualification still needs independently prepared larger benchmarks, authorised real-data ingestion, independent approver identity/key custody and external event anchoring, a tested/licensed AIP bridge and independent execution observer, customer hardware/physical isolation, cgroup aggregate limits and multi-user isolation, broader forgetting/poisoning/drift evaluation, incremental adapter learning, and export parity/GGUF/llama.cpp/Ollama deployment. No automatic harvesting, model self-modification or promotion exists.

Read REPRODUCE.md for exact installation/execution procedures, EXPERIMENTS.md for failed and superseded trials, ADVERSARIAL_MATRIX.md for test scope, and LEDGER.md for the implementation history.
