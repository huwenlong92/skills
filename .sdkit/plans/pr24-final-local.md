# PR #24 本地最终技术验收

适用范围：Template Evolution V1 Draft PR #24 的本地协议验收与范围内修复。

- task_id：pr24-final-local；Revision：1。
- 原始基线：078d2222c9d7aa80375d62ced328670d4e9a577e；main：226465e5f951cc1f1394a1c91e4c3f682f822b83。
- 当前用户授权：独立 Worktree 验收；仅 #24 范围修复、精确暂存、提交、普通 Push；保持 Draft。
- 允许范围：协议脚本、Fixture、templateops references、本验收报告和交接。
- 禁止范围：其他 PR 分支、业务或模板仓库、全局工具链、合并、部署、主动 CI、破坏性 Git。
- Primary：sdkit-skills；命中 workflow、Template Evolution 全部 references 与根 Git/Orchestration/Development Execution 协议。
- 阶段依赖：实时状态与工作区保护 → 原有 Fixture → 复现/修复 → 全仓与临时联合兼容 → 普通提交/Push 核验。
- 验收标准：原有 28 项及新增回归、Manager/Catalog/Frontmatter、链接、diff、敏感路径全部通过；#20/#21 联合组合通过；未知状态停止受影响写入。
- 偏差：D1，追加 19 项回归并修复已复现的 9 个缺口；未扩大产品能力，不实现 Apply。
- D2/D3 必须先取得当前用户授权；禁止以测试通过替代真实业务或 Agent 行为验收。
- 恢复入口：[报告](../../docs/testing/template-evolution-v1/final-local.md)，恢复时核验实际 Git 和远端 Head；不得覆盖其他 Worktree。

阶段状态和命令退出码以报告及其 JSON 证据为准；最终交付 SHA 以 Git/Provider 为准。

完成标准：上述本地条件全部满足且普通 Push 的实际远端 Head 已核验；保持 Draft/Open，未完成的外部行为测试明确 BLOCKED。
