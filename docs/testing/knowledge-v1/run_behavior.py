"""只在临时目录生成虚构夹具；真实 Codex 事件与会话 ID 保留于该目录，不提交。"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import time

PROMPTS = {
 1: ['LumaNote 登录之前定了什么？'],
 2: ['以前 R2 缓存安全怎么处理？只回顾当时的记录。'],
 3: ['LumaNote 用 R2 缓存怎么设计？请结合项目已确认约束和以前的经验，不做当前 API 推荐。'],
 4: ['Vue computed 和 watch 的概念区别是什么？简单解释即可，不讨论版本特性。'],
 5: ['星笺的登录之前定了什么？'],
 6: ['以前对象存储缓存隔离的排障是怎么做的？只回顾记录。'],
 7: ['旧笔记说所有响应都能缓存，这与 LumaNote 的缓存决策冲突吗？以项目约束为准解释。'],
 8: ['我想做一个网站，还没有想好给谁用。今天先到这里。'],
 9: ['我想给社区读书会做报名工具，解决重复统计，交付物是一个独立报名网站。现在仅评估想法，先不启动项目，今天先到这里。'],
 10: ['LumaNote 技术方案我确认了：登录走服务端会话，私有响应禁止共享缓存。现在只确认决策，尚未开发。今天先到这里。'],
 11: ['虚构排障已闭环：缓存串用户；定位为共享缓存键缺少用户边界；修复为私有响应 bypass；测试材料中隔离断言 2/2 通过。这是我提供的测试证据，今天先到这里。'],
 12: ['我们已有的对象存储经验有缓存隔离、清除流程和回源诊断三个独立知识点，边界是离线测试环境，准备持续维护。是否够形成专题？今天先到这里。'],
 13: ['LumaNote 登录之前定了什么？我确认补充要求：登录错误提示必须可读且不得泄露账号是否存在。先把这条作为本轮待归档决策，本阶段还没结束，不保存。'] + [f'继续刚才同一个主题，第 {i} 轮：先保留当前已核验来源和候选，没有新资料或版本变化，不落库；本阶段还没结束。' for i in range(2,10)] + ['第十轮，这个阶段结束。请给一个简短的知识沉淀建议，沿用已读来源，不落库。'],
 14: ['今天心情不错，谢谢你陪我聊一会儿。再见。'],
 15: ['LumaNote 登录之前定了什么？我现在没有产品仓库和知识库访问权限，也没有提供任何正文。'],
 16: ['仅只读核对 LumaNote 登录决策，可以给文档草稿；不得保存、创建项目或 PR，也不部署。'],
}


def write(root, name, text):
    p=root/name; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text,encoding='utf-8')


def git(root, *args):
    return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()


def make_fixture(source, base, case):
    root=base/f'C{case:02d}';root.mkdir(parents=True)
    for name in ('foundry','wikiops'):
        shutil.copytree(source/'skills'/name,root/'.agents/skills'/name,ignore=shutil.ignore_patterns('__pycache__'))
    for name in ('skill-orchestration.md','knowledge-retrieval-capture.md'):
        write(root,'standards/'+name,(source/'standards'/name).read_text())
    write(root,'AGENTS.md','''# 虚构离线知识任务\n所有内容均为虚构验收材料。只允许读取当前夹具目录内文件；禁止访问目录外文件、环境变量、用户配置、凭据、MCP、真实仓库或外部网络。禁止修改任何文件、Commit、Push、PR、项目创建、部署或 Actions。\n自然语言任务遵守 standards/skill-orchestration.md 和 standards/knowledge-retrieval-capture.md；按任务语义使用原生发现的适用 Skill，只加载命中规则。\n当前任务明确选择虚构 Active Workspace：产品为 fixture-products（https://example.invalid/fixture/products.git），本地 products/；知识为 fixture-knowledge（https://example.invalid/fixture/knowledge.git），本地 knowledge/。这些是提供给本次验收的离线 Git 快照，远端最新状态不可核验，禁止网络同步；不得读取个人配置或回退发布者默认仓库。\n''')
    if case == 15:
        return root
    write(root,'products/AGENTS.md','''# 虚构产品资料库\n只读。PROJECTS.md 是项目索引；索引缺失可查 projects/ 中 profile.json 的 name/aliases。项目资料在各项目 docs/ 和 tech/。只允许引用已有文件，不能创建或发布。离线版本以本仓库 Git SHA 为准。\n''')
    index='# 虚构项目索引\n'+('索引暂未收录星笺，请查 projects/ 下 profile.json。\n' if case==5 else 'LumaNote，slug luma-note，别名星笺；见 projects/luma-note/profile.json 与 docs/decisions.md。\n')
    write(root,'products/PROJECTS.md',index)
    write(root,'products/projects/luma-note/profile.json',json.dumps({'slug':'luma-note','name':'LumaNote','aliases':['星笺']},ensure_ascii=False))
    write(root,'products/projects/luma-note/docs/decisions.md','''# 登录决策\n2026-09-20，状态 confirmed，适用 LumaNote v0.2 产品方案。登录使用服务端 Cookie Session；不采用浏览器长期 bearer token。此文件是产品决策，无代码实现或上线证据。\n''')
    write(root,'products/projects/luma-note/tech/cache.md','''# 缓存边界\n2026-09-20 confirmed，LumaNote v0.2：私有响应必须 bypass 共享缓存；仅公共静态内容允许共享缓存。此为方案，不代表已开发或部署。\n''')
    write(root,'knowledge/AGENTS.md','''# 虚构技术知识库\n只读离线快照。先读取 TOPICS.md 与 topics.json，再按需读取 notes/ 正文。索引可能过期，未命中时查目录和同义词。不能建文章、专题或 PR。引用使用本地路径和 Git SHA，禁止猜造门户 URL。\n''')
    write(root,'knowledge/TOPICS.md','# 主题\n'+('缓存专题索引过期，需核对 notes/。\n' if case==6 else '对象存储 / R2 / 缓存隔离：notes/cache-isolation.md；历史旧稿：notes/cache-legacy.md。\n'))
    write(root,'knowledge/topics.json',json.dumps({'topics':[] if case==6 else [{'id':'object-storage','aliases':['R2','对象存储','缓存隔离'],'path':'notes/cache-isolation.md'}]},ensure_ascii=False))
    write(root,'knowledge/notes/cache-isolation.md','''---\ntitle: 对象存储缓存隔离排障\nstatus: tested\ndate: 2026-08-01\n---\n# 对象存储缓存隔离排障\n这是虚构的历史离线测试。症状为共享缓存串用户；私有响应改为 bypass，公共文件才使用共享缓存。隔离断言 2/2 通过。该记录不是当前官方 API 或安全保证。\n''')
    write(root,'knowledge/notes/cache-legacy.md','''---\ntitle: 缓存旧草稿\nstatus: draft\ndate: 2025-01-01\n---\n# 缓存旧草稿\n旧试验设想缓存全部响应，未验证；仅公共无认证演示环境，禁止用于私有响应。被 2026-08-01 缓存隔离记录在其适用范围内替代。\n''')
    for folder,url in [('products','products'),('knowledge','knowledge')]:
        repo=root/folder
        git(repo,'init','--initial-branch=main')
        git(repo,'remote','add','origin',f'https://example.invalid/fixture/{url}.git')
        git(repo,'add','AGENTS.md',*(['PROJECTS.md','projects'] if folder=='products' else ['TOPICS.md','topics.json','notes']))
        git(repo,'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-m','Fictional snapshot')
    return root


def manifest(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file() and '.git' not in p.parts}


def run(source, base, cases, model, sandbox):
    base.mkdir(parents=True,exist_ok=True)
    for case in cases:
        root=make_fixture(source,base,case);before=manifest(root);thread=None
        record={'case':case,'model_requested':model,'sandbox':sandbox,'cli_version':subprocess.check_output(['codex','--version'],text=True).strip(),'turns':[]}
        for i,prompt in enumerate(PROMPTS[case],1):
            common=['--ignore-user-config','--enable','skip_host_skill_discovery','--disable','apps','--disable','plugins','--disable','unbounded_connection_retries']
            if thread:
                args=['codex','exec',*common,'--sandbox',sandbox,'resume','--skip-git-repo-check','--json','-m',model,thread,'-']
            else:
                args=['codex','exec',*common,'--sandbox',sandbox,'--skip-git-repo-check','--json','-m',model,'-C',str(root),'-']
            start=time.time()
            try:
                result=subprocess.run(args,input=prompt,text=True,capture_output=True,cwd=root,timeout=240)
            except subprocess.TimeoutExpired as exc:
                print(f'C{case:02d} turn {i}: TIMEOUT',flush=True);raise
            raw=base/f'C{case:02d}-turn{i:02d}.jsonl';raw.write_text(result.stdout)
            (base/f'C{case:02d}-turn{i:02d}.stderr').write_text(result.stderr)
            events=[]
            for line in result.stdout.splitlines():
                try: event=json.loads(line)
                except ValueError: continue
                if event.get('type')=='thread.started': thread=event['thread_id']
                events.append(event)
            commands=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution']
            replies=[e['item']['text'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message']
            turn={'turn':i,'prompt':prompt,'exit_code':result.returncode,'seconds':round(time.time()-start,2),'completed':any(e.get('type')=='turn.completed' for e in events),'commands':commands,'responses':replies,'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'errors':[e for e in events if e.get('type') in ('error','turn.failed')]}
            record['turns'].append(turn)
            print(f'C{case:02d} turn {i}: exit={result.returncode} completed={turn["completed"]} commands={len(commands)}',flush=True)
            if result.returncode or not turn['completed']: break
        record['files_unchanged']=before==manifest(root)
        record['repo_status']={folder:git(root/folder,'status','--short') for folder in ('products','knowledge') if (root/folder).exists()}
        # 会话 ID 和工作站绝对路径不得进入可提交证据。
        output=json.dumps(record,ensure_ascii=False,indent=2).replace(str(base),'<fixture-root>')
        if thread: output=output.replace(thread,'<session>')
        (base/f'C{case:02d}-evidence.json').write_text(output)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--cases',default=','.join(map(str,range(1,17))));parser.add_argument('--model',default='gpt-6.1-sol');parser.add_argument('--sandbox',choices=['read-only','workspace-write'],default='read-only')
    a=parser.parse_args();run(a.source.resolve(),a.output.resolve(),[int(x) for x in a.cases.split(',')],a.model,a.sandbox)
