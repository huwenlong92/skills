#!/usr/bin/env python3
"""Conservative AGENTS.md Skill bootstrap; explicit opt-in, no network or installs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile

START = "<!-- sdkit-skill-bootstrap:start -->"
END = "<!-- sdkit-skill-bootstrap:end -->"
MAPPINGS = {"nuxtjs": "sdbase-nuxtjs-portal", "rust-sdcore": "sdkit-rust-core", "sdkitgo": "sdbase-go", "sdkit": "sdkit-go-core", "vab-admin": "sdbase-vab-admin"}
SKILLS = set(MAPPINGS.values()) | {"sdbase-lite", "sdbase-admin-lite", "sdbase-flutter-app"}
def sha(data):
    return hashlib.sha256(data).hexdigest()

def plan(raw, skill, template, revision, old):
    text = raw.decode("utf-8")
    if text.count(START) != text.count(END) or text.count(START) > 1:
        raise ValueError("malformed bootstrap markers")
    if old and MAPPINGS.get(old) != skill:
        raise ValueError("invalid old/new mapping")
    # Existing unmanaged legacy references require human review: do not rewrite custom prose.
    if old and re.search(r"(?<![\w-])" + re.escape(old) + r"(?![\w-])", text.replace(START, "").replace(END, "")):
        raise ValueError("legacy reference outside managed block; review required")
    block = ("\n" + START + "\n## SDKit Skill 接入\n\n"
             + f"- 已核验模板：`{template}`，版本：`{revision}`。\n"
             + f"- Primary Skill：`{skill}`；必须核验实际项目身份与已安装 Skill。\n"
             + "- 共享协议权威来源：`huwenlong92/skills` 的 `standards/skill-orchestration.md`、`standards/development-execution.md`、`standards/project-skill-bootstrap.md`；"
             + "仅通过可用的已安装 Skill 或 Git Provider 读取，不把跨仓库路径当作本地相对链接。\n"
             + "- 必要规范无法读取时停止受影响操作；本入口不授权提交、数据库写入或部署。\n"
             + END + "\n")
    if START in text:
        a, b = text.split(START, 1)
        _, c = b.split(END, 1)
        result = a.rstrip("\n") + block + c.lstrip("\n")
    else:
        result = text.rstrip("\n") + "\n" + block
    return result.encode("utf-8")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--skill", required=True, choices=sorted(SKILLS))
    p.add_argument("--template", required=True)
    p.add_argument("--revision", required=True)
    p.add_argument("--old-skill", choices=sorted(MAPPINGS))
    p.add_argument("--expected-sha256")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--authorized", action="store_true")
    args = p.parse_args()
    root = Path(args.project).resolve()
    target = root / "AGENTS.md"
    if not root.is_dir() or target.is_symlink():
        p.error("invalid project or symlink AGENTS.md")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", args.template) or not re.fullmatch(r"[A-Za-z0-9_.-]{7,80}", args.revision):
        p.error("template identity/revision must be verified identifiers")
    raw = target.read_bytes() if target.exists() else b""
    try:
        new = plan(raw, args.skill, args.template, args.revision, args.old_skill)
    except (UnicodeError, ValueError) as exc:
        p.error(str(exc))
    changed = raw != new
    if args.apply and changed:
        if not args.authorized or not args.expected_sha256:
            p.error("--apply requires --authorized and --expected-sha256")
        if args.expected_sha256 != sha(raw):
            p.error("stale source hash; refusing write")
        if target.exists() and target.read_bytes() != raw:
            p.error("concurrent change detected")
        backup = None
        if target.exists():
            import os
            fd, name = tempfile.mkstemp(prefix="sdkit-agents-backup-", suffix=".md")
            os.close(fd)
            backup = Path(name)
            backup.write_bytes(raw)
        import os
        fd, name = tempfile.mkstemp(prefix=".AGENTS.", dir=root)
        os.close(fd)
        temp = Path(name)
        try:
            temp.write_bytes(new)
            if target.exists():
                temp.chmod(target.stat().st_mode & 0o777)
            if target.exists() and target.read_bytes() != raw:
                raise RuntimeError("concurrent change detected")
            temp.replace(target)
            if target.read_bytes() != new:
                raise RuntimeError("post-write verification failed")
        finally:
            if temp.exists():
                temp.unlink()
        print(json.dumps({"status": "updated", "backup": str(backup) if backup else None, "sha256": sha(new)}, ensure_ascii=False))
    else:
        print(json.dumps({"status": "dry-run" if not args.apply else "unchanged", "changed": changed, "before_sha256": sha(raw), "after_sha256": sha(new)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
