"""Export synthetic signed state and native audit bytes without any private key."""
import argparse,json,sqlite3
from pathlib import Path
from airon_adaptation.integrity import write_json

p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--demo',required=True);p.add_argument('--output',required=True);a=p.parse_args()
root=Path(a.root);config=json.loads((root/'provision.json').read_text())
if config.get('synthetic_test_authorization') is not True:raise RuntimeError('Synthetic evidence export only')
demo=json.loads(Path(a.demo).read_text())
result={'schema':'airon-public-snapshot/v1','source_revision':demo['source_revision'],'stores':{},
        'native_revision':config['native']['source_revision'],'independent_execution':'CANNOT_PROVE'}
for name,folder in [('core','control'),('adaptation','adaptation')]:
    db=sqlite3.connect((root/folder/'state.db').resolve().as_uri()+'?mode=ro',uri=True)
    result['stores'][name]={'public_key_hex':demo['evidence'][name]['public_key_hex'],
        'objects':[{'id':r[0],'kind':r[1],'sealed':json.loads(r[2])} for r in db.execute('select id,kind,record from objects order by rowid')],
        'records':[json.loads(r[0]) for r in db.execute('select record from events order by seq')]}
    db.close()
native=Path(config['native_state'])
result['native']={'audit_utf8':(native/'audit.jsonl').read_text(),
    'capabilities':{p.name:p.read_text() for p in sorted((native/'capabilities').glob('*.json'))},
    'public_configuration':json.loads(Path(config['native']['config']['path']).read_text())}
write_json(Path(a.output),result)
