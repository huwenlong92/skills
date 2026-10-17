---
name: nuxtjs-modules-placement
description: Nuxt.js src/modules 中页面私有区块、业务域共享区块和共享完整流程的结构规则
---

# Modules 规范

本文适用于新增、修改或移动 `src/modules/<domain>` 中的业务组件。`src/modules` 是业务区块层，不是 Nuxt framework modules，也不是所有路由页面的固定主体层。

## 允许放置的内容

```text
src/modules/<domain>/<page>/<section>/index.vue
src/modules/<domain>/<shared-section>/index.vue
src/modules/<domain>/<flow>/index.vue
```

- 只服务一个页面的独立区块放入 `<domain>/<page>/<section>/index.vue`。
- 同一业务域至少两个真实页面复用的稳定区块放入 `<domain>/<shared-section>/index.vue`。
- 至少两个真实路由完全复用同一业务流程，且满足 [page.md](../code/page.md) 的薄路由壳例外时，完整流程允许放入 `<domain>/<flow>/index.vue`。
- 某个组件自己的私有子组件放入该组件目录的 `components/<child>/index.vue`；其他页面禁止直接 import 其私有目录。
- 与组件紧密绑定的 `types.ts`、`options.ts` 或纯转换文件允许放在组件目录；业务 API 仍必须放在 `src/api`。

## 禁止的结构

- 禁止创建 `src/modules/<domain>/components` 作为无语义收纳层。
- 禁止默认把页面请求、状态和完整模板迁入 `modules`，再把所有 `src/pages` 变成薄 import。
- 禁止把多张页面交给一个配置驱动的“通用页面渲染器”；各路由的业务状态和动作必须由页面明确表达。
- 禁止在 `src/modules` 放无业务语义的基础 UI、跨项目 framework 能力、无状态通用工具或多个业务域混合逻辑。
- 禁止用 `workspace`、`common`、`record-list` 一类泛化目录承接多个不同页面动作。

## 命名与结构

- `<domain>`、`<page>`、`<section>` 和 `<flow>` 必须使用短 kebab-case 业务语义。
- 父目录已经表达的 domain 或 page 禁止在子目录重复。
- UI 形态不能代替业务语义；只有同一业务含义存在多种必须区分的 UI 形态时才允许增加 `form`、`card` 等后缀。
- Vue 主实现统一使用 `index.vue`；禁止在 domain 根目录平铺 `XxxCard.vue`、`XxxDialog.vue` 或 `hero-banner.vue`。
- 页面和其他模块只能从组件入口导入，禁止依赖其私有 `components`。

## 与其他目录的边界

- `src/pages` 拥有路由 meta、页面主数据和组合关系，详见 [page.md](../code/page.md)。
- 组件调用范围和提升门禁以 [placement.md](../components/placement.md) 为唯一权威。
- 跨两个以上业务域且 API 稳定的组件进入 `src/components`；跨项目 framework 能力进入 `layers/core`。

## 验收

- 每个 module 组件必须标明它是页面私有区块、业务域共享区块还是共享完整流程，并满足对应调用数量。
- 使用共享完整流程时必须检查所有路由满足薄路由壳的四项条件。
- 必须检查没有 domain 级通用 `components` 收纳层、完整页面默认迁移或配置驱动页面渲染器。
- 必须检查目录名简短、业务语义清楚、入口为 `index.vue`，调用方没有 import 私有子组件。
