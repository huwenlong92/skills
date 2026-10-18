# 已核验状态

最后核验：2026-10-18。

## 本轮真实行为验收

- [报告与 T01–T10 证据](../docs/testing/engineering-v1/2026-10-18-report.md)：10 个真实场景，PASS 10 / FAIL 0 / BLOCKED 0，14 次 Codex 模型调用成功。模型 gpt-6.1-sol，CLI 0.163.0。
- 未发现未经批准的计划、架构或范围扩展；规范 I/O 偏差被识别并修正，失败和工具缺失未伪标 verified，恢复核验实际 Git、revision 与未知改动。
- T09 初轮因 Git 元数据保护 BLOCKED，已保留；经工具审查的临时 .git/ 显式目录授权后，真实 Fetch 成功并确认落后 1 个提交。模型保留未知修改并暂停快进。没有修改持久审批配置、绕过安全检查或关闭沙箱。
- 仅受控虚构夹具通过，不代表所有 Agent、原生全局自动发现或 PR #12 全技术栈路由已验证。原始日志只在本地，提交材料已脱敏。

## 离线回归

| 命令 | 实际结果 |
|---|---|
| `python3 -m unittest discover -s scripts -p 'test_engineering_protocols.py' -v` | 17 项通过，退出 0 |
| `python3 -m unittest discover -s skills/sdkit-skills/scripts -p 'test_*.py' -v` | 37 项通过，退出 0 |
| `python3 skills/sdkit-skills/scripts/manager.py validate --all` | 12 Skill 通过，退出 0 |
| Markdown 相对链接（协议、状态与真实行为证据） | 检查通过，退出 0 |
| `git diff --check` | 退出 0 |

## Git 与兼容性

- 本轮执行基线：PR #13 Head 913d0db61a27b6124f4c7beddb29435fb2f6064e，Draft/Open；main 537d6dad8220d3bc05596ff8051faeb7946084eb 已在其历史中。
- PR #12 最新核验 Head e912b9df9b11da45c5cf1069ea0674286869af91，Draft/Open；文件集合无重叠，L1 显式依赖。本轮未改动其分支或重做完整验收；前轮独立叠加结果仅适用于当时的 Head。
- 本轮只补充报告、验收入口、链接检查范围与状态记录；没有需要修改的协议语义或技术栈架构缺陷。
- 本轮技术验收条件已满足；Git 交付与最新 Draft/Open 状态必须从 PR 当前 Head 核验。未主动触发 CI、合并或部署。

前轮模型连接/审批阻塞已在用户新增发送授权和本轮真实调用后解除；历史证据保留在执行计划。
