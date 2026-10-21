# Schema Snapshot V1

适用于离线快照归一化和指纹比较。

- 必须声明 dialect、databaseVersion、normalizerVersion、scope、coverage、objects。
- 对象身份重复、Coverage 不完整或 Scope 不匹配禁止报告 Equal。
- 对象排序与 SHA-256 必须确定性；禁止猜测跨方言类型等价。
- system 和 system_data 仍受保护，比较不授权修改。

RANGE 分区快照必须同时包含父子OID、实际边界、DEFAULT挂载和按月分布、分区键及关联对象覆盖；按 [分区维护](range-partitions.md) 审查，缺少任一项不得证明迁移/清理安全。

完成标准：不同输入顺序产生相同指纹，未知证据安全降级。
