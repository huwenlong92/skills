---
name: nuxtjs-core-layer
description: Nuxt.js layers/core 的 framework 能力门禁、目录边界和禁止的业务依赖
---

# Core Layer 规范

本文适用于新增或修改 `layers/core`、core layout、theme、request、auth、route、plugin、middleware、store、component、composable 和 utils。

## Core 能力门禁

能力必须同时满足以下条件才允许进入 `layers/core`：

1. 至少两个业务域需要，或已确认会被两个项目复用。
2. 属于 Nuxt 配置、layout、theme、auth、request、route、upload、permission 等 framework 机制。
3. 对业务方暴露稳定的 props、config、composable、adapter 或 type API。
4. 不依赖某个业务接口、业务字段、页面路由、角色名称或产品文案。

任一条件不满足时必须放在 `src/pages`、`src/modules`、`src/components`、`src/composables` 或 `src/utils` 的对应职责目录。

## 目录职责

| 路径 | 职责 |
|---|---|
| `layers/core/nuxt.config.ts` | core modules、alias、css、runtime config 和构建基础配置 |
| `layers/core/layouts` | 跨项目 layout shell |
| `layers/core/assets/styles` | framework token、theme、全局样式和 Element Plus 覆盖 |
| `layers/core/components` | 通过能力门禁的稳定组件 |
| `layers/core/composables` | request、auth、theme、title 等 framework 组合能力 |
| `layers/core/config` | routeRules 等 framework 配置 |
| `layers/core/middleware`、`plugins` | 全局生命周期和路由接入 |
| `layers/core/stores` | theme、layout、route 等 framework 状态 |
| `layers/core/types`、`utils` | 无业务依赖的类型和纯工具 |

## 实现边界

- 根 `nuxt.config.ts` 只允许接入 core layer、项目 modules 和项目覆盖；业务路由和业务接口禁止写入 core config。
- Element Plus 全局覆盖必须集中在 core 样式入口；单页面视觉差异禁止修改 core theme。
- core component 禁止绑定业务 API；数据必须通过 props、events 或稳定 adapter 输入。
- core composable 禁止 import `src/api` 或业务 store。
- `useAppRequest` 必须统一处理项目后端 envelope，并兼容项目确认的 cookie session 与 Bearer token 方式。
- `AppUpload` 只有封装稳定上传协议且不绑定业务资源时才允许放 core；业务卡片、列表、详情和文案禁止进入 core。

## 验收

- 每个 core 修改必须逐项通过四个能力门禁，并列出真实业务域或项目调用方。
- 必须搜索新增 core 文件的 import 和文案，确认没有业务 API、字段、route、role 或产品内容。
- 修改 core config、layout、theme、plugin 或 middleware 后必须执行 production build，并验证至少一个消费页面。
- 必须检查业务页面没有因单页需求反向修改 core 全局行为。
