# AIRON enterprise console capability audit

Baseline and rollback revision: `b1131570e816cf7d651cea9bc4ec83d3f9a7661a` on PR #5. The preserved VANIAN source is `e574a03206d29a4cf1d4fd8637231999f43b2aaf`. A clean checkout at the rollback revision reproduces the previous console. Use a copy of the workspace database when testing a rollback.

| Baseline capability | Classification | Evidence and boundary |
| --- | --- | --- |
| Route contracts and branded application | REAL | `src/navigation.ts`, `src/intelligence-navigation.ts` and the navigation contract cover 46 inherited routes and seven intelligence routes. |
| Local knowledge API and access | REAL | `intelligence/local_api.py` binds 127.0.0.1:8766, checks host, origin and bearer, and pairs the console at port 8787. Selectable profiles require explicit sample mode. |
| Vault | REAL | SQLite documents, normalized source questions and FTS5 search. The UI reads TXT/Markdown in the browser and sends editable text. |
| Uploaded binary provenance, PDF, page/chunk retrieval | UNAVAILABLE | The baseline hashes the extracted text and depends on a pre-registered question for workspace retrieval. |
| Private AI Workspace | PARTIAL | Exact source excerpts, citations and abstention work. Optional `/api/chat` validates an exact echo from one configured tag. No UI model picker or recorded token counts. |
| Expert Teach, Institutional Memory, Trust & Evidence | REAL | SQLite proposals, independent review, versioned activation, reuse, role-filtered history and JSON export survive restart. Knowledge audit events are application records. |
| Runtime probe | REAL | Database allocation and process CPU time are measured. The optional model probe checks only the configured tag. |
| Execution telemetry for the local knowledge service | UNAVAILABLE | No common measurements connecting requests, retrieval, ingestion and model usage to the inherited operations routes. |
| Inherited dashboard in demo mode | SYNTHETIC | `src/server/fixtures.ts` and the seeded D1 evaluation tenant supply records. Editing a fixture is a real application action on evaluation data. |
| Authenticated live bridge and archived verification | REAL | `bridge/`, `src/server/live.ts` and the packaged native/WASM evidence verifier have baseline native and browser tests. Archived observations have bounded scope. |
| Organization-wide agent discovery | UNAVAILABLE | Synthetic discovery records and unbound host observations do not establish enterprise-wide logical agent identity. |
| Baseline qualification | REAL | [51 passing workflow, native/adapter and browser tests](https://github.com/richardrich999888-rgb/AIRON-native-/actions/runs/45227698048). |

## Entry points

The inherited application uses the catch-all Next-compatible console route and `app/api/[...resource]/route.ts`. Enterprise Intelligence uses `src/ui/Intelligence.tsx` and POST requests to `/knowledge/{info,pair,state,import,import-sample,search,ask,propose,review,runtime,export}`. SQLite tables are documents, sources, teachings and events with a vault FTS index. The local launcher starts the Python service and Wrangler. The native verifier builds pinned Rust tools and compares the archived outputs. The original live bridge has separate authentication.

## Delivered UI and API contracts

| Console entry | Local operation and persistent records | Data classification |
| --- | --- | --- |
| Knowledge Vault | `upload`, `import`, `search` → bounded parser → original bytes, file/text SHA-256, page chunks, FTS5. Failed transactions roll back. | REAL |
| Private AI Workspace | `runtime` enumerates installed tags. `ask` searches SQLite, resolves the latest approved correction and optionally calls Ollama. `cancel` is scoped to the paired actor and active request ID. | REAL deterministic and installed-model paths. Runtime availability depends on the host. |
| Expert Teach | `propose`, `review` and `state` → separate contributor and reviewer, serialized version allocation, immutable decisions, activation on approval. | REAL |
| Institutional Memory / Trust & Evidence | `state`, `export` → actor, reviewer, source, reuse count, version and knowledge events. | REAL application records |
| Intelligence Overview / Sovereign Runtime | `state`, `runtime`, `measurements` → document totals, model availability, process CPU, storage and measured local calls. Explicit sample admin may invoke `restart`. | REAL |
| Runtime Activity / Conversation Explorer | Local Runtime → `measurements` → spans or workspace requests with outcomes, identities, duration, document and trace. Employee view is actor-scoped. | REAL local measurements |
| Token Usage / Spending | Local Runtime → model spans, nullable provider token counts and measured mean latency. | REAL usage. Monetary cost UNAVAILABLE. |
| AI Agents / Inventory / Lineage / Execution Evidence / Verification | Local Runtime → `verify-archive`, `tool-runs`. The authorized paired operator starts a fixed child process. Both bundled WASM verifiers execute. The locally recorded relationship and the two independent signed archive inputs are distinguished. | REAL application observation and real archive verification. Independent current-host action attribution UNAVAILABLE. |
| Existing security, monitoring, governance and FinOps views | Original data-source selector, seed tenant and live-provider bridge retained. | SYNTHETIC in evaluation mode. PARTIAL when an authenticated source supplies only a subset of the measures. |

Local reads are under `POST /knowledge/`. Data-changing local requests are authorized server-side. Presentation profiles require explicit startup configuration. The service stores full file content in the source tables. The measurements table contains operation metadata and trace IDs. No model prompts, file bodies, tariff assumptions or model weights are exported as telemetry.
