---
name: nuxtjs-page
description: Nuxt.js 文件路由页面的命名、页面所有权、数据职责和薄壳例外
---

# 页面代码规范

本文适用于新增、修改、拆分或重命名 `src/pages` 下的 Nuxt 路由页面。业务区块的拆分与放置必须同时读取 [components/placement.md](../components/placement.md) 和 [modules/placement.md](../modules/placement.md)。

## 页面命名

- 页面文件和目录必须使用短 kebab-case，并直接表达 URL 资源或动作。
- 业务域入口使用 `src/pages/<domain>/index.vue`；明确不会增加子路由的叶子页面允许使用 `src/pages/<name>.vue`。
- 动态参数必须使用 Nuxt 文件路由语法，例如 `[id].vue`；创建和编辑页使用 `new.vue`、`[id]/edit.vue` 等短动作名。
- 禁止创建 `XxxPage.vue`、`XxxView.vue`、`XxxContainer.vue` 或重复父目录语义的长页面名。
- 登录、注册、错误页、重定向页等 Nuxt 特殊叶子路由允许使用清楚的单文件名，禁止机械改成目录。

## 页面所有权

路由页面必须直接拥有以下页面级职责：

- `definePageMeta`、路由参数解析和页面 SEO/meta。
- 页面主数据、页面级 loading/empty/error 以及 route-aware refresh。
- 标题、操作入口和主要业务区块的组合关系。
- 多个区块之间的页面级状态与动作协调。

页面不要求保持薄壳。禁止为了形式上的“分层”把整个页面原样搬到一个 module 组件，再让 `src/pages` 只保留 import。页面看起来复杂时，必须按独立业务区块和状态边界拆分，而不是隐藏完整页面。

## 薄路由壳例外

只有满足以下全部条件时，路由页才允许只保留 meta、route context 和完整流程组件：

1. 至少两个真实路由复用完全相同的业务流程。
2. 路由之间只在 meta、访问角色或一个明确 context 参数上不同。
3. 共享流程有稳定输入输出，不通过读取路径字符串猜调用方。
4. 两个路由未来仍由同一业务流程共同演进。

任一条件不满足时，页面必须直接表达自己的主数据和组合。共享完整流程放置以 [modules/placement.md](../modules/placement.md) 为准。

## 数据与交互

- 页面主流程允许直接使用 `useAsyncData`、`useAppRequest`、API 函数和局部 state；只有跨页面共享状态才进入 store。
- 拥有独立请求、表单、提交、分页、loading、empty 或 error 的业务区块必须拆出。
- create、update、delete、upload 或状态动作影响页面主数据时，子组件必须触发 `reload`，页面负责重新取得对应数据。
- 后端已经返回嵌套展示模型时必须直接消费，禁止为显示名称逐项请求 options 或在前端遍历拼装关联对象。
- 只有同一状态被多个页面共享或需要跨路由保留时才允许进入 store。

## 验收

- 必须检查 URL、页面文件和目录均使用短且可读的业务名称，没有 `Page`、`View` 或重复父目录语义。
- 必须确认页面入口可直接看出主数据、业务区块和刷新关系，没有无意义的完整页面转发壳。
- 使用薄路由壳时必须列出两个以上真实路由，并逐项验证四个例外条件。
- 必须按 [components/placement.md](../components/placement.md) 检查独立状态区块已经拆分，简单字段未被过度组件化。
- 页面视觉或交互有改动时必须人工检查目标桌面宽度和移动端宽度。
