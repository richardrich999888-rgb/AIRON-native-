# P0-052 — measured experimental adaptation

Updated 13 November 2026. Draft PR #2; main remains unchanged. This is not a production release or a completed enterprise qualification.

## Last completed real CPU experiment

Source: 53976dce1fbffe00b28ca9c2c7232f143510a36e.
[Actions run 43346110760](https://github.com/richardrich999888-rgb/AIRON-native-/actions/runs/43346110760).
Machine-readable report: evidence/cpu-53976dc.json.

| Observation | Measured result |
|---|---|
| Real Soup LoRA | 27 steps; 120 changed trainable tensors |
| Precision | Loaded BF16/FP32; explicitly converted and checked as FP32 |
| Training plus adapter save | 42.934 seconds |
| Worker wall time | 56.896 seconds |
| Peak training-worker RSS | 1,415,008 KiB |
| CPU | AMD EPYC 7763; runner exposes 4 logical CPUs; 2 observed torch threads |
| Runner RAM | 16,372,448 KiB total; not a 2-CPU/2-GB machine qualification |
| GPU | Not used |
| Routing, six fixed questions | Baseline 1/6; candidate 3/6 |
| Regression, six fixed questions | Baseline 3/6; candidate 5/6 |
| Knowledge controls | Authorised query reached local model; restricted/unknown requests stopped before model |
| Knowledge answer quality | Baseline and candidate both ABSTAINED under exact-source validation |
| Export, approval, activation, rollback | Passed in the experimental HF/PEFT runtime |
| Evidence | Application-signed chain; independent execution CANNOT_PROVE |

Routing/regression scores use closed-choice mean log likelihood over fixed alternatives. They are not unconstrained answer accuracy, general intelligence or statistically established improvement on enterprise data. The training set has 18 synthetic routing records. The regression set was revised after an initial zero-baseline arithmetic suite; this is a development demonstration, not an untouched independent scientific benchmark.

## Qualification gates

| Gate | Status | Evidence or open condition |
|---|---|---|
| M1 source qualification | SCOPED REVIEW DONE | Soup/AIRON/AIP pins, LICENSE/NOTICE and dependency inventories; complete runtime/native redistribution review remains open |
| M2 genuine Soup operations | PASS, scoped | Real isolated Soup data loading, SFT and merge helper |
| M3 real training | PASS, scoped | cpu-53976dc.json; changed tensors and saved/reloaded adapter |
| M4 model lifecycle | PASS, scoped | Frozen evaluation, scripted synthetic-test reviewer, activation, adapted inference and restored baseline |
| M5 complete offline workflow | INCOMPLETE | 63-wheel fresh offline installation passed at 3444026; complete installed workflow previously failed. Latest wheel-notice parser fix and full rerun pending |
| M6 assurance | APPLICATION LEVEL | Real chain verification; retained earlier real chain also verified against reviewed public key/head. AIP and Sniffer Dog not integrated |
| M7 guided demonstration | PARTIAL | Local console implemented; browser rehearsal pending; document generation currently abstains |

The current code has additional fixes under test. Consult the exact run/commit rather than treating the presence of a file or a queued check as a pass.

## Remaining enterprise gaps

Independent approver identity, key custody and external event anchoring; AIP ownership/licensing and tested bridge; independent execution observation; customer hardware and physical air-gap validation; cgroup aggregate limits and multi-user isolation; broad model quality/forgetting/poisoning evaluation; arbitrary approved document ingestion; GPU/QLoRA/layer streaming; incremental adapter learning; GGUF/llama.cpp and Ollama deployment. No automatic conversation harvesting or autonomous promotion exists.
