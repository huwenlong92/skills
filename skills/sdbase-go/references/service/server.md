---
name: service-server
description: sdkitgo service server 的构造、Start、Shutdown 和资源所有权规则
---

# Service Server 规范

本文适用于 `app/{service}/server.go`、`Server` struct、`NewServerWithContext`、`Start`、`Serve` 和 `Shutdown`。新增或修改 HTTP、realtime、worker、crontab 等 service 生命周期时必须读取本文，并同时读取 [provider.md](provider.md)；HTTP Router 装配同时读取 [router.md](router.md)。

## 职责

`server.go` 只负责当前 service 的运行时装配和生命周期：

- 接收已经加载并校验的 service config；
- 解析 `ServiceContext` 中已经注册的 capability；
- 构造 Router、`http.Server`、consumer、scheduler 或当前 service 自有后台资源；
- 启动阻塞式 service runtime；
- 在 Shutdown 中停止接收新工作并释放当前 service 自己创建的资源。

禁止在 `server.go` 定义业务 handler、CRUD、projection、task/template 业务逻辑、配置文件加载或 service Provider 注册。必须在接流量前完成的业务 definition 注册允许由 `NewServerWithContext` 调用，但实际注册逻辑必须位于所属 `infra` package，禁止内联表操作。

## 构造

- `NewServer(cfg)` 只作为无显式 runtime context 的便捷入口，并必须转发到 `NewServerWithContext(cfg, ctx)`；禁止维护两套构造逻辑。
- `NewServerWithContext` 必须使用 `runtime.EnsureServiceContext` 归一化 context，再从中解析 capability；禁止重新读取整个配置文件或自行启动另一套 runtime container。
- 构造过程中创建的 cancel、listener、consumer、logger writer 或其他资源必须立即明确 owner。后续步骤失败时必须释放此前已经创建的资源再返回 error。
- 注入的 capability 默认由 runtime container 拥有，Server Shutdown 禁止关闭；只有构造函数明确创建并记录 `owned` 状态的 fallback 资源才允许由 Server 关闭。
- Router 构造失败、必需 capability 缺失或 runtime component 创建失败必须阻止 Server 返回成功，禁止以 nil component 继续启动。

## Start 与 Serve

- `Start` 必须验证 Server 已初始化，并阻塞运行当前 service；`http.Server.ListenAndServe` 返回 `http.ErrServerClosed` 时视为正常关闭，其他错误必须原样返回。
- 禁止在 `Start` 内再启动一个无人管理的 goroutine 后立即返回；并发运行和信号管理由 core runtime 负责。
- 只有测试、端口复用或进程级 listener 注入存在真实调用方时才允许增加 `Serve(listener)`；该方法必须复用同一 `http.Server`，禁止构造第二套路由。

```go
type Server struct {
	httpServer   *http.Server
	ownedRuntime *serviceRuntime
	cancel       context.CancelFunc
	service      string
}

func NewServerWithContext(cfg config.ServiceConfig, ctx *runtime.ServiceContext[*bootstrap.Config]) (*Server, error) {
	ctx = runtime.EnsureServiceContext[*bootstrap.Config](ctx, cfg.Name, cfg.Type, nil)
	backgroundCtx, cancel := context.WithCancel(context.Background())
	ownedRuntime, err := newOwnedRuntime(backgroundCtx, ctx, cfg)
	if err != nil {
		cancel()
		return nil, err
	}
	router, err := SetupRouterWithContext(ctx, cfg, ownedRuntime)
	if err != nil {
		cancel()
		_ = ownedRuntime.Close()
		return nil, err
	}
	return &Server{
		httpServer:   &http.Server{Addr: cfg.Addr, Handler: router},
		ownedRuntime: ownedRuntime,
		cancel:       cancel,
		service:      cfg.Name,
	}, nil
}
```

示例中的 `ownedRuntime` 仅表示由当前 Server 创建的资源；如果资源来自 `ServiceContext` capability，禁止在错误路径或 Shutdown 中关闭它。

## Shutdown

- `Shutdown(ctx)` 必须允许 nil receiver、未完整启动和重复调用，不得 panic。
- HTTP service 必须先通过 `http.Server.Shutdown(ctx)` 停止接收新请求，再取消和清理当前 service 自己拥有的后台资源；资源需要先停止生产再排空消费时，必须按该资源协议定义顺序，并在测试中固定。
- Shutdown 必须使用调用方传入的 context 和 deadline，禁止换成无期限 `context.Background()`。
- 多个关闭动作都可能失败时必须保留第一个错误，并继续执行不会扩大损坏的必要清理；禁止因前一个 close 失败跳过 cancel、临时文件清理或其他幂等释放。
- Service Server 禁止关闭进程共享的 database、Redis、tracing、eventbus 或其他注入 capability；这些资源由创建它们的 runtime owner 关闭。

## 验收

- 必须测试未初始化 Start、正常启动关闭、监听失败、Router/组件构造失败清理和重复 Shutdown。
- 必须为每个 Server 字段标明资源来源与 owner，并验证注入 capability 在 Server Shutdown 后仍可由其 runtime owner 使用。
- 必须确认 `server.go` 不读取配置文件、不注册 Provider、不包含业务 handler/CRUD，且 Start 没有脱管 goroutine。
