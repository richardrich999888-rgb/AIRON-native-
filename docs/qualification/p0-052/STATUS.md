# P0-052 — experimental integration in progress

Source audit performed on 13 November 2026. This branch is not qualified for deployment.

| Source | Inspected revision |
|---|---|
| AIRON base/main | 04a84e64fc2be36fe03fc73006c9a42285617a02 |
| Soup | af2f5d5000f7baec6386a72a6d16e82383eb5303 (0.77.2) |
| AIP main | 872dbf375838cff464eb019488c63d948015e9b8 |
| AIP P0-048 ref | 61dd73013d02ea7869de104d953f330098df1c32 |

The local execution workspace became unavailable during implementation. Initial PyTorch imports and two training-stack installation attempts exited 137. No OOM diagnosis is asserted: no kernel diagnostic was available. Soup core 0.77.2 and its light dependencies did install successfully. The installed CPU PyTorch version was requested as 2.9.1+cpu; a successful import was not observed.

Before the outage, unshare --user --map-root-user --net true exited zero. A direct bwrap --unshare-all probe failed with "loopback: Failed to create NETLINK_ROUTE socket: Operation not permitted". Running unshare outside bwrap without bwrap's --unshare-net produced no error in a subsequent command, but no complete workload was tested. This is not offline qualification.

Source was preserved through the GitHub API after execution became unavailable. All automated checks and experiments must be read from actual CI results; pending checks are not passes. Fixture checkpoints in tests are intentionally not valid trained models.

## Gates

| Gate | Status | Required evidence |
|---|---|---|
| M1 source qualification | PARTIAL | Source pin and API review done; resolved dependency licence inventory and redistribution review pending |
| M2 genuine Soup operations | PENDING | Execute adapter against the pinned installation |
| M3 real training | BLOCKED locally | Worker training result, changed tensors, loadable adapter |
| M4 model lifecycle | FIXTURE TESTS PENDING | Real baseline, candidate, evaluation, approval, active inference, rollback |
| M5 offline workflow | NOT QUALIFIED | Provisioned end-to-end workflow plus network and outbound-attempt evidence |
| M6 assurance | TESTS PENDING | Ed25519 application record verification with externally trusted public key; AIP/Sniffer Dog remain open |
| M7 investor demonstration | EXPERIMENTAL | Reproducible real run and recorded results, not fixture scores |

Do not use this status file as a substitute for executed acceptance evidence.
