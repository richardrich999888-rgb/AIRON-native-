# AIRON Native — SYNTRIASS Labs

The website and guided demonstration live in [website/](website/). The original SYNTRIASS logo is included. The interface is a portable React/Vite static app, with separate deployment configuration for Netlify and Vercel.

**[Hosting instructions](DEPLOYMENT.md)** · **[Website development](website/README.md)** · **[Local offline demonstration](website/offline/README.md)**

The hosted demo uses synthetic documents, deterministic retrieval, explicit abstention and browser-local execution records. For the original demonstration, actual model inference runs in the separate local package with a preinstalled Ollama model. Self-evolving functionality remains planned; AIP is related work, with no assumed integration.

## Experimental local adaptation — P0-052

[The separate adaptation service](services/model-adaptation/README.md) adds a pinned Soup worker, authorized synthetic datasets, training-job supervision, frozen evaluation, reviewer approval, experimental model activation, rollback and signed application records. It has its own local console, “Private AI That Learns Locally.”

Read the [current qualification status](docs/qualification/p0-052/STATUS.md), [work ledger](docs/qualification/p0-052/LEDGER.md) and [upstream audit](docs/integrations/soup/UPSTREAM_AUDIT.md). Fixture tests do not prove real training. The original Ollama demonstration is not yet wired to the experimental adapter runtime. No broader platform production-readiness or physical air-gap claim is made.
