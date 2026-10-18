---
name: sdkit-dbops
description: 跨语言数据库 SQL Migration 静态校验、Schema Baseline、漂移分析与迁移安全计划时使用；V1 不连接数据库、不执行 SQL。
---

# SDKit Database Schema Collaboration

适用于跨项目 SQL 结构迁移的只读检查与规划。业务 ORM、数据库服务器运维及应用部署不属于本 Skill。

## 分流
1. 先读取 [架构与边界](references/architecture.md)，核验项目身份和既有 Migration 执行器。
2. 配置检查读取 [项目配置](references/project-config.md)；SQL 文件校验读取 [迁移文件](references/migration-files.md)。
3. 任何数据库环境、连接、执行或恢复话题必须读取 [安全门禁](references/safety.md)。
4. V1 工具 `scripts/check_migrations.py` 仅对本地文件进行静态检查，不连接数据库，不提供 apply/down/rollback。

## 禁止
- 禁止在环境不明时试连；禁止 AI 直接或间接操作正式数据库。
- 禁止把现有 Go AutoMigrate 当成已执行的版本化 SQL Migration。
- 禁止把静态 SQL 检测结果当作执行安全证明。
- `system`、`system_data` 基础设施对象默认受保护。

## 完成标准
明确输出已核验、需人工复核、阻断和未执行项；只读分析不得触发数据库写入。
