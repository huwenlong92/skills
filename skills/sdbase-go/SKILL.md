---
name: sdbase-go
description: 开发基于 huwenlong92/sdbase-go 完整模板的 Gin、GORM、PostgreSQL 多服务 Go 应用时使用；单 Web SQLite 的 sdbase-lite 不触发。
---

# SDKit Go 后端

仅当目标仓库已核实采用 SDBase Go 完整模板，或用户明确要求迁入该模板约定时，才使用本 skill。普通 Go 项目与 sdbase-lite 不触发。本文中的路径均以目标项目根目录为基准。

## 仓库定位

开始任务前必须读取 [权威仓库定位](references/repository.md)，先核验目标项目身份与模板来源；不能仅凭语言或项目目录名推断。本 Skill 是新名称主入口，旧名称仅供明确指定的兼容任务使用。

## 执行顺序

1. 读取 [workflow.md](references/workflow.md)。
2. 按实际修改路径和修改语义读取下表命中的全部 reference；新增 Go 文件或修改 `import` block 时同时读取 [code/imports.md](references/code/imports.md)，禁止只凭历史代码猜测规范。
3. 修改前检查目标项目的现有目录、依赖版本和可复用能力。
4. 按 reference 的正向形态实现最小完整修改。
5. 读取 [testing.md](references/testing.md)，执行命中 reference 的完成检查。

## 路径分流

| 目标路径或任务 | 必须读取 |
|---|---|
| 开发环境启动、`sdgo serve`、打包或 `build.yaml` 的包加载配置 | [workflow.md](references/workflow.md) 的“开发启动与打包配置” |
| 数据库连接、查询、dump、恢复、结构开发、seed、清理或远端同步 | [database/safety.md](references/database/safety.md)；结构变更同时读取 [database/migration.md](references/database/migration.md) |
| 完整模板 RANGE 预建、漏月份、DEFAULT 积压、维护脚本或新项目继承/裁剪 | [RANGE 模板维护](references/range-maintenance.md)；数据库安全审查按该文声明的 `sdkit-dbops` Supporting 入口 |
| 新增 Go 文件、修改 import、增加或删除 package alias | [code/imports.md](references/code/imports.md) |
| 新增、修改或评审 map 字面量，包括 GORM Updates 更新字段和 gin.H 响应对象 | [code/formatting.md](references/code/formatting.md) |
| 新增 `app/{service}` 服务及其命令、配置和注册 | [service/creation.md](references/service/creation.md)、[service/config.md](references/service/config.md)、[service/provider.md](references/service/provider.md)；HTTP 服务同时读取 [service/router.md](references/service/router.md) |
| `app/{service}/router.go` | [service/router.md](references/service/router.md)；涉及 middleware 作用域时同时读取 [service/middleware.md](references/service/middleware.md) |
| `app/{service}/handler/**/*.go` | [service/handler.md](references/service/handler.md)、[service/request.md](references/service/request.md)、[http/response.md](references/http/response.md) |
| HTTP 读接口、list、detail、options | [database/query.md](references/database/query.md)、[database/projection.md](references/database/projection.md) |
| HTTP create、update、delete 或写事务 | [service/write-handler.md](references/service/write-handler.md)、[database/query.md](references/database/query.md) |
| HTTP enable、disable、approve、reject、reset、assign、batch 等业务动作 | [service/action-handler.md](references/service/action-handler.md)、[database/query.md](references/database/query.md) |
| Excel 导入或导出 | [service/excel.md](references/service/excel.md)；批量写入同时读取 [database/batch-write.md](references/database/batch-write.md)，异步执行同时读取 [worker/handler.md](references/worker/handler.md) |
| `app/http/**` | [http/foundation.md](references/http/foundation.md)；修改分页或排序时再读 [http/form.md](references/http/form.md)，修改绑定或自定义 tag 时再读 [http/validator.md](references/http/validator.md)，修改响应时再读 [http/response.md](references/http/response.md) |
| `app/{service}/auth/**`、身份映射或 Session 认证契约 | [service/auth.md](references/service/auth.md) |
| `app/middleware/**`、`app/{service}/middleware/**` | [service/middleware.md](references/service/middleware.md)、[service/router.md](references/service/router.md) |
| `app/{service}/server.go`、Start 或 Shutdown | [service/server.md](references/service/server.md)、[service/provider.md](references/service/provider.md) |
| 新增或修改 `app/models/*.go` struct | [models/base.md](references/models/base.md)、[models/struct.md](references/models/struct.md)；涉及 DDL、schema 或分区时再读 [database/migration.md](references/database/migration.md) |
| GORM `BeforeCreate` 或其他 model lifecycle hook | [models/hooks.md](references/models/hooks.md)、[models/struct.md](references/models/struct.md) |
| `migrations/**/*.go`、`command/migrate/**/*.go` | [database/migration.md](references/database/migration.md)、[models/base.md](references/models/base.md)、[models/struct.md](references/models/struct.md) |
| `seeds/**/*.go`、`command/seed/**/*.go` | [database/seed.md](references/database/seed.md) |
| 批量导入、同步、upsert、staging 合并 | [database/batch-write.md](references/database/batch-write.md) |
| `app/infra/**`、`app/{service}/infra/**`、wrapper、业务 adapter、capability、driver 或 runtime adapter 落点 | [infra/placement.md](references/infra/placement.md)、[framework/boundary.md](references/framework/boundary.md)；新增或修改 runtime capability 时同时读取 [infra/capability.md](references/infra/capability.md) |
| `app/{service}/config/**/*.go` | [service/config.md](references/service/config.md) |
| `app/{service}/provider.go`、runtime capability wiring | [service/provider.md](references/service/provider.md) |
| `app/worker/taskdef/**/*.go`、`app/worker/event/**/*.go`、`app/worker/registry.go` | [worker/handler.md](references/worker/handler.md) |
| `app/crontab/**`、crontab template 或 job handler | [crontab/handler.md](references/crontab/handler.md) |
| realtime event、definition、publisher、聚合注册 | [realtime/events.md](references/realtime/events.md) |
| sdkit 框架能力、core/pkg 候选、疑似框架缺陷 | [framework/boundary.md](references/framework/boundary.md) |

