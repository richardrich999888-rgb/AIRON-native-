# AIRON Native open-source capability source inventory

P0-053 — SYNTRIASS Labs Pvt. Ltd.

Branch: `research/p0-053-opensource-capability-library`. Verified base: `main` at `04a84e64fc2be36fe03fc73006c9a42285617a02`.

This branch preserves source for future research. All 19 requested repositories were fetched and pinned as Git submodules. No AIRON runtime integration, training, evaluation, build or deployment was performed.

The exact revisions, declared licences, licence/notice file hashes, clone results, intended capabilities and proposed future review priorities are recorded in [repositories.lock.json](repositories.lock.json). Restoration evidence is in [CLONE_STATUS.md](CLONE_STATUS.md).

## Inventory

Priorities describe future review order only: **P1** first candidates, **P2** secondary/alternative candidates, **P3** platform-specific candidates. Acquisition priority was P0 for all 19.

| Project / source | Local directory | Upstream default branch | Declared licence | Priority | Clone |
|---|---|---|---|---|---|
| [Soup](https://github.com/MakazhanAlpamys/Soup) | `third_party/training/soup` | `main` | Apache-2.0 | P1 | SUCCESS |
| [Unsloth](https://github.com/unslothai/unsloth) | `third_party/training/unsloth` | `main` | Apache-2.0 core; AGPL-3.0 components | P2 | SUCCESS |
| [LLaMA-Factory](https://github.com/hiyouga/LlamaFactory) | `third_party/training/llama-factory` | `main` | Apache-2.0 | P2 | SUCCESS |
| [Axolotl](https://github.com/axolotl-ai-cloud/axolotl) | `third_party/training/axolotl` | `main` | Apache-2.0 root; Axolotl Community License integrations | P2 | SUCCESS |
| [Hugging Face PEFT](https://github.com/huggingface/peft) | `third_party/training/peft` | `main` | Apache-2.0 | P1 | SUCCESS |
| [Hugging Face TRL](https://github.com/huggingface/trl) | `third_party/training/trl` | `main` | Apache-2.0 | P2 | SUCCESS |
| [LitGPT](https://github.com/Lightning-AI/litgpt) | `third_party/training/litgpt` | `main` | Apache-2.0 | P2 | SUCCESS |
| [llama.cpp](https://github.com/ggml-org/llama.cpp) | `third_party/inference/llama-cpp` | `master` | MIT | P1 | SUCCESS |
| [MLX LM](https://github.com/ml-explore/mlx-lm) | `third_party/inference/mlx-lm` | `main` | MIT | P3 | SUCCESS |
| [Docling](https://github.com/docling-project/docling) | `third_party/knowledge/docling` | `main` | MIT | P1 | SUCCESS |
| [Chroma](https://github.com/chroma-core/chroma) | `third_party/knowledge/chroma` | `main` | Apache-2.0 | P1 | SUCCESS |
| [Haystack](https://github.com/deepset-ai/haystack) | `third_party/knowledge/haystack` | `main` | Apache-2.0 | P2 | SUCCESS |
| [LM Evaluation Harness](https://github.com/EleutherAI/lm-evaluation-harness) | `third_party/evaluation/lm-evaluation-harness` | `main` | MIT | P1 | SUCCESS |
| [Evidently](https://github.com/evidentlyai/evidently) | `third_party/evaluation/evidently` | `main` | Apache-2.0 | P2 | SUCCESS |
| [MLflow](https://github.com/mlflow/mlflow) | `third_party/lifecycle/mlflow` | `master` | Apache-2.0 | P2 | SUCCESS |
| [DVC](https://github.com/treeverse/dvc) | `third_party/lifecycle/dvc` | `main` | Apache-2.0 | P2 | SUCCESS |
| [ModelScan](https://github.com/protectai/modelscan) | `third_party/security/modelscan` | `main` | Apache-2.0 | P1 | SUCCESS |
| [Sigstore Cosign](https://github.com/sigstore/cosign) | `third_party/security/cosign` | `main` | Apache-2.0 | P1 | SUCCESS |
| [LangGraph](https://github.com/langchain-ai/langgraph) | `third_party/orchestration/langgraph` | `main` | MIT | P2 | SUCCESS |

## Exact upstream pins and intended capabilities

| Project | Commit SHA | Intended AIRON capability |
|---|---|---|
| Soup | [`527314a446d52ffdeb2975c8dcd2c849a5d534b5`](https://github.com/MakazhanAlpamys/Soup/commit/527314a446d52ffdeb2975c8dcd2c849a5d534b5) | Local fine-tuning workflows and memory-efficient adaptation research. |
| Unsloth | [`d9827dc39670816e0cc6b94b94d4c3c0a4a25f79`](https://github.com/unslothai/unsloth/commit/d9827dc39670816e0cc6b94b94d4c3c0a4a25f79) | Efficient adapter training and model adaptation research. |
| LLaMA-Factory | [`6d1059c727450a4f58e56ad204d01a71abad7781`](https://github.com/hiyouga/LlamaFactory/commit/6d1059c727450a4f58e56ad204d01a71abad7781) | Alternative configurable fine-tuning workflows. |
| Axolotl | [`27bb23ce38373105027470b0d718f5ba87a01cb7`](https://github.com/axolotl-ai-cloud/axolotl/commit/27bb23ce38373105027470b0d718f5ba87a01cb7) | Alternative training orchestration and configuration research. |
| Hugging Face PEFT | [`249e46b32eaad2068fdc62e696dcde14892406ae`](https://github.com/huggingface/peft/commit/249e46b32eaad2068fdc62e696dcde14892406ae) | Parameter-efficient adapters for local model adaptation. |
| Hugging Face TRL | [`eb5a93fd86f3eb76c195d0c37521671a44a26ddb`](https://github.com/huggingface/trl/commit/eb5a93fd86f3eb76c195d0c37521671a44a26ddb) | Supervised and preference-based post-training research. |
| LitGPT | [`5341568a65e918a85cb284fac038de2157eebf3f`](https://github.com/Lightning-AI/litgpt/commit/5341568a65e918a85cb284fac038de2157eebf3f) | Alternative lightweight training and fine-tuning workflows. |
| llama.cpp | [`2a4daf0e08d6a9b6993ee0d4a9a3cfc35a6f405c`](https://github.com/ggml-org/llama.cpp/commit/2a4daf0e08d6a9b6993ee0d4a9a3cfc35a6f405c) | Local quantized model inference. |
| MLX LM | [`56230fa02b8ff8330daf26dc95c28480423ed5fe`](https://github.com/ml-explore/mlx-lm/commit/56230fa02b8ff8330daf26dc95c28480423ed5fe) | Apple Silicon local inference and adaptation research. |
| Docling | [`336e9dde255237a3bf68abaea727d9782f7417a9`](https://github.com/docling-project/docling/commit/336e9dde255237a3bf68abaea727d9782f7417a9) | Local document conversion and extraction for retrieval. |
| Chroma | [`1a3ac2c7c623adbd03ed2508dc27b98cdf26016d`](https://github.com/chroma-core/chroma/commit/1a3ac2c7c623adbd03ed2508dc27b98cdf26016d) | Local vector storage and retrieval. |
| Haystack | [`104a83f8799b1b8d9d18a88eb9a08305133aea2d`](https://github.com/deepset-ai/haystack/commit/104a83f8799b1b8d9d18a88eb9a08305133aea2d) | Retrieval and document-processing pipeline research. |
| LM Evaluation Harness | [`d6de81643928d653435c431bae19945d41d32520`](https://github.com/EleutherAI/lm-evaluation-harness/commit/d6de81643928d653435c431bae19945d41d32520) | Future reproducible language-model evaluation. |
| Evidently | [`34771fe41c08ca074d96a52aaf4a45cd640cbaf5`](https://github.com/evidentlyai/evidently/commit/34771fe41c08ca074d96a52aaf4a45cd640cbaf5) | Future model, data-quality and drift reporting. |
| MLflow | [`c980e95c1c349820b42031e1f9e6f34365fc57a3`](https://github.com/mlflow/mlflow/commit/c980e95c1c349820b42031e1f9e6f34365fc57a3) | Experiment records and model lifecycle tracking. |
| DVC | [`b59add99ee667f2b352cc1be337619f965fe3fea`](https://github.com/treeverse/dvc/commit/b59add99ee667f2b352cc1be337619f965fe3fea) | Versioned data/model references and reproducible pipelines. |
| ModelScan | [`61fcec9c2a37c24c1fb12d84ede30fe248a364bd`](https://github.com/protectai/modelscan/commit/61fcec9c2a37c24c1fb12d84ede30fe248a364bd) | Future static inspection of model serialization artifacts. |
| Sigstore Cosign | [`195ab76b789923862345f5fa9bfe3fac6c453927`](https://github.com/sigstore/cosign/commit/195ab76b789923862345f5fa9bfe3fac6c453927) | Artifact signature and provenance verification research. |
| LangGraph | [`a054ed08dcee7ecc4105706d38c0b4aa0b3c3c32`](https://github.com/langchain-ai/langgraph/commit/a054ed08dcee7ecc4105706d38c0b4aa0b3c3c32) | Stateful agent workflow orchestration research. |

## Licence preservation and component restrictions

All tracked upstream source, LICENSE, NOTICE, COPYING, COPYRIGHT and identified acknowledgement files remain unchanged inside the pinned submodules. The lock file lists exact paths and SHA-256 hashes. Root licence labels do not override component-specific terms. Models, datasets, external services and uninstalled dependencies are not covered by this source inventory.

- **Soup** — Root Apache-2.0 terms and NOTICE are preserved. README explicitly calls out retaining LICENSE/NOTICE and limits on using the Soup name. Root evidence: [LICENSE](https://github.com/MakazhanAlpamys/Soup/blob/527314a446d52ffdeb2975c8dcd2c849a5d534b5/LICENSE), [NOTICE](https://github.com/MakazhanAlpamys/Soup/blob/527314a446d52ffdeb2975c8dcd2c849a5d534b5/NOTICE).
- **Unsloth** — Do not treat the entire checkout as Apache-2.0. README identifies Apache-2.0 core and AGPL-3.0 optional components; COPYING, studio/LICENSE.AGPL-3.0, unsloth/kernels/moe/LICENSE and unsloth/kernels/moe/grouped_gemm/LICENSE contain AGPL-3.0 terms. Component scope must be checked before future reuse. Other vendored licences and notices are retained. Root evidence: [COPYING](https://github.com/unslothai/unsloth/blob/d9827dc39670816e0cc6b94b94d4c3c0a4a25f79/COPYING), [LICENSE](https://github.com/unslothai/unsloth/blob/d9827dc39670816e0cc6b94b94d4c3c0a4a25f79/LICENSE).
- **LLaMA-Factory** — No additional project-specific restriction identified in the reviewed root licence and declarations. Separately licensed dependencies, services, models and data are outside this root-licence label; any bundled notices remain intact. Root evidence: [LICENSE](https://github.com/hiyouga/LlamaFactory/blob/6d1059c727450a4f58e56ad204d01a71abad7781/LICENSE).
- **Axolotl** — Root Apache-2.0 does not describe every subtree. src/axolotl/integrations/LICENSE.md defines a separate Axolotl Community License covering that directory and its subdirectories: section 3.1 restricts commercial activity offering third-party model fine-tuning services/platforms, whether free or paid; section 3.2 includes reverse-engineering and notice-removal restrictions. This is a restricted source-available component. cut_cross_entropy/LICENSE has separate Apple terms and refers to ACKNOWLEDGEMENTS.md. All nested licences/notices remain intact. Root evidence: [LICENSE](https://github.com/axolotl-ai-cloud/axolotl/blob/27bb23ce38373105027470b0d718f5ba87a01cb7/LICENSE).
- **Hugging Face PEFT** — No additional project-specific restriction identified in the reviewed root licence and declarations. Separately licensed dependencies, services, models and data are outside this root-licence label; any bundled notices remain intact. Root evidence: [LICENSE](https://github.com/huggingface/peft/blob/249e46b32eaad2068fdc62e696dcde14892406ae/LICENSE).
- **Hugging Face TRL** — No additional project-specific restriction identified in the reviewed root licence and declarations. Separately licensed dependencies, services, models and data are outside this root-licence label; any bundled notices remain intact. Root evidence: [LICENSE](https://github.com/huggingface/trl/blob/eb5a93fd86f3eb76c195d0c37521671a44a26ddb/LICENSE).
- **LitGPT** — No additional project-specific restriction identified in the reviewed root licence and declarations. Separately licensed dependencies, services, models and data are outside this root-licence label; any bundled notices remain intact. Root evidence: [LICENSE.md](https://github.com/Lightning-AI/litgpt/blob/5341568a65e918a85cb284fac038de2157eebf3f/LICENSE.md).
- **llama.cpp** — Root MIT terms are retained. Vendored components retain their separate MIT, BSD and other notices; these are inventoried below. External model licences are separate. Root evidence: [LICENSE](https://github.com/ggml-org/llama.cpp/blob/2a4daf0e08d6a9b6993ee0d4a9a3cfc35a6f405c/LICENSE).
- **MLX LM** — No additional project-specific restriction identified in the reviewed root licence and declarations. Separately licensed dependencies, services, models and data are outside this root-licence label; any bundled notices remain intact. Root evidence: [LICENSE](https://github.com/ml-explore/mlx-lm/blob/56230fa02b8ff8330daf26dc95c28480423ed5fe/LICENSE).
- **Docling** — README states the codebase is MIT and that individual models have their own licences. No external model packages or weights were acquired. The checkout also preserves the separately licensed bundled material. Root evidence: [LICENSE](https://github.com/docling-project/docling/blob/336e9dde255237a3bf68abaea727d9782f7417a9/LICENSE).
- **Chroma** — No additional project-specific restriction identified in the reviewed root licence and declarations. Separately licensed dependencies, services, models and data are outside this root-licence label; any bundled notices remain intact. Root evidence: [LICENSE](https://github.com/chroma-core/chroma/blob/1a3ac2c7c623adbd03ed2508dc27b98cdf26016d/LICENSE).
- **Haystack** — No additional project-specific restriction identified in the reviewed root licence and declarations. Separately licensed dependencies, services, models and data are outside this root-licence label; any bundled notices remain intact. Root evidence: [LICENSE](https://github.com/deepset-ai/haystack/blob/104a83f8799b1b8d9d18a88eb9a08305133aea2d/LICENSE), [license-header.txt](https://github.com/deepset-ai/haystack/blob/104a83f8799b1b8d9d18a88eb9a08305133aea2d/license-header.txt).
- **LM Evaluation Harness** — Root MIT terms are retained. Referenced benchmarks/datasets and model weights have their own terms; none were separately downloaded or executed. Root evidence: [LICENSE.md](https://github.com/EleutherAI/lm-evaluation-harness/blob/d6de81643928d653435c431bae19945d41d32520/LICENSE.md).
- **Evidently** — No additional project-specific restriction identified in the reviewed root licence and declarations. Separately licensed dependencies, services, models and data are outside this root-licence label; any bundled notices remain intact. Root evidence: [LICENSE](https://github.com/evidentlyai/evidently/blob/34771fe41c08ca074d96a52aaf4a45cd640cbaf5/LICENSE).
- **MLflow** — Root Apache-2.0 terms are retained. The upstream-pinned mlflow/assistant/skills submodule is included recursively and separately inventoried. Root evidence: [LICENSE.txt](https://github.com/mlflow/mlflow/blob/c980e95c1c349820b42031e1f9e6f34365fc57a3/LICENSE.txt).
- **DVC** — No additional project-specific restriction identified in the reviewed root licence and declarations. Separately licensed dependencies, services, models and data are outside this root-licence label; any bundled notices remain intact. Root evidence: [LICENSE](https://github.com/treeverse/dvc/blob/b59add99ee667f2b352cc1be337619f965fe3fea/LICENSE).
- **ModelScan** — Root Apache-2.0 terms and the separate modelscan/tools/LICENSE notice are retained. Upstream test fixtures remain unchanged inside the submodule; no scanner or fixture was executed. Root evidence: [LICENSE](https://github.com/protectai/modelscan/blob/61fcec9c2a37c24c1fb12d84ede30fe248a364bd/LICENSE).
- **Sigstore Cosign** — Root Apache-2.0 terms and COPYRIGHT.txt are retained. Source acquisition does not perform signing, key generation or service registration. Root evidence: [COPYRIGHT.txt](https://github.com/sigstore/cosign/blob/195ab76b789923862345f5fa9bfe3fac6c453927/COPYRIGHT.txt), [LICENSE](https://github.com/sigstore/cosign/blob/195ab76b789923862345f5fa9bfe3fac6c453927/LICENSE).
- **LangGraph** — No additional project-specific restriction identified in the reviewed root licence and declarations. Separately licensed dependencies, services, models and data are outside this root-licence label; any bundled notices remain intact. Root evidence: [LICENSE](https://github.com/langchain-ai/langgraph/blob/a054ed08dcee7ecc4105706d38c0b4aa0b3c3c32/LICENSE).

## Recursive upstream dependency

MLflow pins [`mlflow/skills`](https://github.com/mlflow/skills) at `6a505d8f30b7fbf93533cdf4e7d88fc30d66ba8b` under `third_party/lifecycle/mlflow/mlflow/assistant/skills`. It was fetched and is included in clean restoration checks. Its root licence is Apache-2.0. This is one transitive checkout in addition to the 19 requested projects; the MLflow gitlink fixes its revision without modifying MLflow source.

## Restore the sources

Run in a fresh environment with Git and network access to the public upstream repositories:

```bash
export GIT_LFS_SKIP_SMUDGE=1
git clone --branch research/p0-053-opensource-capability-library --single-branch https://github.com/richardrich999888-rgb/AIRON-native-.git
cd AIRON-native-
git submodule update --init --recursive
git submodule status --recursive
```

For the exact preservation snapshot, check out the AIRON commit reported with this delivery before running the submodule update. Do not use `--remote`: ordinary submodule update follows the committed gitlinks. `.gitmodules` recommends shallow history, which retains the complete ordinary Git file tree at each selected revision. Git LFS objects are intentionally excluded; any pointer files remain preserved.

Submodule pins depend on upstream repository availability. This branch preserves reproducible source references, not an independent permanent mirror of upstream objects. No model weights, datasets, checkpoints, credentials or caches are added as AIRON Git blobs.

Existing AIRON files, application manifests, deployment settings and runtime code are unchanged from the verified base. The only parent-repository additions are `.gitmodules`, 19 gitlinks and the three inventory documents.
