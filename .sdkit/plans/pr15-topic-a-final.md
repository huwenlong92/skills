# PR #15 专题 A 最终集成计划

适用范围：本 PR 最新 main 集成、定向修复、静态和兼容性验收。任务 ID `pr15-topic-a-final`，revision 1；原始基线 `744d022ad5680c6702c9e39354aa88184e9f606f`，main `77e0664fcbb0943f9bd4aa8cad96ab0d14fa4c3a`。

- 用户授权必要修复、普通 Merge、Commit/Push；只在本 PR 独立 Worktree 操作，禁止合并 PR、Ready、部署、主动 CI、真实全局配置、真实安装或业务仓库写入、旧规范库删除。
- 范围为本 PR 原有文件、命中 Reference、定向回归与本计划/报告。禁止纳入其他 PR 尚未合并的内容。历史审计、失败及成功测试均保留。
- 命中 sdkit-skills 管理流程、目标主/旧入口与修改 Reference，以及根 AGENTS、Orchestration、Development Execution、Project Collaboration、Collaboration Awareness。
- D1 范围内缺陷修复重验；D2/D3 重大语义或架构冲突停止受影响修改。路由语义不变时复用既有行为证据，不把历史 BLOCKED 改成 PASS。

| 阶段 | 验收 | 状态 |
|---|---|---|
| C0 | 权威 main/Head、开放 PR、权限/保护、工作区/锁 | verified |
| C1 | 普通 Merge main、语义审查及必要修复 | verified |
| C2 | 相关单元测试、21 Skill、链接/锚点、兼容/证据/敏感扫描 | verified |
| C3 | Push 前远端复核、普通 Commit/Push、Draft 与 mergeable | verified；普通推送 `d99cc23a0903b5ae5ff94ad9580978deb050635f` 后 Draft/Open、MERGEABLE/CLEAN；交接提交的最终 Head 以最终查询为准 |

命令、数量、退出码与未完成边界见 [最终报告](../../docs/acceptance/engineering-standards-retirement/final-integration.md)。恢复时核对真实 Git/远端，再从未验收阶段继续。完成标准：本地必需门禁通过且历史证据不变；远端 Draft/Open、main 是祖先，最终交付状态单独核验。技术可合并不等于授权合并。
