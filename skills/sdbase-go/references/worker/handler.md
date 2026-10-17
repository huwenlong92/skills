---
name: worker-handler
description: sdkitgo queue worker 的 taskdef、event handler、registry、hook 和进度规则
---

# Worker 规范

本文定义 sdkitgo 项目中的 queue worker task 和 handler 组织方式。新增或修改 task type、payload、constructor、worker event handler、registry、queue hook 或任务进度时必须读取本文。

## Task Definition

- worker task type 和 payload struct 放在 `app/worker/taskdef`。
- 业务域 task definition 放在 `app/worker/taskdef/{domain}`。
- task type constant 是稳定契约，不从 UI 文案或 handler 名推导。
- payload struct 跟 task type constant 放在一起。
- task constructor 跟 task type 和 payload 放在一起，例如 `NewArtifactRecognizeTask(payload)`。

## Event Handler

- worker 执行逻辑放在 `app/worker/event`。
- 业务域 handler 放在 `app/worker/event/{domain}`。
- worker handler 接收 `context.Context` 和 payload，不依赖 `gin.Context` 或 HTTP 请求语义。
- 仅当 task contract 明确定义 nil payload 的含义和默认值时，handler 才允许接受 nil，并必须在执行前归一化 payload；其他 task 收到 nil 时必须返回明确错误。
- 简单 payload 解析、业务校验、GORM 查询、更新和单个 transaction 必须直接写在 worker handler，禁止为单个任务创建一对一转发的 operation、service 或 private helper。
- 只有流程包含两个及以上具有独立失败处理、资源生命周期、transaction、重试边界或独立测试价值的阶段时，才允许把这些阶段拆成同 domain package 下的 private helper。代码行数较多、希望缩短 handler 或未来可能复用都不构成拆分条件。
- 被拆出的 helper 必须以阶段业务语义命名并完成该阶段的实际工作；禁止出现只转发相同参数的 `syncXxx`、`handleXxx`、`processXxx` 包装层。
- helper 禁止移动到通用 package，除非已经存在两个及以上 domain 调用方且共享稳定契约。

## Registry

- `app/worker/registry.go` 只注册 runtime middleware、hook 和 task handler。
- `registry.go` 不承载业务执行逻辑。
- final failure cleanup、状态恢复、日志恢复通过 queue hook 接入。

## Runtime 和副作用

- worker 使用 core queue runtime 概念，不写本地 queue 补丁。
- queue runtime 行为有问题时，必须修改实际依赖的 core `queue` package；禁止在业务项目本地绕过。
- 任务契约包含用户可见进度时，必须通过当前业务域已有日志或 realtime helper 记录；禁止直接从 worker 写入 HTTP response 或 UI 专属状态。

## 正向典型形态

Task type、payload 和 constructor 必须放在同一个 `taskdef` 文件：

```go
const TypeResourceActivate = "resource:activate"

type ResourceActivatePayload struct {
	ResourceID int64 `json:"resource_id"`
}

func NewResourceActivateTask(payload ResourceActivatePayload) queue.Task {
	return queue.NewTask(TypeResourceActivate, payload)
}
```

简单 Event handler 直接完成任务专属的数据库逻辑：

```go
func HandleResourceActivate(ctx context.Context, payload *taskdef.ResourceActivatePayload) error {
	if payload == nil {
		return errors.New("resource activate payload is required")
	}
	result := database.DB.WithContext(ctx).
		Model(&models.Resource{}).
		Where("id = ? AND deleted_at IS NULL", payload.ResourceID).
		Updates(map[string]any{
			"status": models.ResourceStatusEnabled,
		})
	if result.Error != nil {
		return result.Error
	}
	if result.RowsAffected == 0 {
		return errors.New("resource not found")
	}
	return nil
}
```

Registry 只组装 middleware 和 registration：

```go
func RegisterEvents(r *queue.Registry, metadata ...queue.RuntimeMetadata) error {
	r.UseRuntime(workermiddleware.RuntimePipelineStages(metadata...)...)

	registrations := []queue.Registration{
		queue.Register(taskdef.TypeResourceActivate, event.HandleResourceActivate),
	}
	return r.RegisterAll(registrations...)
}
```

复杂 handler 只有在存在上述客观阶段边界时才允许拆分，例如“读取并校验不可变输入 artifact”和“在独立 transaction 中集合式合并数据”分别具有自己的失败处理与测试。拆分后 handler 必须直接展示阶段顺序，禁止再增加总入口转发 wrapper。跨入口共享的稳定业务能力必须按 [infra/placement.md](../infra/placement.md) 放入 capability。

## 验收

- 必须核对 task type、payload 和 constructor 同域放置，执行逻辑只位于 `app/worker/event/{domain}`，`registry.go` 只做注册。
- 必须检查简单任务的 payload、校验、查询和写入仍在 handler 中直接可见；每个 private helper 都必须指出命中的阶段拆分条件，不满足时必须内联。
- 必须测试合法 payload、非法或 nil payload、成功执行和 final failure hook；存在重试时必须验证重复执行不会破坏业务状态。
- Queue runtime 缺陷必须在实际依赖的 core package 验证，业务项目不得新增本地补丁。
