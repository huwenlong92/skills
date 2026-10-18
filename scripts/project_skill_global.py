#!/usr/bin/env python3
"""Safely manage one bounded SDKit block in Codex global AGENTS.md."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import re

START = "<!-- sdkit-global-bootstrap:start -->"
END = "<!-- sdkit-global-bootstrap:end -->"
BLOCK = """<!-- sdkit-global-bootstrap:start -->
## SDKit Skill 自动协作

- 开发任务先识别项目 AGENTS.md、真实模板来源、锁定版本与已安装 Skill，按适用的新主入口选择唯一 Primary；旧名称仅用于已验证的历史兼容，禁止重复选择。
- 遵守 huwenlong92/skills 的 standards/skill-orchestration.md、standards/development-execution.md 和 standards/project-skill-bootstrap.md；通过可访问的已安装 Skill 或 Git Provider 读取，不把跨仓库路径当作本地文件。
- 简单任务按需检查；长任务保持计划基线、阶段验收、偏差审批和中断恢复。项目规则优先于全局默认值，规则冲突时停止受影响操作。
- 默认不修改项目 AGENTS.md；仅在项目确需持久化且本次明确授权时最小补齐。禁止自动安装/卸载 Skill、覆盖本地改动、执行数据库变更、提交、合并或部署。
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
        if s.count(begin) != s.count(end) or s.count(begin) > 1:
            findings.append({"type": "invalid-user-marker", "name": name})
    if re.search(r"(?<![\\w-])(?:sdkitgo|nuxtjs|rust-sdcore|vab-admin)(?![\\w-])", s):
        findings.append({"type": "legacy-skill-reference", "action": "review-only"})
    if "engineering-standards" in s:
        findings.append({"type": "legacy-standards-source", "action": "preserve-and-review"})
    return findings

def plan(raw):
    s = raw.decode("utf-8")
    if any(item["type"] == "invalid-user-marker" for item in audit(raw)):
        raise ValueError("malformed existing user marker")
    if s.count(START) != s.count(END) or s.count(START) > 1:
        raise ValueError("invalid managed markers")
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
    home = Path(a.codex_home or os.environ.get("CODEX_HOME") or str(Path.home() / ".codex")).expanduser()
    target = home / "AGENTS.md"
    if not home.is_dir() or home.is_symlink() or target.is_symlink():
        p.error("unsafe CODEX_HOME or target")
    if target.exists() and not target.is_file():
        p.error("target is not a regular file")
    raw = target.read_bytes() if target.exists() else b""
    try:
        new = plan(raw)
    except (UnicodeError, ValueError) as e:
        p.error(str(e))
    findings = audit(raw)
    if not a.apply:
        print(json.dumps({"status": "dry-run", "changed": raw != new, "before_sha256": digest(raw), "after_sha256": digest(new), "findings": findings}))
        return
    if not a.authorized or not a.expected_sha256 or a.expected_sha256 != digest(raw):
        p.error("apply requires authorization and matching dry-run SHA")
    if raw == new:
        print(json.dumps({"status": "unchanged", "sha256": digest(raw)}))
        return
    if target.exists() and target.read_bytes() != raw:
        p.error("concurrent change")
    fd, tmpname = tempfile.mkstemp(prefix=".AGENTS.", dir=home)
    os.close(fd)
    tmp = Path(tmpname)
    backup = None
    try:
        if target.exists():
            fd, backupname = tempfile.mkstemp(prefix="sdkit-codex-agents-backup-", suffix=".md")
            os.close(fd)
            backup = Path(backupname)
            backup.write_bytes(raw)
            backup.chmod(0o600)
        tmp.write_bytes(new)
        tmp.chmod(stat.S_IMODE(target.stat().st_mode) if target.exists() else 0o600)
        if target.exists() and target.read_bytes() != raw:
            raise RuntimeError("concurrent change")
        tmp.replace(target)
        if target.read_bytes() != new:
            raise RuntimeError("verification failed")
    finally:
        if tmp.exists():
            tmp.unlink()
    print(json.dumps({"status": "updated", "sha256": digest(new), "backup": str(backup) if backup else None, "findings": findings}))

if __name__ == "__main__":
    main()
