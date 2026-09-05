---
name: infra-capability
description: sdkitgo 项目 runtime capability bridge 的目录、UseConfigFile、容器绑定和资源所有权规则
---

# Infra Capability 规范

本文适用于 `app/infra/capability/**`、`app/{service}/infra/capability/**`、`runtime.CapabilityContract`、`UseConfigFile` 和 capability 取值 helper。新增或修改 capability bridge 时必须读取本文；选择项目级或 service 私有位置先读取 [placement.md](placement.md)，判断 wrapper、业务 adapter、driver、runtime adapter 或 core/pkg 归属同时读取 [framework/boundary.md](../framework/boundary.md)。

## 两种 Capability

项目 capability 只允许采用以下两种形态：

1. Core facade capability bridge：core 已拥有协议、driver 和 service，项目只把配置文件转换为 facade `Use`。必须使用单个 `{name}.go`，包含 `Name`、必要 type alias、`Use` 和 `UseConfigFile`。它不是 sdkit `runtime.Adapter`，禁止用 runtime adapter metadata 包装普通 capability wiring。
2. 项目业务 capability：项目确实拥有跨入口业务 adapter、service-local client 或生命周期资源。允许定义 `Config`、`Service`、构造逻辑、`UseConfigFile` 和 `FromServiceContext`；只有这些部分各自存在实际逻辑时才拆成 `config.go`、`service.go`、`use.go`，禁止为了目录对称创建空 wrapper。

仅当能力被多个 service 使用时放 `app/infra/capability/{name}`；只被一个 service 使用时放 `app/{service}/infra/capability/{name}`。不能用“未来会复用”选择项目级目录。

## Core Facade Capability Bridge

- `Name` 必须直接复用 facade 的稳定名称，禁止另造同义 capability name。
- `UseConfigFile` 只加载该 capability 对应配置 key，并交给 core facade；禁止复制 driver 创建、连接池、重试、健康检查或关闭逻辑。
- 必需配置使用项目现有 required loader；可选 capability 才允许普通 loader，并必须定义 disabled 语义。

```go
const Name = facade.Name

type Config = facade.Config
type ConfigLoader = facade.ConfigLoader

func Use(loader ConfigLoader) runtime.CapabilityContract {
	return facade.Use(facade.WithConfigLoader(loader))
}

func UseConfigFile(configFile string) runtime.CapabilityContract {
	return Use(func(*runtime.App) (Config, error) {
		var cfg Config
		if err := config.LoadRequiredKey(configFile, "eventbus", &cfg); err != nil {
			return Config{}, err
		}
		return cfg, nil
	})
}
```

## 项目业务 Capability

- Capability metadata 必须明确稳定 `Name`、`Group` 和 `Scope`；依赖其他 capability 时必须通过 runtime dependency 声明，禁止在启动回调中从全局变量碰运气取值。
- 启动回调固定执行“加载当前 key → 归一化与校验 → 从 container 解析依赖 → 构造 service → `Container().Bind`”。任一步失败必须返回 error 并阻止 service 创建。
- 配置归一化和 enabled 校验必须在 capability 构造阶段完成；handler 禁止重复判断 URL、timeout、secret 或 client 是否初始化。
- 可选 capability 在 disabled 时必须返回明确的 unavailable error 或具有明确禁用状态的非 nil service；禁止让调用方因 nil pointer panic。
- 访问 capability 必须通过 `FromServiceContext` 和 `CapabilityLocalFirst(Name)`，禁止定义包级 `defaultService`、`Default()` 或让 handler 读取全局可变实例。
- Shutdown callback 只能释放当前 capability 实例创建的资源并清除闭包引用；从其他 capability 注入的 manager、client、database、Redis 或 eventbus 不得关闭。

```go
func FromServiceContext[T any](ctx *runtime.ServiceContext[T]) *Service {
	if ctx == nil {
		return nil
	}
	value, ok := ctx.CapabilityLocalFirst(Name)
	if !ok {
		return nil
	}
	service, _ := value.(*Service)
	return service
}
```

## Provider 接入

- 使用该能力的 service 必须在 `provider.go` 的 `RuntimeCapabilities` 中显式加入 `UseConfigFile(ctx.ConfigFile)` 或对应 `Use`。
- Service 没有该 capability 就不能启动时，必须同时加入 `RequireCapabilities(Name)`；可选 capability 禁止虚假声明为 required。
- Service-local capability name 需要避免多实例冲突时，必须使用 runtime 提供的 local-name 机制，禁止手写 service 名字符串拼接。
- `RuntimeCapabilities` 只装配 contract，业务调用必须发生在 Server、handler、worker 或 crontab 的明确执行路径中。

## 禁止内容

- Capability package 禁止包含 Gin handler、Router、HTTP response、页面 DTO、普通 CRUD 或单接口 projection。
- 禁止用 capability 包装只有一个调用方的小查询或小转换。
- 禁止在项目 capability 中修补 core driver/runtime 缺陷；命中时按 [framework/boundary.md](../framework/boundary.md) 停止并处理 core 归属。
- 真实 credential、token、DSN 和 secret 禁止写入 metadata、启动日志、错误消息或测试 fixture；测试只能使用明显虚构且无外部权限的值。

## 验收

- 必须测试配置缺失/非法、dependency 缺失、enabled/disabled、container bind、`FromServiceContext` 和 Shutdown 所有权。
- 必须验证同一进程的两个 service 实例不会通过包级全局变量互相覆盖 capability。
- 必须搜索 capability package 中的 `defaultService`、`Default()`、Gin、response 和普通数据库 CRUD；无法证明符合上述形态的命中不通过。
- Core facade capability bridge 必须与实际依赖的 facade API 对照，确认没有复制 driver、连接池、重试和 close 行为。
