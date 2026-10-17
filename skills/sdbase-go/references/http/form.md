---
name: http-form
description: sdkitgo 公共分页、列表和安全排序 request 的固定写法
---

# HTTP Form 规范

本文适用于 `app/http/form`、分页 request、列表 request 和客户端排序。新增或修改 `PageRequest`、`ListRequest`、`SortRequest`、`OrderBy` 或任一列表接口的排序输入时必须读取本文；业务筛选字段继续按 [service/request.md](../service/request.md) 放在所属 handler。

## 公共结构

`app/http/form` 只允许保存跨 HTTP service 使用的稳定请求片段。分页结构固定为：

```go
type PageRequest struct {
	Page  int `json:"page" form:"page,default=1" binding:"min=1"`
	Limit int `json:"limit" form:"limit,default=20" binding:"min=1,max=100"`
}

type ListRequest struct {
	PageRequest
	SortRequest
}
```

- 分页列表必须嵌入 `PageRequest`；同时开放排序时嵌入 `ListRequest`，禁止在每个 handler 重复声明 `page`、`limit`、`order_column` 和 `sort_type`。
- 单个资源的 `search`、`status`、`category_id` 等筛选条件必须继续写在 handler 的匿名 request 中，禁止放入 `app/http/form`。
- `PageRequest` 的默认值和上限不得由单个 handler 修改；接口确实需要超过 100 条时必须改成 options、导出、批处理或专用有界接口，禁止临时放大公共 `limit`。

## 安全排序

客户端排序固定使用：

```go
import "strings"

const (
	SortAsc  = "asc"
	SortDesc = "desc"
)

type SortRequest struct {
	OrderColumn string `json:"order_column" form:"order_column" binding:"omitempty"`
	SortType    string `json:"sort_type" form:"sort_type" binding:"omitempty,oneof=asc desc"`
}

func (r SortRequest) OrderBy(defaultOrder string, allowedColumns map[string]string) string {
	if r.OrderColumn == "" || r.SortType == "" {
		return defaultOrder
	}
	column, ok := allowedColumns[strings.TrimSpace(r.OrderColumn)]
	if !ok || strings.TrimSpace(column) == "" {
		return defaultOrder
	}
	column = strings.TrimSpace(column)
	order := column + " " + sortDirection(r.SortType, SortDesc)
	defaultOrder = filterOrderByColumn(defaultOrder, column)
	if defaultOrder == "" {
		return order
	}
	return order + "," + defaultOrder
}

func sortDirection(value, fallback string) string {
	direction := strings.ToLower(strings.TrimSpace(value))
	if direction == SortAsc || direction == SortDesc {
		return direction
	}
	fallback = strings.ToLower(strings.TrimSpace(fallback))
	if fallback == SortAsc {
		return SortAsc
	}
	return SortDesc
}

func filterOrderByColumn(order, column string) string {
	parts := strings.Split(order, ",")
	kept := make([]string, 0, len(parts))
	for _, part := range parts {
		part = strings.TrimSpace(part)
		if part == "" || orderColumn(part) == column {
			continue
		}
		kept = append(kept, part)
	}
	return strings.Join(kept, ",")
}

func orderColumn(order string) string {
	fields := strings.Fields(strings.TrimSpace(order))
	if len(fields) == 0 {
		return ""
	}
	return fields[0]
}
```

- 客户端提交的是公开排序字段名，不是 SQL column 或表达式。
- Handler 必须把公开字段通过显式 allowlist 映射为带表别名的可信 SQL column，再调用 `SortRequest.OrderBy(defaultOrder, allowedColumns)`。
- `defaultOrder` 必须包含稳定的唯一键兜底顺序，例如 `item.created_at DESC, item.id DESC`；用户选择的字段相同时，`OrderBy` 必须移除默认顺序中的重复字段并保留唯一键兜底。
- 未提供完整排序参数、字段不在 allowlist 或方向非法时，必须退回 `defaultOrder`。
- 禁止把 `request.OrderColumn`、`request.SortType` 或任意客户端字符串直接传给 `Order`、`fmt.Sprintf` 或原生 SQL。
- Allowlist 必须在当前 handler 内直接可见。只有两个以上真实列表接口使用完全相同的公开排序契约和 SQL alias 时，才允许提升为所属 handler package 的 private variable。

正向形态：

```go
request := struct {
	form.ListRequest
	Search string `json:"search" form:"search" binding:"omitempty,max=100"`
}{}
if err := validator.BindQuery(c, &request); err != nil {
	response.Error(c, err)
	return
}

orderBy := request.OrderBy(
	"item.created_at DESC, item.id DESC",
	map[string]string{
		"name":       "item.name",
		"created_at": "item.created_at",
	},
)
model = model.Scopes(database.Paginate(request.Page, request.Limit)).Order(orderBy)
```

最终 `Scan` 和错误响应继续按 [service/handler.md](../service/handler.md) 的列表接口顺序执行，禁止忽略查询错误。

## 验收

- 必须测试默认分页、非法 page/limit、默认排序、每个开放排序字段、asc/desc 和未知字段回退。
- 必须搜索 `Order(request.`、`Order(fmt.Sprintf` 以及由 request 字段拼接的 SQL；任何未经 allowlist 映射的命中都不通过。
- `app/http/form` 不得出现业务资源名、数据库查询或单接口筛选字段。
