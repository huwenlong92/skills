---
name: go-map-formatting
description: sdkitgo 多行 map 字面量和 GORM 更新字段的逐行排版规则
---

# Go Map 排版规范

本文适用于 sdkitgo 项目中新增、修改或评审 map 字面量的场景，包括 GORM 更新字段和 `gin.H` 响应对象。

## 规则

- 多行 map 字面量必须每个键值对独占一行，最后一个键值对也必须保留尾逗号；禁止在同一行并排放置多个键值对。
- GORM `Updates(map[string]any{...})` 包含两个及以上更新字段时，必须展开为多行，逐行列出字段。
- 空 map 或只有一个键值对的 map 允许保持单行；本规则不要求拆分链式调用，也不改变字段选择、字段值和错误处理逻辑。
- 缩进及键值对齐必须交给 `gofmt`；禁止为了手工对齐加入与 `gofmt` 冲突的空格。必须人工检查每行键值对数量，禁止仅凭格式化命令成功就认定符合规则。

## 正向典型形态

以下片段只展示更新字段的排版，调用前的请求校验、记录查询和更新范围检查必须按写接口规范完成：

```go
if err := database.DB.WithContext(c.Request.Context()).Model(&row).Updates(map[string]any{
	"name":       strings.TrimSpace(request.Name),
	"code":       strings.TrimSpace(request.Code),
	"sort":       request.Sort,
	"updated_by": auth.AdminID(c),
}).Error; err != nil {
	response.Error(c, errors.ErrInternalServer)
	return
}
```

禁止写成：

```go
updates := map[string]any{
	"name": strings.TrimSpace(request.Name), "code": strings.TrimSpace(request.Code),
	"sort": request.Sort, "updated_by": auth.AdminID(c),
}
```

## 验收

- 必须人工检查本次新增或修改的多行 map，每行最多一个键值对，并保留尾逗号。
- 必须检查包含两个及以上字段的 GORM 更新 map 已展开为多行。
- 修改 Go 文件后必须运行 `gofmt`，并检查 diff 仅包含预期排版或本次授权的逻辑修改。

