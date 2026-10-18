#!/usr/bin/env python3
"""检查本仓库 Markdown 相对文件与标题/显式 HTML 锚点，不访问网络。"""
import argparse
import html
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

LINK = re.compile(r'\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+"[^"\n]*")?\s*\)')
REFERENCE = re.compile(r'^ {0,3}\[[^]\n]+\]:\s*<?([^\s>]+)>?', re.M)


def outside_fences(text):
    lines, fence = [], None
    for line in text.splitlines():
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            continue
        if marker:
            fence = marker[1]
        elif not line.startswith(('    ', '\t')):
            lines.append(line)
    return '\n'.join(lines)


def anchors(text):
    body = outside_fences(text)
    result = set(re.findall(r'<[^>]+\b(?:id|name)=[\"\']([^\"\']+)[\"\']', body))
    counts = {}
    lines = body.splitlines()
    for number, line in enumerate(lines):
        match = re.match(r'^ {0,3}#{1,6}\s+(.+?)(?:\s+#+\s*)?$', line)
        heading = match[1] if match else None
        if not heading and number + 1 < len(lines) and line.strip() and re.fullmatch(r' {0,3}(?:=+|-+)\s*', lines[number + 1]):
            heading = line.strip()
        if heading:
            heading = re.sub(r'!?\[([^]]+)\]\([^)]+\)', r'\1', heading)
            heading = html.unescape(re.sub(r'<[^>]*>', '', heading)).lower()
            slug = re.sub(r'[^\w\s-]', '', heading).replace(' ', '-')
            # Duplicate headings receive distinct suffixes; existing suffixes also reserve IDs.
            candidate = slug
            index = counts.get(slug, 0)
            while candidate in result:
                index += 1
                candidate = f'{slug}-{index}'
            counts[slug] = index
            result.add(candidate)
    return result


def check(root):
    root = Path(root).resolve()
    docs = sorted(p for p in root.rglob('*.md') if not any(part.startswith('.') and part != '.sdkit' for part in p.relative_to(root).parts))
    links = fragments = 0
    errors = []
    for doc in docs:
        prose = outside_fences(doc.read_text(encoding='utf-8'))
        prose = re.sub(r'(`+)(?!`)(.+?)(?<!`)\1(?!`)', '', prose, flags=re.S)
        targets = [a or b for a, b in LINK.findall(prose)] + REFERENCE.findall(prose)
        for dest in targets:
            url = urlsplit(dest)
            if url.scheme or url.netloc:
                continue
            links += 1
            target = (doc.parent / unquote(url.path)).resolve() if url.path else doc
            if not target.is_relative_to(root) or not target.exists():
                errors.append(f'{doc.relative_to(root)} -> {dest}: missing or outside repository')
            elif url.fragment:
                fragments += 1
                if target.suffix != '.md' or unquote(url.fragment) not in anchors(target.read_text(encoding='utf-8')):
                    errors.append(f'{doc.relative_to(root)} -> {dest}: missing anchor')
    return {'documents': len(docs), 'relative_links': links, 'anchors': fragments, 'errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = check(args.root)
    print(f"Markdown: {result['documents']} files, {result['relative_links']} relative links, {result['anchors']} anchors, {len(result['errors'])} errors")
    for error in result['errors']:
        print(error)
    return int(bool(result['errors']))


if __name__ == '__main__':
    raise SystemExit(main())
