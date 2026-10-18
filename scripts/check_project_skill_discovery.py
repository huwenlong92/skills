from pathlib import Path
import importlib.util, json, os, selectors, subprocess, tempfile, time
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
source=args.source.resolve()
spec=importlib.util.spec_from_file_location('manager',source/'skills/sdkit-skills/scripts/manager.py');manager=importlib.util.module_from_spec(spec);spec.loader.exec_module(manager)
run=Path(tempfile.mkdtemp(prefix='sdkit-native-discovery-')).resolve()
entries=manager.catalog()['skills'];pairs={'sdkit-go-core':'sdkit','sdkit-rust-core':'rust-sdcore','sdbase-go':'sdkitgo','sdbase-vab-admin':'vab-admin','sdbase-nuxtjs-portal':'nuxtjs'}
for entry in entries:
 parent=run/'independent'/entry['name'];parent.mkdir(parents=True)
 manager.install(entry['name'],parent)
 assert {p.name for p in parent.iterdir()}=={entry['name']}
 manager.install(entry['name'],parent,update=True)
 assert manager.manifest(parent/entry['name'])==manager.manifest(manager.source(entry['name']))
print('independent install/update:',len(entries),'passed',flush=True)
scopes={}
for label,names in [('primary',[e['name'] for e in entries if e['name'] not in pairs.values()]),('legacy',list(pairs.values()))]:
 cwd=run/label;parent=cwd/'.agents/skills';parent.mkdir(parents=True)
 subprocess.run(['git','init','-q',str(cwd)],check=True)
 for name in names:manager.install(name,parent)
 scopes[str(cwd)]=set(names)
home=run/'codex-home';home.mkdir()
env={k:v for k,v in os.environ.items() if k in ['PATH','HOME','USER','SHELL','TMPDIR','LANG','LC_ALL']};env['CODEX_HOME']=str(home);env['HOME']=str(run/'user-home');Path(env['HOME']).mkdir();env['DISABLE_TELEMETRY']='1'
global_script=source/'scripts/project_skill_global.py'
if global_script.exists():
 import sys;sys.path.insert(0,str(source/'scripts'));import project_skill_global
 (home/'AGENTS.md').write_bytes(project_skill_global.plan(b'# Synthetic acceptance rules\n'))
stderr=(run/'app-server-stderr.txt').open('w')
p=subprocess.Popen(['codex','app-server','--disable','apps','--disable','plugins','--stdio'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr,env=env,text=True,bufsize=1)
selector=selectors.DefaultSelector();selector.register(p.stdout,selectors.EVENT_READ)
def request(n,method,params):
 p.stdin.write(json.dumps({'id':n,'method':method,'params':params})+'\n');p.stdin.flush()
 deadline=time.monotonic()+25
 while time.monotonic()<deadline:
  if not selector.select(timeout=1):continue
  line=p.stdout.readline()
  if not line:raise RuntimeError('app-server exited')
  d=json.loads(line)
  if d.get('id')==n:
   if 'error' in d:raise RuntimeError(str(d['error']))
   return d['result']
 raise TimeoutError(method)
try:
 request(1,'initialize',{'clientInfo':{'name':'sdkit-bootstrap-acceptance','version':'1.0'},'capabilities':{'experimentalApi':True}})
 p.stdin.write(json.dumps({'method':'initialized'})+'\n');p.stdin.flush()
 response=request(2,'skills/list',{'cwds':list(scopes),'forceReload':True})
 (run/'skills-list-response.json').write_text(json.dumps(response,ensure_ascii=False,indent=2))
 print('response top-level keys',list(response),flush=True)
 results=[]
 for item in response.get('data',[]):
  cwd=item.get('cwd');expected=scopes.get(cwd)
  if expected is None:continue
  assert not item.get('errors'), item.get('errors')
  actual={s['name'] for s in item.get('skills',[]) if str(s.get('path','')).startswith(cwd+'/.agents/skills/')}
  assert actual==expected,(expected-actual,actual-expected,item.get('errors'))
  results.append({'scope':'primary' if len(expected)>5 else 'legacy','expected_count':len(expected),'found':sorted(actual),'errors':item.get('errors',[])})
 assert len(results)==2,results
 sanitized={'independent_install_update':len(entries),'native_discovery':results,'model_calls':0}
 (run/'sanitized-summary.json').write_text(json.dumps(sanitized,ensure_ascii=False,indent=2))
 args.output.write_text(json.dumps(sanitized,ensure_ascii=False,indent=2))
 print(json.dumps(sanitized,ensure_ascii=False),flush=True)
finally:
 p.terminate()
 try:p.wait(timeout=5)
 except subprocess.TimeoutExpired:p.kill();p.wait()
 stderr.close()
