#!/usr/bin/env bash
# Root only for cgroup assignment. Drop to the invoking runner before execution.
set -euo pipefail
test "$EUID" -eq 0
: "${P056_UID:?Missing non-root runner UID}"
: "${P056_GID:?Missing runner GID}"
test "$P056_UID" -gt 0
test "$#" -gt 0
case "${P056_PROFILE:?Missing qualification profile}" in
  full) group=/sys/fs/cgroup/airon-p056; prefix=cgroup; quota='400000 100000';;
  minimum) group=/sys/fs/cgroup/airon-p056-minimum; prefix=minimum-cgroup; quota='200000 100000';;
  *) exit 2;;
esac
test "$(cat "$group/memory.max")" = 8589934592
test "$(cat "$group/cpu.max")" = "$quota"
printf '%s\n' "$$" > "$group/cgroup.procs"
test "$(cat /proc/self/cgroup)" = "0::/${group##*/}"
cat /proc/self/cgroup > "qualification/$prefix-membership.txt"
cp "$group/memory.max" "qualification/$prefix-memory-limit.txt"
cp "$group/cpu.max" "qualification/$prefix-cpu-limit.txt"
exec setpriv --reuid "$P056_UID" --regid "$P056_GID" --init-groups "$@"
