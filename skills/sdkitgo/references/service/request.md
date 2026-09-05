---
name: service-request
description: sdkitgo handler request struct、JSON、query、form 绑定和 binding tag 规则
---

# HTTP Request 规范

本文适用于 sdkitgo 服务中的 HTTP request struct、JSON/query/form 绑定和 binding tag。新增或修改请求字段或绑定方式时必须读取本文；修改公共 binding 入口或自定义 tag 时同时读取 [http/validator.md](../http/validator.md)。

## 绑定

- JSON 请求参数使用 `app/http/validator.BindJSON(c, &request)`。
- Query 请求参数使用 `app/http/validator.BindQuery(c, &request)`。
- Form 请求参数使用 `app/http/validator.BindForm(c, &request)`。
- 绑定错误直接 `response.Error(c, err)` 后返回。
- 只被一个 handler 使用的 request struct 必须在 handler 内匿名定义；仅当两个及以上 handler 使用完全相同的传输契约时，才允许在所属 handler package 定义 named request struct。禁止把 HTTP request struct 放入 `app/models` 或跨入口公共 DTO package。
- request 字段必须同时写 `json` 和 `form` tag；仅当字段明确禁止从其中一种传输格式绑定时，才允许省略对应 tag，并必须在相邻注释说明原因。

示例：

```go
request := struct {
	ParentID int64 `json:"parent_id" form:"parent_id" binding:"required,gt=0"`
}{}
if err := validator.BindQuery(c, &request); err != nil {
	response.Error(c, err)
	return
}
```

## 校验

- 没有额外规则的可选字段使用 `binding:"omitempty"`。
- 能用 `binding` tag 表达的校验必须放在 request struct 上，例如 `required`、`gt=0`、`oneof=0 1 2`、`required_with`、`gtfield`。
- handler 禁止重复检查 binding 已保证的条件。例如示例中的 `ParentID` 已由 `binding:"required,gt=0"` 保证存在且大于 0，handler 不得再次判断同一条件。
- 自定义 validator 的准入条件、文件位置和写法以 [http/validator.md](../http/validator.md) 为唯一权威规则。
- handler 里只保留需要业务上下文的校验，例如数据库存在性、权限、状态流转。

## 验收

- 必须人工核对本次修改的每个 request 字段都有正确的 `json`、`form` 和 `binding` tag，或有符合上述条件的省略说明。
- 必须测试至少一个合法请求和每类新增校验的非法请求，确认 binding 错误通过 `response.Error(c, err)` 返回。
- 禁止在 handler 中保留与 binding tag 重复的条件判断。
