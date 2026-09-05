---
name: service-config
description: sdkitgo app service 的 config struct、loader、默认值和 capability 配置规则
---

# Service Config 规范

本文适用于 sdkitgo 项目的 service config、配置加载和默认值归一化。新增或修改 service config struct、config loader、兼容字段、默认值或 capability config adapter 时必须读取本文。

## 放置位置

- service config 放在 `app/{service}/config`。
- config loader 文件必须按 service 语义命名，例如 `service.go`；禁止使用无法表达所属 service 的 `config.go`、`common.go` 作为跨服务配置入口。
- capability config adapter 放在 `app/infra/capability/*` 或 `app/{service}/infra/capability/*`。

## 加载规则

- service config 通过 core config 能力从 config file 加载。
- 不在 handler、worker event、crontab template 中直接读取环境变量或配置文件。
- provider 负责把 `ctx.ConfigFile`、`ctx.Name`、`ctx.BaseConfig()` 传入 config loader。
- config loader 返回完整可用 config；调用方不再补散落默认值。

## 默认值和归一化

- 默认值、兼容字段、worker profile、queue config 等归一化放在 config loader 或明确 helper 中。
- 不把默认值判断散落在 handler、server、worker event 或 crontab handler 中。
- config struct 字段名必须表达配置语义，禁止使用 UI 文案作为字段命名依据。
- 多 service 共享的配置结构满足 [framework/boundary.md](../framework/boundary.md) 的 sdkit 归属条件时必须判定为框架候选；不满足 sdkit 条件、但表达当前项目稳定共享语义时必须放 `app/infra`。服务私有配置禁止放入 `app/infra`。

## 错误处理

- 必需配置缺失时返回明确错误。
- service 专属配置错误必须带 service name 或 config key，便于定位。
- 不用空配置静默启动依赖能力，除非该能力明确是 optional。

## 正向典型形态

Config loader 必须按“读取 service spec → 从 base 初始化 → 加载 service 文件配置 → 合并覆盖 → 应用默认值 → 校验”的顺序返回完整配置。下面的字段已经精简：

```go
type ServiceConfig struct {
	Name    string
	Type    string
	Enabled bool
	Addr    string
	Queue   queue.Config
}

type fileConfig struct {
	Addr string `mapstructure:"addr" yaml:"addr"`
}

func Load(configPath string, name string, base *bootstrap.Config) (cfg ServiceConfig, err error) {
	if name == "" {
		name = "api"
	}
	spec, err := loadServiceSpec(configPath, name)
	if err != nil {
		return cfg, runtime.WrapServiceConfigError(name, "api", name, err)
	}
	defer func() {
		if err != nil {
			err = runtime.WrapServiceConfigError(name, cfg.Type, name, err)
		}
	}()

	cfg = fromBase(base)
	cfg.Name = name
	cfg.Type = "api"
	raw, err := loadFileConfig(configPath, name)
	if err != nil {
		return cfg, err
	}
	applyServiceSpec(&cfg, spec)
	applyFileConfig(&cfg, raw)
	applyDefaults(&cfg)
	if err := validateServiceConfig(cfg, name); err != nil {
		return cfg, err
	}
	return cfg, nil
}
```

禁止让 provider、handler、worker event 或 crontab handler 在 `Load` 返回后继续补 `Addr`、queue profile 或其他默认值。

## 验收

- 必须核对 service config 位于 `app/{service}/config`，capability config adapter 位于与调用范围匹配的 infra 目录，且 handler、worker event、crontab template 未直接读取环境变量或配置文件。
- 必须测试必需配置缺失、默认值归一化和至少一个有效配置；兼容字段存在时必须测试新旧字段的唯一优先级。
- Provider 和其他调用方不得在 loader 返回后再次补默认值。
