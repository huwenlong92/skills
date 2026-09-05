---
name: service-provider
description: sdkitgo service provider、kind、capability、runtime wiring 和 factory 规则
---

# Service Provider 规范

本文适用于 sdkitgo service provider、capability 声明和 runtime wiring。新增或修改 service 注册、service kind/group、required capability、runtime capability、config loader 绑定或 service factory 时必须读取本文；配置归一化同时读取 [config.md](config.md)，实现 capability bridge 同时读取 [infra/capability.md](../infra/capability.md)。新增完整 service 时还必须读取 [creation.md](creation.md)。

## Provider 职责

- service provider 负责注册 service、声明 kind/group、声明 required capability、配置 runtime capability、创建 service 实例。
- provider 不承载业务 handler、worker task、crontab job 或 realtime event 执行逻辑。
- provider 中的依赖关系必须显式表达，不隐式依赖全局状态。

## Service 注册

- HTTP service 使用 `runtime.ServiceKindHTTP`。
- Queue/worker service 使用 `runtime.ServiceKindQueue` 和合适的 worker group。
- API、worker、crontab、realtime 等 service group 必须使用 core runtime 已有分组表达；core 缺少所需分组时必须按 [framework/boundary.md](../framework/boundary.md) 的边界处理，禁止在项目内复制 runtime 分组机制。
- service name 使用短稳定名称，例如 `admin`、`web`、`api`、`worker`、`crontab`、`realtime`。

## Capability

- `RequireCapabilities` 声明 service 启动必需能力。
- `RuntimeCapabilities` 中只做 capability wiring 和 config loader 绑定。
- Capability 的 `UseConfigFile`、container bind、取值和资源所有权必须遵循 [infra/capability.md](../infra/capability.md)；禁止在 Provider 内复制 capability 构造实现。
- 项目级 capability bridge 放 `app/infra/capability/*`。
- 服务私有 capability bridge 放 `app/{service}/infra/capability/*`。
- capability bridge 只能包含项目配置转换、业务契约适配和 wiring；框架行为必须交给 core facade。它不是 sdkit `runtime.Adapter`；需要新增 runtime adapter contract 时必须按 [framework/boundary.md](../framework/boundary.md) 处理。
- 如果 capability 行为属于 core facade bug，必须改 core，禁止在 provider 里绕过。

## Config Loader

- provider 调用 service config loader 时，必须传入 loader 契约声明需要的 `ctx.ConfigFile`、`ctx.Name` 和 `ctx.BaseConfig()`。
- capability config 属于 core 配置结构时必须使用 core config loader；属于当前项目配置结构时必须使用项目薄 adapter 加载。
- 默认值和业务配置归一化以 [config.md](config.md) 为唯一权威规则；禁止在 provider 中重复实现。

## Service Factory

- service factory 负责加载 config、创建 server/service、返回 runtime service adapter。
- HTTP service 必须返回 `runtime.HTTPService`；仅当项目已有服务包装实现相同 runtime 生命周期契约且本次不改变该契约时，才允许继续返回该包装。
- 非 HTTP service 实现 core runtime 需要的 `ServiceInfo`、`Start`、`Shutdown`。
- 创建失败时直接返回错误，不吞掉配置或依赖错误。

## 正向典型形态

Provider 必须保持链式声明；capability wiring 和 service factory 分开表达：

```go
func Provider() runtime.ServiceProvider[*bootstrap.Config] {
	return runtime.ServiceProviderFunc[*bootstrap.Config](func(app *runtime.ServiceApp[*bootstrap.Config]) error {
		app.Service("api").
			Kind(runtime.ServiceKindHTTP).
			RequireCapabilities(database.Name, redis.Name).
			RuntimeCapabilities(func(ctx runtime.RuntimeCapabilityContext[*bootstrap.Config]) []runtime.CapabilityContract {
				return []runtime.CapabilityContract{
					database.UseConfigFile(ctx.ConfigFile),
					redis.UseConfigFile(ctx.ConfigFile),
				}
			}).
			FactoryContext(func(ctx runtime.ServiceContext[*bootstrap.Config]) (runtime.Service, error) {
				cfg, err := config.Load(ctx.ConfigFile, ctx.Name, ctx.Base)
				if err != nil {
					return nil, err
				}
				srv, err := NewServerWithContext(cfg, &ctx)
				if err != nil {
					return nil, err
				}
				return runtime.HTTPService{
					InfoValue: cfg.ServiceInfo(),
					StartFunc: srv.Start,
					StopFunc:  srv.Shutdown,
				}, nil
			})
		return nil
	})
}
```

禁止在 `RuntimeCapabilities` 或 `FactoryContext` 中内联业务 handler、queue task、crontab job 或配置归一化。

## 验收

- 必须核对 service kind、group、name、required capability 和 runtime capability 与实际启动依赖一致。
- Provider 只能包含注册、声明、config loader 绑定和 wiring；不得出现业务 handler、task、job、event 执行逻辑或配置默认值。
- 必须运行 service provider 构建或启动测试，并验证必需 capability 缺失和 config loader 失败会阻止 service 创建。
