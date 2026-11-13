# AIP signing-byte interoperability experiment

The test-only contract at AIRON ddde09b24d88dc44d9c4a662881f6bdb8c4798cd passed [Actions run 43361491548](https://github.com/richardrich999888-rgb/AIRON-native-/actions/runs/43361491548). It links a separately checked-out, unmodified aip-crypto crate at AIP 872dbf375838cff464eb019488c63d948015e9b8. Rust 1.90.0 and that checkout's original Cargo.lock were used; the observed lock SHA-256 is a6ff8e31556445e8f478271c449590e7ca71562a3df5679e8b31f433faf46e65.

| Executed check | Result |
|---|---|
| Python verification of retained real offline report using source-reviewed hash/key/head | Passed; 20 linked records |
| AIP verify_ed25519_raw over each original domain-prefixed AIRON signing byte string | 20/20 passed |
| AIP rejection of changed message, signature and public key for each record | 60/60 rejected |
| AIP sign_ed25519_raw over an explicit public-seed interoperability vector | Passed |
| Python cryptography verification of that AIP-produced signature | Passed |
| Verification-stage network isolation | Distinct namespace, zero routes, failed deliberate IP/DNS probes |
| AIP checkout changed by the test | No tracked source change |

Original report: ../../qualification/p0-052/evidence/aip-raw-contract-ddde09b.json. The current EVIDENCE_INDEX.json binds its bytes. The test is reproducible through tests/integration/aip-signature and .github/workflows/p0-052-aip-signature.yml. The same contract passed again at 060ff1d (run 43362170890), 3ce3cfe (43371870508) and 6077c9a (43373086477). These repeat executions do not increase the number of independent test cases.

The boundary is deliberately narrow: Python constructs AIRON's existing canonical bytes, and Rust consumes them without parsing JSON. This does not qualify Rust/Python JSON canonicalization, AIP EvidencePacket semantics, delegation or authority binding, independent signer custody, external event anchoring, Sniffer Dog observation or kernel attestation. The record assurance remains APPLICATION_SIGNED / independent execution CANNOT_PROVE.

AIP remains separately owned proprietary infrastructure in the inspected revision. No AIP source or linked binary is copied into this repository, uploaded as an artifact, bundled with the model service or added as a production dependency. The test result is retained. Production integration still requires an appropriate ownership/licensing decision and a fuller signed-record/identity contract. A successful raw signature check alone does not satisfy those gates.
