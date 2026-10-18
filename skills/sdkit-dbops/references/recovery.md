# Recovery V1

适用于失败 Migration 的离线恢复报告。状态为 investigation_required、reconciled、new_plan_required 等；失败、部分提交和未知 DDL 不得自动重试或 down。MySQL/Oracle 不可假设事务回滚。必须保存证据、重新采集、重新审批。

完成标准：工具只生成恢复建议，不执行恢复。
