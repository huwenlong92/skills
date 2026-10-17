---
name: nuxtjs-directories
description: Nuxt.js 项目的目录职责、允许内容和禁止的新分层
---

# 目录职责

本文适用于 Nuxt.js 项目中的新增文件、移动文件和新建目录。无法确定代码落点时必须先读取本文，再读取表中链接的详细规范。

## 目录总图

| 路径 | 唯一职责 | 禁止放置 |
|---|---|---|
| `layers/core` | 跨项目稳定的 Nuxt framework、layout、theme、request、auth、plugin、middleware 和基础组件能力 | 业务页面、业务 API、业务字段或产品文案 |
| `src/pages` | Nuxt 文件路由、`definePageMeta`、页面级数据与业务区块组合 | 供其他页面直接复用的组件、通用工具 |
| `src/modules` | 页面私有业务区块、同业务域共享区块和通过薄路由壳门禁的跨路由完整流程 | 无业务语义的基础组件、Nuxt framework module |
| `src/components` | 跨页面或跨业务域复用、API 已稳定的组件 | 单页面区块、完整路由页面、绑定单一路由的动作 |
| `src/api` | 客户端可用的业务请求函数与请求/响应类型 | 页面状态、UI 组件、服务端凭据 |
| `src/store/modules` | 用户态、跨页面业务状态、缓存、pending 去重与清理动作 | 单页面表单状态、DOM 状态 |
| `src/composables` | 至少两个页面复用的组合行为 | 某个页面的完整业务流程 |
| `src/utils` | 无状态、无页面语义的纯函数 | 请求、store、组件状态和页面编排 |
| `src/config` | 当前项目固定配置与公开协议开关 | 部署密钥、动态注册表、页面临时常量 |
| `src/layouts` | 当前产品对 core layout 的项目级覆盖或新增业务外壳 | 某一个页面的内容区块 |
| `src/middleware` | 当前项目的 Nuxt 路由中间件 | 页面按钮权限和 UI 组件 |
| `src/plugins` | 当前项目需要 Nuxt 生命周期安装的插件 | 普通 helper、单页面逻辑 |
| `src/assets`、`src/icon` | 参与构建的业务图片、样式资源和自定义图标 | 框架 token、公开稳定 URL 资源 |
| `public` | 按稳定 URL 原样公开的静态文件 | 需要构建优化的组件资源、凭据或私密文件 |
| `server` | Nitro server route、server middleware、server plugin 和仅服务端 adapter | 客户端组件、可进入浏览器 bundle 的业务 UI |

组件调用范围以 [components/placement.md](../components/placement.md) 为唯一权威；页面入口与页面所有权以 [code/page.md](../code/page.md) 为唯一权威；`src/modules` 内部结构以 [modules/placement.md](../modules/placement.md) 为唯一权威。

## 新建目录门禁

- 新文件必须先归入上表已有职责，禁止为单次需求新增 `features`、`shared`、`common`、`helpers`、`services` 或第二套 `modules`。
- Nuxt 官方 module 只有在需要接入 build/runtime hook 或提供可配置框架能力时才允许创建，禁止与业务 `src/modules` 混用。
- `server` 目录只有代码必须在 Nitro 服务端运行时才允许使用；只做客户端 API 调用的代码必须进入 `src/api`。
- 历史目录与本文不一致时，本次新增文件按本文放置；任务范围外的历史文件禁止批量迁移。
- 表中没有对应职责时，必须先判断它属于页面、业务复用、项目扩展或 core framework；仍无法归属时停止新建目录并说明缺失边界。

## 验收

- 每个新增文件必须能对应目录总图中的一行，且没有命中该行的禁止项。
- 必须检查没有新增与现有职责同义的顶层源码目录。
- 新增或移动页面、组件、module 时必须继续通过对应权威 reference 的调用范围和命名检查。
- `server` 与 private runtime config 中的内容必须检查没有进入客户端 bundle。
