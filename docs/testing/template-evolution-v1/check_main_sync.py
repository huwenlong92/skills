"""验收 PR #24 同步的 Catalog、证据保全、敏感路径及文件范围；仅只读检查。"""
from pathlib import Path
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
ORIGINAL = '7c78d7a9dd550a7e7ffb8cfc2b50f2a8917fa9b6'
MAIN = '8777b036311349fef7a99cdf094c36fd7011c15c'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def main():
    catalog = json.loads((ROOT / 'catalog.json').read_text())
    incoming = json.loads(git('show', MAIN + ':catalog.json'))
    entries = {x['name']: x for x in catalog['skills']}
    assert len(entries) == len(catalog['skills']) == 23
    assert all(entries[x['name']] == x for x in incoming['skills'])
    assert set(entries) == {p.name for p in (ROOT / 'skills').iterdir() if p.is_dir() and not p.name.startswith('.')}
    for name in ('sdkit-dbops', 'sdkit-templateops'):
        assert sum(x['name'] == name for x in catalog['skills']) == 1
    # 同步不得更改 TE 实现、既有报告或提前引入 #20 的 Orchestration。
    preserved = ['scripts/template_evolution_protocol.py', 'scripts/test_template_evolution.py', 'standards/skill-orchestration.md']
    preserved += git('ls-tree', '-r', '--name-only', ORIGINAL, 'skills/sdkit-templateops', 'docs/testing/template-evolution-v1').decode().splitlines()
    for f in preserved:
        assert (ROOT / f).read_bytes() == git('show', ORIGINAL + ':' + f), f
    for f in git('ls-tree', '-r', '--name-only', MAIN, 'skills/sdkit-dbops').decode().splitlines():
        assert (ROOT / f).read_bytes() == git('show', MAIN + ':' + f), f
    assert not (ROOT / 'standards/git-collaboration.md').exists()
    paths = set(git('diff', '--name-only', 'origin/main').decode().splitlines())
    paths.update(git('ls-files', '--others', '--exclude-standard').decode().splitlines())
    exact = {'catalog.json', 'scripts/template_evolution_protocol.py', 'scripts/test_template_evolution.py', 'standards/skill-orchestration.md', '.sdkit/STATUS.md', '.sdkit/TASKS.md', '.sdkit/HANDOFF.md'}
    allowed = ('skills/sdkit-templateops/', 'docs/testing/template-evolution-v1/', '.sdkit/plans/pr24-')
    patterns = {
        'personal_path': r'/Users/|/home/|/private/tmp/|/private/var/|/tmp/',
        'credential': r'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
        'conflict_marker': r'^(?:<{7}|={7}|>{7})(?: |$)',
    }
    errors = []
    for f in sorted(paths):
        assert f in exact or f.startswith(allowed), ('unrelated file', f)
        p = ROOT / f
        assert p.is_file() and not p.is_symlink(), f
        # 扫描器中的正则是检测签名，不是泄露的路径或密钥。
        if p == Path(__file__).resolve():
            continue
        for n, line in enumerate(p.read_text().splitlines(), 1):
            for kind, pattern in patterns.items():
                if re.search(pattern, line):
                    errors.append({'file': f, 'line': n, 'kind': kind})
    result = {'catalog_skills': len(entries), 'main_entries_preserved': len(incoming['skills']), 'preserved_files': len(preserved), 'scanned_files': len(paths) - 1, 'errors': errors}
    print(json.dumps(result, ensure_ascii=False))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
