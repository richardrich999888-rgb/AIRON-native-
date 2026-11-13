"""LM Evaluation Harness with the frozen local task and real llama.cpp backend.

This verifies the harness integration, not general benchmark competence. It
intentionally has no remote dataset loader, score cache or fabricated logits.
"""
import argparse
import json
import os
import re
from pathlib import Path
for k in ('HF_HUB_OFFLINE','HF_DATASETS_OFFLINE','TRANSFORMERS_OFFLINE','HF_HUB_DISABLE_TELEMETRY','DO_NOT_TRACK'):
    os.environ[k]='1'
from lm_eval.api.model import LM
from lm_eval.api.task import Task
from lm_eval.api.instance import Instance
from lm_eval.api.metrics import mean
from lm_eval.evaluator import evaluate
from airon_runtime.inference import generate_prompt
from airon_adaptation.integrity import file_hash,write_json

PROTOCOL=Path(__file__).resolve().parents[1]/'fixtures/qualification/protocol.json'

class LocalModel(LM):
    def __init__(self,config):super().__init__();self.config=config;self.raw=[]
    def loglikelihood(self,requests):raise NotImplementedError('Not qualified: backend does not expose logits')
    def loglikelihood_rolling(self,requests):raise NotImplementedError('Not qualified: backend does not expose logits')
    def generate_until(self,requests):
        result=[]
        for r in requests:
            context,options=r.args
            output=generate_prompt(self.config,'Classify the synthetic report. Return exactly one of its listed labels. No explanation.',context,max_tokens=24)
            self.raw.append(output)
            # Remove only the CLI end-of-text marker, not a wrong model answer.
            result.append(re.sub(r'\[end of text\]\s*$','',output['text']).strip())
        return result

class LocalTask(Task):
    VERSION=1
    OUTPUT_TYPE='generate_until'
    def __init__(self,protocol):
        self.protocol=protocol;self.families={f['id']:f for f in protocol['families']}
        super().__init__(config={'task':'airon_p056_synthetic','output_type':'generate_until','num_fewshot':0})
    def download(self,*args,**kwargs):pass # Dataset is the immutable local protocol, no HF loader.
    def has_training_docs(self):return False
    def has_validation_docs(self):return False
    def has_test_docs(self):return True
    def test_docs(self):return self.protocol['holdout']
    def doc_to_text(self,doc):
        f=self.families[doc['family']]
        labels=[*f['capability']['outcomes'],'NOT_APPLICABLE','AMBIGUOUS']
        return 'Labels: '+', '.join(labels)+'.\nApproved policy: '+f['manual']+'\nReport: '+doc['text']
    def doc_to_target(self,doc):return doc['expected']
    def construct_requests(self,doc,ctx,**kwargs):
        return Instance(request_type='generate_until',doc=doc,arguments=(ctx,{'until':['\n'],'max_gen_toks':24}),idx=0,
                        metadata=kwargs.get('metadata',(None,None,None)))
    def process_results(self,doc,results):return {'exact_match':float(results[0]==doc['expected'])}
    def aggregation(self):return {'exact_match':mean}
    def higher_is_better(self):return {'exact_match':True}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--report',required=True);a=p.parse_args()
    assert file_hash(PROTOCOL)==PROTOCOL.with_suffix('.sha256').read_text().split()[0]
    config=json.loads((Path(a.root)/'provision.json').read_text())
    model=LocalModel(config['llama']);task=LocalTask(json.loads(PROTOCOL.read_text()));task.set_fewshot_seed(56)
    results=evaluate(model,{'airon_p056_synthetic':task},bootstrap_iters=0,log_samples=True)
    write_json(Path(a.report),{'schema':'airon-lm-harness/v1','protocol_sha256':file_hash(PROTOCOL),
        'source_revision':os.environ.get('AIRON_SOURCE_COMMIT'),'results':results,'raw_generations':model.raw,
        'scope':'Real generation on the frozen local synthetic task; not a public standard benchmark score'})
