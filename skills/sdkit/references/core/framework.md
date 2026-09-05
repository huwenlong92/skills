---
name: sdkit-core-framework
description: sdkit core 中配置、注册、生命周期、capability、facade 和默认实现的组织规则
---

# sdkit Core 规范

本文适用于已经判定归属 `core/` 的 sdkit 框架能力。新增或修改 core package、facade、capability、runtime binding、配置或生命周期时必须读取本文；归属尚未确定时先读取 [core-vs-pkg.md](../architecture/core-vs-pkg.md)。

## Core 职责

- `core/` 必须承载 sdkit 对能力的统一契约、配置绑定、注册、生命周期、capability、facade 或默认实现选择。
- `core/` 可以依赖 `pkg/` 的独立实现；禁止把 driver 协议细节复制进 core。
- core package 必须暴露业务项目可直接消费的稳定入口，禁止要求每个项目重复组装相同 runtime 细节。
- 需要全局默认实例时，必须同时保留可显式注入和测试的构造路径；禁止只有不可替换的 package global。

## Package 组织

- 一个 core package 必须对应一个框架能力，例如 `database`、`queue`、`crontab`、`realtime`、`storage`。
- capability contract、config、binding、manager、facade 和 lifecycle 必须放在该能力的 core package 内或其明确子包。
- provider 或 driver 的具体协议实现必须放入对应 `pkg/`；禁止放在 `core/{capability}/driver` 形成第二套实现层。
- core package 禁止 import 业务项目代码。

## 公共 API

- 公共 API 必须以能力语义命名，禁止暴露单个业务项目的字段、状态或配置结构。
- 修改已有公共函数、interface 或配置字段前必须搜索所有真实消费方。
- 可以向后兼容时必须保留旧调用路径并标记迁移入口；只有用户明确授权 breaking change 时才允许直接删除。
- facade 必须只表达统一能力，provider 特有选项必须停留在 provider config 或 adapter。

## 验收

- core package 必须至少承担一项配置、注册、生命周期、capability、facade 或默认选择职责。
- driver 或协议细节必须由 `pkg/` 提供，core 只负责契约与组装。
- 必须验证显式构造路径和 runtime 集成路径。
- 公共 API 变更必须核对真实消费方，并说明兼容结果。
