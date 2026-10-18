# Drift V1

适用于两份脱敏 Snapshot 的只读比较。

- Equal 仅表示受管理范围内结构相同，不代表 History 一致。
- 不同对象返回 Drift，证据不足或版本不兼容返回 Unknown。
- 禁止连接生产数据库或自动执行 DDL。

完成标准：结果确定性，未知状态不得误报 Equal。
