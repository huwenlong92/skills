---
name: infra-placement
description: sdkitgo app/infra、服务私有 infra、业务 adapter、capability bridge 和共享 core 的放置规则
---

# Infra 规范

本文定义 sdkitgo 项目中的项目级 infra 和服务私有 infra 边界。新增、移动或评审 `app/infra`、`app/{service}/infra`、业务 adapter、capability bridge 或项目公共组件时必须读取本文；实现 runtime capability 同时读取 [capability.md](capability.md)，判断 wrapper、driver、runtime adapter 或 sdkit 框架归属时同时读取 [framework/boundary.md](../framework/boundary.md)。

## 项目级 infra

`app/infra` 是项目级公共能力区，不是项目默认的业务层、工具箱或复杂代码收纳目录。

只有当前已经被项目内多个 runtime service 或运行入口使用，并且共享的是稳定业务不变量、项目 adapter、项目 component 或集中注册契约时，才放这里。多个 handler 调用、代码较长或文件较多不能单独证明项目级 infra 归属。

## 唯一归属判定

| 代码含义 | 必须放置 | 禁止放置 |
|---|---|---|
| 只属于一个 HTTP endpoint 的查询、校验、转换或 CRUD | 对应 handler | `app/infra`、`app/{service}/infra` |
| 多个 HTTP service 共用的 binding、form、response 等 HTTP 协议约定 | `app/http` | `app/infra` |
| 两个以上 request 共用的纯格式校验 tag | `app/http/validator/custom` | `app/infra` |
| 只属于一个 model 的创建时标识、前缀或默认值 | 对应 `app/models/{table}.go` 的 `BeforeCreate` | `app/infra`、全项目 model 元数据注册表 |
| 只服务一个 runtime service 的 adapter 或 capability wiring | `app/{service}/infra` | `app/infra` |
| 当前项目多个 service 共用的稳定业务契约、adapter 或 component | `app/infra` | 任一单独 service 的 `infra` |
| 跨项目通用且可脱离 runtime 的 parser、normalizer、算法、client 或 driver | 实际依赖的 sdkit `pkg/` | 项目 `app/infra`、sdkit `core/` |
| 跨项目通用的 runtime、database、queue、crontab、realtime、storage、密钥生命周期等机制 | 实际依赖的 sdkit `core/` | 项目 `app/infra` |

无法证明存在多个真实 service 调用方时，禁止使用“未来会复用”把代码放入 `app/infra`。

虚构例子：

- `app/infra/capability/*`：围绕 core facade 的项目 capability config bridge，或项目自己拥有生命周期的 runtime capability。
- `app/infra/component/*`：当前项目自己实现的可复用组件，例如 queue store、access log writer。
- `app/infra/realtime`：跨服务 realtime event 契约和 helper。
- `app/infra/catalogsync`：多个 service 共同使用的 catalog 同步 contract 和 adapter。
- `app/infra/searchindex`：多个 service 共同使用的搜索索引 writer。

下列名称不能证明代码属于 `app/infra`：`service`、`query`、`view`、`projection`、`policy`、`helper`、`utils`、`common`。必须继续检查真实调用入口与共享不变量。

## 服务私有 infra

`app/{service}/infra` 是服务私有 infra。

依赖某个 service 的 config、权限、runtime 形态、UI 契约或 route 语义的 adapter，放服务自己的 infra。

虚构例子：

- `app/console/infra/realtime`：console 自己拥有的 realtime event definition 和 adapter。
- `app/console/infra/policy`：只服务 console 的策略配置与审计编排。
- `app/api/infra/catalogsync`：只服务 API 的 catalog 同步 adapter。
- `app/crontab/infra/store`、`app/crontab/infra/lock`：crontab service adapter。
- `app/console/infra/capability/queueops`：console 私有 queue operation capability wiring。

## 新增公共能力前

新增 project-level capability、component、adapter 前，必须先判断它是否属于 core。

如果它满足 [framework/boundary.md](../framework/boundary.md) 的 sdkit 归属条件，必须判定为 sdkit `core/` 或 `pkg/` 候选。sdkit 仓库不在当前任务范围时，必须先说明所需框架变更并取得用户授权。

只有用户确认留在当前项目，或它确实只表达当前项目业务语义时，才放入 `app/infra`。

## 允许保留的四类形态

项目级 `app/infra` 只允许保留下列形态之一：

1. 两个以上 runtime service 或运行入口共同依赖的稳定业务不变量；例如同一资源对 HTTP、worker 和 crontab 必须保持一致的状态机与原子写入。
2. 项目 model 对 sdkit 或第三方稳定接口的实现；例如使用项目表实现 queue store 或 access log writer。
3. 项目级 runtime capability wiring；它只负责配置转换、依赖声明、container bind 与自身资源关闭。
4. 必须集中可见的跨 service 契约与注册；例如 realtime event definition 聚合。

未命中其中任何一项时必须移出 `app/infra`。普通业务流程必须直接写在 handler、worker handler 或 crontab run handler；复杂流程允许按 [service/handler.md](../service/handler.md) 的条件提取私有阶段，但复杂度本身不能作为迁入 infra 的依据。只有具备服务私有适配契约或生命周期职责时才允许放入 `app/{service}/infra`。

