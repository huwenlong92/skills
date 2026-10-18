---
name: sdkitgo-framework-boundary
description: sdkitgo 业务项目复用 sdkit、识别框架缺口以及区分 core 与 pkg 候选的边界
---

# sdkit 框架边界

本文适用于 sdkitgo 业务项目中出现公共基础能力、疑似 sdkit 缺陷或准备向 sdkit 沉淀代码的场景。新增项目 wrapper、capability、driver、runtime adapter 或修改 sdkit 依赖前必须读取本文；本文只负责业务项目侧的归属判断，不定义 sdkit 框架仓库内部实现规范。

## 先检查实际依赖

- 实现基础能力前必须从目标项目的 `go.mod`、`go.work`、`replace` 和仓库说明确认实际依赖的 sdkit 版本与源码。
- 禁止假定 sdkit 位于某个本机固定目录。
- 必须搜索实际版本中已有的公开 API、facade、capability、provider 和 driver；已有能力满足契约时，业务项目必须直接复用或只做薄 adapter。
- 禁止用项目 wrapper、兼容分支、重复实现或局部补丁绕过已经确认的 sdkit 缺陷。

## 先区分五种代码

新增公共 package 前必须先按行为分类，禁止只凭目录名或类型名判断：

| 名称 | 可观察行为 | 允许位置 | 禁止位置 |
|---|---|---|---|
| Wrapper | 只把参数原样转给已有 core/pkg API，返回值和错误也不转换 | 默认不新增，调用方直接使用原 API；只有 capability 配置 bridge 按 [capability.md](../infra/capability.md) 处理 | `app/infra`、`app/{service}/infra` 中的单调用方转发包 |
| 业务 adapter | 把 core/pkg/第三方能力转换为项目接口、项目数据或稳定业务策略，但不拥有 runtime 注册与关闭 | 单 service 放 `app/{service}/infra/{name}`；多个真实 service 共用放 `app/infra/{name}` | `core/`、`pkg/`、`app/http` |
| Runtime capability | 返回或实现 `runtime.CapabilityContract`，负责配置加载、依赖声明、实例创建、container bind 和所创建资源的 Shutdown | 按调用范围放 `app/{service}/infra/capability/{name}` 或 `app/infra/capability/{name}`；sdkit 通用生命周期能力属于 core 候选 | handler、model、普通业务 adapter、`pkg/` driver |
| Driver | 在稳定、与 provider 无关的接口后实现一种协议或供应商，并可脱离 sdkit runtime 显式构造 | sdkit 通用实现属于 `pkg/{capability}/{driver}` 候选；仍含项目 schema、权限或状态机时留在项目 infra，且不得伪装成通用 driver | handler、core facade、runtime orchestration |
| Runtime adapter | 实现 sdkit `runtime.Adapter`、`CapabilityAdapter`、`ProviderAdapter` 或 `CommandAdapter`，只把已有 contract 加入 runtime adapter registry | 项目 composition root 可以构造 sdkit 已提供的 adapter；新增 adapter contract 或通用注册机制属于 `core/runtime` 候选 | 普通 `app/infra` 业务 adapter、handler、driver package |

`adapter` 一词未带 `runtime` 时一律解释为业务 adapter；只有代码真实实现 sdkit runtime adapter interface 时才能称为 runtime adapter。Runtime capability 拥有初始化与关闭生命周期，runtime adapter 只包装已有 contract 的注册元数据，两者禁止互相替代。

### Wrapper 判定

以下特征全部成立时就是无效 wrapper，必须删除并让调用方直接使用已有 API：

- 只有一个真实调用方；
- 参数、返回值和错误语义没有转换；
- 不增加项目权限、状态机、幂等、审计或原子性边界；
- 不负责 capability config loader、container bind 或资源生命周期。

仅名称变化、缩短调用表达式、隐藏 import path 或“以后方便替换”都不是保留 wrapper 的理由。若代码增加了稳定项目语义，必须按业务 adapter 判定；若代码拥有 runtime 生命周期，必须按 capability 判定，禁止继续叫 wrapper。

## 项目与 sdkit 的判定顺序

混合 package 必须先按下文“复合能力拆分”分开职责，再对每项职责按以下顺序判定；禁止先按调用方数量排除框架能力：

1. 代码只是转发已有 API 且没有配置、语义或生命周期转换：禁止新增 wrapper，调用方直接使用原 API。
2. 不含项目语义，补充 sdkit 已有配置、注册、生命周期、facade 或 runtime adapter contract 的缺口：它是 sdkit `core/` 候选，即使当前只有一个调用方。
3. 不含项目语义，是契约明确、可独立构造、无需 sdkit runtime 的算法、协议、client 或 driver：它是 sdkit `pkg/` 候选。
4. 包含项目 model、schema、状态机、权限、route、业务配置或文案：留在业务项目，再按下列项目内规则定位。
5. 不含项目语义但新契约尚不明确：禁止先建立“临时公共层”或上提框架；必须说明缺少的稳定边界并向用户确认。

项目内先看职责，再看调用范围：普通流程留在所属 handler；业务 adapter 按真实调用范围放服务私有 infra 或 `app/infra`；拥有项目 runtime 生命周期时才按 [capability.md](../infra/capability.md) 放项目 capability。多个调用方或复杂流程本身均不构成新增 infra package 的理由。

