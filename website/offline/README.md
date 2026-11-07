# AIRON Native local demonstration

This self-contained UI and Python gateway uses synthetic data only. No cloud model calls or CDNs are used by the console. The interface and gateway run without Internet access after Python, Ollama, and model weights have been provisioned. The hosted Sites preview itself is not an air-gap deployment.

## Start
1. Extract this complete archive. Python 3.10+ is required; no Python dependencies are needed.
2. Before isolation, install Ollama and acquire a model suitable for your device, subject to its license. Run `ollama list` to find its exact installed name. Weights are not included.
3. Disable Ollama cloud features with `OLLAMA_NO_CLOUD=1`, restart Ollama, and use firewall/network isolation for a real air-gap test. The gateway contacts only `http://127.0.0.1:11434`; it does not fetch models, follow redirects, or use HTTP proxies. Local tags alone do not prove isolation.
4. Run `python3 server.py --model YOUR_INSTALLED_MODEL_NAME --role analyst`.
5. Open the printed loopback URL. In Runtime settings, paste the terminal pairing token. The token is kept in UI memory, not localStorage. Connect, then run the scenarios.
6. To demonstrate administrator access, stop and restart with `--role admin`; pair with the new token. The gateway binds the role to the session and ignores client-supplied role fields.

Rehearsal mode works without Ollama and returns deterministic excerpts. Local mode invokes the preinstalled model only for an authorized supported question. It must return JSON with the exact source ID and full quote. Any unexpected or unsupported response is withheld. This is a constrained extractive validation demonstration, not general semantic RAG or model quality benchmarking.

## Compute controls
One request at a time; 2,048-token context; at most 256 generated tokens; temperature zero; model unloaded after request (`keep_alive: 0`). No hardware memory, throughput or latency baseline is claimed. Model size and actual peak memory depend on the selected device and weights. The first request may be slow because the model is cold.

## Records and repeatability
Browser runs, notes and test results stay in localStorage on this origin. Export a pilot JSON pack from the UI. The gateway additionally writes `records/session-*.jsonl` with mode 0600. Application SHA-256 chains detect ordinary byte edits but are unsigned and can be rewritten or truncated by an operator. The assurance remains CANNOT_PROVE. AIP signing, trusted anchoring and independent kernel observation are not integrated.

Run `python3 -m unittest test_server.py` for local gateway unit tests. Tests stub the Ollama response; a passing unit test is not a successful real-model test. Check the on-screen verification list for target-hardware, identity, air-gap and accountability acceptance items.

## Boundaries
All business documents are fictional and shipped in the UI. Browser role selection is a rehearsal, not authentication; do not load sensitive documents. The loopback pairing token is a single-device demonstration control, not enterprise identity or tenant isolation. This package does not include self-evolving behavior, weight updates, autonomous fine-tuning, P2P distribution, AIP signing, or production security accreditation.

## Related work
The separate AIP README was reviewed on 7 Nov 2026, without running its tests: https://github.com/richardrich999888-rgb/AIP-agent-identity-protocol- . It describes signed authority-bound records and labels its unauthenticated HTTP service a prototype. This console does not import AIP code.

Ollama protocol references used: https://docs.ollama.com/api/chat and https://docs.ollama.com/api/tags . Review the installed runtime configuration for your deployment.

Logo: the supplied SYNTRIASS spiral crown asset is preserved unchanged; the UI uses CSS framing.
