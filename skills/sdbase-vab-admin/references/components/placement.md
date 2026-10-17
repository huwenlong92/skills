---
name: vab-admin-component-placement
description: Vab Admin 页面私有、模块共享和全局组件的拆分、放置与命名规则
---

# 组件放置与命名

本文适用于 Vab Admin 项目中新增、拆分、移动或重命名 Vue 组件。页面主文件变复杂、准备创建 `components` 目录或提升组件复用范围时必须读取本文。

## 先按调用范围放置

| 调用范围 | 必须放置 | 示例形态 |
|---|---|---|
| 只服务当前页面 | `src/views/<module>/<page>/components/<name>/index.vue` | `components/create/index.vue` |
| 同一业务模块内至少两个真实页面复用 | `src/views/<module>/components/<name>/index.vue` | `components/status/index.vue` |
| 至少两个业务模块复用，但仍带稳定业务域语义 | `src/components/<domain>/<name>/index.vue` | `src/components/account/avatar/index.vue` |
| 至少两个业务模块复用，且不含业务域语义 | `src/components/<name>/index.vue` | `src/components/page-state/index.vue` |
| 需要全局安装、统一协议或统一基础交互 | `src/plugins/App<name>` | `src/plugins/AppUpload/index.vue` |

- 新组件必须从最窄调用范围开始。未找到两个真实调用页面时禁止放入模块共享目录；未找到两个真实业务模块时禁止放入全局目录。
- 组件提升时只移动已经稳定的组件 API；调用方的页面请求、路由判断和权限动作继续留在调用方。
- Vab 已有 `Vab*` 组件必须直接复用。项目扩展只有满足最后一行条件时才使用 `App*`；禁止用 `App*` 包装单一业务组件。

## 什么时候必须拆

页面或组件命中以下任一条件时必须继续拆分：

- 同时包含两个以上具有独立业务语义、各自拥有状态或交互流程的区块；同一列表的查询、表格和分页不因此强制拆成三个组件。
- 某个抽屉、弹窗、详情、创建、编辑、审核、上传、导入或状态变更拥有自己的表单、校验、提交或 loading。
- 某个区块拥有独立请求、分页、空态、展开状态或错误状态。
- 父文件需要维护多个互不依赖的 form ref、dialog state 或 request state。
- 同一段 UI 已经被两个真实页面复用。

拆分不以固定行数为门槛。文件很长只是检查信号；是否拆分必须由独立职责和状态边界决定。拆分后的父页面必须能一眼看出页面由哪些业务区块组成，禁止把整页原样搬入一个 `XxxPage` 或 `XxxView` 组件。

只有一个没有值映射或输入协议的简单字段、无业务语义的图标或一段只使用一次的模板不得单独拆组件。固定枚举与远端 options 属于明确的语义组件，必须按 [business-options.md](business-options.md) 分流，不受这条简单字段限制。

## 命名

- 目录名必须使用短 kebab-case 业务名或动作名，例如 `create`、`edit`、`detail`、`audit`、`member`、`status`。
- 目录已经表达 module、page 和 component 层级，名称禁止重复这些上下文。禁止 `system-admin-role-permission-dialog` 这类路径信息堆叠。
- 主实现统一使用 `index.vue`。同一业务含义确有输入变体时，才在同目录增加 `select.vue`、`radio.vue` 或 `checkbox.vue`。
- import 标识符使用 PascalCase，并使用当前文件内最短且无歧义的名称。页面私有组件允许使用 `Create`、`Edit`、`Detail`；出现同名冲突时才补资源名。
- 禁止无必要的 `Page`、`View`、`Component`、`Dialog`、`Drawer`、`Form` 后缀。只有同一业务含义在同一作用域存在多种 UI 形态时才允许用 UI 后缀消歧。
- 模板中的本地组件标签必须使用 kebab-case。
- 组件需要 `defineOptions({ name })` 时，name 必须是当前作用域最短且可识别的 PascalCase 名；页面 route name 的规则以 [router/menu.md](../router/menu.md) 为准。

## 父子职责

- 页面负责页面级查询条件、主数据、路由动作、打开子组件以及协调刷新。
- 子组件负责自己的表单、校验、提交、局部 loading 和局部展示状态。
- 子组件完成会影响父级数据的 create、update、delete、upload 或状态动作后，必须触发 `reload`；父组件监听 `@reload` 后刷新主数据。
- 禁止使用 `saved` 代替 `reload`，也禁止让子组件直接调用父页面的列表请求函数。
- 全局通用组件禁止直接请求调用方页面的业务 API；数据必须通过 props、events 或稳定 adapter 传入。具有固定资源语义的远端 options 组件必须通过所属 store 加载自身 options，按 [remote-options.md](remote-options.md) 执行，禁止接管调用页面的主请求。

## 正向结构

```text
src/views/catalog/item/
├── index.vue
└── components/
    ├── create/
    │   └── index.vue
    ├── detail/
    │   └── index.vue
    └── edit/
        └── index.vue

src/views/catalog/components/status/
├── index.vue
├── options.ts
└── select.vue
```

`item/index.vue` 只展示查询、主列表、分页以及 `Create`、`Detail`、`Edit` 的组合关系；三个子组件各自拥有自己的交互状态。

页面入口保持可读的组合关系：

```vue
<script setup lang="ts">
import Create from './components/create/index.vue'
import Detail from './components/detail/index.vue'
import Edit from './components/edit/index.vue'

const createRef = ref<InstanceType<typeof Create>>()
const detailRef = ref<InstanceType<typeof Detail>>()
const editRef = ref<InstanceType<typeof Edit>>()

async function fetchData() {
  // 只处理本页查询、主列表、分页和 loading。
}
</script>

<template>
  <vab-query-form><!-- 查询与主操作 --></vab-query-form>
  <el-table><!-- 主列表与打开子组件的入口 --></el-table>
  <app-pagination />

  <create ref="createRef" @reload="fetchData" />
  <detail ref="detailRef" />
  <edit ref="editRef" @reload="fetchData" />
</template>
```

子组件拥有自己的提交过程，只向父页面报告刷新语义：

```vue
<script setup lang="ts">
const emit = defineEmits<{ reload: [] }>()

async function submit() {
  // 当前组件的校验、提交和局部 loading。
  emit('reload')
}
</script>
```

## 验收

- 必须列出每个新增或提升组件的真实调用页面，并按调用范围验证目录。
- 必须检查页面主文件仍清楚显示页面区块与数据刷新关系，没有退化成单一完整页面组件的转发壳。
- 必须检查每个独立表单、弹窗、抽屉、详情或独立请求区块已拆出，且简单字段没有被过度组件化。
- 必须检查目录名为短 kebab-case、入口为 `index.vue`、import 名为最短无歧义 PascalCase，且没有重复路径语义或无必要 UI 后缀。
- 必须验证子组件成功后触发 `reload`，父组件收到后刷新对应数据。
