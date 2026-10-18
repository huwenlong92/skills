# Bootstrap 安全收尾计划

Plan Baseline r1：仅修改 PR #14 的 Bootstrap 协议、脚本、测试及验收资料；禁止写真实全局配置、旧规范库、业务项目或迁移 Skill。独立规范迁移走其他分支。

| 阶段 | 验收 | 状态 |
|---|---|---|
| P1 文件事务修复 | 脱敏临时目录安全测试 | Verified |
| P2 规范退出与完整草案 | 保留自定义语义、真实配置指纹不变 | Verified |
| P3 全仓及发现回归 | 真实命令退出码、隔离 Home 原生发现 | Pending |
| P4 交付 | 仅必要文件 Commit、核对远端 Head 后普通 Push、保持 Draft | Pending |

D0/D1 限定上述范围；D2/D3 必须停止受影响改动并修订计划、取得必要批准。迁移缺口不得借此进入 #14。

本轮离线与原生发现证据见 docs/acceptance；模型路由 BLOCKED，不将全流程标 Verified。Draft 交付单独记录真实 Commit/PR。
