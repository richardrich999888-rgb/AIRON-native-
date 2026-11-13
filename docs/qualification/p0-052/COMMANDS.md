# Executed commands and evidence locations

Commands below distinguish this workspace from the Linux Actions runner. The workflow file is the executable reference for dependency preparation, isolated installation, training, browser rehearsal and fault tests. A command's presence here is not a pass; STATUS.md and the exact run/report determine the observed result.

## Source inspection and delivery

The three repositories were cloned and inspected before integration. AIRON's base is 04a84e64fc2be36fe03fc73006c9a42285617a02; Soup is af2f5d5000f7baec6386a72a6d16e82383eb5303; AIP main is 872dbf375838cff464eb019488c63d948015e9b8. Source paths and scope are enumerated in UPSTREAM_AUDIT.md.

The implementation worktree is airon-p052-work. Source inspection included git status, git branch -a, git log, git rev-parse HEAD, rg/rg --files, Python/package manifests, actual training/loop/export/bundle code and tests. Changes are on codex/p0-052-airon-soup-offline-adaptation, with draft PR #2 targeting main. Branch updates used GitHub tree/commit/ref operations with an expected-head lease because the local git push credential was unavailable. No force-push or merge was performed.

## Executed locally on the implementation checkout

```sh
PYTHONPATH=../p052-test-deps ../.venv/bin/python -m pytest -q tests/integration/soup
../.venv/bin/python -m compileall -q services/model-adaptation
node --check services/model-adaptation/airon_adaptation/ui/app.js
git diff --check
git diff 04a84e64fc2be36fe03fc73006c9a42285617a02 --name-only
```

At tested runtime 6077c9a the CI suite passed 111 cases. After retaining the final reports, the unchanged suite passed 121 cases locally in 4.10 seconds: 80 controller/adversarial/transport/harness checks and 41 retained-report checks. Python compilation, JavaScript syntax and git diff checks also passed. The pytest suite contains fixture/controller tests and separately labelled retained real-evidence checks. Local model provisioning failed before download because the workspace proxy required socksio; this workspace also denies the AF_UNIX probe. No local real-training or isolation pass is claimed. The actual full experiment ran in Actions.

Downloaded Actions artifacts were independently checked in this workspace: compare ZIP SHA-256 against GitHub metadata, reject unsafe/duplicate/link archive paths, verify signed chains using retained key/head anchors, compare each candidate file with its signed manifest, inspect safetensors with safe_open, count the actual FP32 tensors and nonzero LoRA-B updates (120/60 at a297332; 420/210 at 692a129 and 6077c9a), and compare primary/offline adapter hashes. Original signed JSON bytes were preserved. adapter-artifact-a297332.json, adapter-artifact-692a129.json and adapter-artifact-6077c9a.json record those checks; the archive hash and source revision make their scope explicit.

The b4b9505 and a297332 network audits were independently rerun over all 173 downloaded raw trace files; the 692a129 and latest 6077c9a audits were each repeated over all 163 files. In each case, each trace hash matched their reports and the classifier again found eleven probe windows and no violations. This is separate artifact inspection, not an independent identity authority or customer-site attestation.

## Executed by the Actions contract job

```sh
python -m pytest -q tests/integration/soup --junitxml=contract-results.xml
python services/model-adaptation/scripts/verify_evidence.py \
  docs/qualification/p0-052/evidence/cpu-28daa9b.json \
  --trusted-public-key 29e42921f7e07fcf21babec55dbc38fcd0e1269f23bbb91eb9d5db138271addc \
  --expected-head 84b49c9b914d20fc596b4b4c776e22a6ff379f093c601e4291988e67eec691d6
```

In website/offline: python -m unittest test_server.py. At the repository root: npm --prefix website ci, npm test, npm run build. Latest full run 43373086529 passed 111 pytest checks in its contracts job, 15 original gateway tests, eight website cases and the build. These are separate suites; repeat runs are not additional independent test cases.

## Real CPU and offline execution

Read .github/workflows/p0-052.yml for exact environment preparation and commands, including:

- provision.py --approve-synthetic-data, with the pinned model manifest.
- probe_sandbox.py, invoking actual Soup dataset loading in the restricted worker.
- strace -ff -e trace=network around run_acceptance.py --approve-synthetic-test-deployment.
- prepare_wheelhouse.py, followed by a fresh venv installation under unshare --user --map-root-user --net with pip --no-index --no-cache-dir --require-hashes.
- strace around offline_acceptance.py, with a separately recorded parent network namespace.
- audit_network.py over every complete offline trace.
- check_console.py against the actual completed workspace, using Playwright Chromium.
- run_fault_acceptance.py --authorize-synthetic-fault-tests, requiring actual optimizer progress before cancellation and the safetensors parser's actual malformed-header rejection.
- collect_runtime.py for binary hashes, linker dependencies and selected OS package versions.

REPRODUCE.md contains copyable commands with operator-chosen absolute paths. Each run retains observed reports, raw traces, worker logs, exact wheels/notice inventory, the actual trained adapters and their manifests. Failed or skipped stages remain failures/incomplete. The scripted test reviewer is explicit test authorization and does not establish independent human approval.

## Read-only review without rerunning training

Use EVIDENCE_INDEX.json to verify retained report hashes and source-reviewed public anchors. Inspect EXPERIMENTS.md for rejected candidates and diagnostic failures. Review the real adapter artifacts from the linked Actions runs before loading them, with the approved base/model manifest. GitHub artifact retention is finite; retain an approved copy before expiry or reproduce from source. The repository deliberately does not include the private signing key, state database, complete model weights or a full OS image.

## Executed AIP byte-contract experiment

The separate workflow p0-052-aip-signature.yml checked out the exact AIP revision without modifying it, ran cargo +1.90.0 build --locked -p aip-crypto against its original manifest/lock, and compiled AIRON’s small Rust consumer with rustc --extern. Python prepared verified real-record bytes; an unshare network namespace then ran the actual AIP verification/tamper checks and Python verification of AIP signing. Runs 43361491548, 43362170890, 43371870508 and latest 43373086477 passed. See AIP_CONTRACT.md for counts and trust/licensing boundaries. No AIP source or linked binary is redistributed.

## Final evidence-only delivery

The last commit uses [skip ci] because only documentation and retained evidence changed. Runtime, fixtures, tests and workflow files are byte-identical to tested 6077c9a. Before committing, git diff --name-only HEAD was checked to contain only docs/ paths, the original website/package runtime was compared with inspected main, all 41 retained reports were verified by the 121-case local suite, and the latest derived benchmark timing/count/size fields were compared directly with original reports. Final Actions conclusions were success for runs 43373086529 and 43373086477. This is not a claim that Actions reran the documentation commit.
