---
name: service-handler
description: sdkitgo 常规 Gin handler 的目录分类、直接 GORM list/detail/options 查询和 helper 规则
---

# HTTP Handler 规范

本文定义 sdkitgo 常规 Gin handler 的目录、函数形态和直接查表习惯。新增、修改、拆分或评审 `app/{service}/handler/**/*.go` 时必须读取本文；请求绑定读取 [request.md](request.md)，响应读取 [http/response.md](../http/response.md)，CRUD 写接口读取 [write-handler.md](write-handler.md)，非 CRUD 写动作读取 [action-handler.md](action-handler.md)，查询 projection 读取 [database/projection.md](../database/projection.md)。

## 目录与文件

handler 使用一级业务模块目录分类，资源作为文件：

```text
app/console/handler/
  catalog/
    item.go
    category.go
  account/
    profile.go
    preference.go
  operations/
    job.go
    queue.go
```

- 一级目录必须表示稳定业务模块，例如 `catalog`、`account`、`operations`；package 名必须与目录名一致。
- 文件名必须表示具体资源，例如 `item.go`、`category.go`；禁止使用 `catalog_item.go` 把目录含义重复写进文件名。
- 同一资源的 list、options、detail、create、update、delete 必须放在同一文件；仅当用户明确要求拆分已有超大资源文件时，才允许继续按同一资源的稳定子能力拆文件，禁止按 CRUD 动作拆分。
- 禁止按动作拆成 `item_list.go`、`item_create.go`、`item_update.go`，也禁止为单个 handler 创建 `item/create.go`。
- Router 必须按 URL 语义嵌套多层 group，但 handler 目录禁止机械复制每一层 URL。目录用于业务模块分类，文件用于资源分类，函数用于操作分类。
- handler 根目录只放服务级、跨模块入口；已经具有稳定模块归属的资源必须进入对应一级目录。

## 常规 Handler 形态

- 常规 handler 必须是包级函数：`func Xxx(c *gin.Context)`。
- 常规 query、options 和 CRUD handler 禁止定义 `Handler struct`、`NewHandler`、receiver method 或返回 `gin.HandlerFunc` 的端点工厂。
- 仅当基础设施管理 handler 已经存在并且必须持有 runtime operation facade 时，才允许保持项目既有 struct 形态；禁止把该例外复制到普通业务 CRUD。
- Handler 直接使用 core database facade 和 GORM 完成请求绑定、业务校验、查询、projection、普通写入和必要事务。
- 禁止为单个 HTTP query/CRUD 新建 service、repository、manager、usecase、operation wrapper 或一组一对一转发 helper。
- 不同 HTTP service 即使访问同一张表，也必须分别维护请求、权限条件、查询和 response projection，禁止建立包含所有入口字段的通用 CRUD service 或 DTO。

## 列表接口

`GetXxxList` 必须按以下顺序直接写在 handler：匿名 request、绑定、匿名 projection、GORM model、条件过滤、`Count`、Join/Select、分页排序 Scan、response。

```go
func GetCatalogItemList(c *gin.Context) {
	request := struct {
		form.PageRequest
		Search string `json:"search" form:"search" binding:"omitempty"`
		Status *int16 `json:"status" form:"status" binding:"omitempty,oneof=0 1"`
	}{}
	if err := validator.BindQuery(c, &request); err != nil {
		response.Error(c, err)
		return
	}

	var total int64
	list := make([]struct {
		ID        int64     `json:"id"`
		Code      string    `json:"code"`
		Name      string    `json:"name"`
		Status    int16     `json:"status"`
		CreatedAt time.Time `json:"created_at"`
	}, 0)

	model := database.DB.WithContext(c.Request.Context()).
		Table(database.Table(&models.CatalogItem{}) + " AS item").
		Where("item.deleted_at IS NULL")
	if search := strings.TrimSpace(request.Search); search != "" {
		like := "%" + search + "%"
		model = model.Where("(item.code LIKE ? OR item.name LIKE ?)", like, like)
	}
	if request.Status != nil {
		model = model.Where("item.status = ?", *request.Status)
	}

	if err := model.Count(&total).Error; err != nil {
		response.Error(c, errors.ErrInternalServer)
		return
	}
	if err := model.Select([]string{
		"item.id",
		"item.code",
		"item.name",
		"item.status",
		"item.created_at",
	}).Scopes(database.Paginate(request.Page, request.Limit)).
		Order("item.id DESC").
		Scan(&list).Error; err != nil {
		response.Error(c, errors.ErrInternalServer)
		return
	}

	response.Success(c, gin.H{
		"list":  list,
		"total": total,
	})
}
```

