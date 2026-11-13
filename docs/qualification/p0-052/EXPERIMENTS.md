# Recorded adaptation experiments

All runs below used the same pinned SmolLM2-135M-Instruct base and Soup source. Routing scores are closed-choice likelihood classification on six fixed prompts, not general language-model accuracy. The factual regression suite has six prompts and a 3/6 baseline. The original zero-baseline arithmetic suite was replaced explicitly during development. Hyperparameter trials reuse development evaluation material; no untouched scientific holdout or statistical generalization claim is made.

| Source / Actions run | Training change | Observed result | Promotion outcome |
|---|---|---|---|
| 28daa9b / 43340130645 | 18 routing records; precision not fully measured | 27 steps, 120 tensors changed; routing 1/6→3/6; factual 3/6→5/6 | Historical scoped lifecycle passed; do not use its timing as a verified FP32 benchmark |
| 3444026 / 43343169905 | First fresh offline wheel install | 63-wheel isolated install passed; duplicate import mounts caused training serialization failure | No offline acceptance |
| e71de2e / 43344029528 | Package mount narrowed | Worker exited 137 near step 25; cause not diagnosed | Rejected/incomplete |
| 34d150c / 43345441994 | Added worker diagnostic stack traces | Slow backward computation; stopped by 300-second limit | Rejected/incomplete |
| 53976dc / 43346110760 | Explicitly convert/check all training tensors FP32 | 27 steps; 42.934 s training/save; 1,415,008 KiB peak RSS; routing 3/6 and factual 5/6 | Historical scoped lifecycle passed; document answers abstained |
| c1f9ad7 / 43347812566 | Fresh offline wheel/runtime fixes | Complete isolated install and lifecycle; 35.596 s training/save; 1,380,696 KiB peak RSS; zero unexpected network violations | Historical offline scope passed; browser harness failed CSP check; document answers abstained |
| 921f111 / 43349342064 | Add 12 disjoint source-copy training records; LR .001; 45 steps | Real full-source answer; routing 3/6; factual 0/6; 97.230 s training/save | Current policy rejected factual regression before deployment |
| 1669945 / 43350087374 | Repeat same candidate; independent fault harness | Quality rejection repeated; actual cancellation and malformed model rejection passed | No promotion |
| fe2046d / 43350750912 | Same 30 records, LR .0003; 45 steps | Routing 2/6; factual 6/6; candidate source-copy failed; 77.827 s training/save; 1,711,396 KiB peak RSS | Current policy rejected lost document behavior before deployment |
| b4b9505 / 43354134754 | Same 30 records, LR .0001 | Offline 45 steps; 95.782 s; routing 2/6; factual 3/6; full-source answer; isolated workflow/browser passed | Lifecycle v2 passed; stricter fault-harness diagnostic failed |
| a297332 / 43356140596 | Failed-job diagnostics fixed; actual adapter artifacts retained | Entire workflow passed; offline 99.931 s, 1,726,268 KiB; 120 changed tensors; real faults and signed browser download passed | v2 passed; 2/6 routing insufficient under later v3 |
| 0f46ef0 / 43358210167 | 102 train records; aligned copy instruction; LR .0003; v3 minimum 50% routing | Reached 92/153 steps; SIGSEGV during asynchronous 120-second diagnostic dump | No registration or activation; quality not evaluated |
| 7b964cd / 43359489727 | Remove periodic diagnostic stack walk only | Reached 149/153 steps; stopped at 300 seconds by external wall limit; no recurrence of diagnostic SIGSEGV | No candidate or activation; next trial changes training-only time budget |

| 14ef531 / 43360855201 | 480-second training budget, unchanged q/v rank-8 LoRA | 153 steps; 139.470 s; 1,804,324 KiB RSS; routing 1/6; factual 4/6; full-source answer | v3 rejected routing; no activation |

| ddde09b / 43361491412 | Repeat 102-row q/v-only configuration on AMD EPYC 9V45 | 153 steps; 166.715 s; routing 1/6; factual 4/6; full-source answer | Routing rejection reproduced |
| 060ff1d / 43362170915 | Seven attention/MLP LoRA targets; all other learning inputs unchanged | 153 steps, 420 tensors; 222.741 s; 2,020,080 KiB; routing 3/6; factual 0/6; full-source answer | v3 rejected catastrophic forgetting |

The twelve copy-training records exclude the approved document corpus and frozen question. Both evaluation data and acceptance thresholds remain unchanged across the retention trials. Candidate failures are retained with signed events, model/dataset/config hashes and real scores in evidence/. No rejected candidate was activated. An automated synthetic-test reviewer is expressly labelled and does not establish independent human authorization.

Hardware varies across GitHub runners; compare each report's CPU, memory and wall-clock measurements. All qualified precision measurements above use two torch CPU threads; no GPU was used. Historical source snapshots and failures remain in Git history.
