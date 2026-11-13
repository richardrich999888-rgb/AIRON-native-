"""Require positive kernel accounting and the exact declared resource profile."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--cpus',type=int,choices=[2,4],required=True)
p.add_argument('--membership',required=True);p.add_argument('--report',required=True);a=p.parse_args()
prefix=Path(a.prefix)
read=lambda suffix:Path(str(prefix)+'-'+suffix+'.txt').read_text().strip()
peak=int(read('memory-peak'));cpu=dict(line.split() for line in read('cpu-stat').splitlines())
events=dict(line.split() for line in read('memory-events').splitlines())
limit=int(read('memory-limit'));quota=read('cpu-limit');membership=read('membership')
assert limit==8589934592 and 0 < peak <= limit,'Missing or out-of-bounds cgroup accounting'
assert quota==f'{a.cpus*100000} 100000','Unexpected CPU limit'
assert int(cpu['usage_usec'])>0,'No measured workload'
assert int(events['oom_kill'])==0,'Cgroup OOM killed a process'
assert membership==a.membership,'Unexpected cgroup membership'
result={'memory_peak_bytes':peak,'cpu':cpu,'events':events,'memory_limit_bytes':limit,
        'cpu_quota':quota,'membership':membership,'status':'PASS'}
Path(a.report).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