- 列表必须返回 `list` 和 `total`。
- `list` 必须使用 `make([]struct {...}, 0)`，保证空结果编码为 `[]`。
- 筛选条件和 projection 必须在当前 handler 可见；禁止下沉到仅被当前 handler 调用的 `listXxx` 或 query object。
- 列表中的关联 object 或 array 必须按 [database/projection.md](../database/projection.md) 由 SQL 直接构造；禁止扫描扁平行后使用 `for range` 查询、匹配或组装关联结构。

## Detail 接口

`GetXxxDetail` 必须按以下顺序直接写在 handler：匿名 request、绑定、匿名 projection、GORM model、权限与可见性条件、Join/Select、`Take`、错误映射、response。

```go
func GetCatalogItemDetail(c *gin.Context) {
	request := struct {
		ID int64 `json:"id" form:"id" binding:"required,gt=0"`
	}{}
	if err := validator.BindQuery(c, &request); err != nil {
		response.Error(c, err)
		return
	}

	var detail struct {
		ID       int64             `json:"id"`
		Category datatypes.JSONMap `json:"category" gorm:"type:jsonb"`
		Code     string            `json:"code"`
		Name     string            `json:"name"`
		Status   int16             `json:"status"`
	}
	model := database.DB.WithContext(c.Request.Context()).
		Table(database.Table(&models.CatalogItem{}) + " AS item").
		Joins("INNER JOIN " + database.Table(&models.CatalogCategory{}) + " AS category ON category.id = item.category_id AND category.deleted_at IS NULL").
		Where("item.id = ? AND item.deleted_at IS NULL", request.ID).
		Select([]string{
			"item.id",
			"jsonb_build_object('id', category.id, 'code', category.code, 'name', category.name) AS category",
			"item.code",
			"item.name",
			"item.status",
		})
	if err := model.Take(&detail).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			response.Error(c, apperrors.ErrNotFound)
			return
		}
		response.Error(c, apperrors.ErrInternalServer)
		return
	}
	response.Success(c, detail)
}
```

- Detail 必须使用 query 参数接收资源标识，并通过 `validator.BindQuery` 绑定；禁止从 `/:id` path 读取业务资源标识。
- Detail 必须使用 handler 内匿名 projection，禁止直接返回完整 model。
- 单条 projection 必须使用 `Take`；未命中必须单独映射 `gorm.ErrRecordNotFound`，禁止把未命中与数据库故障返回成同一个错误。
- 权限、组织、工作区和资源可见性条件必须进入当前查询；禁止先无范围加载记录，再在响应前补做权限判断。
- 当前行的关联对象和数组按 [database/projection.md](../database/projection.md) 直接由 SQL 构造。Detail 包含多个相互独立的一对多集合时，必须按该文件的集合拆分规则在同一 handler 内分别查询并直接组合 response。

## 数据库 Options 接口

`GetXxxOptions` 直接投影为前端选项，不分页、不 `Count`，成功时直接返回数组：

