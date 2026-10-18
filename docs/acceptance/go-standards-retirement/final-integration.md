# PR #17 专题 A 最终集成验收

适用范围：本 PR 的最新 main 集成、定向修复及最终本地验收。初始 Head `4959778ae5380836fd810f2ac7f03ed1c9baab46`，main `77e0664fcbb0943f9bd4aa8cad96ab0d14fa4c3a`。普通 Merge 在独立 Worktree 完成，无文本冲突，未使用 ours/theirs、Reset Hard、Rebase 或 Force Push。

## 结果与范围

- Go 模板实时 main `924078a0b011e6a5434b5f9805befca82a225126` 的只读归档确认：go.mod 使用 sdkit v0.1.28；app/admin/handler 下确有 system/security/ops；app/models/base.go 定义两个基础设施 schema，模型使用匹配 helper。没有假定地理注册表已预置。
- 保留 PR 的本地 replace/发布退出、基础设施 handler 保护与按需地理字段独立语义；旧 go.work 只读核验、不删除。两个旧新入口的原 description 不变。
- D1 修复：原规则仅禁止业务 model 进入 system/system_data，未完整覆盖业务清理动作。本轮在两套 database/safety.md 同步补齐精确对象授权、开发库边界、默认 public 审计和清理后基础设施不变核验。正式库 AI 禁止连接/间接操作门禁保留。此补齐不改变 Skill 路由。
- 未连接任何数据库、未运行 Go 消费方构建；这是文档和模板源码一致性验收，不能据此声称数据库执行安全已实测。没有无法解决的合并语义冲突。


本轮核心回归共 **118 个 unittest**，全部通过；21 Skill 校验和 Markdown 相对链接/锚点零错误。命令输出与数量见 [最终检查](final-integration-checks.json)。

| 命令 | 数量 | 退出码 |
|---|---:|---:|
| `python3 -m unittest discover -s scripts -p test_engineering_protocols.py -v` | 17 | 0 |
| `python3 -m unittest discover -s skills/sdkit-skills/scripts -p test_*.py -v` | 44 | 0 |
| `python3 -m unittest discover -s skills/dockerops/scripts -p test_*.py -v` | 41 | 0 |
| `python3 -m unittest discover -s scripts -p test_markdown_links.py -v` | 7 | 0 |
| `python3 -m unittest discover -s scripts -p test_ui_design.py -v` | 9 | 0 |
| `python3 skills/sdkit-skills/scripts/manager.py validate --all` | 静态检查 | 0 |
| `python3 scripts/check_markdown_links.py` | 静态检查 | 0 |
| `git diff --check` | 静态检查 | 0 |

[兼容性记录](final-integration-compatibility.json)：历史验收资料 3 文件逐字节保留。详细 Reference 除新旧身份说明 repository.md 外一致；main 中知识/UI/编排/开发执行入口不变。路由语义无实质变化，复用 main 已有 T01–T10、U01–U12 与知识 16 场景的适用证据；旧迁移探针 BLOCKED 历史仍保留，本轮模型调用 0，不将静态与原生发现冒充模型重测。

## Git 与权限

- 开始核验：main 未保护，适用规则集为空，当前账号具有 Push 权限；四个目标 PR 为 Draft/Open、MERGEABLE/CLEAN，其他三个相关分支未混入本 PR。GitHub 分支/Head/权限状态均为按需快照，不能代替最终实时核验。
- Push 前必须核验 main、目标 Head 与相关开放 PR；未预期前进时停止覆盖。普通 Commit/Push 后保持 Draft/Open；最终 Head、Merge Commit 和 mergeable 以交付时 GitHub 查询及最终回复为准。
- 未合并 PR、Ready、部署或主动 CI；未修改真实全局 AGENTS、已安装 Skill、业务仓库或旧规范库。原工作区未知文件和其他 Worktree 保留。

## 完成标准与未完成边界

本地指定门禁、兼容性、历史证据保留和源码一致性核验通过。当前源码具备本 PR 范围的技术合并准备条件；不代表真实业务构建/浏览器/数据库验收、跨 Agent 全量路由或旧规范库删除已通过。后续真实配置整理、安装更新、合并及删除均须单独授权。
