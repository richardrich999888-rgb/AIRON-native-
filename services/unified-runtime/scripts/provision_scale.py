"""Explicit online acquisition of hash-pinned qualification models only."""
from pathlib import Path
import argparse
import urllib.request,hashlib,json,time,shutil
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--approve-download',action='store_true',required=True);a=p.parse_args()
root=Path(a.output).resolve();root.mkdir(parents=True,exist_ok=True)
pins=json.loads((Path(__file__).resolve().parents[1]/'scale-models.lock.json').read_text())
for model in pins['models']:
 if model['status']!='APPROVED_FOR_SYNTHETIC_QUALIFICATION':continue
 path=root/model['filename']
 if path.exists() and hashlib.file_digest(path.open('rb'),'sha256').hexdigest()==model['sha256']:continue
 assert shutil.disk_usage(root).free>model['size_bytes']+1024**3
 url='https://huggingface.co/'+model['identifier']+'/resolve/'+model['revision']+'/'+model['filename']+'?download=true'
 with urllib.request.urlopen(url,timeout=120) as src,path.with_suffix('.part').open('wb') as dest:
  shutil.copyfileobj(src,dest)
 part=path.with_suffix('.part')
 assert part.stat().st_size==model['size_bytes']
 assert hashlib.file_digest(part.open('rb'),'sha256').hexdigest()==model['sha256']
 part.rename(path)
 print(json.dumps({'filename':path.name,'sha256':model['sha256'],'bytes':path.stat().st_size,'verified':True}),flush=True)
