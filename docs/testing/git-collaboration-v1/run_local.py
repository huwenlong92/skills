"""从完整源码运行全仓 Python 测试、Manager 和 Markdown 检查并保存脱敏结果。

运行：python3 docs/testing/git-collaboration-v1/run_local.py --output <新目录>
输出目录必须不存在；不调用模型、远端 Git、CI 或用户配置。
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    records = []
    with tempfile.TemporaryDirectory(prefix="git-collaboration-regression-") as temp:
        temp = str(Path(temp).resolve())
        env = dict(os.environ, TMPDIR=temp, PYTHONDONTWRITEBYTECODE="1")
        env["GIT_COLLABORATION_EVIDENCE"] = str(output / "cli-results.json")
        tests = sorted(root.glob("scripts/test*.py")) + sorted(root.glob("skills/**/test*.py"))
        commands = [["python3", str(p.relative_to(root)), "-v"] for p in tests]
        commands += [["python3", "skills/sdkit-skills/scripts/manager.py", "validate", "--all"],
                     ["python3", "scripts/check_markdown_links.py"]]
        for command in commands:
            p = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True)
            text = (p.stdout + p.stderr).replace(str(root), "<source>").replace(temp, "<temp>")
            count = re.search(r"Ran (\d+) tests?", text)
            records.append({"command": " ".join(command), "exit_code": p.returncode,
                            "tests_run": int(count[1]) if count else None, "output": text})
            print(command[1], p.returncode, int(count[1]) if count else "", flush=True)
    result = {"environment": "TMPDIR=canonical isolated directory; PYTHONDONTWRITEBYTECODE=1",
              "commands": records, "tests_run": sum(x["tests_run"] or 0 for x in records),
              "failed_commands": sum(x["exit_code"] != 0 for x in records)}
    (output / "local-results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return bool(result["failed_commands"])


if __name__ == "__main__":
    raise SystemExit(main())
