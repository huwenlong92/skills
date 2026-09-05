---
name: service-router
description: sdkitgo Gin router 的逐层 Group、中间件作用域和 handler 注册规则
---

# HTTP Router 规范

本文定义 sdkitgo Gin 路由树、逐层 `Group`、中间件作用域和 handler 注册方式。修改 `app/{service}/router.go`、route path、HTTP method、group 或 middleware 时必须读取本文；新增 middleware 实现同时读取 [middleware.md](middleware.md)，非 CRUD 动作 handler 同时读取 [action-handler.md](action-handler.md)。

## 逐层 Group

Router 必须使用逐层 `Group` 表达 URL 层级。目录只负责 handler 的业务模块分类，不能代替 RouterGroup；RouterGroup 也不能要求 handler 按每层 URL 建目录。

```go
catalogGroup := router.Group("catalog", middleware.SessionRequired(), middleware.Casbin())
{
	inventoryGroup := catalogGroup.Group("inventory")
	{
		itemsGroup := inventoryGroup.Group("items")
		{
			itemsGroup.GET("", catalog.GetItemList)
			itemsGroup.GET("options", catalog.GetItemOptions)
			itemsGroup.GET("detail", catalog.GetItemDetail)
			itemsGroup.POST("create", catalog.CreateItem)
			itemsGroup.POST("update", catalog.UpdateItem)
			itemsGroup.POST("delete", catalog.DeleteItem)
		}
	}

	taxonomyGroup := catalogGroup.Group("taxonomy")
	{
		categoriesGroup := taxonomyGroup.Group("categories")
		{
			categoriesGroup.GET("", catalog.GetCategoryList)
			categoriesGroup.GET("options", catalog.GetCategoryOptions)
			categoriesGroup.POST("create", catalog.CreateCategory)
			categoriesGroup.POST("update", catalog.UpdateCategory)
			categoriesGroup.POST("delete", catalog.DeleteCategory)
		}
	}
}
```

- 每个 group path 和 route path 必须是相对片段，不带前导 `/`。
- 多层资源路径必须逐层 `Group`；禁止把 `catalog/inventory/items` 压成一个长字符串注册。
- 每个 group 必须使用表达所属资源的变量名，例如 `catalogGroup`、`inventoryGroup`、`itemsGroup`；禁止使用 `g1`、`subGroup`、`group2`。
- 每个 group 使用独立代码块包住所属子 group 和路由，使完整层级可直接阅读。
- 资源 group 的列表使用 `GET("")`，不得增加多余的 `list` 路径。
- 资源名使用复数和 kebab-case，例如 `items`、`item-options`、`sync-rules`。
- 禁止在 path、group、handler 或请求类型名中增加 `v1`、`v2`。仅当用户明确要求同时维护多套外部契约时才允许版本路径。
- 业务路由禁止使用 `/:id`、`/:code`。GET 的资源标识放 query，POST 的资源标识放 JSON body，并通过统一 validator 绑定。

## Method 与动作顺序

- 查询、options 和 detail 使用 `GET`。
- create、update、delete、status、dispose、evaluate 等写操作统一使用 `POST`。
- 同一资源内按列表、options、detail、create、update、delete、其他业务动作的顺序注册。
- 业务动作必须使用明确动词，例如 `evaluate`、`dispose`、`batch-dispose`；禁止使用 `action`、`operate`、`handle`。
- Enable、approve、reset、assign 和 batch 等非 CRUD 动作必须遵循 [action-handler.md](action-handler.md) 的状态与事务规则。

## Middleware

- 被两个及以上同类路由共享的 middleware 必须挂在能覆盖它们的最窄公共 group，由子 group 继承；禁止在每条 route 重复注册。
- 单路由独有的资源校验 middleware 保留在该 route。
- middleware 顺序固定为：会话/身份认证 → 工作区或组织上下文 → Casbin 权限 → 资源所有权/分派校验 → handler。
- `Casbin()` 依赖工作区或组织中间件产生的上下文时，必须放在对应中间件之后。
- 同一路径前缀下存在不同认证条件时，必须创建 sibling group 分别挂载 middleware，禁止为了少写 group 而扩大 middleware 作用域。

## 注册边界

- `app/{service}/router.go` 必须集中显示当前 service 的完整路由树。
- Router 必须直接注册 handler package 的包级函数，例如 `itemsGroup.GET("", catalog.GetItemList)`。
- 禁止仅为缩短 `router.go` 提取一组 `registerXxxRoutes()` 小函数。
- 禁止在 router 中创建普通业务 Handler struct、repository、service locator 或依赖表。
- handler 文件按 [handler.md](handler.md) 使用 `handler/{module}/{resource}.go`；URL 有三层不代表 handler 必须建立三层目录。

## 验收

- 必须列出或测试每条修改路由的 HTTP method、完整 path、middleware 顺序和 handler。
- 路由重构不得改变现有 method、完整 path 或 middleware 作用域；只有用户明确要求契约变化时才允许改变。
- 必须核对公共 middleware 只挂载一次，单路由 middleware 没有扩散到 sibling route。
- 必须人工检查 `router.go`，确认无需跳转到多个 `registerXxxRoutes()` 才能还原完整路由树。
