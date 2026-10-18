# PR #18 最终本地验收计划

适用范围：ui-design V1 集成与真实 Codex 行为验收；任务 ID `pr18-final-acceptance`，revision 3（保留 revision 1 原始基线与 revision 2 命名整合记录）。

- 原始 Git 基线：`5983179b279dcc8c75b62c43bb19962c6580e316`；main `8b22285aa2abba995e88f49718800c167c7e2413`。
- 已确认：用户授权隔离 Worktree、临时 Codex Home、本地测试、公开协议与虚构材料模型测试、范围内修复、Commit 与普通 Push；禁止合并、Ready、部署、主动触发 CI、真实配置/Skill/业务修改、复制认证。
- 允许：ui-design、必要的 Foundry 最小路由修复、定向回归脚本、验收报告与本任务状态。禁止混入 #14–#17 或重构 Foundry Workspace/Git/发布。
- 命中：sdkit-skills 及安装安全；OpenAI Docs 认证/安全文档；目标 ui-design 五份 references、Foundry 入口与 prototypes；仓库协作感知、编排与开发执行协议。
- D0/D1：范围内缺陷可修复并保存回归证据；D2/D3：扩大范围或改变安全边界必须停止受影响操作并取得明确授权。

| 阶段 | 依赖与验收 | 当前状态 |
|---|---|---|
| S1 Git/规范 | 实时 SHA、开放 PR 文件集、独立 Worktree、全部指定文档审计 | verified；无直接文件重叠，main 已为祖先 |
| S2 本地回归 | 指定命令、迁移、链接/锚点、21 Skill 与交接质量 | verified；118 unittest 全通过、validate 21、链接/锚点见最终报告 |
| S3 模型行为 | 认证与访问边界预检后真实执行 U01–U12，含三种设计来源交接 | verified；用户独立登录后完成真实 U01–U12 与三种交接来源；18 CLI 运行均退出 0，图片生成 1 次，证据见最终报告 |
| S4 交付 | 全仓复验、脱敏报告、远端核验、Commit/普通 Push、Draft/Open | implemented；本轮最终证据与全仓回归完成后，按实时远端状态普通 Commit/Push；保持 Draft/Open |

实际命令、退出码和阶段证据以最终验收报告为准；所有阶段须完整通过方可声明最终技术可合并。恢复入口：本计划、TASKS、STATUS、HANDOFF 与报告；先核对实际 Git，禁止以文档代替证据。

revision 2：提交前远端重命名为 sdkit-ui-design，按授权同步最新 Head。普通 Merge 保留历史、手工语义解决交接冲突，Catalog/路由/测试同步新名称，新增第 9 项一致性回归。不扩大设计职责或改变真实模型预期；初始基线保持不变。

revision 3：用户完成隔离浏览器登录后恢复。先通过实际官方受限权限探针和逐次离线输入审查，修正只对临时进程生效的 Skill 入口禁用选择器；没有复制认证或修改真实配置。真实目标矩阵 12 PASS，U05 三类来源通过，首轮夹具缺失/歧义及重测完整保留。命令/退出码、初始材料、实际加载、产物和失败历史见 docs/testing/ui-design-v1/REPORT.md 及 cases/。恢复时另发现 #19 与 Foundry/Orchestration 存在 L2 文件交集，本轮不改其源文件或合入其代码。
