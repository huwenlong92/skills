# 一次性审计与 Nuxt 补齐计划

Plan Baseline r1：只读旧规范库并对账 20 Skills；本分支只提交审计、Nuxt 主入口及旧兼容入口的缺口。Go、Vab 在独立分支，不修改 #14。禁止修改业务项目、真实 Codex 配置和旧规范库。重大 UI/宿主协议归属冲突停止并记录，不擅自新增 Skill 架构。

| 阶段 | 状态 | 验收 |
|---|---|---|
| P1 只读审计 | Implemented | 实际目录、指纹、规则组矩阵与停止项 |
| P2 Nuxt 规范 | Implemented | 对照实际模板，不复制全文；35 项模板测试 |
| P3 回归与原生发现 | Pending | 离线全仓及隔离 Home |
| P4 Draft 交付 | Pending | 远端重新核验、普通 Push、保持 Draft |

未解决规则组不得因已生成审计而标成迁移完成。D2/D3 必须停止受影响改动并走审批。

本轮离线与原生发现证据见 docs/acceptance；模型路由 BLOCKED，不将全流程标 Verified。Draft 交付单独记录真实 Commit/PR。
