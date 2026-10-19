#!/usr/bin/env python3
"""仅在 macOS 隔离临时项目执行已有 Wrangler；禁止外网，Preview 仅放行 loopback。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wrangler', type=Path, required=True, help='已安装 wrangler 包目录，只读复用')
    parser.add_argument('--output', type=Path, required=True, help='脱敏 JSON 输出路径')
    args = parser.parse_args()
    dependency = args.wrangler.resolve()
    package = json.loads((dependency/'package.json').read_text())
    assert package['name'] == 'wrangler'
    version = package['version']
    root = Path(tempfile.mkdtemp(prefix='sdkit-cfops-real-cli-')).resolve()
    # 复制本地 pnpm 依赖闭包，保留内部相对布局；禁止 CLI 物理路径落回业务项目。
    original = dependency
    store = next((p for p in dependency.parents if p.name == '.pnpm'), None)
    assert store is not None, '当前夹具仅支持已安装 pnpm 依赖闭包；禁止退回在线安装'
    cloned = root/'dependencies/.pnpm'
    pending = [dependency.relative_to(store).parts[0]]
    copied = set()
    while pending:
        name = pending.pop()
        if name in copied: continue
        copied.add(name)
        src, dst = store/name, cloned/name
        for base_dir, dirs, files in os.walk(src):
            for item in [*dirs,*files]:
                link = Path(base_dir)/item
                if link.is_symlink():
                    target = link.resolve()
                    assert target.is_relative_to(store), '依赖指向闭包外，停止'
                    pending.append(target.relative_to(store).parts[0])
        shutil.copytree(src,dst,symlinks=True)
    for base_dir, dirs, files in os.walk(cloned):
        for item in [*dirs,*files]:
            link=Path(base_dir)/item
            if link.is_symlink():
                source_link=store/link.relative_to(cloned)
                target=cloned/source_link.resolve().relative_to(store)
                link.unlink();link.symlink_to(os.path.relpath(target,link.parent))
    dependency = cloned/original.relative_to(store)
    home = root/'home'; home.mkdir()
    node = shutil.which('node')
    assert node and shutil.which('sandbox-exec'), '需要 node 与 macOS sandbox-exec，不允许降级为无隔离运行'
    env = {'PATH':os.environ['PATH'], 'HOME':str(home), 'XDG_CONFIG_HOME':str(home/'.config'),
           'TMPDIR':str(root), 'CI':'true', 'NO_COLOR':'1', 'WRANGLER_SEND_METRICS':'false'}
    base = '(version 1)\n(deny default)\n(allow process*)\n(allow signal (target same-sandbox))\n(allow file-read*)\n(allow sysctl-read)\n(allow mach-lookup)\n(allow ipc-posix*)\n'
    base += '(allow file-write* (subpath '+json.dumps(str(root))+') (literal "/dev/null"))\n'
    # HOME/XDG 不依赖真实配置；额外拒绝真实用户凭据目录读取。
    for name in ['.codex','.config','.wrangler','.cloudflare','.aws','.ssh','.agents']:
        base += '(deny file-read* (subpath '+json.dumps(str(Path.home()/name))+'))\n'
    base += '(deny file-read* (subpath '+json.dumps(str(store.parent.parent))+'))\n'
    offline = root/'offline.sb'; offline.write_text(base)
    local = root/'local.sb'; local.write_text(base+'(allow network* (local ip "localhost:*") (remote ip "localhost:*"))\n')
    cli = [node, str(dependency/'bin/wrangler.js')]
    results = []

    def run(label, directory, command, required=(), expected_code=0, category='real-wrangler-offline'):
        p = subprocess.run(['sandbox-exec','-f',str(offline),*command],cwd=directory,env=env,text=True,capture_output=True,timeout=45)
        text = p.stdout+p.stderr
        (root/(label+'.log')).write_text(text)
        results.append({'id':label, 'class':category, 'exit_code':p.returncode,
                        'status':'PASS' if p.returncode==expected_code and all(s in text for s in required) else 'FAIL',
                        'expected_markers':list(required)})
        return text

    for label, kind in [('pages-static','static'),('pages-nuxt-shape','ssr'),('worker','worker')]:
        p = root/label; p.mkdir(); (p/'node_modules').mkdir()
        (p/'node_modules/wrangler').symlink_to(dependency, target_is_directory=True)
        (p/'package.json').write_text(json.dumps({'private':True,'devDependencies':{'wrangler':version}}))
        (p/'dependency-lock.json').write_text(json.dumps({'version':version,'package_sha256':hashlib.sha256((dependency/'package.json').read_bytes()).hexdigest()}))
        config = 'name = "example-'+label+'"\ncompatibility_date = "2026-09-01"\n'
        if kind == 'worker':
            config += 'main = "worker.mjs"\n'
            (p/'worker.mjs').write_text('export default {fetch(){return new Response("Local Worker fixture")}};\n')
        else:
            config += 'pages_build_output_dir = "dist"\n'
            dist=p/'dist';dist.mkdir();(dist/'index.html').write_text('<!doctype html><h1>Local static fixture</h1>')
            if kind == 'ssr':
                (dist/'_worker.js').mkdir()
                (dist/'_worker.js/index.js').write_text('export default {fetch(){return new Response("<!doctype html><h1>Local SSR fixture</h1>",{headers:{"Content-Type":"text/html"}})}};\n')
                (dist/'_routes.json').write_text(json.dumps({'version':1,'include':['/*'],'exclude':[]}))
        (p/'wrangler.toml').write_text(config)
    p = root/'worker'
    run('version',p,cli+['--version'],[version])
    run('pages-deploy-help',root/'pages-static',cli+['pages','deploy','dist','--project-name','example-pages-static','--branch','review','--commit-hash','0'*40,'--commit-dirty=false','--help'],['--project-name','--branch','--commit-hash','--commit-dirty'])
    run('pages-preview-help',root/'pages-static',cli+['pages','dev','dist','--ip','localhost','--help'],['--ip','--port'])
    run('worker-dry-run',p,cli+['deploy','--config','wrangler.toml','--dry-run','--outdir','.runtime-dist'],['dry-run'])
    output=p/'.runtime-dist'
    results.append({'id':'worker-output','class':'real-wrangler-offline','status':'PASS' if any(output.glob('*.js')) else 'FAIL'})

    helper=Path(__file__).resolve().parents[3]/'skills/sdkit-cfops/scripts/cfops.py'
    for label, kind in [('pages-static','pages-static'),('pages-nuxt-shape','pages-nuxt'),('worker','worker')]:
        project=root/label
        (project/'build.mjs').write_text('import {writeFileSync} from "node:fs";writeFileSync("build-marker","local fixture build");\n')
        target={'kind':kind,'project':'example-'+label,'account_id':'0'*32,'config':'wrangler.toml',
                'environment':'preview','production_branch':'release','branch':'review','worker_env':'',
                'cli':cli,'wrangler_version':version,'build':[node,'build.mjs'],
                'output':'.runtime-dist' if kind=='worker' else 'dist',
                'required_files':['worker.js'] if kind=='worker' else ['_worker.js/index.js','_routes.json'] if kind=='pages-nuxt' else ['index.html']}
        # 实际 Wrangler 使用入口名作为 bundle 文件名。
        if kind=='worker':target['required_files']=['worker.js']
        plan=project/'.sdkit/cloudflare/release.json';plan.parent.mkdir(parents=True)
        plan.write_text(json.dumps({'schema_version':1,'targets':{'review':target}}))
        run('helper-build-'+label,project,[sys.executable,str(helper),'build','--target','review'],['artifact_sha256='],category='helper-with-real-wrangler')
        if kind=='pages-static':
            original_target=dict(target)
            for case, changes, marker in [
                ('wrong-project',{'project':'wrong-project'},'Pages name'),
                ('wrong-environment',{'environment':'production'},'分支与声明环境冲突'),
                ('wrong-version',{'wrangler_version':'4.0.0'},'Wrangler 实际版本'),
            ]:
                target={**original_target,**changes}
                plan.write_text(json.dumps({'schema_version':1,'targets':{'review':target}}))
                (project/'build-marker').unlink(missing_ok=True)
                run('helper-'+case,project,[sys.executable,str(helper),'build','--target','review'],[marker],1,'helper-negative-offline')
                assert not (project/'build-marker').exists()
            target=original_target
            plan.write_text(json.dumps({'schema_version':1,'targets':{'review':target}}))
            config=project/'wrangler.toml';old=config.read_text()
            config.write_text(old+'account_id="'+'f'*32+'"\n')
            run('helper-wrong-account',project,[sys.executable,str(helper),'build','--target','review'],['配置账户'],1,'helper-negative-offline')
            config.write_text(old)
            redirect=project/'.wrangler/deploy/config.json';redirect.parent.mkdir(parents=True,exist_ok=True);redirect.write_text('{}')
            run('helper-dynamic-config',project,[sys.executable,str(helper),'build','--target','review'],['动态或重定向配置'],1,'helper-negative-offline')
            redirect.unlink()

    # 证明离线 sandbox 确实阻止外网，而不是仅设置环境变量。
    denied=subprocess.run(['sandbox-exec','-f',str(offline),node,'-e','const n=require("net").connect(443,"1.1.1.1");n.on("error",e=>process.exit(e.code==="EPERM"?0:2));n.on("connect",()=>process.exit(3));setTimeout(()=>process.exit(4),2000)'],env=env,cwd=root,capture_output=True,timeout=5)
    results.append({'id':'network-denial','class':'sandbox-boundary','status':'PASS' if denied.returncode==0 else 'FAIL','exit_code':denied.returncode})

    for label, expected in [('pages-static','Local static fixture'),('pages-nuxt-shape','Local SSR fixture')]:
        project=root/label
        # 所有地址使用 localhost，端口由系统分配后传给实际 CLI。
        import socket
        with socket.socket() as sock:
            sock.bind(('localhost',0));port=sock.getsockname()[1]
        log=(root/(label+'-preview.log')).open('w')
        process=subprocess.Popen(['sandbox-exec','-f',str(local),*cli,'pages','dev','dist','--ip','localhost','--port',str(port)],cwd=project,env=env,stdout=log,stderr=log,start_new_session=True)
        ok=False
        try:
            opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
            deadline=time.monotonic()+25
            while time.monotonic()<deadline and process.poll() is None:
                try:
                    with opener.open(f'http://localhost:{port}/',timeout=1) as response:
                        ok=response.status==200 and expected in response.read().decode()
                    if ok: break
                except (OSError,ValueError): pass
                time.sleep(.25)
        finally:
            if process.poll() is None: os.killpg(process.pid,signal.SIGTERM)
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
            log.close()
        results.append({'id':label+'-preview','class':'real-wrangler-loopback','status':'PASS' if ok else 'FAIL','http_body_verified':ok})
    result={'wrangler_version':version,'credentials_inherited':False,'real_cloud_commands_executed':False,
            'copied_dependency_packages':len(copied),'business_project_reads_denied':True,'fixture_compatibility_date':'2026-09-01',
            'nuxt_scope':'synthetic Nitro Pages artifact shape; no real Nuxt build claimed','results':results}
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    # 原始日志只留在临时目录，失败时本地定位，不提交其路径与内容。
    (args.output.parent/'local-log-location.txt').write_text(str(root)+'\n')
    return int(any(r['status']!='PASS' for r in results))


if __name__=='__main__':raise SystemExit(main())
