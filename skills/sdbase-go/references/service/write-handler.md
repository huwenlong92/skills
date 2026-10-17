---
name: service-write-handler
description: sdkitgo create、update、delete handler 的直接 GORM 写入与事务规则
---

# HTTP Write Handler 规范

本文定义 sdkitgo 常规 create、update、delete 和写事务的 GORM 写法。新增或修改持久化写入、状态变更或删除 handler 时必须读取本文，并同时读取 [handler.md](handler.md)、[request.md](request.md) 和 [http/response.md](../http/response.md)。

## 共同规则

- Create、update、delete 必须使用独立包级 handler：`CreateXxx`、`UpdateXxx`、`DeleteXxx`。
- 路由固定使用 `POST /xxx/create`、`POST /xxx/update`、`POST /xxx/delete`。
- 当前接口的存在性检查、唯一性检查、差异计算、GORM 写入和必要 transaction 必须直接写在 handler。
- 禁止为普通写接口新增 CRUD service、repository、manager、usecase，或只有一个调用方的 `findXxx`、`buildXxxUpdates`、`saveXxx`、`deleteXxx` helper。
- 多表需要保持同一原子结果时必须使用 `db.Transaction`；单表一次写入禁止仅为形式统一增加 transaction。
- 对外通知和 realtime event 必须在数据库 transaction 成功提交后发送，禁止在 transaction 内产生不可回滚的外部副作用。

## Create

Create 必须按“绑定 → 归一化 → 业务校验 → 构造 model → GORM Create/Transaction → 返回 ID”的顺序直接实现：

```go
func CreateResource(c *gin.Context) {
	request := struct {
		Code   string `json:"code" form:"code" binding:"required,max=64"`
		Name   string `json:"name" form:"name" binding:"required,max=128"`
		Status int16  `json:"status" form:"status" binding:"required,oneof=0 1"`
	}{}
	if err := validator.BindJSON(c, &request); err != nil {
		response.Error(c, err)
		return
	}

	code := strings.TrimSpace(request.Code)
	name := strings.TrimSpace(request.Name)
	db := database.DB.WithContext(c.Request.Context())
	var exists int64
	if err := db.Model(&models.Resource{}).
		Where("deleted_at IS NULL").
		Where("code = ?", code).
		Count(&exists).Error; err != nil {
		response.Error(c, errors.ErrInternalServer)
		return
	}
	if exists > 0 {
		response.Error(c, errors.New(errors.CodeConflict, errors.SubCodeConflict, "资源编码已存在"))
		return
	}

	row := models.Resource{Code: code, Name: name, Status: request.Status}
	if err := db.Create(&row).Error; err != nil {
		response.Error(c, errors.ErrInternalServer)
		return
	}
	response.Success(c, gin.H{"id": row.ID})
}
```

有关联表时，在一个 transaction 中先 `Create(&row)`，再使用生成的内部 ID 写关联；禁止拆成无法回滚的多个独立写入。

## Update

- Update 必须先查询当前 model，区分 `gorm.ErrRecordNotFound`，再计算并写入实际变化。
- 可选更新字段必须使用 pointer，确保“未传入”和“显式零值”可以区分。
- 使用 `map[string]any` 明确更新字段；禁止使用包含未传零值的完整 request/model 执行 `Save`。
- 更新字段 map 的排版必须遵循 [code/formatting.md](../code/formatting.md)。

```go
func UpdateResource(c *gin.Context) {
	request := struct {
		ID     int64   `json:"id" form:"id" binding:"required,gt=0"`
		Name   *string `json:"name" form:"name" binding:"omitempty,max=128"`
		Status *int16  `json:"status" form:"status" binding:"omitempty,oneof=0 1"`
	}{}
	if err := validator.BindJSON(c, &request); err != nil {
		response.Error(c, err)
		return
	}

	db := database.DB.WithContext(c.Request.Context())
	var row models.Resource
	if err := db.Where("id = ? AND deleted_at IS NULL", request.ID).Take(&row).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			response.Error(c, apperrors.ErrNotFound)
			return
		}
		response.Error(c, apperrors.ErrInternalServer)
		return
	}

	updates := make(map[string]any)
	if request.Name != nil {
		name := strings.TrimSpace(*request.Name)
		if row.Name != name {
			updates["name"] = name
		}
	}
	if request.Status != nil && row.Status != *request.Status {
		updates["status"] = *request.Status
	}
	if len(updates) > 0 {
		if err := db.Model(&row).Updates(updates).Error; err != nil {
			response.Error(c, apperrors.ErrInternalServer)
			return
		}
	}
	response.OK(c)
}
```

## Delete

- Delete 必须先加载目标并确认普通业务可见性。
- 具有 GORM soft delete 契约的 model 使用 `Delete`；项目明确通过字段控制软删除时使用 `Model(...).Updates(...)`。
- 删除主表和关联表必须保持一致时使用 transaction。
- 禁止普通业务 delete 使用 `Unscoped().Delete` 或物理 SQL 删除。

```go
func DeleteResource(c *gin.Context) {
	request := struct {
		ID int64 `json:"id" form:"id" binding:"required,gt=0"`
	}{}
	if err := validator.BindJSON(c, &request); err != nil {
		response.Error(c, err)
		return
	}

	db := database.DB.WithContext(c.Request.Context())
	var row models.Resource
	if err := db.Where("id = ? AND deleted_at IS NULL", request.ID).Take(&row).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			response.Error(c, apperrors.ErrNotFound)
			return
		}
		response.Error(c, apperrors.ErrInternalServer)
		return
	}
	if err := db.Delete(&row).Error; err != nil {
		response.Error(c, apperrors.ErrInternalServer)
		return
	}
	response.OK(c)
}
```

## 验收

- 必须验证 create 的重复业务键、update 的不存在/未传字段/显式零值、delete 的目标范围和重复请求。
- Transaction 必须验证中途任一步失败时，同一原子边界内的全部数据库写入都已回滚。
- 必须检查 transaction 内没有 realtime、HTTP、邮件、短信或其他不可回滚外部副作用。
- 必须执行 [handler.md](handler.md) 的 private helper 候选扫描；只有一个调用方的常规表操作包装必须内联，复杂阶段按该文件的提取条件判定。
