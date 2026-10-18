#!/usr/bin/env python3
"""Safely manage one bounded SDKit block in Codex global AGENTS.md."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
from project_skill_io import apply, read, markers

START = "<!-- sdkit-global-bootstrap:start -->"
END = "<!-- sdkit-global-bootstrap:end -->"
BLOCK = """<!-- sdkit-global-bootstrap:start -->
## SDKit Skill 自动协作

- 开发任务先识别项目 AGENTS.md、真实模板来源、锁定版本与已安装 Skill，按适用的新主入口选择唯一 Primary；旧名称仅用于已验证的历史兼容，禁止重复选择。
- 遵守 huwenlong92/skills 的 standards/skill-orchestration.md、standards/development-execution.md 和 standards/project-skill-bootstrap.md；从已核验的完整 skills 源码仓库或 Git Provider 读取；独立 Skill 安装不包含根 standards/，不把跨仓库路径当作本地文件。
- 简单任务按需检查；长任务保持计划基线、阶段验收、偏差审批和中断恢复。项目规则优先于全局默认值，规则冲突时停止受影响操作。
- 默认不修改项目 AGENTS.md；仅在项目确需持久化且本次明确授权时最小补齐。禁止覆盖未知本地改动；本入口不授予 Skill 安装/卸载、Git 写入、数据库变更或发布权限，这些操作必须依据本次明确授权。
- 规范或项目身份无法核实时报告缺口，不假称已加载或验证。
<!-- sdkit-global-bootstrap:end -->
"""

def digest(b):
    return hashlib.sha256(b).hexdigest()

KNOWN_BLOCKS = ("no-superpowers", "wiki-knowledge-vault", "git-initialization-rules", "database-operation-rules", "local-web-development-rules", "engineering-standards-rules", "gitnexus-index-only")

def audit(raw):
    s = raw.decode("utf-8")
    findings = []
    for name in KNOWN_BLOCKS:
        begin, end = f"<!-- BEGIN: {name} -->", f"<!-- END: {name} -->"
        if s.count(begin) != s.count(end) or s.count(begin) > 1 or (begin in s and end in s and s.index(begin) > s.index(end)):
            findings.append({"type": "invalid-user-marker", "name": name})
    if re.search(r"(?<![\w-])(?:sdkit|sdkitgo|nuxtjs|rust-sdcore|vab-admin)(?![\w-])", s):
        findings.append({"type": "legacy-skill-reference", "action": "review-only"})
    if "engineering-standards" in s:
        findings.append({"type": "legacy-standards-source", "action": "preserve-and-review"})
    return findings

def plan(raw):
    s = raw.decode("utf-8")
    if any(item["type"] == "invalid-user-marker" for item in audit(raw)):
        raise ValueError("malformed existing user marker")
    markers(s, START, END)
    if START in s:
        before, tail = s.split(START, 1)
        _, after = tail.split(END, 1)
        return (before + BLOCK.rstrip("\n") + after).encode("utf-8")
    separator = "" if not s else ("" if s.endswith("\n\n") else "\n" if s.endswith("\n") else "\n\n")
    return (s + separator + BLOCK).encode("utf-8")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--codex-home")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--authorized", action="store_true")
    p.add_argument("--expected-sha256")
    a = p.parse_args()
    try:
        home, original = read(a.codex_home or os.environ.get("CODEX_HOME") or str(Path.home() / ".codex"))
        raw = original[1]
        new = plan(raw)
        findings = audit(raw)
        if not a.apply:
            result = {"status": "dry-run", "changed": raw != new, "before_sha256": digest(raw), "after_sha256": digest(new), "findings": findings,
                      "draft": new.decode("utf-8")}
        else:
            result = {**apply(home, original, new, a.authorized, a.expected_sha256), "findings": findings}
    except (OSError, UnicodeError, ValueError) as exc:
        p.error(str(exc))
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
