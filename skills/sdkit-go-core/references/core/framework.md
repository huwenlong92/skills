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

## Capability 从声明到关闭

适用范围：新增 Capability、默认实例、公共 API 或业务接入入口时必须核对本节。

- Provider 必须声明所需 Capability；Bootstrap 注册公共工厂；Runtime 负责依赖排序、初始化、作用域、所有权、状态和 Shutdown。禁止在普通业务路径重新装配 Runtime。
- 普通 Handler/Service 必须直接使用已初始化的 Core 公开 API；已有 API 能表达需求时必须复用，禁止为了调用形式一致增加包装。
- Facade 必须保留初始化、显式实例、多实例隔离和兼容职责。默认实例必须拒绝其他 App 静默覆盖，显式指定 App 时禁止回退另一个 App 的默认实例。
- 默认绑定必须在资源关闭前撤销；包级调用必须定义未初始化/关闭后的错误或既有无资源 fallback 语义。禁止访问已关闭资源、误关借用资源或把未初始化错误吞成成功。
- 多 App、ServiceLocal、多租户和特殊资源必须保留显式实例路径。Auth/Session/事务/身份必须继续使用请求 context，禁止把请求状态转为进程全局状态。
- 新增公共 API 必须有真实消费需求、未初始化与关闭测试、默认冲突/显式隔离、所有权/回滚、关键 race 和消费方编译证据；不得修改已发布 tag，消费方必须等待新版本再升级正式依赖。

正向形态（框架接口示意）：

```go
// 声明与初始化属于装配入口；业务调用仅使用能力 API。
tasks, err := queue.ListTasks(ctx, query)
entries, err := crontab.ListEntries(ctx)
err = database.Transaction(ctx, func(tx *gorm.DB) error { return nil })
```

反例：普通业务每次通过 Runtime 解析 Operations，或 Router 仅为保存 Operations 构造转发对象。

完成检查：逐项核验 Provider/Bootstrap/Runtime 边界、默认/显式实例、请求 context、关闭顺序与所有权，并执行上述验收；兼容入口不以零搜索命中为目标。
