import os,sys,subprocess,json,time,urllib.request,urllib.error,argparse,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
args=argparse.ArgumentParser();args.add_argument('--root',required=True);args.add_argument('--output',required=True);a=args.parse_args()
root=Path(a.output).resolve();root.mkdir(exist_ok=True,parents=True);repo=Path(__file__).resolve().parents[3]
env={**os.environ,'PYTHONPATH':str(repo/'services/unified-runtime')+':'+str(repo/'services/model-adaptation')}
p=subprocess.Popen([sys.executable,'-m','airon_runtime.server','--root',str(Path(a.root).resolve()),'--port','8767'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
report={'schema':'airon-console-qa/v1','source_revision':os.environ.get('AIRON_SOURCE_COMMIT'),'checks':{},'browser_errors':[]}
try:
 tokens={}
 while len(tokens)<4:
  line=p.stdout.readline()
  if not line:raise RuntimeError(p.stderr.read())
  if ' token: ' in line:
   actor,token=line.strip().split(' token: ');tokens[actor]=token
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path=(shutil.which("google-chrome") or shutil.which("chromium")),args=["--no-sandbox"])
  page=browser.new_page(viewport={'width':1440,'height':1100})
  page.on('pageerror',lambda e:report['browser_errors'].append(str(e)))
  page.goto('http://127.0.0.1:8767/')
  page.locator('#token').fill(tokens['operator']);page.locator('#connect').click()
  page.wait_for_function("document.querySelector('#state').textContent==='Connected to local runtime'")
  assert 'maintenance' in page.locator('#documents').inner_text().lower()
  page.locator('#route').select_option('execute');page.locator('#question').fill('cooling hours 210 vibration 2');page.locator('#ask').click()
  page.wait_for_function("document.querySelector('#answer').textContent.includes('INSPECT')")
  assert '0 model calls' in page.locator('#result-route').inner_text()
  report['checks']['real_procedure']=True
  page.locator('#token').fill('');page.screenshot(path=str(root/'ui-desktop.png'),full_page=True)
  page.locator('#token').fill(tokens['viewer']);page.locator('#connect').click()
  page.wait_for_function("document.querySelector('#identity').textContent.startsWith('viewer')")
  assert page.locator('#documents').inner_text()=='None registered.'
  report['checks']['lower_clearance_view']=True
  page.set_viewport_size({'width':390,'height':844});page.locator('#token').fill('');page.screenshot(path=str(root/'ui-mobile.png'),full_page=True)
  assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
  report['checks']['mobile_no_overflow']=True
  browser.close()
 for name,headers in [('anonymous',{}),('hostile_origin',{'Authorization':'Bearer '+tokens['operator'],'Origin':'https://attacker.invalid'})]:
  request=urllib.request.Request('http://127.0.0.1:8767/api',data=json.dumps({'operation':'status','params':{}}).encode(),headers={'Content-Type':'application/json',**headers})
  try:urllib.request.urlopen(request);raise AssertionError('Unauthorized HTTP operation accepted')
  except urllib.error.HTTPError as e:assert e.code==400;report['checks'][name]=True
 assert not report['browser_errors']
 report['status']='PASS'
finally:
 p.terminate();p.wait(timeout=10);(root/'ui-qa.json').write_text(json.dumps(report,indent=2)+'\n')
