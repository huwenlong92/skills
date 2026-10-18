# PR #14 专题 A 最终集成计划

适用范围：本 PR 最新 main 集成、定向修复、静态和兼容性验收。任务 ID `pr14-topic-a-final`，revision 1；原始基线 `50ba0de9d26d1b471068607ec4a5e11ce6274b9e`，main `77e0664fcbb0943f9bd4aa8cad96ab0d14fa4c3a`。

- 用户授权必要修复、普通 Merge、Commit/Push；只在本 PR 独立 Worktree 操作，禁止合并 PR、Ready、部署、主动 CI、真实全局配置、真实安装或业务仓库写入、旧规范库删除。
- 范围为本 PR 原有文件、命中 Reference、定向回归与本计划/报告。禁止纳入其他 PR 尚未合并的内容。历史审计、失败及成功测试均保留。
- 命中 sdkit-skills 管理流程、目标主/旧入口与修改 Reference，以及根 AGENTS、Orchestration、Development Execution、Project Collaboration、Collaboration Awareness。
- D1 范围内缺陷修复重验；D2/D3 重大语义或架构冲突停止受影响修改。路由语义不变时复用既有行为证据，不把历史 BLOCKED 改成 PASS。

| 阶段 | 验收 | 状态 |
|---|---|---|
| C0 | 权威 main/Head、开放 PR、权限/保护、工作区/锁 | verified |
| C1 | 普通 Merge main、语义审查及必要修复 | verified |
| C2 | 相关单元测试、21 Skill、链接/锚点、兼容/证据/敏感扫描 | verified |
| C3 | Push 前远端复核、普通 Commit/Push、Draft 与 mergeable | verified；普通推送 `3045df85163d90bb0977ced0504e0338ebe55f74` 后 Draft/Open、MERGEABLE/CLEAN；交接提交的最终 Head 以最终查询为准 |

命令、数量、退出码与未完成边界见 [最终报告](../../docs/acceptance/bootstrap-standards-retirement/final-integration.md)。恢复时核对真实 Git/远端，再从未验收阶段继续。完成标准：本地必需门禁通过且历史证据不变；远端 Draft/Open、main 是祖先，最终交付状态单独核验。技术可合并不等于授权合并。

## revision 2：#17 合并后同步

保留 revision 1 原始基线。用户授权从 `cb167d335c158bf24af7a6324c7b69735d3de956` 普通合入 main `8c049239ef90a6b4215ba425cef439168cb43dd2`，仅处理本 PR 集成冲突及必要修复/回归/Commit/普通 Push。命中规范与原计划相同；范围增加本轮报告与结果，不引入其他未合并 PR。禁止 Ready/合并/部署/主动 CI、真实配置或安装、业务与旧规范库写入；D2/D3 停止受影响操作。

C0 已核验：目标与其他 Head、main、权限及干净 Worktree；C1 verified：四个独立历史追加冲突逐段联合。C2 verified：本 PR 回归和证据保留均通过，命令退出 0。C3 待验证：普通提交/推送与远端状态。恢复入口为 [本轮报告](../../docs/acceptance/bootstrap-standards-retirement/post-pr17-integration.md)；以实际 Git 和测试证据为准。
