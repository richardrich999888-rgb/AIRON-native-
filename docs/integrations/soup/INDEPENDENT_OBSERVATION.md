# Independent observation: inspected contract and open gate

AIRON's current evidence level remains APPLICATION_SIGNED / independent_execution CANNOT_PROVE. The actual offline workflow has an external strace capture from the same Actions runner; its IP/DNS audit and downloaded trace recheck are useful observations within that runner's administration boundary. They are not Sniffer Dog attestations or independently authenticated agent attribution.

## Source inspected

The separately cloned AIP main remains at 872dbf375838cff464eb019488c63d948015e9b8. Its main checkout does not contain the newer observer crates. Targeted source inspection of immutable P0-048 revision 61dd73013d02ea7869de104d953f330098df1c32 covered:

- aip-standalone/aip-observe/src/lib.rs: separates unsigned probe batches from collector signatures, sensor health and continuity. Availability is explicit; missing observations must not become evidence of nonexecution.
- aip-standalone/aip-edge-observer/src/main.rs: the reference observer declares pidfd-anchored process polling and proc-net socket tables. It deliberately does not declare continuous kernel tracepoint coverage. Its separately held in-process key establishes a process boundary, not a separate host or administrator.
- validation/airi/observers/audit_observer.py: the Linux audit witness changes global audit state, needs a compatible privileged host and refuses an existing registered audit consumer. It is a cross-check, not an AIP authorization input.
- validation/external/auditd/STATUS.md: describes the distinction between audit syscall observation and Sniffer Dog's tracepoint path. Its historical test results are not AIRON execution evidence.

No proprietary observer code was copied, modified, linked into AIRON, redistributed or executed in this experiment. The separately executed raw-signature compatibility experiment is described in AIP_CONTRACT.md; it does not qualify these observation mechanisms.

## Observed implementation-workspace constraint

Read-only checks on 13 November 2026 found CapEff=0000000000000000, NoNewPrivs=1 and Seccomp=2. auditctl, bpftrace and bpftool were absent. perf_event_paranoid was 2, and neither standard tracefs/debugfs path exposed sched_process_exec's event ID. Rust/cargo was also unavailable locally. No global audit configuration was changed or claimed tested. These observations apply to this workspace, not every possible Actions/customer host.

The available polling reference cannot by itself qualify continuous training-process execution, model-file loads, filesystem writes and network activity. Integrating it without coverage/health and namespace/process-instance joins would create misleading assurance. The independent-execution gate therefore remains OPEN.

## Concrete next contract

An authorized testbed integration must bind the AIRON job and deployment IDs to the actual worker process instance (boot identity, PID namespace, start time/pidfd and cgroup where applicable), retain observer capability and loss/health intervals, compare model-read/output-write/network observations against the signed manifests, and verify separately trusted collector keys and continuity. Missing coverage must produce CANNOT_PROVE. The observer must not gain deployment authority or access to private training content merely to label a job.

This requires a separately administered compatible host/collector, an explicit production ownership/licensing decision and an executed integration contract. No production dependency on VANIAN is introduced by P0-052.
