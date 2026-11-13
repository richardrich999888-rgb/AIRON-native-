"""Frozen synthetic comparisons. No output substitutes or outcome tuning."""
import argparse
import hashlib
import json
import math
import os
import platform
import re
import resource
import statistics
import subprocess
import time
from pathlib import Path

from airon_runtime.core import Core
from airon_runtime.inference import generate_prompt
from airon_adaptation.integrity import write_json, file_hash
from provision import provision

PROTOCOL = Path(__file__).resolve().parents[1]/"fixtures/qualification/protocol.json"

def cpu_seconds():
    return sum(x.ru_utime+x.ru_stime for x in
               (resource.getrusage(resource.RUSAGE_SELF),resource.getrusage(resource.RUSAGE_CHILDREN)))

def wilson(ok,n):
    if not n:return None
    z=1.96;p=ok/n;d=1+z*z/n
    middle=(p+z*z/(2*n))/d
    radius=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [middle-radius,middle+radius]

def label(text,labels):
    # No semantic grading or answer repair. This policy is frozen before run 1.
    text=re.sub(r"\[end of text\]\s*$","",text).strip()
    return text if text in labels else "ABSTAINED"

def setup(args,folder,protocol):
    provision(folder,args.assets,args.aip_dir,args.bin_dir,args.llama,args.gguf,
              capability_ids=[f['capability']['id'] for f in protocol['families']])
    core=Core(folder);op=core.principal('operator');reviewer=core.principal('reviewer')
    preparation=[]
    for f in protocol['families']:
        start=time.monotonic();cpu=cpu_seconds()
        doc_id=f['capability']['evidence_refs'][0]
        core.call(op,'ingest',{'doc_id':doc_id,'title':f['id']+' synthetic policy',
                              'classification':'restricted','text':f['manual']})
        proposed=core.call(op,'capability',{'action':'propose','payload':{'capability':f['capability']}})
        h=proposed[0]['hash']
        cases=folder/(f['id']+'-development.jsonl')
        cases.write_text(''.join(json.dumps({**c,'label':c['expected']})+'\n' for c in f['development']))
        suite=folder/(f['id']+'-suite.json')
        subprocess.run([core.config['native']['cli']['path'],'suite-sign','--key',core.config['suite_key'],
            '--cases',str(cases),'--suite-id','p056-frozen-'+f['id'],'--tenant','synthetic-plant',
            '--task',f['id'],'--out',str(suite)],check=True,capture_output=True)
        result=core.call(op,'capability',{'action':'validate','payload':{'hash':h,'suite':json.loads(suite.read_text())}})
        if not result[0]['passed']:raise RuntimeError(json.dumps(result))
        for action in ('approve','activate'):
            core.call(reviewer,'capability',{'action':action,'payload':{'hash':h}})
        preparation.append({'family':f['id'],'wall_s':time.monotonic()-start,'cpu_s':cpu_seconds()-cpu,
                            'capability_hash':h,'validation':result,'scope':'Expert-authored typed artifact, no autonomous acquisition'})
    return core,preparation

