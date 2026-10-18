# Baseline 与 History V1

适用于离线 Baseline 与 Migration History 校验。

- V1 只读取脱敏 JSON；禁止连接数据库、执行 SQL 或采纳真实 Baseline。
- Baseline 必须记录身份、方言、Scope、指纹、Normalizer 版本和校验和。采纳必须独立授权与隔离验证。
- 已应用 Migration ID 唯一、SHA-256 不可变；失败、运行中和未知 Attempt 必须阻断同步。
- Go AutoMigrate 不得伪装成版本化 SQL History。

- 离线工具 `scripts/validate_baseline.py` 只校验描述符，不会采纳 Baseline，也不证明数据库结构真实一致。

完成标准：离线证据可验证，缺失或冲突必须拒绝。
