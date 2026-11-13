"""Offline signature, state and native artifact verification; no application keys."""
import argparse,hashlib,json
from pathlib import Path
from airon_adaptation.evidence import verify_chain,verify
from airon_adaptation.integrity import write_json

p=argparse.ArgumentParser();p.add_argument('--snapshot',required=True);p.add_argument('--report',required=True);a=p.parse_args()
snapshot=json.loads(Path(a.snapshot).read_text());result={'schema':'airon-public-snapshot-check/v1','source_revision':snapshot['source_revision'],'stores':{}}
decoded={}
for name,store in snapshot['stores'].items():
    key=bytes.fromhex(store['public_key_hex'])
    result['stores'][name]=verify_chain(store['records'],key)
    decoded[name]=[(row['kind'],verify(row['sealed'],key)) for row in store['objects']]
    result['stores'][name]['verified_objects']=len(decoded[name])
anchors=[v for k,v in decoded['core'] if k=='anchor'];caps=[v for k,v in decoded['core'] if k=='capanchor']
assert anchors and caps,'Missing signed native anchors'
sha=lambda text:hashlib.sha256(text.encode()).hexdigest()
assert anchors[-1]['sha256']==sha(snapshot['native']['audit_utf8']),'Native audit substitution'
assert caps[-1]['manifest']=={k:sha(v) for k,v in snapshot['native']['capabilities'].items()},'Native capability substitution'
result.update(status='PASS',native_artifacts_match_signed_anchors=True,
    trust_scope='Public keys and latest heads must be independently pinned by the recipient to resist complete history replacement; this does not prove independently observed execution')
write_json(Path(a.report),result);print(json.dumps(result))