def main(a):
    root=Path(a.root).resolve();root.mkdir(mode=0o700)
    frozen=json.loads(PROTOCOL.read_text())
    expected=PROTOCOL.with_suffix('.sha256').read_text().split()[0]
    if file_hash(PROTOCOL)!=expected:raise RuntimeError('Frozen protocol changed')
    result={'schema':'airon-p056-benchmark/v1','protocol_sha256':expected,
        'source_revision':os.environ.get('AIRON_SOURCE_COMMIT','WORKTREE'),
        'hardware':{'platform':platform.platform(),'affinity':sorted(os.sched_getaffinity(0)),
            'meminfo':Path('/proc/meminfo').read_text().splitlines()[0],'gpu':False},
        'model':{'path_name':Path(a.gguf).name,'sha256':file_hash(Path(a.gguf))},
        'caveats':[frozen['interpretation'],'Every inference starts a new model process; warm means filesystem cache, not a resident model.',
                   'RSS is process-tree plus controller sampled every 20ms; no cgroup-enforced 8GB host qualification.',
                   'B3 uses existing native runtime through its new process interface; this is not a rerun of v0.1/v0.2 research benchmarks.',
                   'B0 has no policy context; B1 receives authorized retrieval; B2 receives reviewed prompt skills. Different context is intentional.'],
        'B4':{'status':'SEPARATE_TASK_FAMILY','reason':'P0-052 adapter learns enterprise-routing labels, not these procedure labels; use genuine lifecycle report and do not compare accuracies across tasks.'},
        'rows':[],'summary':{},'status':'RUNNING'}
    path=Path(a.report);write_json(path,result)
    cores=[]
    try:
        unified,prep=setup(a,root/'unified',frozen);cores.append(unified)
        native,prep_native=setup(a,root/'native',frozen);cores.append(native)
        result['acquisition']={'unified':prep,'native':prep_native}
        families={f['id']:f for f in frozen['families']}
        for repeat in range(frozen['repeats']):
            for case in frozen['holdout']:
                f=families[case['family']]
                labels=[*f['capability']['outcomes'],'NOT_APPLICABLE','AMBIGUOUS']
                for baseline in ('B0','B1','B2','B3','B5'):
                    start=time.monotonic();cpu=cpu_seconds()
                    row={'baseline':baseline,'case_id':case['id'],'family':case['family'],'repeat':repeat,
                         'cache_phase':'first_pass' if repeat==0 else 'filesystem_warm',
                         'expected':case['expected'],'model_calls':1 if baseline in ('B0','B1','B2') else 0}
                    try:
                        if baseline in ('B3','B5'):
                            params={'capability_id':f['capability']['id'],'text':case['text']}
                            value=(native.native.call('execute',params,'operator') if baseline=='B3'
                                   else unified.call(unified.principal('operator'),'execute',params))
                            predicted=value['result']['outcome'].get('label','ABSTAINED')
                            row['model_calls']=value['result']['cost']['model_calls']
                        else:
                            system='Classify the synthetic report. Return exactly one label from: '+', '.join(labels)+'. No explanation.'
                            context=''
                            if baseline=='B1':
                                hits=unified.call(unified.principal('operator'),'search',{'question':f['id']})['result']['hits']
                                if len(hits)!=1:raise RuntimeError('Required authorized source unavailable')
                                context='Approved policy: '+hits[0]['text']+'\n'
                            if baseline=='B2':
                                context='Reviewed skill: '+f['manual']+'\n'
                                for example in f['development'][:2]:
                                    context+='Example: '+example['text']+' => '+example['expected']+'\n'
                            value=generate_prompt(unified.config['llama'],system,context+'Report: '+case['text'],max_tokens=frozen['max_tokens'])
                            predicted=label(value['text'],labels)
                        row.update({'predicted':predicted,'correct':predicted==case['expected'],
                                    'incorrect_positive':predicted not in ('ABSTAINED',case['expected']),
                                    'abstained':predicted=='ABSTAINED','result':value,'status':'MEASURED'})
                    except Exception as e:
                        row.update({'status':'FAILED','error':str(e),'correct':False,'incorrect_positive':False,'abstained':True})
                    row['wall_s']=time.monotonic()-start;row['cpu_s']=cpu_seconds()-cpu
                    result['rows'].append(row);write_json(path,result)
                print(f"P056_BENCH repeat={repeat} case={case['id']}",flush=True)
        for baseline in ('B0','B1','B2','B3','B5'):
            rows=[r for r in result['rows'] if r['baseline']==baseline]
            unique=[r for r in rows if r['repeat']==0]
            measured=[r for r in rows if r['status']=='MEASURED']
            times=sorted(r['wall_s'] for r in measured)
            result['summary'][baseline]={'tasks':len(unique),'observations':len(rows),'failed':len(rows)-len(measured),
                'correct_unique':sum(r['correct'] for r in unique),'accuracy_unique':sum(r['correct'] for r in unique)/len(unique),
                'accuracy_wilson_95':wilson(sum(r['correct'] for r in unique),len(unique)),
                'incorrect_positive_unique':sum(r['incorrect_positive'] for r in unique),
                'abstention_unique':sum(r['abstained'] for r in unique)/len(unique),
                'model_calls_per_task':statistics.mean(r['model_calls'] for r in rows),
                'cpu_s_mean':statistics.mean(r['cpu_s'] for r in rows),
                'latency_p50_s':statistics.median(times) if len(times)>=30 else None,
                'latency_p95_s':times[math.ceil(.95*len(times))-1] if len(times)>=30 else None,
                'peak_aggregate_rss_bytes':max((r['result']['measurement']['peak_aggregate_rss_bytes'] for r in measured),default=None),
                'ttft_s':None}
        result['status']='COMPLETED_WITH_FAILURES' if any(r['status']=='FAILED' for r in result['rows']) else 'COMPLETED'
        result['disk_bytes']=sum(p.stat().st_size for p in root.rglob('*') if p.is_file())
        result['evidence']=unified.call(unified.principal('reviewer'),'evidence',{})
    finally:
        for c in cores:c.close()
        write_json(path,result)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for arg in ('root','report','assets','aip-dir','bin-dir','llama','gguf'):p.add_argument('--'+arg,required=True)
    p.add_argument('--approve-synthetic-test-deployment',action='store_true',required=True)
    main(p.parse_args())
