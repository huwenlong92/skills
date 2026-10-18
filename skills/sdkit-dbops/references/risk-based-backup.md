# Risk-Based Backup Decision V1

适用于离线变更计划的分层检查与恢复保障建议。

- L0：本地 SQL/Migration 静态检查，不读取数据库；L1：Schema/History 元数据；L2：受影响表规模、行数估计、依赖和锁；L3：恢复点与备份方案。
- L1/L2 需要未来单独授权的 Provider，PR #26 不连接数据库；不得为结构对比默认下载全量业务数据。
- 结构变更开发前必须遵守 sdbase-go 的已验证基线备份门禁；已有目标数据库执行前必须有目标最新且可恢复的备份。仅有 schema-only 文件不能恢复业务数据。
- 根据对象范围、RPO/RTO、恢复粒度、版本、依赖、一致性、存储/网络成本及备份性能影响推荐 existing-pitr、verified-snapshot、targeted-backup、full-backup 或 none-for-read-only。
- 推荐不代表可用，可用不代表恢复已验证。JSON 自称 verified 不可当成外部认证。
- 大型远程库优先评估已有快照/PITR 或目标表备份，禁止为了对比 Schema 自动全量拉回本地。
- 缺少可验证恢复点、备份过期、恢复粒度不覆盖依赖或 RPO/RTO 不满足时，计划必须 Blocked。
- 生产库禁止 AI 直接或间接连接、备份和恢复；仅输出人工审阅建议。

完成标准：计划描述最低充分恢复方案与证据需求，不执行备份、不签发授权。
