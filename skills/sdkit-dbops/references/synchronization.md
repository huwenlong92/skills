# Synchronization V1

适用于离线 Local/Remote History 与 Snapshot 对账。优先级：无效证据或未解决 Attempt → unknown/incomplete；同 ID 不同哈希 → checksum_mismatch；结构不一致但历史一致 → schema_drift；历史前缀关系 → local_ahead/remote_ahead；其他 → diverged/history_mismatch。仅输出计划，不复制数据库。

完成标准：冲突状态不可被普通领先状态覆盖。
