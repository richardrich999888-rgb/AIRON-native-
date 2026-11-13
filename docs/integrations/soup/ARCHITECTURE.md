# AIRON local adaptation architecture

The existing hosted React demonstration and Python/Ollama gateway remain separate. The new Linux-only local control plane owns a private workspace, immutable artifact manifests, signed lifecycle records and a SQLite transaction boundary. It exposes a small loopback API with two server-bound demonstration roles.

A fixed worker imports Soup in a separate user/network/PID namespace. Its mounts contain only the Python environment, AIRON worker code, the approved base, the approved dataset, an optional registered adapter and the current job's output directory. The controller database, signing key, other job outputs, real home directory, inherited credentials and host Ollama service are not mounted. Network isolation failure causes the operation to fail; there is no unsandboxed fallback.

## API contract

POST /api/operation with Authorization: Bearer TOKEN and JSON {"operation": "...", "params": {...}}. Maximum body 1 MiB. Host/Origin checks and a fixed operation allowlist precede dispatch. Actor and role come from the session, never from the JSON body.

| Operation | Parameters | Enforcement / upstream mapping |
|---|---|---|
| prepare_dataset | rows, authorization | Synthetic CC0 only, explicit training authorization, fixed schema and splits; then canonical ChatML JSONL |
| validate_dataset | dataset_id | Rehash and revalidate; Soup native loading also runs in worker |
| create_training_job | base_id, dataset_id, config | Config only epochs/lr/rank/seed, numeric bounds; no arbitrary commands/plugins/paths |
| start_training | job_id | One training worker; Soup SFTTrainerWrapper setup/train |
| get_training_status | job_id | Persisted CREATED/RUNNING/SUCCEEDED/FAILED/CANCELLED/INTERRUPTED |
| cancel_training | job_id | Revoke pending job or kill supervised process group |
| register_checkpoint | job_id | Successful training only; fixed job output, rehash, data-only files, LoRA/base binding |
| evaluate_candidate | candidate_id | Frozen baseline and candidate test/regression splits; finite metrics, exact row counts |
| export_model | candidate_id | Isolated Soup _merge_adapter; HF safetensors only |
| request_deployment | candidate_id, evaluation_id | Passing matching evaluation; bind its digest and current deployment version |
| approve_deployment | approval_id, decision | Reviewer role; requester cannot approve own request |
| activate_model | approval_id | Reverify artifacts/report; consume version-bound approval and swap experimental active pointer atomically |
| rollback_model | none | Verify previous artifacts then atomically restore pointer |
| infer | dataset_id | Approved frozen prompts, local base plus active adapter; no cloud fallback |
| status / evidence | none | Read signed state / export signed chain |

Model import is an administrative Python provisioning operation, intentionally absent from HTTP. Example row: {"prompt":"Route this invoice", "answer":"K7", "split":"train"}. Dataset authorization must exactly equal {"synthetic":true,"approved_for_training":true,"license":"CC0-1.0"}. Training config example: {"epochs":3,"lr":0.001,"rank":8,"seed":52}.

## State and crash behavior

SQLite WAL, FULL synchronous commits and signed object envelopes protect ordinary corruption and unauthorized edits without the private key. A process lock prevents concurrent controller ownership. On restart a RUNNING job becomes INTERRUPTED. It cannot be registered. No automatic unsafe optimizer deserialization or checkpoint recovery occurs.

Activation changes the experimental runtime's model pointer. It does not mutate weights, replace the original model or change Ollama. Inference verifies artifacts and loads the active adapter from disk. Activation is transactionally atomic; if subsequent inference fails, output is withheld and the reviewer may roll back. The acceptance driver restores the prior model even if adapted inference raises.

## Trust boundary

The host OS administrator and same OS account are trusted. Filesystem checks are not a defense against an administrator racing filesystem operations, altering the Python environment, replacing the signing key, rolling back the entire database or generating false records. Tokens are bearer credentials for a single-workstation demonstration, not enterprise identity, two independent human identities or multi-tenant isolation.

Jobs have per-process address-space (6 GiB), CPU (600 seconds), file (1 GiB/file), descriptor and wall-clock limits. These are not cgroup aggregate memory/disk quotas. Production deployment requires a distinct service user, signed supply-chain artifacts, independent approver identity, key custody, external event anchoring and measured target-hardware resource controls.

## Assurance interface

AIRON exports an airon-model-change/v1 payload inside an Ed25519 envelope. Signed bytes are ASCII canonical JSON prefixed with AIRON-MODEL-LIFECYCLE-v1 followed by a zero byte. The envelope contains SHA-256(payload) and a base64 signature. A verifier must receive the trusted public key out of band. A previous-envelope hash and sequence bind the chain; tail truncation requires an externally trusted head.

The AIP bridge contract is a payload sink/signature-provider boundary for future integration, not an implemented AIP EvidencePacket. AIP's inspected raw sign_ed25519_raw/verify_ed25519_raw functions could sign the same bytes, subject to licence/ownership decision and actual cross-language tests. AIRON uses cryptography Ed25519 independently today. Never label its records AUTHORITY_BOUND, COUNTERPARTY_SIGNED or kernel-observed.

Training identity, authorizing actor, dataset/base/config digests, adapter digest, evaluation report, approval, deployment version and rollback appear across linked signed events. No secret material is exported. Sniffer Dog is not integrated. strace in acceptance CI provides a separate syscall trace for that runner; a trace is not cryptographically independent attestation.

## Research decisions

Incremental adapter training, merge parity beyond the selected helper, replay buffers, drift alarms and automatic monitoring remain research items. The current controller accepts only fresh LoRA jobs. Each cycle requires new authorized data, frozen evaluation and separate approval. No user-conversation harvesting, model-written control-plane changes or autonomous promotion exists.

Bundle preparation is a separate trusted operation: bundle.py reuses Soup assembly, signs the archive digest, verifies every regular member against the manifest and rejects undeclared bytes. It never extracts an archive or claims dependency closure from a filename alone.

The regression gate also requires a nonzero baseline regression score. A suite on which the baseline gets every case wrong cannot qualify preservation. The initial four arithmetic prompts produced 0/4; they were replaced, before acceptance, with a fixed six-question factual suite. Historical failure evidence is retained. The routing training and test prompts were not changed.
