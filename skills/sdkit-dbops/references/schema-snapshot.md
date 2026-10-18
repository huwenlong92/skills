# Schema Snapshot V1

适用于离线快照归一化和指纹比较。

- 必须声明 dialect、databaseVersion、normalizerVersion、scope、coverage、objects。
- 对象身份重复、Coverage 不完整或 Scope 不匹配禁止报告 Equal。
- 对象排序与 SHA-256 必须确定性；禁止猜测跨方言类型等价。
- system 和 system_data 仍受保护，比较不授权修改。

完成标准：不同输入顺序产生相同指纹，未知证据安全降级。