## 排除条件

- 只转发 core/pkg API、只改函数名或提供 `Default().Xxx()` 短路径的 wrapper 必须删除，调用方直接使用原 API。
- 从一个或几个 handler 抽出的 list、detail、options、view、projection 或 DTO 组装，若没有独立安全边界与跨 service 契约，必须回到对应 handler；能够由 SQL projection 形成结果时禁止以 `app/infra/*view` 隐藏查询。
- 纯 parser、normalizer、formatter、hash、随机数、编码和可独立测试算法，跨项目通用时必须进入或复用 sdkit `pkg/`；HTTP 布尔校验按 [validator.md](../http/validator.md) 放置。
- model 自有的创建时标识、前缀、默认值和行内校验必须按 [hooks.md](../models/hooks.md) 回到对应 model；禁止仅为共享少量生成代码建立项目级注册表。
- 同一个 package 混合纯机制、runtime 生命周期和项目业务常量时必须拆分后分别判定；禁止整包照搬到 sdkit，也禁止因其中含业务常量就把全部通用机制留在项目。
- 普通 infra package 中禁止维护本应由 runtime capability 管理的 package global、连接缓存或资源生命周期；必须改为 capability，或修复 sdkit core 的统一入口。

## 存量审计顺序

审计既有 `app/infra` package 时必须按以下顺序逐项判断：

1. 列出生产调用方，并区分 handler 数量与 runtime service/运行入口数量。
2. 标出 package 是否依赖项目 model、Gin/HTTP、core facade、第三方 SDK、全局状态或外部资源。
3. 先删除无语义 wrapper，再把 HTTP 协议适配、model 自有逻辑和通用纯机制移到各自唯一归属。
4. 对剩余业务代码说明它保护的稳定不变量、原子性、安全边界或接口契约；无法说明时必须回到 handler 或服务私有 infra。
5. 一次重构只迁移已确认的 package；禁止仅凭目录名批量移动全部存量代码。

## 放置规则

- 禁止创建项目级 `app/domain` 目录。被多个 HTTP service、Worker、Crontab 或 Seed 入口共同使用且满足上文稳定契约条件的业务能力放在 `app/infra/{name}`；只有拥有 runtime 生命周期时才称为 capability，并按 [capability.md](capability.md) 放置。单入口普通编排必须留在对应 handler，私有 adapter 才允许进入服务私有 infra。
- 不以“领域代码”为由另起一套 `domain` 分层；目录归属按复用范围和运行入口边界判断，模型仍统一放在 `app/models`，数据库迁移统一放在根目录 `migrations`。
- 禁止因为“未来复用”把代码移到 `app/infra`。
- 禁止把单个接口使用的小查询、小转换、小校验或普通 CRUD 包装成“公共方法”放进 `app/infra`。读接口能用 `JOIN`、子查询或数据库聚合直接形成 projection 时，查询必须留在对应 handler；代码较长、字段较多或少量重复都不是提升到 `app/infra` 的理由。
- 依赖 Gin binding、HTTP response 或其他传输语义的跨 HTTP 服务约定放在 `app/http`，并遵循 [http/foundation.md](../http/foundation.md)；禁止把 HTTP 公共层放进 `app/infra`。
- `app/infra` 不依赖具体 handler、router、页面概念或单个 service 的 config 格式。
- 项目 capability bridge 只能包含配置转换、业务契约适配和 wiring，并遵循 [capability.md](capability.md)；框架行为必须交给 core facade。
- 如果 bug 属于 core，停止在项目代码里打补丁，并在获得范围授权后修改 core。
- 如果服务私有 adapter 后来被多个服务使用，只移动稳定共享契约或组件到 `app/infra`；服务私有 wiring 仍留在本服务。


## Storage Capability

- 项目需要跨服务使用 storage 能力时，必须通过 `app/infra/capability/storage` 接入 core storage facade；仅单个服务使用时放在 `app/{service}/infra/capability/storage`。
- `app/infra/capability/storage` 只做配置加载和 capability wiring，不实现 storage 协议。
- Storage 的 `UseConfigFile`、container bind 和资源所有权按 [capability.md](capability.md) 实现。
- handler 或 service 不直接手写本地文件、S3、OSS、COS 的协议细节。
- 仅表达当前项目业务语义的上传限制、目录规则和权限校验允许放在 handler、service 或业务 infra；通用 storage 行为必须留在 core。
- 新增 storage driver、credential 生成、分片上传行为或 store manager 行为时，必须先改 core storage。

## 验收

- 每个新增 infra package 都必须由真实调用者证明归属范围；不能用“未来复用”作为依据。
- 每个保留的 `app/infra` package 必须能归入“跨入口业务不变量、项目接口实现、runtime capability wiring、集中注册契约”之一。
- `app/infra` 不依赖 handler、router、页面或单一 service config。
- capability bridge 只包含配置转换和 wiring，不复制 core 行为。
- 必须搜索新增或修改 package 的全部生产调用方；只有多个 handler、没有多个 runtime service 或稳定跨入口契约时，不得据此判定为项目级 infra。
- 必须核对没有把 HTTP custom tag、model 自有创建逻辑、通用纯机制或单接口 projection 新增到 `app/infra`。
