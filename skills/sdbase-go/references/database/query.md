---
name: database-query
description: sdkitgo handler 中 GORM Table、JOIN、子查询、软删除和分页查询规则
---

# Database Query 规范

本文适用于 sdkitgo handler 和 service 中的 GORM 查询。新增或修改 Model 查询、`Table(...)`、Join、子查询、CTE、原生 SQL、软删除可见性或分页时必须读取本文。

## 软删除可见性

- 本节约束业务 schema 中使用 `BaseFullModel` 的表；`system`、`system_data` 基础设施内部表按组件自身契约处理，不得因业务域软删除改造顺带增加条件或改变查询语义。
- 普通业务读取必须只返回 `deleted_at IS NULL` 的记录；Model 查询、`Table(...)`、Join、子查询、CTE 和原生 SQL 都必须显式体现该条件，不能假设 `BaseFullModel` 会自动注入过滤。
- 每个参与业务语义的别名都要独立过滤，例如主表使用 `item.deleted_at IS NULL`，关联分类使用 `category.deleted_at IS NULL`；只过滤主表不能替代 Join 表过滤。
- 写入、状态机、幂等重放和唯一性检查同样必须排除已软删除记录；仅当明确的治理规则把历史隐藏记录视为占位或永久占号时，才允许使用不带过滤的治理查询，并必须在代码中说明该规则。
- 仅数据治理、恢复、审计取证和受控迁移允许读取已软删除记录；入口必须显式命名并受权限、原因和审计约束，不得让普通 list/detail 接口通过请求参数绕过过滤。
- 追加式日志、事件、快照和回执的软删除仅改变普通界面可见性，物理记录和业务字段保持不变。

## 分页

- list handler 嵌入 `app/http/form.PageRequest`；开放客户端排序时改为嵌入 `ListRequest`，具体结构与 allowlist 规则以 [http/form.md](../http/form.md) 为准。
- 使用 `database.Paginate(request.Page, request.Limit)`。
- 禁止手写 `Offset((page - 1) * limit).Limit(limit)`。
- 分页列表保留单独的 `Count` 查询。

## 正向典型形态

使用 `Table`、Join 或 projection 时，每个参与业务语义的表别名必须在查询中直接写出软删除条件：

```go
model := database.DB.WithContext(c.Request.Context()).
	Table(database.Table(&models.CatalogItem{}) + " AS item").
	Joins("LEFT JOIN " + database.Table(&models.CatalogCategory{}) + " AS category ON category.id = item.category_id AND category.deleted_at IS NULL").
	Where("item.deleted_at IS NULL")

var total int64
if err := model.Count(&total).Error; err != nil {
	response.Error(c, errors.ErrInternalServer)
	return
}

if err := model.Select([]string{
	"item.id",
	"item.name",
	`CASE
		WHEN category.id IS NULL THEN NULL
		ELSE jsonb_build_object(
			'id', category.id,
			'code', category.code,
			'name', category.name
		)
	END AS category`,
}).Scopes(database.Paginate(request.Page, request.Limit)).
	Scan(&list).Error; err != nil {
	response.Error(c, errors.ErrInternalServer)
	return
}
```

完整列表 handler 的 bind、过滤和 response 顺序以 [service/handler.md](../service/handler.md) 的正向典型形态为准。

## 验收

- 必须逐个检查查询涉及的业务表别名，确认每个别名都有 `deleted_at IS NULL`；治理入口必须具有显式命名、权限、原因和审计约束。
- 分页列表必须验证总数查询与列表查询使用相同业务筛选条件，并通过边界页测试或人工 SQL 核对确认结果一致。
- 禁止出现手写 offset 算式或允许普通 list/detail 请求读取软删除记录的参数。