## 共同门禁

- 正式库禁止 AI 直接或间接操作，只允许提供人工执行指导；数据库任务必须遵循 [database/safety.md](references/database/safety.md) 的环境核验、先备份再开发、本地验收与远端开发库同步门禁。
- reference 中用于表达代码形态的目录名、model、字段、schema、route 和业务文案必须是虚构示例；实现时必须替换为目标项目的真实语义，禁止复制示例标识符充当业务设计。标明源码依据的模板现有能力清单属于事实核验，不是业务设计示例。
- 常规 HTTP 查询和 CRUD 必须直接写在 handler；共享不变量或确有独立阶段的复杂流程，才允许按 [handler.md](references/service/handler.md) 提取 private helper。复杂度不构成新增 capability 的理由。
- 关联展示对象、数组或数据库树能够由 PostgreSQL 表达时，必须在 handler 查询中使用 `JOIN`、相关子查询、`LEFT JOIN LATERAL`、`jsonb_build_object` 或 `jsonb_agg` 直接形成最终 projection；禁止查询后用 Go `for range` 补关联或组装 JSON。
- `app/http` 只承载跨 HTTP 服务复用的协议层约定；`app/infra` 只承载项目级跨服务能力；单服务能力放在 `app/{service}/infra`。
- Router 必须显式展示完整 group 层级和 handler 注册；crontab、worker、realtime event 同样必须保留集中可见的注册入口，禁止用 `init()` 或文件扫描隐藏注册关系。
- 禁止猜测共享 sdkit core 的 checkout 路径；必须从 `go.mod`、`go.work`、仓库规则或用户输入中解析。
- 修改共享 core 前必须确认其在任务范围内。core 不在范围内时，说明所需变更并取得授权，确认前停止修改。
- 禁止使用项目内 wrapper、兼容分支或重复实现掩盖 core 缺陷。
