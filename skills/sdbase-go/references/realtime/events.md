---
name: realtime-events
description: sdkitgo realtime event definition、publisher、room helper 和集中注册规则
---

# Realtime Event 规范

本文定义 sdkitgo realtime event 的归属、definition、publisher 方法和集中聚合。新增或修改 event name、payload、room/subject helper、publisher、transport 或 event 注册时必须读取本文。

## 分散归属，集中聚合

- 跨多个 service 的公共 event contract 放在 `app/infra/realtime`。
- 由单一 service 或业务入口拥有的 event contract 放在 `app/{service}/infra/realtime`。
- service 私有 realtime package 使用 `events.go` 保存该 service 拥有的 event constant 和 definitions，使用 `{resource}.go` 保存对应资源的 publisher。禁止把所有 publisher 继续堆进 `events.go`。
- `app/infra/realtime/events.go` 保存跨 service 的公共 event contract 和 definition 聚合 helper；`app/infra/realtime/subject.go` 只保存多个 service 共用的稳定 subject 编码。只服务一个 service 的 subject 或 room 规则必须留在该 service 的 realtime package。
- 每个拥有者 package 必须通过 `Events() []apprealtime.EventDefinition` 返回自己拥有的完整 definitions。
- Realtime gateway 必须在 `app/realtime/events.go` 显式导入需要对外提供的 event packages，并通过 `MergeEventDefinitions(...)` 集中聚合。
- 禁止把所有业务事件常量堆进一个全局文件；也禁止仅依靠各 package 的 `init()` 自动注册，导致 gateway 无法直接看出完整事件集合。

```text
app/infra/realtime/
  events.go                 跨 service event contract 与聚合 helper
  subject.go                跨 service subject 编码
app/console/infra/realtime/
  events.go                 console 拥有的 definitions
  resource.go               resource publisher
app/realtime/events.go       gateway 集中聚合入口
```

```go
func realtimeEventDefinitions() []apprealtime.EventDefinition {
	return apprealtime.MergeEventDefinitions(
		apprealtime.Events(),
		consolerealtime.Events(),
	)
}
```

新增服务事件时，必须同时修改所属 package 的 `Events()` 和实际承载该事件的 gateway 聚合入口。

## Event Definition

- Event name 是稳定协议，必须使用共享 constant；不得从 UI 文案、handler 名或临时功能名推导。
- Event name 使用点分层级表达业务事实或状态变化，例如 `catalog.resource.changed`、`console.account.permission.changed`。
- Definition 必须明确 `Name`、`Transports`、`Scope` 和 `Description`；支持默认 SSE 订阅时必须显式设置 `DefaultSSE`。
- Event constant、definition 和公共 payload contract 必须跟拥有该 event contract 的 package 放在一起。
- service 私有 publisher 必须放在 `app/{service}/infra/realtime/{resource}.go`。它允许发布 `app/infra/realtime` 已定义的公共 event，但必须直接引用公共 constant，禁止在 service package 重复声明同名 event。
- 被多个 service 使用的 subject 编码必须放在 `app/infra/realtime/subject.go`；service 私有 subject 或 room 编码必须放在自己的 realtime package。禁止把 subject/room 字符串拼接散落在 handler、worker 和 crontab 中。
- Payload 必须表达业务事实，禁止包含按钮文字、组件状态、toast 文案等 UI 渲染字段。
- 被多个 publisher 使用或字段较多的稳定 payload 必须定义 typed struct；只被一个 publisher 使用的简单刷新提示允许直接使用 `map[string]any`，禁止只为包装一两个固定字段创建单调用方 mapper。

```go
const EventResourceChanged = "resource.changed"

func Events() []apprealtime.EventDefinition {
	return []apprealtime.EventDefinition{
		{
			Name:        EventResourceChanged,
			Transports:  []string{apprealtime.TransportSSE},
			Scope:       apprealtime.ScopeBroadcast,
			Description: "资源配置变化，客户端刷新资源数据",
			DefaultSSE:  true,
		},
	}
}
```

## Publisher 方法

