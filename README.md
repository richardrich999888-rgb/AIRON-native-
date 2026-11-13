# AIRON Native — SYNTRIASS Labs

The website and guided demonstration live in [`website/`](website/). The original SYNTRIASS logo is included. The interface is a portable React/Vite static app, with separate deployment configuration for Netlify and Vercel.

**[Hosting instructions](DEPLOYMENT.md)** · **[Website development](website/README.md)** · **[Local offline demonstration](website/offline/README.md)**

The hosted demo uses synthetic documents, deterministic retrieval, explicit abstention and browser-local execution records. Actual model inference runs only in the separate local package with a preinstalled Ollama model. Self-evolving functionality remains planned; AIP is related work, with no assumed integration.

This repository currently contains the demonstration website and local demo scaffold. It does not establish implementation or validation of the broader AIRON Native platform.

## P0-056 unified local runtime (draft qualification)

The `codex/p0-056-unified-airon-runtime` branch adds a real local runtime combining Docling ingestion, native access-controlled SQLite retrieval, llama.cpp inference, approved SYNTRIASS procedural capabilities, and the preserved Soup learning lifecycle. Its local console is separate from the hosted static website.

Read [the qualification report](docs/qualification/p0-056/FINAL_REPORT.md), [build/install instructions](docs/qualification/p0-056/BUILD_AND_INSTALL.md), and [limitations](docs/qualification/p0-056/KNOWN_LIMITATIONS.md) before running or presenting it. The working synthetic vertical slice is not a claim of independent qualification or autonomous skill acquisition. The proprietary native component remains in AIP behind a versioned interface; nothing is merged automatically.
