"""Inference-only scale qualification; never implies training feasibility."""
import argparse
import json
import os
import platform
import resource
import statistics
import time
from pathlib import Path
from airon_runtime.inference import generate_prompt
from airon_adaptation.integrity import write_json,file_hash
from benchmark import label,wilson

BASE=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--provision',required=True);p.add_argument('--models',required=True);p.add_argument('--report',required=True);a=p.parse_args()
    config=json.loads(Path(a.provision).read_text())['llama'];protocol=json.loads((BASE/'fixtures/qualification/protocol.json').read_text())
    families={f['id']:f for f in protocol['families']}
    cases=[r for r in protocol['holdout'] if int(r['id'].rsplit('-',1)[1])<6]
    report={'schema':'airon-inference-scale/v1','source_revision':os.environ.get('AIRON_SOURCE_COMMIT'),
        'hardware':{'platform':platform.platform(),'affinity':sorted(os.sched_getaffinity(0)),'meminfo':Path('/proc/meminfo').read_text().splitlines()[0],'gpu':False},
        'protocol_sha256':file_hash(BASE/'fixtures/qualification/protocol.json'),
        'scope':'18 preselected cases across three families, two runs; inference only. New process per call; warm means filesystem cache. Same-author synthetic data.',
        'models':[]}
    for spec in json.loads((BASE/'scale-models.lock.json').read_text())['models']:
        result={'model':spec,'rows':[]};report['models'].append(result)
        path=Path(a.models)/spec['filename']
        if spec['status']!='APPROVED_FOR_SYNTHETIC_QUALIFICATION':
            result['status']=spec['status'];write_json(Path(a.report),report);continue
        if not path.is_file() or file_hash(path)!=spec['sha256']:
            result['status']='BLOCKED_MISSING_OR_UNAPPROVED_MODEL';write_json(Path(a.report),report);continue
        for repeat in range(2):
            for case in cases:
                f=families[case['family']];labels=[*f['capability']['outcomes'],'NOT_APPLICABLE','AMBIGUOUS']
                start=time.monotonic()
                try:
                    output=generate_prompt({'binary':config['binary'],'model':{'path':str(path.resolve()),'sha256':spec['sha256']}},
                        'Classify the synthetic report. Return exactly one label from: '+', '.join(labels)+'. No explanation.',
                        'Approved policy: '+f['manual']+'\nReport: '+case['text'],max_tokens=24)
                    predicted=label(output['text'],labels)
                    row={'case_id':case['id'],'repeat':repeat,'expected':case['expected'],'predicted':predicted,
                         'correct':predicted==case['expected'],'abstained':predicted=='ABSTAINED','output':output,'status':'MEASURED'}
                except Exception as e:row={'case_id':case['id'],'repeat':repeat,'status':'FAILED','error':str(e),'correct':False}
                row['wall_s']=time.monotonic()-start;result['rows'].append(row);write_json(Path(a.report),report)
        first=[r for r in result['rows'] if r['repeat']==0];measured=[r for r in result['rows'] if r['status']=='MEASURED']
        times=sorted(r['wall_s'] for r in measured)
        result['summary']={'correct_unique':sum(r['correct'] for r in first),'tasks':len(first),
            'wilson_95':wilson(sum(r['correct'] for r in first),len(first)),
            'latency_p50_s':statistics.median(times) if len(times)>=30 else None,
            'latency_p95_s':times[round(.95*len(times))-1] if len(times)>=30 else None,
            'peak_aggregate_rss_bytes':max((r['output']['measurement']['peak_aggregate_rss_bytes'] for r in measured),default=None),
            'training':'NOT_RUN','ttft_s':None}
        result['status']='COMPLETED' if len(measured)==len(result['rows']) else 'COMPLETED_WITH_FAILURES'
        write_json(Path(a.report),report);print(json.dumps({'model':spec['identifier'],'status':result['status'],'summary':result['summary']}),flush=True)
