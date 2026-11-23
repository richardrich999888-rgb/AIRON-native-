# P0-062 console qualification

The [hosted workflow](https://github.com/richardrich999888-rgb/AIRON-native-/actions/runs/45240436358) tested application revision `314878171ac9fc833c5ebbf4f08451deaa3ee591`. Both the deterministic acceptance job and the real Ollama job passed on Ubuntu 24.04.

| Check | Observed result |
| --- | --- |
| Original VANIAN checkout | Its pinned baseline build and browser drill-down passed. |
| Python knowledge service | 14 passed, including PDF parsing, source hashes, rollback after rejection, migration, independent approval, duplicate requests, cancellation ownership and telemetry scope. |
| Native AIP, adapters and console core | 26 passed, zero skips. |
| Full Playwright suite | 17 passed, zero skips or retries. The navigation contract retains all 53 routes. |
| Presentation paths | Separate Chromium rehearsal with Ollama and another with deterministic retrieval. Both exercised two-page PDF import, overview refresh, citation, abstention, approval, employee reuse, export, audit, usage views, fixed tool execution and persistence after a UI-triggered restart. |
| UI quality | Production build and TypeScript passed. Existing visual baselines passed. Axe reported zero serious or critical violations on the scanned login and intelligence views. ESLint exited successfully with 26 warnings. |
| Original website’s offline service | 15 tests passed in the development environment. |

The model runner verified the Ollama image digest and the installed model manifest before opening the application. For **What is the amber spindle interval?**, `qwen2.5:0.5b` returned **The amber spindle interval is 72 hours.** The cited passage was on page 2, chunk 2. The observed model request took **1,463.293 ms**, with **63 input tokens** and **16 output tokens**. This measures one local request including model checks.

The [measured response](measured-inference.json) came from the browser's authenticated request to the real service. The screenshots below are original 1440 × 960 Chromium captures. The complete model-run archive contains **23 screenshots** and the response JSON. Its downloaded SHA-256 was `694bbb5727b62073a26ea2e0089a7998aae4dd26c024a0ffba678d1b51de7ae8`. The deterministic archive contained **20 screenshots** with SHA-256 `397ceeb2131ea7c0f425fb87490f6e90b086c22293920a26fdd6b428881e5ebb`. Both were checked against GitHub's artifact metadata. [Complete model-run artifact](https://github.com/richardrich999888-rgb/AIRON-native-/actions/runs/45240436358/artifacts/14851297632).

| Application state | Capture |
| --- | --- |
| Index and fingerprint the original two-page PDF | [Knowledge Vault](14-pdf-ingestion.png) |
| Inspect the cited passage | [Deterministic source evidence](15-pdf-citation.png) |
| Display actual model, answer, latency and tokens | [Private AI Workspace](16-ollama-answer.png) |
| Replay the packaged signed inputs | [AIP archive verification](17-tool-verification.png) |
| Inspect locally recorded operations | [Runtime Activity](18-local-runtime.png) |
| Inspect actual usage and pricing availability | [Token Usage](19-local-tokens.png) · [Spending](20-local-spending.png) |
| Inspect the reviewer decision | [Trust & Evidence](21-pdf-approval.png) |
| Reopen approved knowledge after restarting the service | [Institutional Memory](22-pdf-memory-after-restart.png) |

The local tool invocation was observed by the application. The signed archive verified its receipt and returned `CannotProve / ActionEvidenceUnavailable` for the historical action. The separate observer archive contained three events. Neither archive establishes independent observation of the current host.

[Launch instructions, five-minute script, dependency inventory and fallback](../P0-062_DEMONSTRATION.md) · [UI-to-API and data-source matrix](../P0-062_CAPABILITY_AUDIT.md)
