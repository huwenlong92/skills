# Recovery V1

适用于失败 Migration 的离线恢复报告。状态为 investigation_required、reconciled、new_plan_required 等；失败、部分提交和未知 DDL 不得自动重试或 down。MySQL/Oracle 不可假设事务回滚。必须保存证据、重新采集、重新审批。

RANGE 分区及DEFAULT维护失败必须同时读取 [分区维护](range-partitions.md)，区分 rolled_back、committed 与 unknown；不得以重试幂等代替提交状态调查。

完成标准：工具只生成恢复建议，不执行恢复。
