---
name: models-base
description: sdkitgo 持久化模型选择 BaseModel 或 BaseFullModel 的确定性规则
---

# Models Base 规范

本文适用于 sdkitgo 持久化 model 的基础字段选择。新增或修改映射数据库表的 struct、调整 `BaseModel` 或 `BaseFullModel`、处理软删除语义时必须读取本文；业务字段、schema、`TableName` 和 GORM tag 同时读取 [struct.md](struct.md)。

## 定义位置

- 通用时间字段必须定义在 `app/models/base.go`。
- 业务 model 禁止重复手写 `created_at`、`updated_at` 和 `deleted_at`。
- base model 必须嵌入在 struct 末尾，放在业务字段之后。

## 选择规则

| 表类型 | 必须使用 |
|---|---|
| `public` 或其他业务 schema 的新表，包括业务日志、事件、快照、回执 | `BaseFullModel` |
| `system`、`system_data` 中已存在的基础设施内部表 | 保持该组件已经定义的 `BaseModel` 或 `BaseFullModel`；只有用户明确要求时才允许改变 |
| 不映射数据库表的 request、response、projection 或配置 struct | 两者都不嵌入 |

- 所有业务 schema 的新建持久化表默认嵌入 `BaseFullModel`，同时具备 `created_at`、`updated_at` 和 `deleted_at`。没有命中下述确认条件时，必须直接采用该默认值，不得把基础 model 选择交还给用户。
- 除 `system`、`system_data` 的既有基础设施例外外，只要 struct 对应项目拥有的持久化业务表，就必须选择 `BaseFullModel`；禁止仅因“这张表不需要删除”“这是日志表”或“这是关联表”自行改用 `BaseModel`。
- 只有出现下列任一明确不适配信号时，才允许暂停实现并向用户确认是否改用 `BaseModel` 或不嵌入基础 model：
  - struct 映射数据库 view、外部系统拥有的表或只读镜像，当前项目不能增加基础字段；
  - 本次只兼容既有表，而该表缺少 `updated_at` 或 `deleted_at`，并且任务范围不包含 schema 变更；
  - 实际依赖的基础设施组件已经定义了与 `BaseFullModel` 冲突的固定字段或写入契约。
- 命中确认条件只表示必须向用户说明冲突，不表示 AI 可以自行选择次选方案。用户确认前不得创建 model 或 migration。
- `system`、`system_data` schema 属于已稳定的基础设施内部表。业务需求不得因为全表扫描顺带修改这些 model、迁移、查询或 handler；只有用户明确点名基础设施范围时才允许修改。
- 除上述基础设施 schema 外，`BaseModel` 只作为 `BaseFullModel` 的内部组成保留，禁止作为业务表、业务日志、事件、快照或回执的直接基类。

## 软删除语义

- `deleted_at` 只表达常规读取可见性，不替代业务状态。
- 关闭、停用、撤回、失败、过期等领域终态必须使用各自状态字段表达。
- 业务域内的追加式日志、事件、快照和外部回执必须保持业务字段不可变。
- 允许软删除追加式记录时，只允许单向修改 `deleted_at` 及配套的 `updated_at`，用于从普通业务界面隐藏记录；禁止物理删除或借软删除改写历史事实。

## 验收

- 新建业务表必须嵌入 `BaseFullModel`，并且嵌入位置位于业务字段末尾。
- `system`、`system_data` 之外不得直接嵌入 `BaseModel`。
- 未使用 `BaseFullModel` 时，必须记录命中的不适配信号和用户确认结果；缺少其中任一项即不通过。
- request、response、projection 和配置 struct 不得嵌入 database base model。
- 人工检查领域终态由业务状态字段表达，`deleted_at` 未替代状态机。
