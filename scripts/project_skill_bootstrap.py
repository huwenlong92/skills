#!/usr/bin/env python3
"""Conservative AGENTS.md Skill bootstrap; explicit opt-in, no network or installs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from project_skill_io import apply, read, markers

START = "<!-- sdkit-skill-bootstrap:start -->"
END = "<!-- sdkit-skill-bootstrap:end -->"
MAPPINGS = {"nuxtjs": "sdbase-nuxtjs-portal", "rust-sdcore": "sdkit-rust-core", "sdkitgo": "sdbase-go", "sdkit": "sdkit-go-core", "vab-admin": "sdbase-vab-admin"}
SKILLS = set(MAPPINGS.values()) | {"sdbase-lite", "sdbase-admin-lite", "sdbase-flutter-app"}
def sha(data):
    return hashlib.sha256(data).hexdigest()

def plan(raw, skill, template, revision, old):
    text = raw.decode("utf-8")
    parts = markers(text, START, END)
    if old and MAPPINGS.get(old) != skill:
        raise ValueError("invalid old/new mapping")
    # Existing unmanaged legacy references require human review: do not rewrite custom prose.
    if old and re.search(r"(?<![\w-])" + re.escape(old) + r"(?![\w-])", "".join(parts) if parts else text):
        raise ValueError("legacy reference outside managed block; review required")
    block = (START + "\n## SDKit Skill 接入\n\n"
             + f"- 已核验模板：`{template}`，版本：`{revision}`。\n"
             + f"- Primary Skill：`{skill}`；必须核验实际项目身份与已安装 Skill。\n"
             + "- 共享协议权威来源：`huwenlong92/skills` 的 `standards/skill-orchestration.md`、`standards/development-execution.md`、`standards/project-skill-bootstrap.md`；"
             + "仅从已核验的完整 skills 源码仓库或 Git Provider 读取，不把跨仓库路径当作本地相对链接。\n"
             + "- 必要规范无法读取时停止受影响操作；本入口不授权提交、数据库写入或部署。\n"
             + END + "\n")
    if parts:
        result = parts[0] + block.rstrip("\n") + parts[1]
    else:
        separator = "" if not text or text.endswith("\n\n") else "\n" if text.endswith("\n") else "\n\n"
        result = text + separator + block
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
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", args.template) or not re.fullmatch(r"[A-Za-z0-9_.-]{7,80}", args.revision):
        p.error("template identity/revision must be verified identifiers")
    try:
        root, original = read(args.project)
        raw = original[1]
        new = plan(raw, args.skill, args.template, args.revision, args.old_skill)
        if args.apply:
            result = apply(root, original, new, args.authorized, args.expected_sha256)
        else:
            result = {"status": "dry-run", "changed": raw != new, "before_sha256": sha(raw), "after_sha256": sha(new), "draft": new.decode("utf-8")}
    except (OSError, UnicodeError, ValueError) as exc:
        p.error(str(exc))
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
