# Data Destruction Guard V1

适用于离线 Migration、SQL、Seed、ORM、回填及数据清理风险评估。

- 无条件 DELETE、TRUNCATE、DROP TABLE/SCHEMA、DELETE 后重建、受保护 system/system_data 对象默认 Blocked。
- 动态 SQL、存储过程、间接 ORM/Seed 清理无法静态证明安全时标记 Unknown 并 Blocked；不得仅因未匹配关键词判定安全。
- UPDATE、REPLACE、INSERT OVERWRITE、分区切换和级联删除需独立审查受影响数据与依赖。
- 识别结果是保守风险信号，不是完整 SQL AST；不得用来授权执行。
- 本地持久开发库、远程共享开发库及预发布库不得默认清空数据；生产库禁止 AI 直接或间接操作。
- 任何受保护 Schema 操作不得因备份存在而自动解锁。
- V1 只分析显式提供的离线操作声明与 SQL 文本；不读取真实数据库，不调用 ORM/Seed。

完成标准：破坏性操作阻断；未知来源或间接写入默认阻断；没有自动执行入口。
