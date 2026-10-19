#!/usr/bin/env python3
"""Cloudflare 项目离线检查、显式执行与 HTTP 验收；Python 3.11+ 标准库。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request


class CheckError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise CheckError(message)


def local_path(root, value):
    require(isinstance(value, str) and value and not Path(value).is_absolute(), "路径必须为非空项目相对路径")
    p = root / value
    require(p.resolve().is_relative_to(root), "路径越出项目")
    require(not any(x.is_symlink() for x in [p, *p.parents] if x.is_relative_to(root)), "禁止符号链接路径")
    return p


def jsonc(text):
    # 先按字符串状态去注释，再仅在字符串外去尾随逗号。
    out, i, quoted, escaped = [], 0, False, False
    while i < len(text):
        c = text[i]
        if quoted:
            out.append(c)
            if escaped:
                escaped = False
            elif c == '\\':
                escaped = True
            elif c == '"':
                quoted = False
            i += 1
        elif c == '"':
            quoted = True
            out.append(c)
            i += 1
        elif text[i:i+2] == '//':
            end = text.find('\n', i)
            i = len(text) if end < 0 else end
        elif text[i:i+2] == '/*':
            end = text.find('*/', i+2)
            require(end >= 0, "JSONC 注释未闭合")
            out.append(' ')
            i = end + 2
        else:
            out.append(c)
            i += 1
    text = ''.join(out)
    out, quoted, escaped = [], False, False
    for i, c in enumerate(text):
        if not quoted and c == ',' and text[i+1:].lstrip().startswith(('}', ']')):
            continue
        out.append(c)
        if quoted and escaped:
            escaped = False
        elif quoted and c == '\\':
            escaped = True
        elif c == '"':
            quoted = not quoted
    return json.loads(''.join(out))


def read_config(path):
    text = path.read_text(encoding='utf-8')
    if path.suffix == '.toml':
        return tomllib.loads(text)
    require(path.suffix in {'.json', '.jsonc'}, "不支持的配置格式")
    return jsonc(text) if path.suffix == '.jsonc' else json.loads(text)


def argv(value):
    require(isinstance(value, list) and value and all(isinstance(s, str) and s for s in value), "命令必须为非空字符串数组")
    return value


def audit_build(root, command, seen=None):
    """阻断可识别的隐式写入；不能替代 Agent 对任意程序调用链的人工审阅。"""
    seen = set() if seen is None else seen
    text = ' '.join(command)
    require(not re.search(r'\bwrangler(?:@\S+)?\s+(?:pages\s+deploy|deploy|r2|kv|d1|secret|queues|versions|deployments)\b', text), "构建入口包含云端写入或不受支持的 Wrangler 子命令")
    require(not re.search(r'\b(?:terraform\s+(?:apply|destroy)|git\s+push|gh\s+workflow\s+run)\b', text), "构建入口包含发布、CI 或基础设施写入")
    if command[0] in {'npm', 'pnpm', 'yarn'} and len(command) >= 3 and command[1] == 'run':
        name = command[2]
        require(name not in seen, "构建脚本存在循环引用")
        seen.add(name)
        package = json.loads(local_path(root, 'package.json').read_text(encoding='utf-8'))
        scripts = package.get('scripts', {})
        require(name in scripts, "构建 package script 不存在")
        for key in ['pre' + name, name, 'post' + name]:
            if key in scripts:
                audit_build(root, shlex.split(scripts[key]), seen.copy())
    for part in command:
        if part.endswith(('.sh', '.py', '.js', '.mjs', '.cjs')) or part.startswith(('deploy/', 'scripts/')):
            path = local_path(root, part)
            if path.is_file() and path.suffix != '.json':
                key = path.relative_to(root).as_posix()
                require(key not in seen, "构建文件存在循环引用")
                seen.add(key)
                # 分词仅用于发现显式危险调用；动态执行、插件和 source 必须人工检查。
                audit_build(root, shlex.split(path.read_text(encoding='utf-8'), comments=True), seen.copy())


def guard_dynamic_config(root):
    for name in ['wrangler.ts', 'wrangler.js', 'wrangler.mjs', 'wrangler.cjs', '.wrangler/deploy/config.json']:
        require(not (root / name).exists(), "框架动态或重定向配置未适配，停止执行")


def load(root, plan, target):
    data = json.loads(local_path(root, plan).read_text(encoding='utf-8'))
    require(data.get('schema_version') == 1, "计划 schema_version 必须为 1")
    require(target in data.get('targets', {}), "必须指定计划中存在的目标")
    t = data['targets'][target]
    require(t.get('kind') in {'pages-static', 'pages-nuxt', 'worker'}, "未知发布类型")
    require(t.get('environment') in {'preview', 'production'}, "必须明确 preview/production")
    require(re.fullmatch(r'[a-z0-9][a-z0-9-]*', t.get('project', '')), "项目名无效")
    require(re.fullmatch(r'[0-9a-f]{32}', t.get('account_id', '')), "必须配置明确账户 ID")
    require(re.fullmatch(r'\d+\.\d+\.\d+', t.get('wrangler_version', '')), "必须锁定精确 Wrangler 版本")
    argv(t.get('cli'))
    argv(t.get('build'))
    audit_build(root, t['build'])
    require(isinstance(t.get('required_files'), list) and t['required_files'], "必须声明必要产物")
    config = local_path(root, t.get('config'))
    guard_dynamic_config(root)
    c = read_config(config)
    require(isinstance(c, dict), "Wrangler 配置必须为对象")
    require(not c.get('build'), "Wrangler 自定义 build hook 必须先适配，禁止隐式重复构建")
    # 明确配置以外的历史配置不能被静默忽略。
    for directory in [root, root / 'deploy/cloudflare']:
        for name in ['wrangler.toml', 'wrangler.json', 'wrangler.jsonc']:
            candidate = directory / name
            require(not candidate.exists() or candidate == config, "存在其他 Wrangler 配置，必须先审阅消除歧义")
    env = t.get('worker_env', '')
    if t['kind'] == 'worker':
        require(isinstance(env, str), "worker_env 必须为字符串；空串表示已确认顶层配置")
        require('worker_env' in t, "Worker 必须显式声明 worker_env")
        require(not env or env in c.get('env', {}), "Worker env 不存在")
        effective = dict(c)
        effective.update(c.get('env', {}).get(env, {}) if env else {})
        require(not effective.get('build'), "Worker env 自定义 build hook 必须先适配")
        # 不猜测 Wrangler 命名 env 的隐式后缀。
        if env:
            require(c['env'][env].get('name'), "命名 env 必须显式声明 name")
        require(effective.get('name') == t['project'], "Worker name 与计划不一致")
        require('pages_build_output_dir' not in c, "Worker 误用了 Pages 配置")
        require(bool(effective.get('main')), "Worker 必须声明入口")
        require(local_path(root, str(config.parent.relative_to(root) / Path(effective['main']))).is_file(), "Worker 入口不存在")
        if effective.get('account_id'):
            require(effective['account_id'] == t['account_id'], "Worker env 账户与计划不一致")
    else:
        require(config.parent == root and config.name in {'wrangler.toml', 'wrangler.json', 'wrangler.jsonc'}, "Pages 必须使用项目根目录标准配置，不支持 --config")
        require(c.get('name') == t['project'], "Pages name 与计划不一致")
        require(not env, "Pages 不能套用 Worker 命名 env")
        branch, production = t.get('branch'), t.get('production_branch')
        require(isinstance(branch, str) and branch and isinstance(production, str) and production, "必须明确部署分支和云端生产分支")
        require((branch == production) == (t['environment'] == 'production'), "分支与声明环境冲突")
        output = local_path(root, t.get('output'))
        actual = config.parent / c.get('pages_build_output_dir', '')
        require(actual.resolve() == output.resolve(), "Pages 产物目录与配置不一致")
    if c.get('account_id'):
        require(c['account_id'] == t['account_id'], "配置账户与计划不一致")
    output = local_path(root, t.get('output'))
    require(output != root and not any(x in {'.git', '.agents', '.codex'} for x in output.relative_to(root).parts), "产物目录禁止指向源码根或工具元数据")
    for f in t['required_files']:
        local_path(local_path(root, t['output']), f)
    return t


def git(root, *args):
    p = subprocess.run(['git', '-C', str(root), *args], text=True, capture_output=True)
    require(p.returncode == 0, "无法读取项目 Git 状态")
    return p.stdout.strip()


def source(root):
    require(Path(git(root, 'rev-parse', '--show-toplevel')).resolve() == root, "root 必须为真实 Git 项目根目录")
    for name in ['MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply', 'BISECT_LOG']:
        p = Path(git(root, 'rev-parse', '--git-path', name))
        require(not (p if p.is_absolute() else root / p).exists(), "Git 操作进行中，停止发布")
    h = hashlib.sha256(git(root, 'diff', '--binary', 'HEAD').encode())
    # -z 避免含空格或换行的路径被错误拆分；不读取被忽略的 Secret 文件。
    names = subprocess.run(['git', '-C', str(root), 'ls-files', '--others', '--exclude-standard', '-z'], capture_output=True, check=True).stdout
    for name in sorted(n for n in names.split(b'\0') if n):
        path = local_path(root, os.fsdecode(name))
        require(path.is_file(), "未跟踪对象必须为普通文件")
        h.update(name + b'\0' + hashlib.sha256(path.read_bytes()).digest())
    return {'sha': git(root, 'rev-parse', 'HEAD'), 'dirty': bool(git(root, 'status', '--porcelain', '--untracked-files=all')), 'worktree_sha256': h.hexdigest()}


def artifacts(root, t):
    out = local_path(root, t['output'])
    require(out.is_dir(), "构建产物目录不存在")
    files = list(t['required_files'])
    if t['kind'] == 'pages-nuxt':
        files += ['_worker.js/index.js', '_routes.json']
    for f in files:
        require(local_path(out, f).is_file(), "缺少必要构建产物")
    h, count = hashlib.sha256(), 0
    for p in sorted(out.rglob('*')):
        require(not p.is_symlink(), "产物禁止符号链接")
        require(p.is_dir() or p.is_file(), "产物禁止非普通文件")
        if p.is_file():
            h.update(p.relative_to(out).as_posix().encode() + b'\0')
            h.update(hashlib.sha256(p.read_bytes()).digest())
            count += 1
    require(count > 0, "产物为空")
    return h.hexdigest()


def execute(root, command):
    # 不打印参数/环境，CLI 自身输出由终端管理，禁止额外启用 debug/trace。
    p = subprocess.run(command, cwd=root)
    require(p.returncode == 0, "项目命令失败；如已开始部署，必须核对 Provider 后才能重试")


def cli_check(root, t):
    require(not os.environ.get('WRANGLER_ENV') and not os.environ.get('CLOUDFLARE_ENV'), "存在隐式环境选择变量，必须先核实并移除歧义")
    p = subprocess.run(t['cli'] + ['--version'], cwd=root, text=True, capture_output=True)
    require(p.returncode == 0, "项目 Wrangler 不可用；禁止自动安装")
    versions = re.findall(r'(?<!\d)(\d+\.\d+\.\d+)(?!\d)', p.stdout)
    require(versions == [t['wrangler_version']], "Wrangler 实际版本与计划不一致")


def worker_flags(t):
    return ['--env', t['worker_env']] if t.get('worker_env') else []


def build(root, t):
    guard_dynamic_config(root)
    config_bytes = local_path(root, t['config']).read_bytes()
    audit_build(root, t['build'])
    cli_check(root, t)
    execute(root, t['build'])
    guard_dynamic_config(root)
    require(local_path(root, t['config']).read_bytes() == config_bytes, "构建改写了生效配置，停止发布")
    if t['kind'] == 'worker':
        execute(root, t['cli'] + ['deploy', '--config', t['config'], *worker_flags(t), '--dry-run', '--outdir', t['output']])
    return artifacts(root, t)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def verify(t, origin):
    u = urllib.parse.urlsplit(origin)
    require(u.scheme in {'http', 'https'} and u.hostname and not u.username and not u.password and not u.query and not u.fragment and u.path in {'', '/'}, "origin 必须为不含凭据/路径/查询的 HTTP(S) 源")
    require(u.scheme == 'https' or u.hostname == 'localhost', "非 localhost 必须 HTTPS")
    probes = t.get('probes')
    require(isinstance(probes, list) and probes, "必须声明探针")
    opener = urllib.request.build_opener(NoRedirect())
    failed = False
    for i, probe in enumerate(probes, 1):
        try:
            path = probe['path']
            require(isinstance(path, str) and path.startswith('/') and not path.startswith('//') and '\\' not in path, "探针必须为同源路径")
            parsed = urllib.parse.urlsplit(path)
            require(not parsed.scheme and not parsed.netloc and not parsed.fragment and not parsed.query, "探针禁止跨域、查询和 fragment")
            require(isinstance(probe['status'], int) and not 300 <= probe['status'] < 400, "探针不得以跳转为成功")
            require(bool(probe.get('content_type')) and bool(probe.get('contains')), "探针必须声明类型和预期正文")
            try:
                response = opener.open(origin.rstrip('/') + path, timeout=15)
            except urllib.error.HTTPError as e:
                response = e
            with response:
                require(response.status == probe['status'], "HTTP 状态不符")
                require(response.headers.get_content_type() == probe['content_type'], "Content-Type 不符")
                body = response.read(2 * 1024 * 1024 + 1)
                require(len(body) <= 2 * 1024 * 1024, "响应过大，需项目专用验收")
                require(probe['contains'].encode('utf-8') in body, "预期正文缺失")
            print(f'probe {i}: PASS')
        except (CheckError, OSError, ValueError, KeyError, TypeError):
            # 不打印 URL、响应或异常原文，避免泄漏受控内容。
            print(f'probe {i}: FAIL')
            failed = True
    require(not failed, "HTTP 验收未通过")


def deploy(root, t, args):
    require(args.write, "部署必须显式 --write；该开关不替代授权和云端预检")
    before = source(root)
    require(args.expected_sha == before['sha'], "源码 SHA 与预期不一致")
    require(t['environment'] != 'production' or not before['dirty'], "生产发布必须为干净提交")
    require(os.environ.get('CLOUDFLARE_ACCOUNT_ID') == t['account_id'], "显式账户环境变量与计划不一致")
    digest = build(root, t)
    after = source(root)
    require(after == before, "构建期间 Git 状态变化，停止发布")
    command = t['cli'] + (['deploy', '--config', t['config'], *worker_flags(t)] if t['kind'] == 'worker' else [
        'pages', 'deploy', t['output'], '--project-name', t['project'],
        '--branch', t['branch'], '--commit-hash', before['sha'], '--commit-dirty=' + str(before['dirty']).lower()])
    directory = local_path(root, '.sdkit/cloudflare/.local')
    require(git(root, 'check-ignore', '.sdkit/cloudflare/.local/last-deploy.json'), "必须先忽略本地发布记录目录")
    directory.mkdir(parents=True, exist_ok=True)
    receipt = local_path(root, '.sdkit/cloudflare/.local/last-deploy.json')
    record = {**before, 'target': args.target, 'project': t['project'], 'environment': t['environment'], 'config': t['config'], 'artifact_sha256': digest, 'status': 'failed-or-unknown'}
    receipt.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    execute(root, command)
    record['status'] = 'cli-success-provider-readback-required'
    receipt.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('上传命令完成；部署 ID、版本、URL、绑定及真实访问必须另行核验')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['check', 'build', 'preview', 'deploy', 'verify'])
    p.add_argument('--root', default='.')
    p.add_argument('--plan', default='.sdkit/cloudflare/release.json')
    p.add_argument('--target', required=True)
    p.add_argument('--write', action='store_true')
    p.add_argument('--expected-sha')
    p.add_argument('--origin')
    args = p.parse_args()
    try:
        root = Path(args.root).resolve()
        t = load(root, args.plan, args.target)
        if args.command == 'check':
            state = source(root)
            print(json.dumps({'local_check': 'PASS', 'cloud_check': 'NOT_RUN', 'target': args.target, **state}, ensure_ascii=False))
        elif args.command == 'build':
            print('artifact_sha256=' + build(root, t))
        elif args.command == 'preview':
            cli_check(root, t)
            artifacts(root, t)
            command = ['dev', '--config', t['config'], *worker_flags(t), '--ip', 'localhost'] if t['kind'] == 'worker' else ['pages', 'dev', t['output'], '--ip', 'localhost']
            execute(root, t['cli'] + command)
        elif args.command == 'verify':
            require(args.origin, 'verify 必须显式指定 origin')
            verify(t, args.origin)
        else:
            deploy(root, t, args)
    except (CheckError, OSError, ValueError, KeyError, TypeError) as e:
        # JSON/TOML 解析器异常可能带原文；仅安全输出已知校验信息。
        message = str(e) if type(e) is CheckError else '读取或执行失败；请检查文件格式、字段和工具，不输出原始内容'
        print('BLOCKED: ' + message, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
