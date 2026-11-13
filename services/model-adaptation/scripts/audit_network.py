"""Fail on IP activity outside labelled isolation probes; archive every trace digest."""
import argparse
import json
import re
from pathlib import Path
from airon_adaptation.integrity import file_hash, write_json


def classify(paths):
    violations, allowed, hashes, windows = [], [], {}, 0
    for path in sorted(paths):
        hashes[path.name] = {"sha256": file_hash(path), "bytes": path.stat().st_size}
        inside = False
        for number, line in enumerate(path.read_text().splitlines(), 1):
            if "airon-isolation-probe-begin" in line:
                if inside:
                    violations.append({"file": path.name, "line": number, "reason": "nested marker"})
                inside = True
                windows += 1
                continue
            if "airon-isolation-probe-end" in line:
                if not inside:
                    violations.append({"file": path.name, "line": number, "reason": "unmatched end"})
                inside = False
                continue
            is_ip = "AF_INET" in line
            send_without_address = re.match(r"(sendto|sendmsg|sendmmsg)\(", line) and not any(
                family in line for family in ("AF_UNIX", "AF_NETLINK", "AF_INET"))
            if not is_ip and not send_without_address:
                continue
            # Creating an IP socket is logged but is not an egress attempt.
            if line.startswith("socket("):
                allowed.append({"file": path.name, "line": number, "kind": "socket_creation", "detail": line})
                continue
            expected_target = (('inet_addr("198.51.100.1")' in line and "htons(443)" in line)
                               or ('inet_addr("127.0.0.1")' in line and "htons(11434)" in line)
                               or "htons(53)" in line)
            failed = bool(re.search(r"= -1 (ENETUNREACH|ECONNREFUSED|EHOSTUNREACH|EACCES|EPERM)", line))
            if inside and line.startswith("connect(") and expected_target and failed:
                allowed.append({"file": path.name, "line": number, "kind": "deliberate_failed_probe", "detail": line})
            else:
                violations.append({"file": path.name, "line": number, "reason": "unclassified IP activity", "detail": line})
        if inside:
            violations.append({"file": path.name, "reason": "unterminated probe window"})
    if not hashes or windows < 11:
        violations.append({"reason": "Missing trace files or complete controller/worker probe coverage", "windows": windows})
    return {"schema": "airon-syscall-audit/v1", "passed": not violations, "probe_windows": windows,
            "traces": hashes, "allowed": allowed, "violations": violations,
            "boundary": "strace outside the controller namespace; markers label deliberate probes, not independent agent attribution"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    prefix = Path(args.prefix)
    result = classify(prefix.parent.glob(prefix.name+".*"))
    write_json(args.report, result)
    print("NETWORK_AUDIT="+json.dumps(result))
    raise SystemExit(0 if result["passed"] else 2)


if __name__ == "__main__":
    main()
