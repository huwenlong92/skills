---
name: sdkit-dbops
description: 跨语言数据库 SQL Migration 静态校验、Schema Baseline、漂移分析、RANGE 分区维护与迁移安全计划时使用；V1 不连接数据库、不执行 SQL。
---

# SDKit Database Schema Collaboration

适用于跨项目 SQL 结构迁移的只读检查与规划。业务 ORM、数据库服务器运维及应用部署不属于本 Skill。

## 分流
1. 先读取 [架构与边界](references/architecture.md)，核验项目身份和既有 Migration 执行器。
2. 配置检查读取 [项目配置](references/project-config.md)；SQL 文件校验读取 [迁移文件](references/migration-files.md)。
3. 任何数据库环境、连接、执行或恢复话题必须读取 [安全门禁](references/safety.md)。
4. V1 工具 `scripts/check_migrations.py` 仅对本地文件进行静态检查，不连接数据库，不提供 apply/down/rollback。

5. 离线 Baseline 与 History 读取 [基线与历史](references/baseline-history.md)。
6. Snapshot 与 Drift 读取 [快照规范](references/schema-snapshot.md) 和 [差异规则](references/drift.md)；方言能力读取对应 providers reference。

7. 离线计划和证据检查读取 [History Evidence](references/history-evidence.md)、[Migration Plan](references/migration-plan.md)、[同步状态](references/synchronization.md)、[授权](references/approval.md) 与 [恢复](references/recovery.md)。

8. 数据破坏风险与备份建议读取 [Data Destruction Guard](references/data-destruction-guard.md) 和 [Risk-Based Backup](references/risk-based-backup.md)。所有离线建议均不构成备份已验证或 SQL 执行授权。

9. 受控数据库操作需求读取 [Controlled Operations](references/controlled-operations.md)、[Authorization](references/authorization.md)、[Backup & Recovery](references/backup-and-recovery.md)、[Execution Verification](references/execution-verification.md)；`scripts/check_operation_intent.py` 仅校验离线意图，绝不签发执行授权。

10. RANGE 月分区预建、漏跑、DEFAULT迁移、清理与恢复计划，读取 [分区维护](references/range-partitions.md)；只审查计划与证据，不执行数据库操作。

## 禁止
- 禁止在环境不明时试连；禁止 AI 直接或间接操作正式数据库。
- 禁止把现有 Go AutoMigrate 当成已执行的版本化 SQL Migration。
- 禁止把静态 SQL 检测结果当作执行安全证明。
- `system`、`system_data` 基础设施对象默认受保护。

## 完成标准
明确输出已核验、需人工复核、阻断和未执行项；只读分析不得触发数据库写入。
