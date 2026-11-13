# Adversarial coverage

Controller, HTTP, archive, process-supervision and syscall-classifier coverage is in tests/integration/soup/. Controller model/checkpoint bytes in that suite are labelled fixtures; retained report checks verify real evidence separately. At 6077c9a, all 111 checks passed in CI (80 controller/adversarial/transport/harness checks and 31 retained-report checks). The final documentation commit adds ten original retained reports; COMMANDS.md records the final local verification count. Separate real execution evidence is named below; fixture passes do not establish real-model acceptance.

| Requested case | Implemented check | Scope / remaining gap |
|---|---|---|
| Poisoned datasets | Instruction/control/URL quarantine, unapproved feedback/rehearsal rejection, cross-split duplicate rejection, replay manifest tamper and size bounds | Heuristics; semantic poisoning not solved |
| Malicious checkpoint | Fixed output registration, manifest tamper rejection, LoRA/base binding | Only successful worker outputs accepted; actual malformed safetensors load rejected in faults-6077c9a.json |
| Unsafe loading | Reject .bin/.pt/.pkl/.py, custom-code config | Real loader logged SafetensorError, header too large; the passing harness requires that parser cause |
| Traversal/symlinks | Parent traversal, absolute paths, symlink and hardlink rejection | OS account trusted; no hostile-admin race claim |
| Job privilege escalation | Unknown config/command/plugin rejection; mount allowlist | Real namespace/filesystem isolation probe separate |
| Unauthorized activation | Operator role denied, pending approval denied | Local bearer roles, not enterprise identity |
| Modified hashes | Changed candidate blocks activation | Signed registry authority is local controller |
| Tampered evaluation | Recomputed hash without valid signature rejected | Cryptographic fixture test |
| Forged approval | Altered signed approval rejected | Private key not compromised in test |
| Training interruption | Cancelled job denied; restart marks RUNNING interrupted | faults-6077c9a.json: observed optimizer progress, cancellation killed the actual process with return code -9; no candidate; subsequent real baseline inference over 12 rows passed |
| Corrupt checkpoint recovery | Modified completed output denied | No unsafe optimizer recovery |
| Failed export | No export registry entry on worker failure | Fixture failure injection |
| Isolation violation | No unsandboxed fallback; namespace/probe checks; classifier rejects unexpected IP traffic | network-6077c9a.json: complete v3 offline workflow, eleven probe windows, 163 externally rechecked traces and zero violations |
| Unauthorized documents | Adaptation role bound by server; denied/unknown queries stop before model; original gateway tests retained | Real baseline document answer and denial/abstention recorded in offline-6077c9a.json |
| Rollback after failure | Original pointer retained on failed activation; corrupt rollback refused | Real adapted-inference/rollback acceptance driver |
| Continual-learning regression | Routing must improve and reach at least 50%; factual score cannot fall; approved-source answer must pass | Real .001 trial lost factual performance; .0003 trial lost document behavior; both blocked before deployment. Narrow suite, not proof against general forgetting |

The syscall observer runs outside the isolated controller process tree. Probe markers remain application-generated labels, and the observer shares the runner's OS administration boundary. These results do not establish privileged-adversary resistance, independent signer custody or kernel attribution to an independently authenticated agent identity.

The 692a129 real cancellation harness failed because it expected primary-only progress, despite genuine mixed-dataset training. Its failed report is preserved. 3ce3cfe corrects the denominator and adds regression checks; run 43371870472 passed real cancellation and malformed-model rejection. Source 6077c9a additionally preserves baseline inference after cancellation and requires that real check in its latest run. A fixture/log-detector pass is not counted as successful real cancellation.
