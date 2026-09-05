---
name: nuxtjs
description: 为 Nuxt 4 和 Vue 3 门户应用执行 SDKit Nuxt.js 约定。创建、修改、评审或调试 layer、页面、module、组件、API 与 SSR 数据、Pinia 状态、route meta、runtime config、主题、资源、业务选项和验证时使用。
---

# Nuxt.js

本 skill 适用于 Nuxt 门户仓库。禁止把 Vue 后台的 table、drawer、`src/views` 或后台菜单约定应用到 Nuxt 门户。路径均以目标项目根目录为基准。

## 必须执行的流程

1. 读取 [workflow.md](references/workflow.md)。
2. 读取分流表中与本次修改匹配的每一份 reference；新增或移动文件、目录时必须额外读取 [structure/directories.md](references/structure/directories.md)。
3. 修改前检查目标仓库的 Nuxt 版本、`srcDir` 配置、layers、包管理器、scripts 和一个同类现有页面。
4. 完成实现并执行 [workflow.md](references/workflow.md) 为本次修改指定的验证。

## Reference 分流

| 修改内容 | 读取 |
|---|---|
| 新增、移动文件或目录，判断目录职责 | [structure/directories.md](references/structure/directories.md) |
| `layers/core`、框架 capability、layout、全局 composable/plugin | [layers/core.md](references/layers/core.md) |
| Vue/TypeScript 基础、命名、composable、本地状态 | [code/base.md](references/code/base.md) |
| `src/pages` 和页面所有权 | [code/page.md](references/code/page.md) |
| `src/modules/<domain>` 落点和 module 组件结构 | [modules/placement.md](references/modules/placement.md) |
| 全局/domain/module 组件边界 | [components/placement.md](references/components/placement.md) |
| 判定 options 属于固定枚举、远端注册表还是展示模型 | [components/business-options.md](references/components/business-options.md) |
| 固定 enum/status/type 的 options、展示、输入或 `useStatusRender` | [components/enum-components.md](references/components/enum-components.md) |
| 后台可维护注册表 options 组件、版本化 API、store、pending、SSR hydrate、缓存和刷新 | [components/remote-options.md](references/components/remote-options.md) |
| 请求 wrapper、API 文件/函数、SSR 初始化数据 | [api/request.md](references/api/request.md) |
| 文件路由、`definePageMeta`、菜单、认证、`routeRules` | [router/page-meta.md](references/router/page-meta.md) |
| Pinia store、缓存、pending 去重、旧 store | [store/state.md](references/store/state.md) |
| Runtime config、环境变量、API base、构建配置 | [config/env.md](references/config/env.md) |
| 主题、样式、layout shell、Element Plus 覆盖 | [ui/style.md](references/ui/style.md) |
| `public`、assets、图片、SVG、图标 | [assets/media.md](references/assets/media.md) |

## 停止条件

- 禁止假定 `src/pages` 是薄转发层；必须遵循 [code/page.md](references/code/page.md) 的单一所有权模型。
- 禁止把凭据或仅服务端可见的 upstream 地址放入 public runtime config。
- 未满足对应 reference 的客观落点条件时，禁止新增 store、composable、全局组件、layout 或 core-layer capability。
