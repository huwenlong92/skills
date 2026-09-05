---
name: sdkitgo-workflow
description: 使用 sdkitgo 规范修改业务项目时的读取、实施、验证和停止流程
---

# 执行流程规范

本文定义使用 sdkitgo skill 创建、修改、评审或调试项目时的共同流程。开始任何 sdkitgo 任务时必须读取本文；具体代码规则继续按 `SKILL.md` 分流表读取。

## 修改前

- 必须先读取 `SKILL.md` 的路径分流，并加载本次任务命中的全部 reference。
- 新增 Go 文件或修改 `import` block 时必须读取 [code/imports.md](code/imports.md)；别名规则不得从历史文件反推。
- 新增完整 service 时读取 [service/creation.md](service/creation.md)、[service/config.md](service/config.md) 和 [service/provider.md](service/provider.md)。
- 新增或修改 HTTP endpoint 时至少读取 [service/handler.md](service/handler.md)、[service/request.md](service/request.md) 和 [http/response.md](http/response.md)；读接口继续读取 [database/query.md](database/query.md) 与 [database/projection.md](database/projection.md)，写接口继续读取 [service/write-handler.md](service/write-handler.md)。
- 修改 `app/http` 或 custom validator 时读取 [http/foundation.md](http/foundation.md) 和 [http/validator.md](http/validator.md)。
- 修改 model、schema、字段或分区时读取 [models/base.md](models/base.md) 和 [models/struct.md](models/struct.md)；涉及 GORM hook 时读取 [models/hooks.md](models/hooks.md)，涉及 DDL 时继续读取 [database/migration.md](database/migration.md)。
- 修改 worker、crontab 或 realtime event 时分别读取 [worker/handler.md](worker/handler.md)、[crontab/handler.md](crontab/handler.md)、[realtime/events.md](realtime/events.md)。
- 涉及项目公共能力、服务私有 adapter 或 capability 落点时读取 [infra/placement.md](infra/placement.md)；涉及通用框架能力或疑似 sdkit 缺陷时继续读取 [framework/boundary.md](framework/boundary.md)。
- 必须检查目标项目实际目录和已有实现。历史写法与 skill 冲突时，新代码和本次修改按 skill 执行，但不得顺带重构不在任务范围内的历史代码。

## 实现中

- 必须先复用项目和实际依赖的 core 已有能力；已有能力满足契约时禁止重复实现。
- 普通 HTTP 查询、projection、options、CRUD 和请求级 transaction 必须直接留在 handler；不能证明提取门槛时禁止新增小方法或 CRUD service。
- Handler 使用一级业务模块目录分类，Router 使用逐层 group 表达 URL；禁止把 Router 的每层 URL 机械复制成 handler 目录。
- `app/http` 只保存公共 HTTP 协议约定；项目级和服务私有 infra 必须按 [infra/placement.md](infra/placement.md) 的契约与调用范围判定，禁止仅因业务流程复杂就迁入 infra。
- Worker、crontab 和 realtime event 必须同时维护各自的领域文件与集中注册入口，禁止通过 `init()` 或扫描隐藏注册关系。
- Core 已有能力时，项目只做薄 adapter、配置加载或业务编排；禁止用项目 wrapper、兼容分支或局部补丁绕过 core bug。

## 验收

- 必须核对新代码唯一归属于 core、`app/http`、`app/infra`、`app/{service}/infra`、handler、worker、crontab 或 realtime event contract 中的一处。
- 必须检查新增或修改的 `app/infra` package 能否归入 [infra/placement.md](infra/placement.md) 允许的四类形态；HTTP 协议适配、model 自有创建逻辑、可独立复用的纯机制和单接口 projection 不得留在其中。
- 必须检查 handler 中的权限条件、查询、projection、普通 CRUD 和 transaction 是否仍然直接可见；只有一个调用方的 `listXxx`、`buildXxxQuery`、`createXxx`、`updateXxx` 等 wrapper 必须内联。
- 必须检查 Router 的完整 path、method、group 层级和 middleware 继承没有意外变化。
- 必须检查 request binding、response helper、model base、schema helper、软删除条件和 projection 符合命中 reference。
- 必须检查新增 service 的 app 目录、独立命令、service 配置、instances 声明和 `cmd/serve` Provider 注册齐全。
- 必须检查 crontab template、worker task 和 realtime event 均有显式集中注册，并且业务定义仍归属自己的领域 package。
- 必须读取 [testing.md](testing.md)，运行与改动风险匹配的最小有效测试；无法运行时必须说明具体原因。
