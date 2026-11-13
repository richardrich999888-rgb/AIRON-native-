# AIP raw signature contract experiment

This optional test-only harness consumes an independently checked-out AIP crypto crate at 872dbf375838cff464eb019488c63d948015e9b8. It copies no AIP source and adds no production dependency. AIP's declared proprietary licence/ownership still requires an explicit decision before distribution or runtime integration.

Python first verifies a retained real AIRON report against the source-reviewed report hash, public key and chain head. It emits the exact domain-prefixed signing bytes. The Rust harness calls AIP's actual verify_ed25519_raw for every record, rejects changed messages, signatures and keys, and signs a separate public-seed test message with sign_ed25519_raw. Python must then verify that AIP-generated signature. The test uses AIP's original Cargo.lock and Rust 1.90.0; source changes fail verification. Preparation requires networking; the verification stage runs in a distinct network namespace with failed connectivity probes.

Run the commands in .github/workflows/p0-052-aip-signature.yml. The current scratch workspace lacks cargo, so Rust compilation and the AIP portion are pending until that Actions job actually succeeds. A successful Python preparation alone is not a passed contract test.

This verifies a raw byte interface. Rust does not parse or canonicalize AIRON JSON. It does not create an AIP EvidencePacket, establish delegation/authority, protect signer custody, attest execution or integrate Sniffer Dog. The report remains APPLICATION_SIGNED / independent execution CANNOT_PROVE. The workflow retains its result only, not proprietary source or linked binaries.
