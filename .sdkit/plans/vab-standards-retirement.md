# vab 规范一次性迁移计划

Plan Baseline r1：只修改本技术栈主入口与对应旧兼容入口的命中 Reference、必要分流和验收资料。禁止修改 PR #14、其他 Skill、业务仓库及旧规范库；不安装或卸载真实 Skill。

| 阶段 | 验收 | 状态 |
|---|---|---|
| P1 只读核验 | 旧规范与实际模板来源、现有 Skill 对账 | Implemented |
| P2 迁移缺口 | 确定性规则、正反例、完成标准及新旧一致 | Implemented |
| P3 回归 | Manager、协议、DockerOps、链接与原生发现 | Pending |
| P4 Draft PR | 重查远端后仅必要文件普通 Push，不合并 | Pending |

D2/D3 超出范围必须停止并取得必要批准；测试失败不得标 Verified。

本轮离线与原生发现证据见 docs/acceptance；模型路由 BLOCKED，不将全流程标 Verified。Draft 交付单独记录真实 Commit/PR。
