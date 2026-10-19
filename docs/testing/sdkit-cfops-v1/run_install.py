#!/usr/bin/env python3
"""只向新建临时 HOME 安装/更新，并调用真实 Codex 原生 skills/list；不调用模型。"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import selectors
import shutil
import subprocess
import tempfile
import time


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();source=a.source.resolve()
    s=importlib.util.spec_from_file_location('manager',source/'skills/sdkit-skills/scripts/manager.py')
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    root=Path(tempfile.mkdtemp(prefix='sdkit-cfops-install-')).resolve()
    home=root/'home';parent=home/'.agents/skills';parent.mkdir(parents=True)
    codex=root/'codex-home';codex.mkdir()
    workspace=root/'workspace';workspace.mkdir()
    subprocess.run(['git','init','-q',str(workspace)],check=True)
    m.install('sdkit-cfops',parent)
    original=m.manifest(m.source('sdkit-cfops'))
    assert m.manifest(parent/'sdkit-cfops')==original
    m.install('sdkit-cfops',parent,update=True)
    assert m.manifest(parent/'sdkit-cfops')==original
    # 独立更新必须保护用户改动；仅在第二个临时安装副本测试。
    guarded=root/'guarded';guarded.mkdir();m.install('sdkit-cfops',guarded)
    entry=guarded/'sdkit-cfops/SKILL.md';entry.write_text(entry.read_text()+'\n本地修改\n')
    blocked=False
    try:m.install('sdkit-cfops',guarded,update=True)
    except ValueError:blocked=True
    assert blocked and entry.read_text().endswith('本地修改\n')
    env={'PATH':os.environ['PATH'],'HOME':str(home),'CODEX_HOME':str(codex),'TMPDIR':str(root),'LANG':'en_US.UTF-8','DISABLE_TELEMETRY':'1'}
    err=(root/'app-server.stderr').open('w')
    command=[shutil.which('codex'),'-c','cli_auth_credentials_store="file"','app-server','--disable','apps','--disable','plugins','--stdio']
    proc=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,cwd=workspace,env=env,text=True,bufsize=1)
    selector=selectors.DefaultSelector();selector.register(proc.stdout,selectors.EVENT_READ)
    def request(n,method,params):
        proc.stdin.write(json.dumps({'id':n,'method':method,'params':params})+'\n');proc.stdin.flush()
        end=time.monotonic()+25
        while time.monotonic()<end:
            if not selector.select(timeout=1):continue
            line=proc.stdout.readline()
            if not line:raise RuntimeError('app-server exited')
            data=json.loads(line)
            if data.get('id')==n:
                assert 'error' not in data,'app-server protocol error'
                return data['result']
        raise TimeoutError(method)
    try:
        request(1,'initialize',{'clientInfo':{'name':'sdkit-cfops-acceptance','version':'1.0'},'capabilities':{'experimentalApi':True}})
        proc.stdin.write(json.dumps({'method':'initialized'})+'\n');proc.stdin.flush()
        data=request(2,'skills/list',{'cwds':[str(workspace)],'forceReload':True})
        matches=[x for item in data.get('data',[]) for x in item.get('skills',[]) if x['name']=='sdkit-cfops']
        assert len(matches)==1
        assert Path(matches[0]['path']).resolve().is_relative_to(home)
        assert all(not item.get('errors') for item in data.get('data',[]))
        private_paths=[x for item in data.get('data',[]) for x in item.get('skills',[]) if not Path(x['path']).resolve().is_relative_to(root)]
        assert not private_paths,'发现宿主 Skill 泄漏，停止验收'
        result={'install':'PASS','update':'PASS','modified_copy_update_blocked':'PASS','manifest_match':True,
                'independent_skill':'sdkit-cfops','native_codex_skills_list':'PASS','discovered_once':True,
                'host_skills_leaked':False,'model_calls':0,'automatic_routing':'NOT_TESTED','credential_files_copied':False}
        a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
    finally:
        proc.terminate()
        try:proc.wait(timeout=5)
        except subprocess.TimeoutExpired:proc.kill();proc.wait()
        selector.close();err.close()


if __name__=='__main__':main()
