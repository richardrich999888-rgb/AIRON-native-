"""P0-056 syscall policy. P0-052's 11-worker acceptance gate stays unchanged."""
import argparse,hashlib,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--expected-probes',required=True,type=int);p.add_argument('--report',required=True);a=p.parse_args()
prefix=Path(a.prefix);violations=[];allowed=[];files={};windows=0
for path in sorted(prefix.parent.glob(prefix.name+'.*')):
    files[path.name]=hashlib.sha256(path.read_bytes()).hexdigest();inside=False
    for number,line in enumerate(path.read_text().splitlines(),1):
        item={'file':path.name,'line':number,'syscall':line}
        if 'airon-isolation-probe-begin' in line:
            if inside:violations.append({**item,'reason':'Nested marker'})
            inside=True;windows+=1;continue
        if 'airon-isolation-probe-end' in line:
            if not inside:violations.append({**item,'reason':'Missing begin marker'})
            inside=False;continue
        if 'AF_INET' not in line and not (re.match(r'(sendto|sendmsg|sendmmsg)\(',line) and 'AF_UNIX' not in line and 'AF_NETLINK' not in line):continue
        if line.startswith('socket('):allowed.append({**item,'kind':'socket_creation_no_egress'});continue
        # Some dependency imports check local IPv6 support. This failed local
        # ephemeral bind neither connects nor transmits a packet.
        if (line.startswith('bind(') and 'AF_INET6' in line and 'htons(0)' in line and '"::1"' in line
                and '= -1 EADDRNOTAVAIL' in line):
            allowed.append({**item,'kind':'failed_loopback_capability_probe'});continue
        target=(('inet_addr("198.51.100.1")' in line and 'htons(443)' in line)
                or ('inet_addr("127.0.0.1")' in line and 'htons(11434)' in line) or 'htons(53)' in line)
        denied=bool(re.search(r'= -1 (ENETUNREACH|ECONNREFUSED|EHOSTUNREACH|EACCES|EPERM)',line))
        if inside and line.startswith('connect(') and target and denied:allowed.append({**item,'kind':'deliberate_failed_isolation_probe'})
        else:violations.append({**item,'reason':'Unexpected IP activity'})
    if inside:violations.append({'file':path.name,'reason':'Unclosed probe window'})
if not files or windows!=a.expected_probes:violations.append({'reason':'Worker probe coverage mismatch','expected':a.expected_probes,'observed':windows})
r={'schema':'airon-p056-network-policy/v1','passed':not violations,'expected_worker_probes':a.expected_probes,'observed_worker_probes':windows,
   'trace_sha256':files,'allowed':allowed,'violations':violations,'scope':'No unclassified IP connection or packet send in captured processes. OS namespace plus labelled application probes; not independent agent attribution.'}
Path(a.report).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'worker_probes':windows,'violations':violations}));raise SystemExit(0 if r['passed'] else 2)
