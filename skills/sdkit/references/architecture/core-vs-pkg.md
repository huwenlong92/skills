---
name: sdkit-core-vs-pkg
description: 判断通用 Go 能力应进入 sdkit core、sdkit pkg 还是留在业务项目
---

# Core、Pkg 与业务项目归属

本文适用于决定新能力、现有 package 或项目公共代码的归属。新增、移动或重构 `core/`、`pkg/`，或者计划把业务项目代码沉淀到 sdkit 时必须读取本文。

## 判定顺序

必须按下列顺序判定，前一项命中后停止：

1. 包含业务 model、字段、schema、状态机、权限、route、页面或项目配置语义：留在业务项目。
2. 补充 sdkit 已有配置、注册、启动、停止、健康检查、capability、facade 或默认实现选择契约的缺口：进入 `core/`，当前调用项目数量不构成否决条件。
3. 不参与框架生命周期，契约明确且可以由调用方显式构造、独立测试和独立使用：进入 `pkg/`。
4. 新生命周期能力已经形成不含项目语义的统一契约：进入 `core/`；禁止把单项目 wiring 作为统一契约。
5. 边界尚未稳定或仍无法判定：禁止加入 sdkit，向用户说明缺少的稳定边界；业务项目中的放置必须服从其 handler/infra 规则，禁止默认塞入 `app/infra`。

## 对照表

| 特征 | `core/` | `pkg/` | 业务项目 |
|---|---|---|---|
| 参与 sdkit runtime 生命周期 | 必须 | 禁止 | 仅保留项目 wiring |
| 提供统一 facade 或 capability | 必须 | 禁止 | 只消费或做业务 adapter |
| 独立算法、协议、client、driver | 由 core 组装 | 必须 | 仅当包含业务语义 |
| 依赖项目 model、schema、权限或 route | 禁止 | 禁止 | 必须 |
| 可脱离 sdkit runtime 独立构造 | 可以包装 | 必须 | 可以 |
| 引用方向 | 可以依赖 `pkg/` | 禁止依赖 `core/` | 可以依赖公开 `core/` 或 `pkg/` |

## 典型选择

- queue 的 service 注册、统一 facade、capability 和 lifecycle 必须进入 `core/queue`。
- Asynq、NATS 或 memory queue 的具体 driver 必须进入 `pkg/queue/{driver}`，由 `core/queue` 选择和组装。
- storage manager、store registry、配置绑定和 facade 必须进入 `core/storage`。
- S3、OSS、COS、本地文件协议实现必须进入 `pkg/storage/{driver}`。
- 纯 hash、token、retry、媒体解析或远程文件协议实现，在不依赖 runtime 时必须进入对应 `pkg/`。
- 项目上传目录、业务可见性、业务 quota、model 绑定或权限判断必须留在业务项目。
- 纯 parser、normalizer、formatter、hash、随机数和编码能力在不依赖 runtime 时必须进入对应 `pkg/`；HTTP custom validator 等传输层适配仍留在业务项目。
- 通用原语必须进入对应 `pkg/`；配置、实例选择、版本管理、facade 与 runtime 生命周期只有形成跨项目统一契约时才进入对应 `core/`。
- 字段用途、业务 namespace、项目配置文案、model 字段拼接和实体格式契约必须留在业务项目；禁止随通用机制进入 sdkit。
- model 创建逻辑可以复用 `pkg/` 的通用生成能力，但实体前缀、hook 和表约束必须留在业务项目。只有不含实体注册表、可独立构造的通用函数才允许成为 `pkg/` 候选。

## 禁止的判断方式

- 禁止仅凭“多个地方会用”决定进入 `core/`；无生命周期职责的通用代码必须进入 `pkg/`。
- 禁止仅凭“只有一个项目在用”否定框架能力；如果它是 sdkit 已有生命周期契约的缺口，必须修复对应 `core/`。
- 禁止在 `core/` 和 `pkg/` 同时复制同一套实现。`core/` 必须通过接口、adapter 或 constructor 组装 `pkg/` 实现。
- 禁止让 `pkg/` import `core/` 来获取配置、logger、全局实例或 facade。
- 禁止把同时包含通用原语、runtime global 和项目 namespace 的混合 package 整体搬入 sdkit；必须先按职责拆分。

## 验收

- 必须能用“业务语义、生命周期、独立构造、依赖方向”四项说明归属。
- `pkg/` 不得 import `core/`，不得读取 sdkit 全局状态。
- `core/` 不得包含业务项目 model、schema、route、权限名或状态常量。
- 同一机制不得在 `core/` 与 `pkg/` 重复实现。
- 从业务项目提取复合能力时必须分别核对纯机制、runtime 生命周期和业务语义；任何项目字段或 model 语义进入 sdkit 即不通过。
