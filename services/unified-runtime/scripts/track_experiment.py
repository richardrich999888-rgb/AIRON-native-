"""Optional local MLflow projection; signed AIRON evidence remains authoritative."""
import argparse
import json
import os
from pathlib import Path
os.environ['MLFLOW_DISABLE_TELEMETRY']='true'
os.environ['DO_NOT_TRACK']='1'
os.environ['MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING']='false'
from airon_adaptation.evidence import verify_chain
from airon_adaptation.integrity import file_hash,write_json

def export(report,output):
    # Only a local SQLite backend and local artifacts are accepted. No server URI.
    output=Path(output).resolve();output.mkdir(mode=0o700,parents=True,exist_ok=True)
    report=Path(report).resolve();data=json.loads(report.read_text())
    if not data.get('evidence'):raise ValueError('Signed AIRON evidence required')
    verification={k:verify_chain(v['records'],bytes.fromhex(v['public_key_hex']),v['verification']['head'])
                  for k,v in data['evidence'].items()}
    from mlflow import MlflowClient
    from mlflow.telemetry.utils import is_telemetry_disabled
    assert is_telemetry_disabled()
    client=MlflowClient(tracking_uri='sqlite:///'+str(output/'experiments.sqlite3'))
    experiment=client.get_experiment_by_name('AIR​ON P0-056')
    experiment_id=experiment.experiment_id if experiment else client.create_experiment('AIR​ON P0-056',artifact_location=(output/'artifacts').as_uri())
    run=client.create_run(experiment_id,tags={'airon.record.authority':'application-signed-evidence',
        'airon.independent_execution':'CANNOT_PROVE','airon.source_revision':data.get('source_revision') or 'UNRECORDED',
        'airon.report.sha256':file_hash(report),'airon.report.schema':data['schema']})
    for baseline,metrics in data.get('summary',{}).items():
        for key,value in metrics.items():
            if isinstance(value,(float,int)) and not isinstance(value,bool):client.log_metric(run.info.run_id,baseline+'.'+key,value)
    for key,gate in data.get('gates',{}).items():
        client.log_param(run.info.run_id,key,gate['status'])
        if gate.get('wall_s') is not None:client.log_metric(run.info.run_id,key+'.wall_s',gate['wall_s'])
    client.log_artifact(run.info.run_id,str(report))
    client.set_terminated(run.info.run_id)
    restored=Path(client.download_artifacts(run.info.run_id,report.name))
    assert file_hash(restored)==file_hash(report)
    manifest={'schema':'airon-mlflow-projection/v1','run_id':run.info.run_id,'tracking_backend':'local SQLite',
        'report_sha256':file_hash(report),'restored_artifact_sha256':file_hash(restored),'verified_chains':verification,
        'telemetry_disabled':True,'security_authority':'Original signed AIRON evidence; MLflow cannot approve or deploy',
        'source_revision':data.get('source_revision')}
    write_json(output/'projection.json',manifest)
    print(json.dumps(manifest))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--report',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();export(a.report,a.output)
