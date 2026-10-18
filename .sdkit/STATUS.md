# 已核验状态

最后核验：2026-10-18。

- main：537d6dad8220d3bc05596ff8051faeb7946084eb。PR #13 原始 Head：6b519574bb2fe63a595be84a4e054c3080e92b82，Draft/Open，查询时 MERGEABLE；main 已是其祖先，无需同步提交。
- PR #12：836e555a1cfc51e1f9f76e261f1e2fbf83796ee5，Draft/Open。L1 显式依赖，无修改文件重叠；`git merge-tree --write-tree` 计算退出 0，无文本冲突。仅创建 detached 测试目录叠加文件，未合并或改动其分支。
- 修复：新旧主入口选择、版本与 lite 边界、未实现 dbops 依赖、环境解析、计划持久化及阶段证据门禁；纠正一个与原文不符的测试断言，扩充链接与回归检查。

## 本地命令证据

| 命令 | PR #13 单独结果 | 叠加 PR #12 结果 |
|---|---|---|
| `python3 -m unittest discover -s scripts -p 'test_engineering_protocols.py' -v` | 17 通过，退出 0 | 17 通过，退出 0 |
| `python3 skills/sdkit-skills/scripts/manager.py validate --all` | 12 Skill，退出 0 | 20 Skill，退出 0 |
| `python3 -m unittest discover -s skills/sdkit-skills/scripts -p 'test_*.py' -v` | 37 通过，退出 0 | 37 通过，退出 0 |
| 协议测试中的 `test_local_relative_links` | AGENTS、全部 standards、全部 .sdkit 链接存在且未越出仓库，退出 0 | 同左，退出 0 |
| `git diff --check` | 退出 0 | 以叠加内容测试，未修改分支历史 |

初测 15 项中 1 项因“不自动安装”与“不得自动安装未授权 Skill”措辞不符而失败；修复断言检查完整禁止规则，并未弱化协议。Python 测试是静态契约与本地工具回归，不能证明自然语言路由正确。

人工检查五份协议后，未发现剩余的授权、Git 门禁或恢复流程冲突。相对链接覆盖内联与引用式目标，排除代码块；不声称已验证外部 URL 内容或运行时触发。扫描修改文件未发现个人绝对路径或凭据模式；人工复核示例为虚构代码。

## 未验证项目

Codex CLI 0.163.0 的真实隔离会话启动后，模型路由发现失败，退出 1，未产生实现。联网重试被自动审批拒绝，原因是尚未明确授权将临时协议与虚构代码发往模型服务；已请求授权。真实十个行为场景、自动发现、新旧入口自然语言选择均未验证。

[行为验收步骤](../standards/engineering-protocol-acceptance.md) 提供夹具及十个场景。夹具生成实际退出 0，初始 unittest 按预期失败并退出 1；这只是夹具检查，不能算 Agent 行为通过。

本次只交付 Draft 修复；尚不满足包含真实行为验证的完整 Ready for Review 条件。未主动触发 CI、合并或部署；提交与 Push 的最终结果以 Git/PR 实时状态为准。
