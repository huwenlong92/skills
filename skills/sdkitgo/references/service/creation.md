---
name: service-creation
description: sdkitgo 新增 app service 时需要创建和修改的目录、命令、配置与注册位置
---

# 新增 Service 规范

本文定义在固定 sdkitgo 项目中新增 `app/{service}` 时需要创建和修改的位置。新增 HTTP、worker、crontab、realtime 或其他 runtime service 时必须读取本文；具体配置、Provider 和 Server 写法同时读取 [config.md](config.md)、[provider.md](provider.md) 与 [server.md](server.md)。

## 命名

- service 目录、provider type、配置 key、实例 type 和命令名必须使用同一个短稳定名称，例如 `admin`、`api`、`web`、`worker`、`crontab`、`realtime`。
- 禁止仅为强调其是服务而增加 `_service`、`-service` 后缀；只有外部既有契约本身包含该后缀时才允许保留。

## HTTP Service 必需位置

新增 HTTP service 必须同时处理以下位置：

```text
app/{service}/
  config/service.go
  handler/
  provider.go
  router.go
  server.go
cmd/{service}/main.go
configs/services/{service}.yaml
configs/services/instances.yaml
cmd/serve/main.go
```

- `config/service.go` 定义 service config、加载、默认值和校验。
- `provider.go` 声明 service name、kind、group、required capability、runtime capability 和 factory。
- `server.go` 只装配并运行 `http.Server` 及服务级生命周期资源，并遵循 [server.md](server.md) 的构造、所有权和 Shutdown 规则。
- `router.go` 初始化 validator、中间件与显式路由树。
- `handler/` 按 [handler.md](handler.md) 的模块目录和资源文件组织。
- `cmd/{service}/main.go` 提供单服务启动命令，并只注册当前 service 的 Provider。
- `configs/services/{service}.yaml` 保存服务运行参数；`configs/services/instances.yaml` 声明 `serve all` 是否启动该实例。
- `cmd/serve/main.go` 必须把新 Provider 加入多服务进程的显式列表。

`auth/`、`middleware/`、`infra/` 仅当该 service 存在真实专属能力时才允许创建；分别遵循 [auth.md](auth.md)、[middleware.md](middleware.md) 和 [infra/placement.md](../infra/placement.md)，禁止复制其他 service 的空目录或无调用方 wrapper。

## 非 HTTP Service

- 非 HTTP service 仍必须具有 `config/`、`provider.go`、运行入口文件、`cmd/{service}/main.go`、service 配置和实例声明。
- Queue service 的 task/event/registry 读取 [worker/handler.md](../worker/handler.md)。
- Crontab service 的 template/registry/infra 读取 [crontab/handler.md](../crontab/handler.md)。
- Realtime gateway 的 event 注册读取 [realtime/events.md](../realtime/events.md)。
- 非 HTTP service 禁止为了结构对称创建空 `router.go` 或 `handler/`。

## 禁止修改的位置

- 普通新增 service 不修改 `command/serve` 的框架实现；只在 `cmd/serve/main.go` 增加 Provider。
- core runtime 已支持目标 service kind 时，禁止在项目内复制 service registry 或 lifecycle。
- 禁止让 service 通过 import side effect 自动注册；单服务入口和多服务入口都必须显式列出 Provider。

## 验收

- 必须核对目录名、Provider name/type、配置顶层 key、instances type 和命令名完全一致。
- 必须分别验证 `cmd/{service}` 单服务启动和 `cmd/serve` 多服务发现；disabled 实例不得启动。
- 必需 capability 缺失、配置缺失和监听失败必须阻止 service 启动；Shutdown 必须释放当前 service 创建的资源。
