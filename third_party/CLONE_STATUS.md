# P0-053 clone and restoration status

Recorded: 2026-11-12T23:57:29.028804+05:30 (Asia/Kolkata).

**Requested repositories: 19. Successfully fetched and pinned: 19. Failed or inaccessible: 0.**

All supplied repository URLs were usable. One metadata lookup for DVC timed out transiently; a subsequent Git remote check succeeded at the supplied `treeverse/dvc` URL. No replacement repository was needed.

| Project | Acquisition | Workspace commit verification |
|---|---|---|
| Soup | SUCCESS | `527314a446d52ffdeb2975c8dcd2c849a5d534b5` |
| Unsloth | SUCCESS | `d9827dc39670816e0cc6b94b94d4c3c0a4a25f79` |
| LLaMA-Factory | SUCCESS | `6d1059c727450a4f58e56ad204d01a71abad7781` |
| Axolotl | SUCCESS | `27bb23ce38373105027470b0d718f5ba87a01cb7` |
| Hugging Face PEFT | SUCCESS | `249e46b32eaad2068fdc62e696dcde14892406ae` |
| Hugging Face TRL | SUCCESS | `eb5a93fd86f3eb76c195d0c37521671a44a26ddb` |
| LitGPT | SUCCESS | `5341568a65e918a85cb284fac038de2157eebf3f` |
| llama.cpp | SUCCESS | `2a4daf0e08d6a9b6993ee0d4a9a3cfc35a6f405c` |
| MLX LM | SUCCESS | `56230fa02b8ff8330daf26dc95c28480423ed5fe` |
| Docling | SUCCESS | `336e9dde255237a3bf68abaea727d9782f7417a9` |
| Chroma | SUCCESS | `1a3ac2c7c623adbd03ed2508dc27b98cdf26016d` |
| Haystack | SUCCESS | `104a83f8799b1b8d9d18a88eb9a08305133aea2d` |
| LM Evaluation Harness | SUCCESS | `d6de81643928d653435c431bae19945d41d32520` |
| Evidently | SUCCESS | `34771fe41c08ca074d96a52aaf4a45cd640cbaf5` |
| MLflow | SUCCESS | `c980e95c1c349820b42031e1f9e6f34365fc57a3` |
| DVC | SUCCESS | `b59add99ee667f2b352cc1be337619f965fe3fea` |
| ModelScan | SUCCESS | `61fcec9c2a37c24c1fb12d84ede30fe248a364bd` |
| Sigstore Cosign | SUCCESS | `195ab76b789923862345f5fa9bfe3fac6c453927` |
| LangGraph | SUCCESS | `a054ed08dcee7ecc4105706d38c0b4aa0b3c3c32` |

One additional upstream-pinned MLflow skills submodule was restored recursively. Its exact SHA and licence are in the lock file.

## Verification

A temporary commit object was built from the staged `.gitmodules` and 19 gitlinks without advancing the AIRON research branch or changing `main`. A separate empty repository fetched that snapshot and checked it out detached; it had no pre-existing `.git/modules` object store. Submodules were then fetched from their public upstream URLs.

```bash
export GIT_LFS_SKIP_SMUDGE=1
git submodule update --init --recursive
```

Result: **PASS**, exit code **0**, at `2026-11-12T18:27:27.567926+00:00`. All **19** direct and **1** transitive submodules matched their pinned commits and tree hashes, with clean working trees. Licence/notice hashes matched in both workspaces.

Tested `.gitmodules` SHA-256: `b2fadd2713579cceb6fcad5816468b3d40e1805b377033ad7a5b2be556fe9d28`.

Tested direct gitlink-set SHA-256: `1b46b6e3e5f6e91a1f6bd06810b7d046b44242bad387b1b7e6a70f4da1b5acc6` (UTF-8 concatenation of sorted `path + NUL + SHA + LF` records).

These source references are unchanged in the final commit; the temporary snapshot omits only the subsequently generated inventory documents.

- All pre-existing AIRON files and object IDs match the base commit.
- The parent index contains exactly 19 mode-160000 submodule entries and four new text blobs: `.gitmodules` plus the three inventory files.
- Added text blobs were checked for credential/private-key patterns and size; no matches or files over 1 MiB.
- No dependency installation, model or dataset download, training, evaluation, upstream test, build or deployment was run.
- Source checkouts retain upstream fixtures/assets; these were not copied into the parent repository or executed.
- This validates acquisition/restoration only. It does not validate runtime compatibility, capability claims or production readiness.

## Restore and inspect

Use the commands in [MANIFEST.md](MANIFEST.md#restore-the-sources). Inspect exact source pins with `git submodule status --recursive`; no line should start with `-`, `+` or `U` after restoration.

Scope complete when the preservation branch and draft PR are published. No integration work is part of P0-053.
