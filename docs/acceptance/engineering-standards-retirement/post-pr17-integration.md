# PR #15：PR #17 合并后的 main 同步

适用范围：从本轮初始 Head `99bfb4d8e82f6b37bd1aa18587d02f3fce3d2a0c` 普通 Merge main `8c049239ef90a6b4215ba425cef439168cb43dd2`。本地 Codex 仅负责同步、必要修复、回归、普通 Commit/Push；Ready 与 PR Squash Merge 由 ChatGPT Web 后续执行。

## 冲突与规则保留

四个冲突均为 `.sdkit/DECISIONS.md`、`HANDOFF.md`、`STATUS.md`、`TASKS.md` 中各 PR 的独立追加记录。逐段联合本 PR 与 #17 的决策、报告段落和任务行；每一方原始行序均保留，没有选择整文件 ours/theirs。旧 Draft/旧 main 断言只表示当时验收，不是当前 #17 状态；#17 已 Squash Merge 为本轮 main。

Nuxt API 环境变量、主题目录、21 份新旧共享 Reference 保留。409 组原记录、原覆盖统计与 R027–R044 增量结论未改，R042 仍阻塞、R043 仍部分通过；audit.json SHA-256 保持 314f6bed66360cc67291a28fb8f33c3cd9f5a9e7b7cdf86c2117df270b344ad6。

没有新增或修改 Skill/协议路由语义；业务规则源码只包含已合并 #17 的变更与本 PR 既有内容。复用前轮适用真实行为证据，模型调用 0。开放 #20 涉及共享协议，按 L2 审阅其文件集合；未引入其任何内容，也没有引入其他未合并 PR。

## 实际回归

本轮 Python **118/118**，命令均退出 0：工程协议 17、Manager/迁移 44、DockerOps 41、Markdown 单测 7、ui-design 9。全部 21 Skill、Markdown 相对链接/锚点、Diff、兼容和敏感扫描通过。另外在既有隔离模板归档（6a23a981cc248a742a8521a04da9f466ad0cc25e）实际重跑五组 Node 测试 36/36、退出 0；不代表重新核验模板最新远端或业务构建。结果见 post-pr17-template-tests.json。

命令、数量和退出码见 [本轮检查](post-pr17-checks.json)；[保留核验](post-pr17-preservation.json)逐字节验证双方既有 docs/ 资料（含历史失败）、命中技术栈 Reference、Go 保护规则和共享路由；没有删除或改写原审计/测试证据。

## Git 交付与限制

普通 Merge Commit 同时保留上述初始 Head 和 main 为双亲；包含本报告的 Merge Commit 可由 `git log -1 --format=%H -- docs/acceptance/engineering-standards-retirement/post-pr17-integration.md` 查询，最终精确 Head 以普通 Push 后实时查询及最终回复为准。Push 前必须重查 main/目标 Head/开放 PR，前进时停止覆盖并重新整合。保持 Draft，不执行 Ready 或 PR 合并。

完成标准：本轮静态和兼容性全部通过，普通 Push 后核验 Head/Draft/mergeable。未修改真实全局配置、真实安装、旧规范库或业务仓库；无部署、主动 CI、强推、Rebase 或 Reset Hard。R036/R041–R044 等既有外部系统验收缺口仍保留，不影响本次纯同步的规则一致性结论，不等于旧规范库获准删除。
