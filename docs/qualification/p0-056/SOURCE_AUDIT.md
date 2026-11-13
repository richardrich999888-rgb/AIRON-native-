# P0-056 source audit — 13 November 2026 IST

Baseline AIRON main: `04a84e64fc2be36fe03fc73006c9a42285617a02`.
P0-052: `1d4a2255549a0ffd881fde26add190a2d8cf4c64` (runtime `6077c9a`).
P0-053: `c85205d6cfa4572261046bd549a397ca6cfcf0a7`.
AIP main: `872dbf375838cff464eb019488c63d948015e9b8`.
AIP interface base, teaching branch: `93c65bcdc293aa950552f1a11515c4b21a553e8e`.

All remote heads captured in evidence/audit.json. The five named AIP branches were inspected at the recorded heads; v0.1/v0.2 reports and implementations are retained in AIP unchanged. Main has neither the teaching runtime nor the Soup integration. No branch is merged. Existing uncommitted work remains in its original directory.

P0-052 is selected by exact paths into the new main-based branch: services/model-adaptation, tests/integration/soup, docs/integrations/soup and docs/qualification/p0-052. Those files remain byte-identical. Soup's serving commit af2f5d5 differs from the newer P0-053 research pin 527314a: keep the demonstrated serving pin. An older local installation failed its tree check; rebuilding the original pin restored all 121 baseline tests. The first complete baseline attempt fails when this host denies an AF_UNIX isolation probe. No sandbox check was removed. Original failed report is retained.

AIP provides the actual typed engine, signed expert suite verification, approval authority grants, activation/rollback, scoped SQLite FTS5 and execution audit. A new private process interface is implemented in AIP, not copied into AIRON. This preserves original ownership/licensing notices. Deployment/redistribution permission for that proprietary component remains unresolved. Local integration testing does not establish a commercial licence.

The source lock records actual commits, trees, root/component licence hashes, nested submodules and dependency manifests. P0-053 sources were reused without duplicate copies. Transformers v5.16.1 and SQLite were newly cloned. Source clones are research inputs, not automatic application dependencies. Upstream source secrets pattern scans include fixtures and are not evidence of absence of secrets. No matching credential values are copied into this report.

Declared MIT/Apache notices must accompany redistribution; Apache notices and modifications must be retained, without implying trademark permission. SQLite's source has a public-domain dedication; deployed CPython/rusqlite SQLite versions are separate dependencies. Full native/platform and transitive redistribution review is still open. Source inventory is not blanket legal clearance.

Initial environment vulnerability scan found 17 advisory entries (including duplicates) in pip 25.0.1 and setuptools 78.1.0. P0-056 upgrades only packaging tooling to pip 26.2 and setuptools 84.2.1; the repeated environment scan found no known advisories. P0-052 source pins/evidence are untouched. This scan covers installed Python distributions, not every source-only candidate or native dependency.

Hardware: Linux 6.18.57 x86-64, AMD EPYC 9V74, nine visible logical CPUs, 10,206,472 KiB visible RAM, no GPU used. Raw inventory is in evidence/audit.json. Two-CPU process affinity and measured aggregate memory are recorded separately; this is not an independently administered 2-vCPU/8-GB testbed.

Historical synthetic procedural improvements do not establish autonomous acquisition: v0.1 generated no valid autonomous capability; v0.2 still needed expert corrections. Historical benchmark figures are not new P0-056 results.

P0-056 implementation revisions: initial composed runtime 16c6bd745edacaa4ad7b435cc52de935e1d1802f; final qualification source 00bb5a74051fd58bfd556703228e96a941dd7dba; companion AIP interface f1ba9fc2072dac1431543fd4961baaa2762b8ea9. Published frozen benchmark tree bb87ca5a914eec7ca39619498d376b822366f2c9 equals local 853fd413090e6cdde8d41c6c793e6004b54ae22b.

Optional tools are now executed through separate qualification scripts: source-pinned LM Evaluation Harness 0.4.14.dev0, source-pinned MLflow-skinny 3.18.1.dev0 with local SQLite, and source-built Cosign using Go 1.27.4 (official distribution SHA-256 7226736c2339719cda28fbf3a54d71aa63bcefe376e98cef00034268dab24840). They are not serving requirements. These source snapshots are pinned research versions, not a blanket stable-release maturity claim.

Scale model licences were read from immutable official Qwen repositories. 0.5B and 1.5B GGUFs are Apache-2.0 and were hash-verified for qualification. The examined 3B model carries the Qwen RESEARCH LICENSE AGREEMENT; commercial permission is unresolved, so no 3B artifact was provisioned. Exact model pins are in services/unified-runtime/scale-models.lock.json.

The additional Cosign binary scan (govulncheck v1.9.0, Go 1.27.4) returned three advisory IDs: GO-2026-4309, GO-2026-4529 and GO-2026-5932. Version-range/symbol matches and configured-feature reachability remain under review. The tested policy uses local public keys, no Rekor, X.509 chain or OpenPGP. This is not blanket clearance; Cosign is optional and is not included in the serving bundle. Full raw scan and the bounded review are retained in evidence/local.

Additional scans: cargo-audit 0.23.0 checked the pinned AIP lockfile's 334 dependencies against RustSec database commit af7b3ec33460b8e2de8d422e16d628518891a519 and returned no known vulnerabilities or warnings. An OSV direct-commit query returned no entries for the 11 source candidates. These checks are retained in evidence/local; neither result guarantees complete advisory coverage, native C/C++ safety or legal redistribution clearance.
