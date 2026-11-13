# P0-056 integration matrix

Tested source: AIRON initial lifecycle `16c6bd745edacaa4ad7b435cc52de935e1d1802f`; final qualification target `0f4cd7e20f4c19577b5a73b9d1dacdc221f3085a`; native interface `f1ba9fc2072dac1431543fd4961baaa2762b8ea9`. See `BENCHMARKS.json` and `evidence/local/PROVENANCE.json` for per-run revisions. Local hardware: Linux 6.18.57, AMD EPYC 9V74, 9 visible CPUs, 10,206,472 KiB RAM, no GPU; inference comparisons restricted to CPUs 0–1. Hosted hardware: Ubuntu 22.04, Linux 6.8 Azure, 4 visible CPUs, 16,371,436 KiB RAM; the corrected two-CPU run enforced an 8 GiB cgroup limit but training timed out; separate four-CPU training and two-CPU serving qualification is in progress. No claim of independent administration.

| Component | Actual integration | Qualification boundary |
|---|---|---|
| AIRON Core | One local API, role-bound principal, bounded worker admission, signed state, deterministic learning rules | Local OS administrator remains trusted; no enterprise IdP or remote multiuser deployment |
| llama.cpp | Pinned real `llama-completion`, local GGUF hash check, bounded context, CPU threads, deadline and memory sampler | 135M, 0.5B and 1.5B inference measured; TTFT unavailable; no resident-server throughput claim |
| Soup / Transformers / PEFT / TRL | Preserved P0-052 controller and exact qualified Soup source; real CPU LoRA, evaluation, approval and rollback | 135M synthetic routing experiment; six original test examples are not generalization evidence |
| Docling | Real Markdown conversion retaining structured export and original source hashes | PDF, OCR, image/table extraction and associated local model provisioning remain unqualified |
| SQLite | Original native tenant/clearance-scoped FTS5; AIRON document versions, signed state and memory | No vector store introduced; cross-store crash can cause fail-closed recovery work |
| SYNTRIASS procedural runtime | Original Rust compiler, expert-suite signatures, scoped reviewer grants, activation, supersession, rollback, zero-model execution | Original source and licence remain in AIP; fixture procedures are expert-authored, not acquired autonomously |
| Memory | Distinct signed record kinds for documents, procedures, task outcomes, learning requests; preserved adapter/evaluation/deployment registry | Outcomes explicitly are not trusted facts; general verified-fact CRUD is not yet exposed |
| Learning controller | Six tested deterministic decision routes; recommendations cannot approve or execute | Reviewer attestation is required; no learned controller |
| LM Evaluation Harness | Pinned source installed in separate qualification environment; actual local generation over frozen 30-case task | Custom synthetic task, not MMLU or a standard public benchmark score; unsupported log-likelihood methods fail explicitly |
| MLflow | Local SQLite plus local artifacts, telemetry disabled; verifies AIRON signatures before projecting results and checks artifact readback hash | Optional projection only; cannot approve deployment or replace signed evidence |
| Cosign | Pinned source built; local key signing and verification passed offline; tamper/wrong-key rejection tested | Explicit empty service configuration, no transparency log or timestamp; optional distribution integrity only; binary-scan advisory review remains OPEN |
| AIP assurance | Versioned native boundary reuses existing AIP crypto through SYNTRIASS; consequential execution remains refused | AIP EvidencePackets, independent agent identity/delegation, Sniffer Dog observer and independently held approval keys are NOT integrated |
| Local interface | Real API-backed documents, roles, models, capabilities, lifecycle actions and evidence; route attribution displayed | Hosted static website remains a separate scaffold and proves no offline service availability |

Source commits, licences, submodules and manifests: `sources.lock.json`. Candidate research pins may differ from qualified wheel versions; the tested wheel lock is authoritative for the installed Python environment. The newer research Soup pin is intentionally not substituted for P0-052's demonstrated pin.