```go
func GetCatalogCategoryOptions(c *gin.Context) {
	list := make([]struct {
		Value int64  `json:"value"`
		Label string `json:"label"`
		Code  string `json:"code"`
	}, 0)
	if err := database.DB.WithContext(c.Request.Context()).
		Table(database.Table(&models.CatalogCategory{}) + " AS category").
		Where("category.deleted_at IS NULL").
		Where("category.status = ?", models.CatalogCategoryStatusEnabled).
		Select([]string{
			"category.id AS value",
			"category.name AS label",
			"category.code",
		}).
		Order("category.sort ASC, category.id ASC").
		Scan(&list).Error; err != nil {
		response.Error(c, errors.ErrInternalServer)
		return
	}
	response.Success(c, list)
}
```

- 只查询选项实际需要的字段，使用 `AS value`、`AS label` 对齐稳定契约。
- 状态条件必须使用 model 常量，禁止写魔法值。
- 必须明确稳定排序；禁止依赖数据库自然顺序。
- 禁止复用分页列表 handler、返回完整 model 或包装成 `gin.H{"list": list}`。

## 代码常量接口

不可由运营修改的状态、动作或协议常量直接在 handler 返回有序 slice：

```go
func GetCatalogItemStatusOptions(c *gin.Context) {
	response.Success(c, []struct {
		Value int16  `json:"value"`
		Label string `json:"label"`
	}{
		{Value: models.CatalogItemStatusEnabled, Label: "启用"},
		{Value: models.CatalogItemStatusDisabled, Label: "停用"},
	})
}
```

- 常量定义必须位于所属 model 或领域 contract；展示用 `value`、`label` 映射允许直接写在 handler。
- 禁止为了两三个常量创建 service、mapper、converter、options helper 或使用无序 map。
- 可由运营新增、改名、排序或停用的选项不得写成代码常量，必须按 [models/struct.md](../models/struct.md) 的业务注册表规则走表查询。

## Helper 提取门槛

常规接口逻辑必须直接写在 handler。只有命中以下任一条件时才允许提取 private helper：

1. 已经存在两个及以上真实调用方，且共享稳定业务不变量、安全边界或原子性要求。
2. 单个复杂流程包含可独立描述的业务阶段，该阶段具有独立失败处理、补偿、资源生命周期或需要独立验证的不变量；提取后 handler 仍明确表达主流程与事务边界。

第二种情况允许只有一个调用方。private helper 必须留在所属 handler package 的资源文件中；禁止仅因流程复杂就创建 service、repository、capability 或迁入 infra。外部能力适配与生命周期 wiring 另按 [infra/placement.md](../infra/placement.md) 判定。

允许的虚构例子包括：多个 handler 共用的条目加载与集合归属校验、稳定的签名处理。禁止提取只为缩短函数的 `bindXxx`、`listXxx`、`detailXxx`、`buildXxxQuery`、`createXxx`、`updateXxx`、`deleteXxx`。

“以后可能复用”、代码较长、字段较多、存在 transaction 或两个入口代码相似，都不满足提取条件。

## 验收

- Binding 错误直接 `response.Error(c, err)` 后返回；持久化错误不得向客户端泄露 SQL 或存储细节。
- 必须核对 handler package 只按一级业务模块和资源文件组织，没有按 URL 或 action 过度拆目录。
- 必须核对常规 Router 直接注册包级函数，没有为普通 CRUD 新增 Handler struct 或依赖表。
- 必须核对 detail 使用 `Select + Take`、独立处理 `gorm.ErrRecordNotFound`，并且资源可见性条件已经进入查询。
- 必须运行下面的候选扫描，并逐个检查命中项；不能证明上述任一提取条件时必须内联：

  ```bash
  rg -n --glob '*.go' '^func (list|detail|query|get|find|create|update|delete|save|bind|build)[A-Z][A-Za-z0-9_]*\(' app
  ```

- 必须继续执行 [request.md](request.md)、[http/response.md](../http/response.md)、[write-handler.md](write-handler.md)、[database/query.md](../database/query.md) 和 [database/projection.md](../database/projection.md) 中本次命中的检查。
