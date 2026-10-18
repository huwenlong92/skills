# PR #14：PR #17 合并后的 main 同步

适用范围：从本轮初始 Head `cb167d335c158bf24af7a6324c7b69735d3de956` 普通 Merge main `8c049239ef90a6b4215ba425cef439168cb43dd2`。本地 Codex 仅负责同步、必要修复、回归、普通 Commit/Push；Ready 与 PR Squash Merge 由 ChatGPT Web 后续执行。

## 冲突与规则保留

四个冲突均为 `.sdkit/DECISIONS.md`、`HANDOFF.md`、`STATUS.md`、`TASKS.md` 中各 PR 的独立追加记录。逐段联合本 PR 与 #17 的决策、报告段落和任务行；每一方原始行序均保留，没有选择整文件 ours/theirs。旧 Draft/旧 main 断言只表示当时验收，不是当前 #17 状态；#17 已 Squash Merge 为本轮 main。

Bootstrap 全局原文字节保护、唯一托管块、授权/SHA、并发锁、备份/恢复/权限与异常文件测试保留；39 项 Bootstrap 测试本轮实际通过。源 scripts/ 未改，复用前轮隔离 21 Skill 安装更新与 16+5 原生发现证据，不冒称本轮重做模型或发现。

没有新增或修改 Skill/协议路由语义；业务规则源码只包含已合并 #17 的变更与本 PR 既有内容。复用前轮适用真实行为证据，模型调用 0。开放 #20 涉及共享协议，按 L2 审阅其文件集合；未引入其任何内容，也没有引入其他未合并 PR。

## 实际回归

本轮 Python **157/157**，命令均退出 0：工程协议 17、Manager/迁移 44、DockerOps 41、Markdown 单测 7、ui-design 9、Bootstrap 39。全部 21 Skill、Markdown 相对链接/锚点、Diff、兼容和敏感扫描通过。

命令、数量和退出码见 [本轮检查](post-pr17-checks.json)；[保留核验](post-pr17-preservation.json)逐字节验证双方既有 docs/ 资料（含历史失败）、命中技术栈 Reference、Go 保护规则和共享路由；没有删除或改写原审计/测试证据。

## Git 交付与限制

普通 Merge Commit 同时保留上述初始 Head 和 main 为双亲；包含本报告的 Merge Commit 可由 `git log -1 --format=%H -- docs/acceptance/bootstrap-standards-retirement/post-pr17-integration.md` 查询，最终精确 Head 以普通 Push 后实时查询及最终回复为准。Push 前必须重查 main/目标 Head/开放 PR，前进时停止覆盖并重新整合。保持 Draft，不执行 Ready 或 PR 合并。

完成标准：本轮静态和兼容性全部通过，普通 Push 后核验 Head/Draft/mergeable。未修改真实全局配置、真实安装、旧规范库或业务仓库；无部署、主动 CI、强推、Rebase 或 Reset Hard。R036/R041–R044 等既有外部系统验收缺口仍保留，不影响本次纯同步的规则一致性结论，不等于旧规范库获准删除。
