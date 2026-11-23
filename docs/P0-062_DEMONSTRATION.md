# AIRON Native enterprise intelligence walkthrough

## Start the local console

Use Linux, Node 24, Python 3.12 with SQLite FTS5 and a Chromium-based browser. The operator installs dependencies before the presentation. Keep the repository directory on a persistent disk.

```sh
git clone --branch feature/airon-native-ciic-enterprise-intelligence https://github.com/richardrich999888-rgb/AIRON-native-.git
cd AIRON-native-/apps/airon-console
python3 -m venv "$HOME/.airon-venvs/console"
"$HOME/.airon-venvs/console/bin/pip" install --require-hashes -r intelligence/requirements.txt
npm ci
npm run build
npm run db:local
PYTHON="$HOME/.airon-venvs/console/bin/python" npm run ciic -- --demo-personas --directory "$HOME/.airon-presenter" --model qwen2.5:0.5b
```

Open **http://127.0.0.1:8787/knowledge-vault**. Demo profiles allow the presenter to switch between fictional users. Use this mode with presentation data only. Omit `--demo-personas` for operator-issued pairing keys. The two modes use separate databases. Ordinary users cannot upload, approve or export. The service checks Host, origin and bearer identity on the loopback interface. The Enterprise Intelligence pairing and inherited console authentication have distinct scopes.

For local model generation, provision Ollama and the model on the same machine before presenting. A reproducible CPU setup using Docker is below. The volume preserves downloaded weights. Run the container creation once. On subsequent launches use `docker start airon-ollama`.

```sh
docker run -d --name airon-ollama -p 127.0.0.1:11434:11434 -v airon-models:/root/.ollama -e OLLAMA_NO_CLOUD=1 ollama/ollama:0.40.17@sha256:ccc42bcd3d5fcf7ab0d532b300382154e1a4da56fc666bdb313b78ebdd912754
docker exec airon-ollama ollama pull qwen2.5:0.5b
curl -fsS http://127.0.0.1:11434/api/tags | python3 -c 'import json,sys; assert any(m["name"]=="qwen2.5:0.5b" and m["digest"]=="a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67" for m in json.load(sys.stdin)["models"])'
```

## Shreyas’s five-minute script

Use a fresh sample workspace for a first rehearsal. The repository includes a two-page, fictional workshop note at `apps/airon-console/tests/fixtures/workshop-note.pdf`. Keep it ready in the browser’s file picker. The following actions take place in the console.

| Time | Action | Say aloud |
| --- | --- | --- |
| 0:00–0:30 | Open **Intelligence Overview** as Mira. Show source documents and approved versions. | “Imagine a new engineer taking over a shift. The inspection interval is written in a manual. The handover procedure is something only the shift lead remembers. Both matter tomorrow morning. At SYNTRIASS, we’re building AIRON Native so the next engineer can use both kinds of knowledge inside the organisation.” |
| 0:30–1:05 | Open **Knowledge Vault**. Select the workshop PDF and save it. Leave the optional question blank. Expand the indexed entry. Return to Overview to see the count. | “I’m adding the actual workshop note. AIRON keeps the original file, indexes its text and records its fingerprint. That gives us a source we can come back to.” |
| 1:05–1:50 | Open **Private AI Workspace** as Dev. Select Local Ollama and the installed model. Ask **What is the amber spindle interval?** Open **Inspect cited passage**. Then ask **Which register records the spindle handover?** | “I’ll ask as the engineer. The answer is 72 hours. Here’s page two, and here are the model and measured token counts. Now I’ll ask where to record the handover. This manual doesn’t say. AIRON leaves that question open.” |
| 1:50–2:50 | Open **Expert Teach** as Leela. Use the same handover question, choose the workshop PDF, enter **Record the spindle handover in register MH-04.** Add **Workshop shift addendum, section 2, supplied by the shift lead.** Submit. Switch to Ravi and approve. | “Leela knows the missing procedure. She records it with a supporting reference. Ravi reviews it as a different person and approves it for reuse. We can see who contributed the answer and who accepted responsibility for it.” |
| 2:50–3:35 | Open Private AI Workspace as Nila. Ask the same handover question in deterministic mode. Open **Institutional Memory**, show version, reviewer and reuse count. Switch to Mira and export the JSON. | “Nila can now ask the same question on the next shift. She gets the reviewed procedure, with its source and version. The organisation can take a copy of the knowledge it has built.” |
| 3:35–4:25 | In **Trust & Evidence**, expand the approval event. Open **Sovereign Runtime** and probe. Open **Runtime Activity** and **Token Usage** from Local execution. | “Here is the approval event. These runtime figures come from requests on this installation. We can see the time and tokens the model used. We leave cost open until the organisation supplies a price.” |
| 4:25–5:00 | Return to Sovereign Runtime as Mira. Choose **Restart local repository**, re-pair, and open Institutional Memory. If time permits, open **Verification → Local Runtime → Run archive verification**. | “The reviewed procedure survives a service restart. This is what we want an organisation to own over time. When a person changes teams, the next person can still find the answer, understand where it came from and see who reviewed it.” |

