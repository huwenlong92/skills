---
name: nuxtjs-router-page-meta
description: Nuxt.js 文件路由、definePageMeta、菜单、鉴权、routeRules 和 router options 规则
---

# 路由与页面 Meta 规范

本文适用于新增或修改 `src/pages` 文件路由、`definePageMeta`、菜单、鉴权、routeRules 和 `src/router.options.ts`。

## 文件路由

- 必须使用 Nuxt `src/pages` 文件路由，页面文件和目录使用短 kebab-case。
- 动态参数必须使用 `[id].vue`、`[...pathMatch].vue` 等 Nuxt 语法。
- 文件路径必须与 URL 语义一致；页面入口的详细命名以 [page.md](../code/page.md) 为准。
- 禁止在 `src/router.options.ts` 手写业务 routes 或覆盖 Nuxt 页面路由生成。

## definePageMeta

- 页面自身 layout、auth 及实际启用的 menu/active menu 必须写在 `definePageMeta`；theme 仅作为实际消费者仍使用的历史标记，禁止覆盖用户全局配色。
- 公开页面必须显式设置 `publicAccess: true`；登录后页面必须显式设置 `requiresAuth: true`。
- 只有实际启用 meta 菜单生成时，菜单入口才必须定义稳定短 key、scope、order 及 parent；固定导航不强制逐页 menu，禁止因保留类型就宣称菜单生成已经实现。
- 详情、预览和编辑页必须通过 `activeMenu` 高亮所属菜单。
- 用户中心页面使用项目已有 user layout 和实际消费的 group meta；只有现有字段无法表达确认需求时才允许扩展 meta 类型。
- 页面禁止重复实现登录跳转、角色或权限守卫。

## routeRules

- `definePageMeta` 只负责页面布局、菜单与访问控制，`routeRules` 只负责 SSR/CSR、prerender 和缓存策略，禁止混用。
- 只有内容在构建时稳定、无需用户身份且更新策略允许重新发布时，公开页才允许 prerender。
- 页面必须按真实首屏与数据安全选择 SSR/CSR，不因用户中心、登录等名称恢复旧 CSR 白名单。需要浏览器专属 API 时必须隔离客户端代码；私有响应禁止共享缓存，渲染策略不能替代后端鉴权。
- routeRules 必须写在根 `nuxt.config.ts` 或 `layers/core/config/route-rules.ts` 的既有权威位置，禁止分散维护。

## 默认规则合并

- 必须检查 `defineAppRouteRules` 实现：当前 core 仅默认 redirect CSR，只有配置代理目标时才增加 `/api/**`；业务覆盖同路径对象是替换，不是深合并。消费版本不同必须以其代码为准。
- routeRules 必须按 URL 而非源文件路径匹配，禁止放入 runtimeConfig.public。动态 prerender 必须有可枚举路由，isr 必须核验平台支持，禁止承诺跨平台一致能力。

## Router Options

- `src/router.options.ts` 只允许维护 Nuxt Router option，例如 `scrollBehavior`。
- 修改滚动或历史行为必须检查普通导航、前进后退、hash 和动态参数页面。

## 验收

- 必须检查生成路由与目标 URL、动态参数和 page meta 一致。
- 公开、登录、角色和权限页面必须分别验证允许与拒绝路径，页面内没有重复守卫。
- 菜单页面必须检查 key、parent、order、activeMenu 和移动端导航结果。
- routeRules 修改必须验证实际 SSR/CSR/prerender 输出与私有数据边界，并运行 production build。
