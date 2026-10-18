# SQL Migration 文件 V1

适用于版本化 SQL Migration 创建、评审、静态校验。

- 文件名为 `YYYYMMDDTHHMMSSZ_<6-16位小写十六进制>_<snake_case>.sql`；时间使用 UTC。
- 单方言文件位于 `database/migrations/`；多方言文件位于 `database/<dialect>/migrations/`。
- 同一管理范围内 ID 不得重复；文件按 ID 字典序排序；SQL 原始字节使用 SHA-256。
- 已应用文件不得修改；真实已应用哈希只能从经过验证的 History 获取，不能用本地文件清单冒充。
- 危险关键字如 DROP、TRUNCATE、ALTER、DELETE、UPDATE、INSERT、GRANT、REVOKE 必须标记人工复核；静态检测不能证明 SQL 无副作用。
- SQL 解析不完整、动态 SQL、存储过程、注释混淆或方言不明时必须标记人工复核，不得自动认定安全。
- 数据修复脚本与结构 Migration 必须区分，不得把批量数据修改隐式纳入常规结构升级。

正例：`20261018T053000Z_a83f2c_add_avatar.sql`。反例：`001.sql`、`20261018_001.sql`。

完成标准：ID、顺序、文件路径、SHA-256 和复核风险可重复输出，且不连接数据库。
