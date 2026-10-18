# Schema Collaboration V1 架构

适用于创建、评审和使用数据库 Schema 协作协议。

- `sdenv` 负责环境发现和已授权的数据库入口；`sdbase-go` 负责 Go Model 与原有迁移命令；dbops 只负责跨语言版本化 SQL 静态检查与后续独立协议。
- V1 仅交付文件校验与规划协议，不提供数据库连接、History 表创建或执行器。
- 迁移驱动分为 `sql`、`external`、`observe`；`external` 不得伪造历史，`observe` 禁止写入。
- 一个数据库对象只能有一个权威结构变更执行路径。Go AutoMigrate 与 SQL 重叠时必须报告冲突。
- 未来 Baseline、History、Snapshot、Drift、Plan、Provider 必须分阶段实现，未验证能力标记 Unsupported。
- Skill 必须独立安装；不得依赖其他未安装 Skill 或个人固定路径。

完成标准：明确 Primary、既有迁移器和能力状态，禁止双执行器隐式写同一对象。
