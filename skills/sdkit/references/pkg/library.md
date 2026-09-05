---
name: sdkit-pkg-library
description: sdkit pkg 中独立算法、协议、client、adapter 和 driver 的组织与依赖规则
---

# sdkit Pkg 规范

本文适用于已经判定归属 `pkg/` 的通用 Go 能力。新增或修改算法、协议、client、adapter、provider 或 driver package 时必须读取本文；归属尚未确定时先读取 [core-vs-pkg.md](../architecture/core-vs-pkg.md)。

## Pkg 职责

- `pkg/` 必须承载可脱离 sdkit runtime 独立构造、独立测试和独立消费的机制实现。
- `pkg/` 禁止 import `core/`，禁止读取 sdkit 全局配置、global facade 或 service registry。
- package 必须通过 constructor、参数或 interface 接收依赖，禁止从业务项目或 core 隐式获取依赖。
- 包含业务 model、schema、状态、权限或 route 语义的实现禁止进入 `pkg/`。

## Driver 与 Provider

- 同一能力的具体实现必须放在 `pkg/{capability}/{driver}`，例如 `pkg/queue/asynq`、`pkg/storage/s3`。
- driver 必须实现由能力层定义的最小接口，禁止反向依赖 core 的 manager 或 facade。
- provider 特有 config 必须留在 provider package；通用 config 只保留所有实现共同需要的字段。
- provider SDK 的类型禁止泄漏到 core 的统一公共接口；adapter 必须在 pkg 内完成转换。

## 独立性

- package test 必须可以在不启动 sdkit runtime 的情况下运行。
- 可以使用标准库和明确的第三方依赖；禁止为了复用 logger、config 或 errors 而 import `core/`。
- 需要 runtime logger、metrics 或 tracing 时，必须通过 interface、callback 或 context 注入。
- package 初始化禁止连接数据库、Redis、网络服务或启动 goroutine；这些动作必须由显式 constructor 或 start 方法触发。

## 验收

- `go test` 必须能在不启动 sdkit runtime 的条件下测试该 package。
- `pkg/` 的 import graph 不得包含 `core/` 或业务项目 package。
- driver SDK 类型不得进入 core 统一接口。
- 网络连接、goroutine 和外部资源必须由显式调用创建和关闭。
