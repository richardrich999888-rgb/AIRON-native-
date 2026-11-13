"""Check actual installed wheels, not a source checkout on PYTHONPATH."""
import argparse
import json
import os
import platform
import sys
from pathlib import Path
import airon_runtime
import airon_adaptation
from airon_runtime.core import Core
from airon_adaptation.integrity import write_json

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--report',required=True)
    p.add_argument('--verify-adaptation',action='store_true');a=p.parse_args()
    r={'schema':'airon-offline-install/v1','source_revision':os.environ.get('AIRON_SOURCE_COMMIT'),
       'platform':platform.platform(),'prefix':sys.prefix,'checks':{},'status':'FAILED'}
    try:
        for package in (airon_runtime,airon_adaptation):
            path=Path(package.__file__).resolve()
            assert path.is_relative_to(Path(sys.prefix).resolve()),'Import came from outside fresh venv'
            r['checks'][package.__name__]=str(path)
        assert len(Path('/proc/net/route').read_text().splitlines())==1,'External route exists'
        c=Core(a.root)
        try:
            actor=c.principal('operator')
            result=c.call(actor,'execute',{'capability_id':'airon.cooling.inspection','text':'cooling hours 210 vibration 2'})
            assert result['result']['cost']['model_calls']==0 and result['result']['outcome']['label']=='INSPECT'
            r['checks']['capability']=result
            r['checks']['docling']=c.call(actor,'ingest',{'doc_id':'package-smoke','title':'Offline package verification',
                'text':'Package verification uses fictional commissioning records.','classification':'restricted'})
            assert c.call(actor,'search',{'question':'commissioning'})['result']['hits']
            c.call(actor,'delete',{'doc_id':'package-smoke'})
            assert not c.call(actor,'search',{'question':'commissioning'})['result']['hits']
            r['checks']['retrieval_and_delete']=True
            answer=c.call(actor,'ask',{'question':'When should we inspect the cooling assembly?','backend':'llama'})
            assert answer['outcome']=='ANSWERED' and answer['model_calls']==1
            r['checks']['inference']=answer
            if a.verify_adaptation:
                r['checks']['adaptation']=c.call(actor,'adapt',{'operation':'infer','params':{'dataset_id':c.config['dataset_id']}})
            r['checks']['evidence']=c.call(c.principal('reviewer'),'evidence',{})
        finally:c.close()
        r['status']='PASS'
    except Exception as e:r['error']=str(e);raise
    finally:write_json(Path(a.report),r)
