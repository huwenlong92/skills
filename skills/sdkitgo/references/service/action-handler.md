---
name: service-action-handler
description: sdkitgo 非 CRUD 业务动作、状态迁移、分配和批量操作的直接 handler 写法
---

# HTTP Action Handler 规范

本文适用于 `EnableXxx`、`DisableXxx`、`ApproveXxx`、`RejectXxx`、`ResetXxx`、`AssignXxx`、`DisposeXxx` 和 batch action 等非 CRUD 写接口。新增或修改业务状态迁移、集合替换、权限分配或批量动作时必须读取本文，并同时读取 [handler.md](handler.md)、[request.md](request.md)、[http/response.md](../http/response.md) 和 [database/query.md](../database/query.md)。

## 放置与命名

- Action handler 必须放在所属资源文件中，并使用表达真实业务动作的包级函数名。禁止建立通用 `action.go`、`operation.go` 或 `command.go` 收纳不同资源动作。
- 同一资源已有 list/detail/CRUD 文件时，action 必须继续放该文件；只有用户明确要求拆分已有超大资源文件时，才允许按稳定子能力拆分，规则以 [handler.md](handler.md) 为准。
- Router 必须使用 `POST` 和明确的 kebab-case 动作 path，并按 [router.md](router.md) 注册。禁止使用 `action`、`operate`、`handle` 等无业务含义名称。

## 直接执行流程

普通 action 必须在 handler 中直接展示以下顺序：

1. 绑定 request；
2. 在权限、组织和软删除范围内加载当前记录；
3. 校验允许的当前状态和动作前置条件；
4. 执行带当前状态条件的 GORM update，或在 transaction 中完成多表原子修改；
5. transaction 提交后发送 realtime、queue、邮件或其他外部副作用；
6. 返回 `response.OK(c)` 或动作契约要求的数据。

- 单表状态变更禁止仅为结构统一创建 transaction。
- 状态迁移 update 必须把预期旧状态写入 `WHERE` 并检查 `RowsAffected`，防止加载后被并发请求改变。`RowsAffected == 0` 必须返回状态冲突或重新加载确认，禁止仍然返回成功。
- 多表修改、集合替换或主记录与操作记录必须同时成功时，必须使用 `db.Transaction(func(tx *gorm.DB) error { ... })`。禁止手动散落 `Begin`、`Rollback`、`Commit`，只有 GORM callback transaction 无法覆盖的底层流式协议才允许手动管理，并必须测试 commit error 和所有退出路径。
- 当前动作专属的查询、状态判断、update map 和 transaction 必须直接留在 handler；helper 提取门槛以 [handler.md](handler.md) 为准。

## 正向状态迁移

```go
func EnableCatalogItem(c *gin.Context) {
	request := struct {
		ID int64 `json:"id" form:"id" binding:"required,gt=0"`
	}{}
	if err := validator.BindJSON(c, &request); err != nil {
		response.Error(c, err)
		return
	}

	db := database.DB.WithContext(c.Request.Context())
	var row models.CatalogItem
	if err := db.Where("id = ? AND deleted_at IS NULL", request.ID).Take(&row).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			response.Error(c, apperrors.ErrNotFound)
			return
		}
		response.Error(c, apperrors.ErrInternalServer)
		return
	}
	if row.Status != models.CatalogItemStatusDisabled {
		response.Error(c, apperrors.ErrConflict)
		return
	}

	result := db.Model(&models.CatalogItem{}).
		Where("id = ? AND deleted_at IS NULL AND status = ?", row.ID, models.CatalogItemStatusDisabled).
		Update("status", models.CatalogItemStatusEnabled)
	if result.Error != nil {
		response.Error(c, apperrors.ErrInternalServer)
		return
	}
	if result.RowsAffected == 0 {
		response.Error(c, apperrors.ErrConflict)
		return
	}
	response.OK(c)
}
```

## 集合分配与批量动作

- Assign 或 replace-set 接口必须先校验全部目标 ID，再在一个 transaction 中批量新增缺失项并集合式删除多余项；禁止在输入循环中逐条 `First`、`Create`、`Save` 或 `Delete`。
- 输入 ID 必须先去重并使用稳定顺序；空集合表示清空还是非法请求必须由 request contract 明确，禁止根据实现方便临时决定。
- Batch action 必须限定最大条数并一次校验作用范围。能够使用 `WHERE id IN ?`、`CreateInBatches`、`ON CONFLICT` 或集合 SQL 完成时，禁止逐条写数据库。
- 每个目标允许独立成功或失败时，响应必须返回逐项结果；所有目标必须原子成功时，任何一项失败必须回滚整个 transaction。两种语义不得混用。

## 验收

- 必须测试目标不存在、非法当前状态、合法迁移、并发状态变化和重复请求语义。
- 多表 action 必须注入中途失败并确认所有数据库写入回滚；外部副作用必须验证只在 commit 成功后发生。
- Assign 和 batch action 必须检查 SQL 数量不随输入条数逐条增长，并覆盖空集合、重复 ID、越权 ID 和超过上限。
- 必须执行 [handler.md](handler.md) 的 helper 候选扫描，不能证明共享不变量或独立复杂阶段的 action wrapper 必须内联。
