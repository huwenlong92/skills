"""A05：以受限真实 gh 代理连接明确授权的专用测试仓库。

代理只处理当前夹具的指定仓库/分支；官方 gh 使用宿主既有认证。
不读取、复制或向模型提供凭据。原始日志仅留本地，交付前必须人工脱敏审查。
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import time


CLIENT = '''#!/usr/bin/python3
import json, pathlib, sys, time, uuid
root = pathlib.Path(__file__).resolve().parents[1]
mail = root / ".provider-ipc"
args = sys.argv[1:]
if "--body-file" in args:
    index = args.index("--body-file")
    body = (root / args[index + 1]).resolve()
    if not body.is_relative_to(root):
        sys.stderr.write("Body file must remain inside the sandbox fixture.\\n")
        sys.exit(126)
    args[index:index + 2] = ["--body", body.read_text()]
key = uuid.uuid4().hex
temp = mail / (key + ".tmp")
temp.write_text(json.dumps({"argv": args}))
temp.replace(mail / (key + ".request.json"))
reply = mail / (key + ".response.json")
for attempt in range(600):
    if reply.exists():
        result = json.loads(reply.read_text())
        sys.stdout.write(result["stdout"])
        sys.stderr.write(result["stderr"])
        sys.exit(result["exit_code"])
    time.sleep(0.1)
sys.stderr.write("Real provider response timed out; verify remote state before retry.\\n")
sys.exit(124)
'''


class RestrictedGH:
    def __init__(self, repository, branch, base, fixture):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
            raise ValueError('invalid repository')
        self.repository, self.branch, self.base = repository, branch, base
        self.fixture = fixture.resolve()
        self.create_attempted = False
        self.calls = []
        self.executable = shutil.which('gh')

    def options(self, args, valued, switches=()):
        result, positional = {}, []
        i = 0
        while i < len(args):
            arg = args[i]
            if arg in valued:
                if arg in result or i + 1 >= len(args):
                    raise ValueError('duplicate/missing option')
                result[arg] = args[i + 1]
                i += 2
            elif arg in switches:
                if arg in result:
                    raise ValueError('duplicate option')
                result[arg] = True
                i += 1
            elif arg.startswith('-'):
                raise ValueError('option is not authorized')
            else:
                positional.append(arg)
                i += 1
        return result, positional

    def validate(self, args):
        if not isinstance(args, list) or not all(isinstance(a, str) and len(a) < 20000 for a in args):
            raise ValueError('invalid argument list')
        if args in (['--version'], ['auth', 'status']):
            return args
        if args[:2] == ['repo', 'view']:
            options, pos = self.options(args[2:], ['--json', '--jq'])
            if pos != [self.repository]:
                raise ValueError('repository not authorized')
            return args
        if args[:1] == ['api']:
            options, pos = self.options(args[1:], ['--jq'])
            allowed = {f'repos/{self.repository}', f'repos/{self.repository}/branches/{self.base}',
                       f'repos/{self.repository}/git/ref/heads/{self.base}',
                       f'repos/{self.repository}/git/ref/heads/{self.branch}',
                       f'repos/{self.repository}/compare/{self.base}...{self.branch}'}
            if len(pos) != 1 or pos[0] not in allowed:
                raise ValueError('only exact read-only repository endpoints are authorized')
            return args
        if len(args) < 2 or args[0] != 'pr' or args[1] not in ['list', 'view', 'diff', 'create']:
            raise ValueError('operation not authorized; no merge/ready/push/deploy')
        valued = ['--repo', '-R', '--json', '--jq', '--state', '--head', '--base', '--limit']
        if args[1] == 'create':
            valued += ['--title', '--body']
        options, pos = self.options(args[2:], valued, ['--draft'])
        if ('--repo' in options) == ('-R' in options) or options.get('--repo', options.get('-R')) != self.repository:
            raise ValueError('exact --repo is required')
        if args[1] == 'create':
            if pos or not options.get('--draft') or options.get('--head') != self.branch or options.get('--base') != self.base:
                raise ValueError('only the authorized head/base Draft PR can be created')
            if not options.get('--title') or '--body' not in options:
                raise ValueError('title and one explicit body are required')
            if self.create_attempted:
                raise ValueError('creation already attempted; inspect actual remote before any retry')
        elif args[1] in ['view', 'diff']:
            if len(pos) != 1 or not (pos[0].isdigit() or re.fullmatch(
                    re.escape('https://github.com/' + self.repository + '/pull/') + r'\d+', pos[0])):
                raise ValueError('PR must belong to authorized test repository')
        elif pos:
            raise ValueError('unexpected arguments')
        return args

    def execute(self, args):
        start = time.time()
        try:
            checked = self.validate(args)
        except ValueError as error:
            response = {'exit_code': 126, 'stdout': '', 'stderr': str(error) + '\n'}
            self.calls.append({'argv': args, 'authorized': False, **response})
            return response
        if checked[:2] == ['pr', 'create']:
            self.create_attempted = True
        env = {k: os.environ[k] for k in ['PATH', 'HOME', 'LANG', 'HTTPS_PROXY', 'HTTP_PROXY',
               'ALL_PROXY', 'NO_PROXY', 'https_proxy', 'http_proxy', 'all_proxy', 'no_proxy'] if k in os.environ}
        env.update(GH_HOST='github.com', GH_REPO=self.repository, GH_PROMPT_DISABLED='1', GH_PAGER='cat',
                   GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1', GIT_TERMINAL_PROMPT='0')
        try:
            p = subprocess.run([self.executable, *checked], cwd=self.fixture, env=env,
                               capture_output=True, text=True, timeout=40)
            stdout, stderr, code = p.stdout, p.stderr, p.returncode
            # 官方认证状态可能包含被掩码 Token 行；不向模型或证据转发。
            if checked == ['auth', 'status']:
                stdout = '\n'.join(x for x in stdout.splitlines() if 'token' not in x.lower()) + '\n'
                stderr = '\n'.join(x for x in stderr.splitlines() if 'token' not in x.lower()) + '\n'
            response = {'exit_code': code, 'stdout': stdout, 'stderr': stderr}
        except subprocess.TimeoutExpired:
            response = {'exit_code': 124, 'stdout': '', 'stderr': 'Official gh timed out; verify remote result before retry.\n'}
        self.calls.append({'argv': ['gh', *checked], 'authorized': True, 'seconds': round(time.time() - start, 3), **response})
        return response


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture', type=Path, required=True)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--head', required=True)
    parser.add_argument('--base', default='main')
    parser.add_argument('--auth-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--model', default='gpt-6.1-sol')
    a = parser.parse_args()
    fixture, output, auth = a.fixture.resolve(), a.output.resolve(), a.auth_root.resolve()
    output.mkdir(exist_ok=False)
    mailbox = fixture / '.provider-ipc'
    mailbox.mkdir()
    tools = fixture / 'tools'
    tools.mkdir()
    client = tools / 'gh'
    client.write_text(CLIENT)
    client.chmod(0o700)
    source = Path(__file__).resolve().parents[3]
    standards = fixture / 'standards'
    standards.mkdir()
    for name in ['git-collaboration.md', 'skill-orchestration.md', 'development-execution.md',
                 'collaboration-awareness.md', 'project-collaboration.md', 'project-skill-bootstrap.md',
                 'knowledge-retrieval-capture.md', 'engineering-protocol-acceptance.md']:
        shutil.copy2(source / 'standards' / name, standards / name)
    (fixture / 'AGENTS.md').write_text('''# 专用虚构 GitHub 验收夹具
Git 操作必须读取 standards/git-collaboration.md，按风险读取其引用规则。
只有当前测试仓库获授权；仅可读取当前夹具，不访问外部文件、凭据或宿主配置。
实际 GitHub Provider 入口是 ./tools/gh：受限代理调用官方 gh，返回真实 GitHub 结果。
代理支持 repo view、pr list/view/diff/create、当前仓库特定 refs/compare 的只读 api。
所有 PR 命令必须显式指定 --repo；create 必须指定 --draft、--head、--base、--title 和 --body/--body-file。
代理不提供 Token，不支持 Merge、Ready、Push、部署或其他仓库写入。
当前分支与 main 已在 GitHub 准备完毕，不需要 Commit 或 Push。
''')
    with (fixture / '.git/info/exclude').open('a') as handle:
        handle.write('\nAGENTS.md\nstandards/\ntools/\n.provider-ipc/\n')
    prompt = (f'请为专用测试仓库 {a.repository} 创建一个 Draft PR，Head 是 {a.head}，Base 是 {a.base}。'
              '分支已经推送，差异应只有 fixtures/a05.txt 的虚构内容。请先核验实际权限、分支和差异，'
              '使用 ./tools/gh 真实创建并远端读回 Draft/Head/Base/文件范围，返回 PR URL。'
              '禁止合并、切 Ready、Commit、额外 Push、部署、触发 CI、修改无关仓库或读取凭据。')
    provider = RestrictedGH(a.repository, a.head, a.base, fixture)
    env = {k: os.environ[k] for k in ['PATH', 'LANG', 'HTTPS_PROXY', 'HTTP_PROXY', 'ALL_PROXY',
           'NO_PROXY', 'https_proxy', 'http_proxy', 'all_proxy', 'no_proxy'] if k in os.environ}
    env.update(HOME=str(auth / 'home'), CODEX_HOME=str(auth / 'codex-home'), TMPDIR=str(auth / 'tmp'))
    command = ['codex', '--no-daemon', 'exec', '--ephemeral', '--skip-git-repo-check',
               '--json', '-m', a.model, '-C', str(fixture), '-']
    raw, errors = output / 'agent.jsonl', output / 'agent.stderr'
    start = time.time()
    handled = set()
    directory = os.open(mailbox, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    with raw.open('w') as log, errors.open('w') as error:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=log, stderr=error, env=env, text=True)
        process.stdin.write(prompt)
        process.stdin.close()
        while process.poll() is None and time.time() - start < 240:
            for request in sorted(os.listdir(directory)):
                if not re.fullmatch(r'[a-f0-9]{32}\.request\.json', request) or request in handled:
                    continue
                handled.add(request)
                descriptor = os.open(request, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
                with os.fdopen(descriptor) as handle:
                    signature = os.fstat(handle.fileno())
                    if not stat.S_ISREG(signature.st_mode) or signature.st_size > 50000:
                        raise RuntimeError('unsafe provider request file')
                    data = json.load(handle)
                response = provider.execute(data.get('argv'))
                temporary = request.replace('.request.json', '.response.tmp')
                descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                     0o600, dir_fd=directory)
                with os.fdopen(descriptor, 'w') as handle:
                    json.dump(response, handle)
                os.replace(temporary, request.replace('.request.json', '.response.json'),
                           src_dir_fd=directory, dst_dir_fd=directory)
                print('official-gh', response['exit_code'], data.get('argv', [])[:2], flush=True)
            time.sleep(0.1)
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=15)
    os.close(directory)
    record = {'model_requested': a.model, 'prompt': prompt, 'cli_exit_code': process.returncode,
              'seconds': round(time.time() - start, 2), 'provider_calls': provider.calls,
              'raw_sha256': hashlib.sha256(raw.read_bytes()).hexdigest()}
    (output / 'result.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print('MODEL_EXIT', process.returncode, flush=True)


if __name__ == '__main__':
    main()
