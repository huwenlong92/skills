# Migration Plan V1

适用于离线迁移计划生成和复核。必须绑定目标身份、Git Commit、Migration ID/哈希、History/Snapshot 指纹、Normalizer 版本及风险。Plan Hash 必须排除自身与展示时间，对规范化语义 JSON 做 SHA-256。禁止生成 SQL 执行入口。任何前置条件变化必须失效。

完成标准：相同语义哈希稳定，篡改与证据不完整阻断执行准备。

## 数据安全扩展（离线门禁已集成）

Data Destruction Guard 与 Backup Decision 已接入 plan_migrations.py 的离线阻断决策，但不提供可信备份证明或执行授权；任何计划的 candidate/requires_approval 都不得被解释为已通过数据安全或恢复保障门禁。当前 Plan Hash 已绑定提供的离线操作清单、备份请求、RPO/RTO 与恢复证据声明的内容指纹，输入变化需重新生成计划；但受影响对象的真实范围、备份实际可恢复性及证据时效尚不能由离线工具独立验证，缺少可信证据时保持 Blocked。

## DBOPS-05 离线安全门禁（已集成）

计划现在绑定源 History/Schema 指纹、目标 History/Schema 指纹、Data Destruction Guard 与 Backup Decision 的离线证据指纹。缺失安全输入、声明式备份或未经外部认证的恢复证据一律导致 decision=blocked，executionAuthorized=false。离线输入不得自行将其提升为 Ready 或签发执行授权。--safety 仅读取本地 JSON；计划校验必须重新计算哈希，计划与目标证据变化必须重新生成。恢复报告由 recovery_report.py 生成调查需求，不执行回滚。
