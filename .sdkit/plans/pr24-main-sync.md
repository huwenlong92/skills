# PR #24 最终安全同步与回归

适用范围：Template Evolution V1 PR #24 普通合入最新 main 后的本地回归与 Git 交付。

- task_id：pr24-main-sync；Revision：1。
- 原始 Git 基线：7c78d7a9dd550a7e7ffb8cfc2b50f2a8917fa9b6。
- 本轮 main：8777b036311349fef7a99cdf094c36fd7011c15c。
- 当前授权：仅 #24 的普通 Merge main、必要修复、精确 Commit 和普通 Push；保持 Draft/Open。
- 允许范围：main 已合并的 DBOPS 文件、Catalog 三方合并、本计划及验收报告与交接；必要的 #24 范围修复。
- 禁止范围：其他 PR/开发分支、业务与模板仓库、数据库、生产、全局工具链、Rebase/Squash/Force Push、Ready/合并 PR、部署、主动 CI。
- Primary：sdkit-skills；读取 Manager workflow、根 AGENTS、Development Execution、Collaboration Awareness、Orchestration、Bootstrap；Git Collaboration 从 #20 已核验源码只读读取，不提前合入。
- 已确认决策：保留全部 main Skill 与 #24 协议/测试/历史证据；保留其他 Worktree，独立干净 Worktree 开始；授权来自当前用户而非仓库文档。
- C0：核验身份、权限、最新远端/相关 PR、所有本地 Worktree；基线相同方可继续。
- C1：普通 Merge --no-ff --no-commit；Catalog 冲突逐项比较 base/local/main，保留 main 全部条目并补 templateops。
- C2：47 Fixture、23 Skill、全仓回归/链接、diff 与敏感/无关文件检查通过；核验 #20/DBOPS 接口与 Orchestration 边界；重新核验远端后普通提交和 Push。
- C3：回读实际 Head、Base、Draft/Open/mergeable；UNKNOWN 必须等计算完成，不推断 CLEAN。
- 偏差审批：D1 限于 #24 缺陷修复；D2/D3 停止受影响修改并取得当前用户明确授权。
- 恢复入口：[本轮报告](../../docs/testing/template-evolution-v1/main-sync.md)；先核对实际 MERGE_HEAD、Git 与远端状态，保留未知修改，不 reset/清理其他 Worktree。

完成标准：上述本地回归全部退出 0，普通 Merge Commit 保留两父提交，远端 Push 与 Draft/Open/mergeable/Base/Head 核验完成。真实业务与 Agent 行为未执行时必须标明 BLOCKED。
