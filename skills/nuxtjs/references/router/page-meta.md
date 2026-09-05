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

- 页面自己的 layout、theme、auth、menu 和 active menu 必须写在 `definePageMeta`。
- 公开页面必须显式设置 `publicAccess: true`；登录后页面必须显式设置 `requiresAuth: true`。
- 页面有菜单入口时必须定义稳定短 `menu.key`、scope 和 order；子菜单必须通过 `menu.parent` 指向父 key。
- 详情、预览和编辑页必须通过 `activeMenu` 高亮所属菜单。
- 用户中心页面使用项目已有 user layout、theme 和 group meta；只有现有字段无法表达确认需求时才允许扩展 meta 类型。
- 页面禁止重复实现登录跳转、角色或权限守卫。

## routeRules

- `definePageMeta` 只负责页面布局、菜单与访问控制，`routeRules` 只负责 SSR/CSR、prerender 和缓存策略，禁止混用。
- 只有内容在构建时稳定、无需用户身份且更新策略允许重新发布时，公开页才允许 prerender。
- 读取用户身份、私有数据或浏览器专属 API 的页面必须使用 SSR 或 CSR 中符合数据安全边界的模式；用户中心默认使用 CSR，除非已实现安全的服务端 session 读取。
- routeRules 必须写在根 `nuxt.config.ts` 或 `layers/core/config/route-rules.ts` 的既有权威位置，禁止分散维护。

## Router Options

- `src/router.options.ts` 只允许维护 Nuxt Router option，例如 `scrollBehavior`。
- 修改滚动或历史行为必须检查普通导航、前进后退、hash 和动态参数页面。

## 验收

- 必须检查生成路由与目标 URL、动态参数和 page meta 一致。
- 公开、登录、角色和权限页面必须分别验证允许与拒绝路径，页面内没有重复守卫。
- 菜单页面必须检查 key、parent、order、activeMenu 和移动端导航结果。
- routeRules 修改必须验证实际 SSR/CSR/prerender 输出与私有数据边界，并运行 production build。
