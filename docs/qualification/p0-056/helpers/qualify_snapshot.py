"""Tamper checks against an actual public snapshot; no private signing keys."""
import argparse,copy,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
from airon_adaptation.evidence import verify_chain

p=argparse.ArgumentParser();p.add_argument('--snapshot',required=True);p.add_argument('--output',required=True);a=p.parse_args()
snapshot=Path(a.snapshot).resolve();data=json.loads(snapshot.read_text())
output=Path(a.output);output.mkdir(parents=True,exist_ok=True)
verifier=Path(__file__).with_name('verify_snapshot.py')
pins={'snapshot_sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),
      'source_revision':data['source_revision'],'native_revision':data['native_revision'],
      'stores':{name:{'public_key_hex':s['public_key_hex'],
          'head':verify_chain(s['records'],bytes.fromhex(s['public_key_hex']))['head']}
          for name,s in data['stores'].items()}}
pinfile=output/'trust-pins.json';pinfile.write_text(json.dumps(pins,indent=2)+'\n')
checks={}
mutations=[
    ('valid',None,True),
    ('wrong_key',lambda s:s['stores']['core'].update(public_key_hex='00'*32),False),
    ('truncated',lambda s:s['stores']['core']['records'].pop(),True),
    ('native_audit',lambda s:s['native'].update(audit_utf8=s['native']['audit_utf8']+'x'),False),
    ('capability',lambda s:s['native']['capabilities'].update({next(iter(s['native']['capabilities'])):'{}'}),False),
    ('signed_object',lambda s:s['stores']['core']['objects'][0]['sealed']['payload'].update(forged=True),False),
    ('empty_trust_pins',None,True),
]
with tempfile.TemporaryDirectory(prefix='airon-snapshot-check-') as temporary:
    temp=Path(temporary)
    for name,change,with_pins in mutations:
        value=copy.deepcopy(data)
        if change:change(value)
        path=snapshot if change is None else temp/(name+'.json')
        if change:path.write_text(json.dumps(value))
        command=[sys.executable,str(verifier),'--snapshot',str(path),'--report',str(temp/(name+'-result.json'))]
        if with_pins:
            trusted=pinfile
            if name=='empty_trust_pins':
                trusted=temp/'empty.json';trusted.write_text('{}')
            command+=['--trust-pins',str(trusted)]
        result=subprocess.run(command,capture_output=True,text=True)
        checks[name]={'exit':result.returncode,'expected':'PASS' if name=='valid' else 'REJECT',
            'passed':(result.returncode==0)==(name=='valid')}
        if name=='valid' and result.returncode==0:
            (output/'pinned-verification.json').write_text((temp/(name+'-result.json')).read_text())
report={'source_snapshot_revision':data['source_revision'],'native_revision':data['native_revision'],
        'verifier_sha256':hashlib.sha256(verifier.read_bytes()).hexdigest(),'checks':checks,
        'status':'PASS' if all(c['passed'] for c in checks.values()) else 'FAIL',
        'custody':'Test-generated pins, same administrator. Recipients must retain trusted pins separately; no independent observation claim.'}
(output/'snapshot-attacks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report));sys.exit(0 if report['status']=='PASS' else 1)