“core 候选”或“pkg 候选”只表示归属结论。sdkit 源码不在当前任务范围时，必须停止修改并先取得用户授权；进入 sdkit 仓库后必须遵循该仓库自己的规则和测试要求。

## 常见框架能力

下列能力涉及统一配置、注册、生命周期或 facade 时属于 sdkit `core/` 候选：

- service runtime 与 capability；
- database、Redis、cache 和 storage facade；
- queue、crontab、realtime 和 eventbus runtime；
- logger、tracing、request ID 和 tracking；
- errors、Gin middleware、auth、security、Casbin 和 rate limit；
- email、SMS、payment 等统一 manager 与 facade。

对应的独立算法、协议 client 和 provider driver 在无需 runtime 时属于 sdkit `pkg/` 候选，禁止因为它服务于某个 core capability 就直接放入 core。

## Storage 虚构判定例

- storage 配置绑定、store registry、manager、facade 和 runtime capability 属于 sdkit `core/storage` 候选。
- local、S3 或其他对象存储协议 driver 在可独立构造时属于 sdkit `pkg/storage/{driver}` 候选。
- 当前项目的上传路径、业务可见性、业务 quota 和权限判断必须留在 handler、`app/infra` 或服务私有 infra。
- 业务项目禁止重新实现 storage manager、driver registry、credential provider 或 provider selection。

## Runtime 虚构判定例

- 项目只需把 `configs` 中的 `eventbus` key 交给现有 facade 时，允许建立 capability config bridge；该 bridge 禁止复制 eventbus 初始化和关闭逻辑。
- 当前 service 需要把 realtime publisher 转成带项目 event name 与审计字段的接口时，它是服务业务 adapter，不是 runtime adapter。
- 新增一个可脱离 runtime 构造的消息协议实现时，它是 `pkg/eventbus/{driver}` 候选，不是项目 capability。
- 需要扩展 `runtime.CapabilityAdapter` 的注册、metadata 或发现机制时，它是 `core/runtime` 候选；业务项目不得用自定义 wrapper 修补 runtime registry。

## 复合能力拆分

同一个项目 package 同时包含通用机制、runtime 生命周期和业务常量时必须拆分，禁止因原 package 被多个调用方使用就整体保留或整体上提。

| 代码职责 | 唯一归属 | 禁止归属 |
|---|---|---|
| HTTP 字段是否合法的 custom tag | `app/http/validator/custom`，只做纯布尔适配 | `app/infra`、sdkit `pkg/` |
| 可脱离传输层的 parser、normalizer、formatter、算法或编码 | 跨项目通用时为 sdkit `pkg/` 候选；仍含项目策略时留在使用它的 handler 或服务私有 infra | sdkit `core/`、项目级工具箱式 `app/infra` |
| 通用机制所需的配置、实例选择、facade 与 runtime 生命周期 | 契约已经跨项目稳定时为对应 sdkit `core/` 候选；仅本项目使用时为项目 capability | 普通无生命周期 `app/infra` package、sdkit `pkg/` global |
| 字段用途、业务 namespace、model 字段拼接和项目枚举 | 对应项目 model 或拥有该业务流程的 handler/项目 infra | sdkit `core/`、sdkit `pkg/` |
| 单个 model 的创建时标识、默认值与行内不变量 | 对应 `app/models/{table}.go` 的 `BeforeCreate` | `app/infra`、sdkit |

Custom tag 可以调用 `pkg/` parser 并把 error 转成 bool，但规范化后的业务值必须由 handler 显式取得。validator 不能替代 parser，parser 也不能因被 validator 调用就留在 `app/http`。

通用原语、实例配置与生命周期、项目业务常量必须分别判定：core 可以通过 facade 组装 pkg 原语，但禁止吸收项目字段名、用途常量或项目配置文案。项目也禁止复制实际 sdkit 依赖已经提供的纯机制。

model 创建时标识可以复用通用随机或编码能力，但实体前缀、格式契约和 hook 必须留在对应 model。仅为 migration 复用、减少 hook 代码或提供类型识别 helper，不允许建立项目级中央注册表。

## 验收

- 每项新增代码必须具有唯一归属：handler、`app/{service}/infra`、`app/infra`、sdkit `core/` 候选或 sdkit `pkg/` 候选。
- 每个 wrapper、业务 adapter、runtime capability、driver 和 runtime adapter 必须按本文可观察行为命名；禁止只凭 package 名自证归属。
- 项目内不得复制 sdkit 已提供的 facade、driver、runtime、middleware 或协议实现。
- 判定为 sdkit 候选但框架源码不在任务范围时，必须停止写入并说明需要的框架变更。
- 判定必须同时核对业务语义、调用范围、生命周期和独立构造能力，禁止只用“可复用”作为理由。
- 混合 package 必须按机制、生命周期和业务语义拆分后分别判定；禁止整包上提 sdkit 或整包留在 `app/infra`。
- 传输校验与值转换、纯机制与 runtime 生命周期、框架契约与项目业务常量、通用生成能力与 model 创建契约必须逐项分开核对。
