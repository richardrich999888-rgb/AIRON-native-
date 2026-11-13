#!/usr/bin/env bash
# Root only for cgroup assignment. Drop to the invoking runner before execution.
set -euo pipefail
test "$EUID" -eq 0
: "${P056_UID:?Missing non-root runner UID}"
: "${P056_GID:?Missing runner GID}"
test "$P056_UID" -gt 0
test "$#" -gt 0
group=/sys/fs/cgroup/airon-p056
test "$(cat "$group/memory.max")" = 8589934592
test "$(cat "$group/cpu.max")" = '200000 100000'
printf '%s\n' "$$" > "$group/cgroup.procs"
test "$(cat /proc/self/cgroup)" = '0::/airon-p056'
cat /proc/self/cgroup > qualification/cgroup-membership.txt
cp "$group/memory.max" qualification/cgroup-memory-limit.txt
cp "$group/cpu.max" qualification/cgroup-cpu-limit.txt
exec setpriv --reuid "$P056_UID" --regid "$P056_GID" --init-groups "$@"
