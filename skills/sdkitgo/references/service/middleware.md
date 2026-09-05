---
name: service-middleware
description: sdkitgo 公共与 service 私有 Gin middleware 的放置、门禁和上下文规则
---

# Service Middleware 规范

本文适用于 `app/middleware`、`app/{service}/middleware`、Gin middleware、route group 门禁和请求上下文写入。新增或修改认证、组织/工作区、Casbin、资源访问、限流、访问日志或错误恢复 middleware 时必须读取本文，并同时读取 [router.md](router.md) 与 [http/response.md](../http/response.md)。

## 放置位置

- 两个以上 HTTP service 共同使用，且不依赖任一 service 身份、配置或 route 语义的项目 middleware 放在 `app/middleware`。
- 依赖某个 service 的 auth、Session、配置、Casbin subject、访问日志格式或组织/工作区语义的 middleware 必须放在 `app/{service}/middleware`。
- 只服务一条 route 的资源存在性、状态或所有权检查必须直接写在 handler；只有两个以上 route 使用完全相同的门禁、上下文输出和错误语义时，才允许提取为 service middleware。
- 跨项目通用的 recovery、request ID、tracking、tracing、CORS、session adapter 等机制属于 sdkit core；项目 middleware 只允许配置和业务适配，禁止复制 core 实现。

## HandlerFunc 形态

- Middleware 必须是返回 `gin.HandlerFunc` 的具名构造函数，例如 `SessionRequired()`、`WorkspaceRequired()`、`RateLimit(cfg)`。
- 失败时必须使用统一 abort response，随后立即 `return`；成功时写入规定的 context 值并调用一次 `c.Next()`。禁止已经写错误响应后继续 handler 链，也禁止同一路径多次调用 `c.Next()`。
- 认证 middleware 必须调用 service `auth` package 的 authenticator，并通过 core Gin auth adapter 保存 identity；禁止自行解析一套并行的用户 ID 字符串 key。
- Middleware 不返回业务 data，不构造 list/detail projection，不执行 create/update/delete，也不吞掉下游错误伪装为成功。
- 允许数据库或 Redis 的资源门禁必须是有界单次检查，并由两个以上 route 真实复用；复杂查询、状态迁移和接口专属判断必须留在 handler。

正向形态：

```go
func SessionRequired() gin.HandlerFunc {
	authenticator := consoleauth.SessionAuthenticator()
	return func(c *gin.Context) {
		c.Request = c.Request.WithContext(authgin.WithContext(c.Request.Context(), c))
		identity, err := authenticator.AuthenticateRequest(c.Request.Context(), c.Request)
		if err != nil || identity == nil || !identity.Authenticated() {
			response.AbortError(c, apperrors.ErrUnauthorized)
			return
		}
		authgin.SetIdentity(c, identity)
		c.Next()
	}
}
```

## Context 契约与顺序

- Middleware 写入的 context 值必须有唯一 owner 和读取 helper；禁止不同 middleware 重复写同义 key，禁止 handler 直接依赖未声明的字符串 key。
- Request `context.Context` 必须继续向数据库和下游调用传递；禁止在 middleware 中替换成 `context.Background()`。
- Middleware 的安装顺序和最窄公共 group 由 [router.md](router.md) 唯一规定。本文件不允许以单 route 重复注册绕过 Router 顺序。
- Access log、risk marker 等需要读取下游状态的 middleware 必须在调用 `c.Next()` 后读取结果；认证和权限门禁必须在 `c.Next()` 前完成并在失败时中止。

## 验收

- 必须测试失败时后续 handler 未执行、成功时只执行一次，以及 context 输出能被约定 helper 读取。
- 必须核对每个 middleware 的真实调用 route 数量和所属 service；单 route 业务检查不得提升为 middleware，跨 service middleware 不得 import service 私有 package。
- 必须列出修改后 Router 中的 middleware 顺序，并验证认证、上下文、Casbin 和资源门禁顺序符合 [router.md](router.md)。
- 必须搜索与 core recovery、request ID、tracking、tracing、CORS、session 同义的项目实现；没有项目适配语义的重复实现不通过。
