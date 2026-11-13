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
| b4b9505 / 43354134754 | Same 30 records, LR .0001 | Pending at entry creation; read STATUS.md and exact run | No advance pass claim |

The twelve copy-training records exclude the approved document corpus and frozen question. Both evaluation data and acceptance thresholds remain unchanged across the retention trials. Candidate failures are retained with signed events, model/dataset/config hashes and real scores in evidence/. No rejected candidate was activated. An automated synthetic-test reviewer is expressly labelled and does not establish independent human authorization.

Hardware varies across GitHub runners; compare each report's CPU, memory and wall-clock measurements. All qualified precision measurements above use two torch CPU threads; no GPU was used. Historical source snapshots and failures remain in Git history.
