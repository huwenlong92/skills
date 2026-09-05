---
name: nuxtjs-component-placement
description: Nuxt.js 页面私有、业务域共享、跨业务和 core 组件的拆分、放置与命名规则
---

# 组件放置与命名

本文适用于 Nuxt.js 项目中新增、拆分、移动或重命名 Vue 组件。页面主文件变复杂、准备创建业务区块或提升组件复用范围时必须读取本文。

## 先按调用范围放置

| 调用范围 | 必须放置 | 示例形态 |
|---|---|---|
| 只服务一个路由页面 | `src/modules/<domain>/<page>/<name>/index.vue` | `src/modules/catalog/items/filter/index.vue` |
| 同一业务域至少两个真实页面复用 | `src/modules/<domain>/<name>/index.vue` | `src/modules/catalog/status/index.vue` |
| 至少两个业务域复用，但仍带稳定业务语义 | `src/components/<domain>/<name>/index.vue` | `src/components/account/phone/index.vue` |
| 至少两个业务域复用，且不含业务语义 | `src/components/<name>/index.vue` | `src/components/page-state/index.vue` |
| 跨项目复用的 Nuxt framework 能力 | `layers/core/components/<name>/index.vue` | `layers/core/components/app-upload/index.vue` |

- 新组件必须从最窄调用范围开始。未找到两个真实页面时禁止提升到业务域共享；未找到两个真实业务域时禁止提升到 `src/components`。
- 只有与 Nuxt layout、request、auth、theme、upload 等框架机制关联、API 稳定且不依赖业务接口或文案的组件，才允许进入 core。
- 页面专属组件不能放入 `src/pages` 子目录，因为 `.vue` 文件可能参与文件路由生成。
- 组件提升时只移动稳定组件 API；路由判断、页面请求和页面权限动作继续留在调用页面。

## 什么时候必须拆

页面或组件命中以下任一条件时必须继续拆分：

- 同时包含两个以上具有独立业务语义、各自拥有状态或交互流程的区块；同一列表的查询、表格和分页不因此强制拆成三个组件。
- 某个表单、详情、审核、上传、导航面板或状态动作拥有自己的校验、提交或 loading。
- 某个区块拥有独立请求、分页、empty、error 或响应式状态。
- 父文件维护多个互不依赖的 form ref、overlay state 或 request state。
- 同一段 UI 已被两个真实页面复用。

拆分不以固定行数为门槛。文件很长只是检查信号；是否拆分由独立职责和状态边界决定。拆分后的页面必须能一眼看出由哪些业务区块组成，禁止为缩短文件把整页原样搬入一个 `XxxPage`、`XxxView` 或 `XxxContainer`；完整流程复用仅允许 [code/page.md](../code/page.md) 中的多路由例外。

只有一个没有值映射或输入协议的简单字段、无业务语义的图标或一段只使用一次的模板不得单独拆组件。固定枚举与远端 options 属于明确的语义组件，必须按 [business-options.md](business-options.md) 分流，不受这条简单字段限制。

## 命名

- 目录名必须使用短 kebab-case 业务名或动作名，例如 `profile`、`identity`、`invitation`、`filter`、`detail`、`status`。
- 路径已经表达 domain 和 page，名称禁止重复这些上下文。
- 主实现统一使用 `index.vue`。同一业务含义确有输入变体时，才在同目录增加 `select.vue`、`radio.vue` 或 `checkbox.vue`。
- import 标识符使用 PascalCase，并使用当前文件内最短且无歧义的名称；发生真实同名冲突时才补业务名。
- 禁止无必要的 `Page`、`View`、`Container`、`Component`、`Dialog`、`Drawer`、`Form`、`Card` 后缀。只有同一业务含义在同一作用域存在多种 UI 形态时才允许用 UI 后缀消歧。
- 模板中的本地组件标签必须使用 kebab-case。

## 父子职责

- 页面负责 route meta、主数据、页面级状态、区块组合和刷新协调。
- 子组件负责自己的展示、表单、校验、提交和局部状态。
- 子组件完成会影响父页面数据的 create、update、delete、upload 或状态动作后必须触发 `reload`；父页面监听后刷新对应数据。
- 禁止使用 `saved` 代替 `reload`，也禁止让子组件直接调用父页面函数。
- 跨业务组件和 core 组件禁止直接请求调用方页面业务 API；数据必须通过 props、events 或稳定 adapter 传入。带固定资源语义的业务 options 组件必须通过所属 store 加载自身 options，按 [remote-options.md](remote-options.md) 执行；禁止因此将业务 options 放入 core。

## 正向结构

```text
src/pages/catalog/items/index.vue

src/modules/catalog/items/
├── filter/
│   └── index.vue
├── result-list/
│   └── index.vue
└── detail/
    └── index.vue

src/modules/catalog/status/
├── index.vue
├── options.ts
└── select.vue
```

页面入口直接组合 `Filter`、`ResultList` 和 `Detail`，并保留主请求与刷新关系；各区块拥有自己的局部状态。

```vue
<script setup lang="ts">
import { getItemList } from '/@/api/catalog/item'
import Detail from '/@/modules/catalog/items/detail/index.vue'
import Filter from '/@/modules/catalog/items/filter/index.vue'
import ResultList from '/@/modules/catalog/items/result-list/index.vue'

definePageMeta({ layout: 'content', publicAccess: true })

const query = ref({ keyword: '' })
const selectedID = ref('')
const { data, pending, refresh } = await useAsyncData('catalog-items', () => getItemList(query.value))
</script>

<template>
  <filter v-model:value="query" @search="refresh" />
  <result-list :items="data?.list || []" :loading="pending" @select="selectedID = $event" />
  <detail :id="selectedID" @reload="refresh" />
</template>
```

该页面直接表达主数据和三个区块的关系；筛选器、结果区和详情区分别维护自己的局部交互，禁止再用一个完整 `CatalogItemsView` 包住它们。

## 验收

- 必须列出每个新增或提升组件的真实调用页面，并按调用范围验证目录。
- 必须检查页面入口仍清楚显示业务区块与刷新关系；完整流程薄壳仅允许 [code/page.md](../code/page.md) 定义的多路由复用例外，禁止为形式分层创建转发壳。
- 必须检查独立表单、详情或独立请求区块已经拆出，简单字段没有被过度组件化。
- 必须检查目录名为短 kebab-case、入口为 `index.vue`、import 名为最短无歧义 PascalCase，且没有重复路径语义或无必要 UI 后缀。
- 必须验证子组件成功后触发 `reload`，页面收到后刷新对应数据。
