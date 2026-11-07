import {mkdirSync,copyFileSync,writeFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {resolve} from 'node:path';
import {documents} from '../lib/demo-engine.ts';
const build=spawnSync(process.execPath,[resolve('node_modules/vite/bin/vite.js'),'build','--config','offline/vite.config.ts'],{stdio:'inherit'});
if(build.status!==0)process.exit(build.status??1);
mkdirSync('outputs/offline',{recursive:true});
for(const file of ['server.py','README.md','test_server.py'])copyFileSync('offline/'+file,'outputs/offline/'+file);
writeFileSync('offline/documents.json',JSON.stringify(documents,null,2));
copyFileSync('offline/documents.json','outputs/offline/documents.json');
copyFileSync('public/syntriass-logo.jpeg','outputs/offline/ui/syntriass-logo.jpeg');
const zip=spawnSync('python3',['-c',`import pathlib,zipfile
root=pathlib.Path('outputs/offline')
with zipfile.ZipFile('public/airon-offline-kit.zip','w',zipfile.ZIP_DEFLATED) as archive:
 for file in sorted(root.rglob('*')):
  if file.is_file():archive.write(file,pathlib.Path('airon-offline-kit')/file.relative_to(root))
print('Offline kit packaged:', pathlib.Path('public/airon-offline-kit.zip').stat().st_size, 'bytes')`],{stdio:'inherit'});
if(zip.status!==0)process.exit(zip.status??1);
