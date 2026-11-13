# Soup source qualification — P0-052

Audit date: 13 November 2026. Scope: the first CPU LoRA integration, not an exhaustive security audit of the upstream project.

## Immutable sources

- AIRON main: 04a84e64fc2be36fe03fc73006c9a42285617a02.
- Soup: af2f5d5000f7baec6386a72a6d16e82383eb5303, package soup-cli 0.77.2, Python >=3.11,<3.14.
- AIP main: 872dbf375838cff464eb019488c63d948015e9b8.
- AIP P0-048 branch tip inspected at reference/README level only: 61dd73013d02ea7869de104d953f330098df1c32.
- Proposed model: HuggingFaceTB/SmolLM2-135M-Instruct at 12fd25f77366fa6b3b4b768ec3050bf629380bac. Model card and HF API declare Apache-2.0. This is a pretrained 135M causal model, not a random toy fixture.

Sources were cloned into an isolated workspace; git status, branch lists, recent commits and dependency manifests were inspected. AIRON contained a React/Vite hosted demonstration and a separate Python/Ollama local gateway, with no pre-existing model adaptation service. The only remote AIRON branches observed were main and research/p0-053-opensource-capability-library. The P0-052 branch was created from the inspected main without modifying main.

## Inspected code and reuse decisions

Paths below are in Soup at the pinned revision. Source inspection is not an executed test.

| Capability | Inspected implementation | AIRON decision |
|---|---|---|
| Package and dependencies | pyproject.toml, AGENTS.md, README.md | Pin a separately installed package. Core CLI is light; training extras are separate. Capture resolved inventory per preparation. |
| SFT / LoRA / QLoRA | trainer/sft.py, config/schema.py, tests/test_smoke_train.py | Invoke SFTTrainerWrapper.setup/train, report_to=none, trust_remote_code=False. CPU float32 LoRA and quantization=none only in first slice. |
| Memory-efficient training | trainer/sft.py setup/checkpointing branches | Preserve upstream implementation. Two threads, batch 2, context 256; no invented throughput claim. |
| Layer streaming | utils/layer_stream.py planner and architecture allowlist; trainer/stream_setup.py setup sections | CUDA memory/transfer feature with RAM/disk tiers. Not enabled or qualified on CPU. No duplication or marketing claim. Runtime/backward parity suite not reproduced. |
| Model loading | trainer/sft.py and utils/trust_remote calls; commands/export.py helper | Only local data-only artifacts with safetensors. AIRON denies custom-code metadata, unsafe extensions and arbitrary model IDs at runtime. |
| Dataset loading | data/loader.py and data/formats imports | AIRON authorizes/validates/fixes splits; Soup performs its native ChatML data loading/tokenization inside the isolated worker. |
| Checkpointing / recovery | SFT train signature, final save path, upstream resume tests listed | Use final inference-only adapter. Do not import optimizer pickle state or silently resume interrupted jobs; restart as a fresh experiment. |
| Evaluation | commands/eval.py surfaces, README/docs command descriptions | First slice uses AIRON's frozen closed-choice likelihood test and regression gate. This is deliberately a narrow reproducible measure, not a replacement for Soup's broader benchmark suite. |
| Merge / export | commands/export.py _merge_adapter, converter/dependency-install paths | Invoke pinned merge helper in sandbox for HF safetensors. Private-helper contract requires CI. GGUF/llama.cpp external conversion and automatic Ollama deployment remain disabled. |
| Model registry / provenance | SFT output/provenance calls, README registry surfaces | AIRON maintains signed artifact manifests and transactional activation state. Upstream registry/ship commands have no production authority. |
| Feedback loop | commands/loop.py, utils/loop_stages.py first-stage implementation | Upstream has explicit pre-wired harvest/train/gate/deploy. Do not start it: automatic harvesting and deployment conflict with explicit dataset authorization and human approval requirements. |
| Air-gap bundle | utils/airgap_bundle.py plan/build/inspect implementations | Reuse assembler for a preparation bundle. Its inspect function reads manifest metadata; it does not verify every member or establish network isolation. AIRON verifies member bytes separately. |
| Existing tests | tests/test_smoke_train.py read; repo test filenames inventoried | Upstream tests were not claimed passed. AIRON fixtures, real-worker probes and real-training acceptance are separate evidence classes. |

No upstream source modifications are made. AIRON calls a pinned public wrapper and one pinned private export helper; this API dependency is intentionally documented. Do not upgrade Soup silently.

## Licence and redistribution

The checked-out LICENSE is Apache-2.0 and NOTICE identifies Makazhan Alpamys and the Soup contributors. Exact copies are retained under third_party/. Keep both with redistributed Soup wheels/source and preserve attribution. If Soup is modified later, identify changed files and retain notices. The AIRON control plane remains governed by the repository's MIT licence; it does not rebrand upstream Soup as proprietary AIRON code.

dependencies.declared.json is an inventory of source-declared core and training ranges, not a complete resolved SBOM. requirements-training.txt narrows the selected CPU stack. Provisioning emits installed package versions, declared licence metadata, licence-file names and pip freeze. A clean-machine wheelhouse, hash-locked resolution and transitive redistribution review are still required before distributing an offline runtime.

The selected model's weight licence is checked independently from Soup's software licence; retain its model card and review its conditions. Synthetic records have their own CC0 declaration. No private conversations, customer data or externally scraped datasets are included.

AIP main's README declares proprietary ownership by K. NAGA SRI GANESH. Its raw Ed25519 signing functions and protocol trust distinction were inspected. No AIP code is copied or added as a production dependency. Ownership/licensing and cross-language contract execution remain open.

## Known boundaries

- No GPU, QLoRA, layer-streaming, adapter incremental-resume, GGUF, or model-family generality claim.
- No claim of exhaustive upstream vulnerability or third-party licence review.
- Prompt-pattern quarantine and exact duplicate checks do not solve semantic poisoning or prove dataset cleanliness.
- LoRA on one synthetic task does not demonstrate general continual learning or absence of catastrophic forgetting.
- Existing Ollama knowledge access controls remain in the original demonstration; this experimental adaptation runtime is separate.
- Frozen evaluation scores measure closed-choice answer likelihood. They do not establish unconstrained answer quality.
- Application signatures are not kernel observation, trusted hardware attestation or proof that the signer told the truth.

## Source links

- https://github.com/MakazhanAlpamys/Soup/tree/af2f5d5000f7baec6386a72a6d16e82383eb5303
- https://github.com/richardrich999888-rgb/AIP-agent-identity-protocol-/tree/872dbf375838cff464eb019488c63d948015e9b8
- https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct/tree/12fd25f77366fa6b3b4b768ec3050bf629380bac
