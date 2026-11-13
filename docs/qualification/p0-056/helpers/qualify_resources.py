"""Exercise real worker exhaustion and cleanup with bounded synthetic processes."""
import argparse,json,os,platform,sys,time
from pathlib import Path
import psutil
from airon_runtime.process import run
from airon_adaptation.integrity import Rejected

p=argparse.ArgumentParser();p.add_argument('--report',required=True);a=p.parse_args()
cases=[
    ('aggregate_memory','import time; x=bytearray(512*1024*1024); time.sleep(10)',{'timeout':15,'max_ram':128*1024**2},'Aggregate child memory policy exceeded'),
    ('deadline','while True: pass',{'timeout':1},'Child deadline exceeded'),
    ('output_limit','import sys; sys.stdout.buffer.write(b"x"*(16*1024**2))',{'timeout':15},'Child failed'),
]
checks={}
for name,code,options,expected in cases:
    start=time.monotonic();error=None
    try:run([sys.executable,'-c',code],**options)
    except Rejected as exc:error=str(exc)
    remaining=[child.pid for child in psutil.Process().children(recursive=True) if child.is_running()]
    checks[name]={'rejected':error is not None,'reason':error,'wall_s':time.monotonic()-start,
                  'remaining_children':remaining,'passed':error is not None and expected in error and not remaining}
healthy=run([sys.executable,'-c','print("healthy after rejection")'],timeout=15)
checks['recovery']={'passed':healthy['stdout'].strip()=='healthy after rejection','measurement':healthy['measurement']}
report={'source_revision':os.environ.get('AIRON_SOURCE_COMMIT'),'hardware':{'platform':platform.platform(),'affinity':sorted(os.sched_getaffinity(0)),
        'meminfo':Path('/proc/meminfo').read_text().splitlines()[0],'gpu':False},'checks':checks,
        'status':'PASS' if all(c['passed'] for c in checks.values()) else 'FAIL',
        'scope':'Actual sampled-RSS rejection, process deadline, output-size limit and child cleanup. Not a full-disk or kernel cgroup exhaustion test.'}
Path(a.report).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));sys.exit(0 if report['status']=='PASS' else 1)
