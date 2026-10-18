# PR #14 专题 A 最终集成验收

适用范围：本 PR 的最新 main 集成、定向修复及最终本地验收。初始 Head `50ba0de9d26d1b471068607ec4a5e11ce6274b9e`，main `77e0664fcbb0943f9bd4aa8cad96ab0d14fa4c3a`。普通 Merge 在独立 Worktree 完成，无文本冲突，未使用 ours/theirs、Reset Hard、Rebase 或 Force Push。

## 结果与范围

- AGENTS 自动合并无冲突；保留 main 的知识检索/沉淀入口和 Bootstrap 的独立授权门禁。全局区块的正文、唯一 Primary 选择及项目级默认只读语义均不变，没有新增路由语义。
- Bootstrap 原 35 项测试保留，新增 4 项实际临时文件回归：FIFO 目标拒绝、锁符号/硬链接拒绝、FIFO 锁拒绝、replace 后持久化失败时保留 journal/backup 并阻断重试，人工核验夹具后显式授权恢复。本轮 Bootstrap **39/39**，与通用 118 项合计 **157/157**。
- 七类虚构个人规则逐字节保留；托管区块唯一、重复执行零差异；无授权/过期 SHA/no-op 无授权阻断；并发内容/删除/创建/权限/inode/符号链接替换阻断；备份 0600、恢复目录 0700、目标原权限保留、新文件 0600、异常 pending 保留均通过。咨询锁不承诺阻止不合作写入者的最终检查窗口，原边界说明保留。
- 隔离 Codex Home 实际运行 initialize 与 skills/list：21 个 Skill 独立安装/更新通过，主入口 **16/16**、旧兼容 **5/5**，错误 0，见 [本轮原生发现](final-native-discovery.json)。仅虚构全局配置，没有真实认证或模型调用；发现结果不等于隐式模型选择。
- 真实全局 AGENTS 只读核验仍含旧库来源；已安装 standards-bootstrap 的说明仍引用旧库。没有运行它、修改它或整理真实全局配置。原工具只追加有界区块，不会自动移除旧工程规范区块；必须在单独授权下人工审阅整理草案，保留全部个人规则并复验幂等/权限/恢复。
- 原始审计证据、旧模型探针 BLOCKED 和所有失败历史保留。Bootstrap 工具本轮不依赖旧库作为日常权威，但真实全局与旧安装的退出尚未执行，不能声明旧规范库可删除。没有未解决的本 PR 技术冲突。


本轮核心回归共 **157 个 unittest**，全部通过；21 Skill 校验和 Markdown 相对链接/锚点零错误。命令输出与数量见 [最终检查](final-integration-checks.json)。

| 命令 | 数量 | 退出码 |
|---|---:|---:|
| `python3 -m unittest discover -s scripts -p test_engineering_protocols.py -v` | 17 | 0 |
| `python3 -m unittest discover -s skills/sdkit-skills/scripts -p test_*.py -v` | 44 | 0 |
| `python3 -m unittest discover -s skills/dockerops/scripts -p test_*.py -v` | 41 | 0 |
| `python3 -m unittest discover -s scripts -p test_markdown_links.py -v` | 7 | 0 |
| `python3 -m unittest discover -s scripts -p test_ui_design.py -v` | 9 | 0 |
| `python3 -m unittest discover -s scripts -p test_project_skill_*.py -v` | 39 | 0 |
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
