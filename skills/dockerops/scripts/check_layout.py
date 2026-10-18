#!/usr/bin/env python3
"""Read-only audit of an explicitly selected Docker layout and literal callers."""
import argparse
import json
from pathlib import Path
import re

OPERATIONS = ('build', 'publish', 'verify', 'webhook', 'cleanup', 'deploy', 'rollback')


def check_layout(project, mode, environments=(), operations=(), required=()):
    root = Path(project)
    docker = root / '.sdkit/docker'
    errors = []
    if mode == 'multi' and (not environments or len(set(environments)) < 2):
        errors.append('multi 模式必须显式声明至少两个环境')
    if mode != 'multi' and environments:
        errors.append('只有 multi 模式允许环境子目录')
    if any(not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]*', e) or e == 'scripts' for e in environments):
        errors.append('环境名称非法或占用 scripts 名称')
    if not (root / 'Makefile').is_file():
        errors.append('缺少项目根 Makefile')
    if not docker.is_dir():
        errors.append('缺少 .sdkit/docker/')
        return errors
    if not (docker / 'README.md').is_file():
        errors.append('缺少 .sdkit/docker/README.md')
    if not any(p.is_file() for p in docker.glob('Dockerfile*') if not p.name.endswith('.dockerignore')):
        errors.append('缺少实际 Dockerfile')
    common = {'README.md', 'scripts', 'config.json'}
    local = {op + '.sh' for op in OPERATIONS} | {'config.json', 'docker-compose.yml', 'nginx.conf.example'}
    allowed = common | (set(environments) if mode == 'multi' else local)
    for p in sorted(docker.iterdir()):
        if p.name.startswith('Dockerfile'):
            continue
        if p.name not in allowed:
            errors.append(f'不符合 {mode} 根目录职责：.sdkit/docker/{p.name}')
    for base in ([docker / e for e in environments] if mode == 'multi' else [docker]):
        if mode == 'multi' and not base.is_dir():
            errors.append(f'缺少环境目录：{str(base.relative_to(root))}')
        for op in operations:
            if not (base / (op + '.sh')).is_file():
                errors.append(f'缺少 {str(base.relative_to(root))}/{op}.sh')
        for kind in required:
            filename = {'compose': 'docker-compose.yml', 'nginx': 'nginx.conf.example'}[kind]
            if not (base / filename).is_file():
                errors.append(f'缺少 {str(base.relative_to(root))}/{filename}')
        if mode == 'multi' and base.exists():
            for p in sorted(base.iterdir()):
                if p.name not in local and not p.name.startswith('Dockerfile'):
                    errors.append(f'不符合环境目录职责：{str(p.relative_to(root))}')
    # A literal reference must resolve even if the file containing it is not executed by tests.
    callers = [root / 'Makefile'] + list(docker.rglob('*.sh'))
    for p in callers:
        if not p.is_file():
            continue
        for lineno, line in enumerate(p.read_text().splitlines(), 1):
            if line.lstrip().startswith('#'):
                continue
            for target in re.findall(r'\.sdkit/docker/[a-zA-Z0-9_./-]+', line):
                if not (root / target).exists():
                    errors.append(f'{str(p.relative_to(root))}:{lineno} 引用不存在：{target}')
    for p in docker.rglob('*'):
        if p.is_symlink() and not p.exists():
            errors.append(f'失效链接：{str(p.relative_to(root))}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('--mode', choices=('single', 'multi', 'artifact'), required=True)
    parser.add_argument('--env', action='append', default=[])
    parser.add_argument('--operation', choices=OPERATIONS, action='append', default=[])
    parser.add_argument('--require', choices=('compose', 'nginx'), action='append', default=[])
    args = parser.parse_args()
    errors = check_layout(args.project, args.mode, args.env, args.operation, args.require)
    print(json.dumps({'ok': not errors, 'errors': errors}, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
