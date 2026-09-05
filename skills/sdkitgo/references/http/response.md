---
name: http-response
description: sdkitgo Gin handler 与 middleware 的成功、错误和中止响应写法
---

# HTTP Response 规范

本文适用于 sdkitgo 服务中的 HTTP 响应输出。新增或修改 handler 成功响应、空成功响应、业务错误、middleware 中止响应或错误包装时必须读取本文。

- 业务错误使用 `response.Error(c, err)`。
- Middleware 拒绝请求时使用 `response.AbortError(c, err)`，随后必须立即 `return`；禁止只写错误但继续执行后续 middleware 或 handler。
- 成功且有数据时使用 `response.Success(c, data)`。
- 成功但无数据时使用 `response.OK(c)`。
- 禁止用 `response.Success(c, nil)` 表示空成功。
- 禁止把 `msg` 塞进 `data`；消息必须使用外层响应字段。

## 正向典型形态

```go
response.Success(c, detail)
response.Success(c, gin.H{"list": list, "total": total})
response.OK(c)
response.Error(c, errors.ErrNotFound)
response.AbortError(c, errors.ErrUnauthorized)
```

五种形态必须按“有数据成功、列表成功、无数据成功、handler 错误、middleware 中止”分别使用，禁止再包一层项目自定义 response helper。

## 验收

- 必须覆盖有数据成功、无数据成功和本次新增错误分支；middleware 修改还必须验证 abort 后下游 handler 未执行。核对其 HTTP 状态、业务错误码和关键响应字段。
- 响应体不得出现 `data.msg`，空成功不得输出 `data: null` 代替 `response.OK(c)`。