Sovereign Runtime can restart the repository only in explicit sample mode as Mira. It drains work, restarts the Python process image on the same disk and rotates pairing keys. The browser stays open. Re-pair any other open tab after restart.

## Rehearsal and fallback

If Ollama is absent, choose **Deterministic source excerpt**. Say “This answer is the indexed passage on page two.” A model failure withholds the answer. Switch engines explicitly to continue. Token counters remain unreported until a real model supplies them. Local model output is constrained to a sentence from the retrieved passage. FTS5 needs sufficiently specific matching words and abstains for ambiguous chunks. This release supports source lookup and human-reviewed corrections, with no model-weight update.

PDF ingestion requires a text layer, up to 64 pages, 2 MiB and 160,000 extracted characters. For a scan, use the approved UTF-8 TXT or Markdown source. When repeating the walkthrough on an existing database, reuse the indexed document. Its content fingerprint prevents duplicate imports. A new directory starts a separate workspace without changing earlier records.

In inherited operations pages choose **Local Runtime** to inspect this installation. **Return to evaluation data** restores the existing synthetic tenant. Archived AIP decisions describe signed historical inputs. The local verifier process reports its own process relationship. Enterprise-wide discovery, independent current-host attribution, SSO/SCIM, cost pricing and formal air-gap qualification remain outside the demonstrated scope.

## Dependencies

| Component | Pinned source and license | Use |
| --- | --- | --- |
| pypdf | [7.1.1, BSD-3-Clause](https://github.com/py-pdf/pypdf) | Text-layer PDF parsing in a resource-limited process. Docling was evaluated for richer conversion. This workflow needs only text and page boundaries. |
| OpenTelemetry Python | [SDK and API 1.45.2, conventions 0.66b2, Apache-2.0](https://github.com/open-telemetry/opentelemetry-python) | Real nested local spans with trace IDs, persisted in SQLite. No external collector. |
| typing-extensions | [4.16.0, PSF-2.0](https://github.com/python/typing_extensions) | Pinned transitive dependency. |
| Ollama | [v0.40.17, MIT](https://github.com/ollama/ollama/tree/v0.40.17) | Loopback model discovery, inspection and structured chat. OCI digest is pinned above. |
| Qwen2.5 0.5B Instruct | [Model card, Apache-2.0](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct) | Ollama manifest SHA-256 `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`. Download on the operator machine. |
| SQLite FTS5 / AIP | Python’s linked SQLite / shipped AIP verifier from `d8ea36255d311b10b9b5b6e844336058622d45c6` | Existing embedded database and pinned archive verifier. Baseline notices remain in the application. |

Python package artifacts are hash-locked in `intelligence/requirements.txt`. License texts are in `intelligence/licenses/`. The bundled model license matches the Ollama manifest license layer. Qdrant was evaluated for vector retrieval and LangGraph for agent orchestration. FTS5 and one allowlisted verifier suffice here and avoid two additional service dependencies.
