# AIRON Native — SYNTRIASS Labs

The enterprise console lives in [apps/airon-console](apps/airon-console/). It connects a loopback model server, a local document and approval repository, measurements and packaged AIP verification to the existing 53 routes. [Launch the console and follow the five-minute walkthrough](docs/P0-062_DEMONSTRATION.md). [Review the capability and data-source matrix](docs/P0-062_CAPABILITY_AUDIT.md).

The website and guided demonstration live in [`website/`](website/). The original SYNTRIASS logo is included. The interface is a portable React/Vite static app, with separate deployment configuration for Netlify and Vercel.

**[Hosting instructions](DEPLOYMENT.md)** · **[Website development](website/README.md)** · **[Local offline demonstration](website/offline/README.md)**

The hosted website uses synthetic documents, deterministic retrieval and browser-local execution records. Enterprise console inference requires an installed local Ollama model. Approved corrections are versioned records in the organisation’s knowledge repository.
