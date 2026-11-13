# Adversarial qualification

Tested source: AIRON initial lifecycle `16c6bd745edacaa4ad7b435cc52de935e1d1802f`; final qualification target `0f4cd7e20f4c19577b5a73b9d1dacdc221f3085a`; native interface `f1ba9fc2072dac1431543fd4961baaa2762b8ea9`. See `BENCHMARKS.json` and `evidence/local/PROVENANCE.json` for per-run revisions. Local hardware: Linux 6.18.57, AMD EPYC 9V74, 9 visible CPUs, 10,206,472 KiB RAM, no GPU; inference comparisons restricted to CPUs 0–1. Hosted hardware: Ubuntu 22.04, Linux 6.8 Azure, 4 visible CPUs, 16,371,436 KiB RAM; the corrected two-CPU run enforced an 8 GiB cgroup limit but training timed out; separate four-CPU training and two-CPU serving qualification is in progress. No claim of independent administration.

Threat model: untrusted documents, questions and API parameters from authenticated local actors; tenant/clearance mismatches; altered files by a test adversary without the administrative signing key; malformed models and lifecycle requests. The OS administrator, provisioned policy and trusted signing keys are assumed honest. Root compromise, stolen reviewer keys, malicious compiler/toolchain and an administrator replacing the whole history are outside this claim.

| Attack / failure | Observed result and scope |
|---|---|
| Cross-tenant and lower-clearance retrieval | Real native SQLite tests return no source; AIRON abstains with zero model calls |
| Unauthorized procedure | Actual native runtime returns refusal and zero model calls |
| Model self-approval / request identity spoofing | Operator cannot approve or attest verification; principal fields in request JSON are rejected |
| Forged expert suite | Native signature check fails; capability cannot be approved |
| Malicious document instruction | Tested injection string quarantined by native ingestion; canary unavailable to retrieval. This is bounded-pattern coverage, not universal injection immunity |
| Source deletion/update | FTS deletion and signed source versions checked; dependent procedure refuses stale knowledge |
| Corrupted adapter/model and hash substitution | Preserved integration tests reject changed artifacts; hosted actual safetensors loader rejects malformed model bytes |
| Dataset authorization / poisoning controls | Preserved P0-052 dataset authorization, manifest, split and mutation checks pass. Semantic poisoning of an expert-approved dataset is not solved |
| Capability/model rollback manipulation | Signed registry and anchored capability-file tests fail closed; actual lifecycle rollback exercised |
| Missing/truncated evidence | Signature, sequence, external expected head, audit and capability anchor tests reject alteration |
| Real interrupted training | Observed genuine optimizer step, cancelled process return -9, candidate registration refused, baseline inference still works |
| Restart recovery and low-space policies | Preserved controller tests cover interrupted-job state and low-space admission; real full-disk/quota and power-loss qualification is still open |
| Bounded queue and resource limits | Busy-worker requests refused; process limits and aggregate sampling active; later hosted lifecycle runs use hard cgroup limits |
| Untrusted / missing offline package | Installation uses pinned wheels with required hashes and no index; installer never enables online fallback |
| Cosign wrong key / changed artifact | Offline key-based verification rejects both; no transparency-log claim |
| Local HTTP boundary | Random role sessions, Host/Origin checks, body bounds and CSP; hosted browser/HTTP checks passed at 104efc4 with no page errors; evidence retained separately |

141 Python regression/integration tests passed locally, including 20 real native/Docling integration tests. Existing SYNTRIASS runtime baseline: 201 tests passed. The broader VANIAN suite has one local ptrace-dependent failure, retained as an environment limitation; it is not presented as a clean pass. Counts overlap across repeated runs and are not summed into a marketing total.

No defence-grade certification, independent kernel observation or production penetration-test claim follows from these tests.

The additional Cosign binary scan (govulncheck v1.9.0, Go 1.27.4) returned three advisory IDs: GO-2026-4309, GO-2026-4529 and GO-2026-5932. Version-range/symbol matches and configured-feature reachability remain under review. The tested policy uses local public keys, no Rekor, X.509 chain or OpenPGP. This is not blanket clearance; Cosign is optional and is not included in the serving bundle. Full raw scan and the bounded review are retained in evidence/local.

Offline snapshot checks: seven actual positive/negative checks passed using the hosted snapshot at 104efc4 and the verifier hash in evidence/hosted-43391397592/snapshot-attacks.json. These include external digest/head checking, wrong-key rejection, truncation, native audit/capability modification, signed-object alteration and empty trust-pin refusal. Same-administrator trust pins do not establish independent observation.

Qualification infrastructure attack/failure: nonprivileged cgroup migration was denied while the previous shell continued. Raw zero accounting was rejected during evidence review. The replacement launcher fails closed, proves membership and drops privileges before the workload. Pre-fix functional passes are not resource-limit passes.

Actual resource-fault probes also passed at 00bb5a7: aggregate RSS admission exceeded its 128 MiB test bound and the worker was killed; a busy process hit its one-second deadline; output beyond the 8 MiB file limit was rejected; all children were reaped and the next worker succeeded. Raw results are in evidence/local/worker-resource-attacks.json. These do not substitute for full-disk or power-loss testing.
