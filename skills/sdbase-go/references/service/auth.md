---
name: service-auth
description: sdkitgo 单个 HTTP service 的身份契约、Session 映射和身份读取规则
---

# Service Auth 规范

本文适用于 `app/{service}/auth`、Session payload、request authenticator、`coreauth.Identity` 映射和 handler 身份读取。新增或修改登录态结构、subject type、身份刷新、单点登录校验或身份 helper 时必须读取本文；请求链拦截和权限门禁同时读取 [middleware.md](middleware.md)。

## 目录职责

`app/{service}/auth` 只保存该 HTTP service 的身份契约：

- subject type、provider name、session key 和 service 自有 cookie/header 名称；
- 可序列化的 Session 用户结构；
- 把 Session、JWT 或其他凭证映射为 `coreauth.Identity` 的 authenticator；
- 认证有效性校验、滑动续期和认证失败清理 hook；
- 从 Gin context 读取当前 service identity、subject ID、username、role ID 和稳定 extra 字段的 helper。

禁止在 `auth` package 放 Gin route、response projection、普通业务 CRUD、页面权限列表、Casbin policy、资源所有权查询或与认证无关的 Redis/数据库操作。通用认证协议、Gin adapter 和 session runtime 属于 sdkit core，项目不得复制实现。

## Identity

- 每个 service 必须使用独立、稳定的 `SubjectTypeXxx`；`Identity(c)` 取出 core identity 后必须校验 subject type，不得把另一个 service 的身份当作当前身份。
- Middleware 认证成功后必须通过 core Gin auth adapter 写入 identity；handler 必须通过本 service 的 `auth.Identity`、`auth.AccountID` 等 helper 读取，禁止散落 `c.Get("userId")`、`c.Get("role")` 等字符串 key 和类型断言。
- 身份 helper 在 identity 不存在或类型不匹配时必须返回 nil 或对应类型零值，禁止 panic。需要登录态的 route 必须由 middleware 保证身份存在，不能让每个 handler 重复解析凭证。
- `Identity.Extra` 只允许保存能够从已验证凭证直接得到、并且当前 middleware 或 handler 确实读取的请求内稳定身份属性；需要实时数据库查询的业务资料、权限以及没有调用方的预留字段不得塞入 Extra。

正向形态：

```go
const SubjectTypeConsole = "console"

func Identity(c *gin.Context) *coreauth.Identity {
	identity := authgin.GetIdentity(c)
	if identity == nil || identity.SubjectType != SubjectTypeConsole {
		return nil
	}
	return identity
}

func AccountID(c *gin.Context) int64 {
	identity := Identity(c)
	if identity == nil {
		return 0
	}
	return identity.SubjectID
}
```

## Session Authenticator

- Session payload 只保存恢复 identity 和校验当前登录有效性所必需的字段；禁止把完整 GORM model、权限树或易变化的业务详情写入 Session。
- Mapper 必须验证 payload 类型、subject ID 和必要 token，再构造 `coreauth.Identity`；非法 payload 必须返回 core unauthorized error。
- 单点登录 token、Session 续期和认证失败清理允许作为 authenticator hook 留在 `auth` package，因为它们属于登录态生命周期；hook 必须使用传入的 `context.Context`，禁止创建脱离请求的后台 goroutine。
- 辅助 cookie 只能表达前端展示用的轻量登录提示，不能作为真实认证依据。真实身份必须来自服务端 Session、JWT 或 core authenticator。
- Session secret、token、cookie 内容和身份凭据禁止写日志或进入错误响应。

## 认证与授权边界

- `auth` 负责“凭证对应谁”；middleware 负责“本请求是否允许继续”；handler 负责当前业务动作的资源范围和状态校验。
- Casbin、组织/工作区门禁和资源所有权不允许进入 identity mapper。只有多个 route 共用的请求门禁才允许进入 [middleware.md](middleware.md)，单接口业务校验必须留在 handler。
- 登录、登出和刷新 token 本身仍是 handler；允许调用 `auth` 中稳定的 Session 生命周期方法，但禁止让 `auth` package 写 HTTP response。

## 验收

- 必须测试合法 identity、缺失 identity、错误 subject type、非法 Session payload、过期或失效 token、续期和失败清理。
- 必须搜索当前 service handler 中新增的 `c.Get(`、`c.Set(` 字符串身份 key；能够由 core adapter 和 `auth` helper 表达时不得保留。
- 必须确认 Session payload 不包含完整 model、权限树、secret 日志或非认证业务数据。
