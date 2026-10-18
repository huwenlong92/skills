# Approval V1

适用于迁移计划授权需求描述。离线工具只能标注 requires_approval、blocked 或 candidate，不签发真实执行授权。生产环境、未知环境、system/system_data 保护对象禁止自动执行。授权必须独立绑定目标身份、Scope、Plan Hash、操作与期限，执行前重新采集状态。

完成标准：离线 JSON 的 approval 字段不能成为授权凭据。