- `PushXxx` 表示向明确 user/subject/room 推送，必须返回 `error`。
- `BroadcastXxx` 表示广播，必须返回 `error`。
- `NotifyXxx` 仅用于业务已经成功、通知失败不应回滚业务的场景；它调用 `PushXxx`/`BroadcastXxx` 并记录失败，不向调用者返回错误。
- 需要通知失败阻止当前操作时，调用方必须使用返回 `error` 的 `PushXxx`/`BroadcastXxx`，禁止使用 `NotifyXxx`。
- 数据库变更触发的 realtime 通知必须在 transaction 成功提交后调用。
- Publisher 必须调用 core realtime facade；禁止直接写 SSE/WebSocket frame、gateway、subscription 或 transport 实现。

```go
type ResourceChangedPayload struct {
	IDs []int64 `json:"ids"`
}

func BroadcastResourceChanged(ctx context.Context, ids []int64) error {
	return corerealtime.Broadcast(ctx, EventResourceChanged, ResourceChangedPayload{
		IDs: ids,
	})
}

func NotifyResourceChanged(ctx context.Context, ids []int64) {
	if err := BroadcastResourceChanged(ctx, ids); err != nil {
		logger.WithContext(ctx, logger.L).Warn("资源变化实时通知失败", zap.Error(err))
	}
}
```

定向用户推送必须先通过公共 subject helper 形成稳定 subject，再调用 core facade。下面的 helper 位于 `app/infra/realtime/subject.go`，publisher 位于虚构 service 的 `app/console/infra/realtime/resource.go`：

```go
const EventResourcePermissionChanged = "console.resource.permission.changed"

func ConsoleSubject(accountID int64) string {
	if accountID <= 0 {
		return ""
	}
	return SubjectKey("console", strconv.FormatInt(accountID, 10))
}

func PushResourcePermissionChanged(ctx context.Context, accountID int64) error {
	subject := apprealtime.ConsoleSubject(accountID)
	if subject == "" {
		return nil
	}
	return corerealtime.PushUser(ctx, subject, EventResourcePermissionChanged, map[string]any{
		"scope": "console",
	})
}

func NotifyResourcePermissionChanged(ctx context.Context, accountID int64) {
	if accountID <= 0 {
		return
	}
	if err := PushResourcePermissionChanged(ctx, accountID); err != nil {
		logger.WithContext(ctx, logger.L).Warn(
			"资源权限变化实时通知失败",
			zap.Int64("account_id", accountID),
			zap.Error(err),
		)
	}
}
```

- `PushUser` 的第一个目标参数必须是 subject helper 的返回值，禁止直接传裸数据库 ID。
- `PushRoom` 的 room ID 必须由 realtime package 已定义的稳定 room helper 生成；如果调用方已经从受信任的 realtime contract 得到完整 room ID，可以直接透传，禁止重复加前缀。
- Subject 或 room helper 返回空字符串时，publisher 必须停止推送；是否返回 error 由该 helper 的既有契约决定，禁止把空目标发送给 core facade。

- 只有同一 room/subject/cache key 规则被两个及以上 publisher 使用，或它本身属于稳定 event contract 时，才允许提取 helper。
- 只被一个 publisher 使用的简单参数转换直接写在 publisher，禁止创建一组小 helper。

## Core 与 Gateway 边界

- `app/realtime` 负责项目 gateway 装配、聚合和 transport adapter，不拥有其他业务 service 的事件语义。
- realtime facade、transport、subscription、delivery 或 gateway 机制有问题时，必须按 [framework/boundary.md](../framework/boundary.md) 判断 sdkit 归属；禁止在业务 publisher 中打补丁。

## 验收

- 必须核对 event name constant、definition 和公共 payload 位于同一所有权域，service publisher 位于发起 service 的 realtime package，并直接引用所属 package 的 event constant。
- 必须核对 `Push`/`Broadcast`/`Notify` 的错误语义与调用场景一致，并确认数据库通知发生在 commit 之后。
- 必须核对 `PushUser` 未直接使用裸数据库 ID，`PushRoom` 使用稳定 room ID，空 subject/room 不会进入 core facade。
- 必须测试 definition 聚合去重、payload 序列化、目标 subject/room，以及至少一种声明支持的 transport。
- 必须搜索 event string 的直接字面量使用；除 constant 定义外，publisher 和订阅方必须引用共享 constant。
