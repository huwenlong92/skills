# PR #18 最终集成修复

适用范围：PR #19 合并后，将最新 main 安全整合进 PR #18。任务 ID `pr18-final-integration`，revision 1。

- 原始 Git 基线：`ad8914562ebf2b9228c43b35b4f8383414609234`；目标 main：`f1df67a6ff070fd4991a16e6135bf3902ee3e0da`。
- 用户已授权：隔离 Worktree、普通 Merge、逐项修复、全部指定本地检查、Commit 和普通 Push。保持 Draft，不合并 PR、不部署、不主动 CI、不强推、不 Reset Hard、不覆盖其他工作区。
- 范围：Foundry 入口、Orchestration、必要 `.sdkit/` 状态与本轮集成报告；保留两方全部有效测试及失败历史。禁止纳入 #14–#17 的独立改动。
- 命中：sdkit-skills 入口/管理流程；Foundry 入口/capture/prototypes；WikiOps 入口/answer/capture；sdkit-ui-design 入口；协作感知、Knowledge Retrieval & Capture、Orchestration、Development Execution。
- 决策：合并 description 的产品设计规范与知识检索/候选职责，保持纯设计 Primary 为 sdkit-ui-design、产品协作 Primary 为 Foundry、通用知识 Primary 为 WikiOps。只做已有规则的文本联合，不增加触发条件、权限或执行职责。
- 偏差：范围内缺陷 D1 必须修复重验；路由语义变化只重测受影响模型场景；D2/D3 扩围停止受影响工作并取得授权。

| 阶段 | 验收 | 状态 |
|---|---|---|
| C0 | 核验 main、#18、#19、开放 PR 与相关文件；新隔离 Worktree | verified |
| C1 | 手工合并 5 个冲突文件，复核自动合并 Orchestration；保留双方知识与 UI 职责和证据 | verified |
| C2 | 工程协议、Manager、ui-design、Markdown、21 Skill 及相关既有本地回归；证据完整性与三类路由审查 | verified；195 unittest、21 Skill，命令退出 0，证据差异 0 |
| C3 | 远端前进检查、普通 Commit/Push、main 祖先关系、Draft/Open、GitHub mergeable | 待验证 |

执行命令、退出码与逐项冲突决议见 [集成报告](../../docs/testing/ui-design-v1/final-integration.md)。恢复必须先核对实际 Git，再从未验收阶段继续；禁止以历史快照代替当前证据。

完成标准：全部指定检查成功，main 已是祖先，双方历史证据未删改，普通推送后 #18 Draft/Open 且 GitHub MERGEABLE；静态检查不冒充本轮真实模型联合行为。
