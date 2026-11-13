# Adversarial coverage

The following automated coverage is in tests/integration/soup/test_lifecycle.py and test_server.py. All model/checkpoint bytes in this suite are labelled fixtures. Results do not establish real-model acceptance.

| Requested case | Implemented check | Scope / remaining gap |
|---|---|---|
| Poisoned datasets | Instruction/control/URL quarantine, unapproved feedback rejection, duplicate split rejection | Heuristics; semantic poisoning not solved |
| Malicious checkpoint | Fixed output registration, manifest tamper rejection, LoRA/base binding | Only successful worker outputs accepted; malformed safetensors must fail in real loader |
| Unsafe loading | Reject .bin/.pt/.pkl/.py, custom-code config | Data-only import tests; actual loader test belongs to real run |
| Traversal/symlinks | Parent traversal, absolute paths, symlink and hardlink rejection | OS account trusted; no hostile-admin race claim |
| Job privilege escalation | Unknown config/command/plugin rejection; mount allowlist | Real namespace/filesystem isolation probe separate |
| Unauthorized activation | Operator role denied, pending approval denied | Local bearer roles, not enterprise identity |
| Modified hashes | Changed candidate blocks activation | Signed registry authority is local controller |
| Tampered evaluation | Recomputed hash without valid signature rejected | Cryptographic fixture test |
| Forged approval | Altered signed approval rejected | Private key not compromised in test |
| Training interruption | Cancelled job denied; restart marks RUNNING interrupted | Real in-flight kill test still required |
| Corrupt checkpoint recovery | Modified completed output denied | No unsafe optimizer recovery |
| Failed export | No export registry entry on worker failure | Fixture failure injection |
| Isolation violation | No unsandboxed fallback; actual probe implementation | Whole-workflow syscall evidence required |
| Unauthorized documents | Existing gateway access tests retained | Adaptation currently accepts synthetic data only |
| Rollback after failure | Original pointer retained on failed activation; corrupt rollback refused | Real adapted-inference/rollback acceptance driver |
| Continual-learning regression | Any regression blocks deployment | Narrow fixed suite; not proof against general forgetting |
