---
name: vab-admin-page
description: Vab Admin 路由页面的目录、命名、页面所有权和标准页面骨架
---

# 页面代码规范

本文适用于 `src/views` 下新增、修改、拆分或重命名路由页面。页面内组件的提取、放置和命名必须同时读取 [components/placement.md](../components/placement.md)。

## 页面目录与命名

- 路由页面必须放在 `src/views/<route-segments>/index.vue`；目录使用短 kebab-case，并与业务路由层级一致。
- 页面入口统一命名为 `index.vue`。禁止新增 `XxxPage.vue`、`XxxView.vue` 或重复完整路由语义的长文件名。
- 页面目录只允许放入口文件和该页面的 `components/`；跨页面共享组件必须按 [components/placement.md](../components/placement.md) 提升。
- 页面 `defineOptions({ name })` 必须与路由 `name` 对齐，且全局唯一；详细规则以 [router/menu.md](../router/menu.md) 为准。

## 页面主文件职责

页面主文件必须让读者直接看出页面由哪些业务区块组成以及数据如何刷新。它只负责：

- 页面级查询条件、主数据请求、分页和 loading。
- 查询区、操作区、主表格或主内容区的组合。
- 路由跳转、打开页面私有组件以及监听 `reload`。
- 多个业务区块之间的页面级状态与动作协调。

创建、编辑、详情、审核、导入、上传、状态变更等拥有独立状态或提交过程的交互，必须拆入页面私有组件。禁止把完整页面原样移入一个 `XxxPage` 或 `XxxView`，再让路由入口只做无意义转发。

模板中能直接读取的简单字段必须直接读取；禁止为了单个字段展示增加无复用价值的方法。存在关联对象或业务维度展示时，必须消费接口返回的嵌套展示模型；只有接口无法改变且用户确认兼容方案时，才允许在前端做临时转换。

## 列表页骨架

- 列表页必须按“查询与操作区、表格、分页”组织，不得再套整页 `vab-card` 或 `el-card`。
- 查询区必须使用 `vab-query-form-top-panel` 展示当前路由的 `meta.icon` 和 `meta.title`，并使用 `vab-query-form`、`vab-query-form-left-panel`、`vab-query-form-right-panel`。
- 筛选项放在左面板，页面主操作放在右面板；禁止另建 `panel-head` 放新增等主操作。
- `vab-query-form-left-panel` 使用项目默认宽度；局部查询区只使用左面板时必须显式写 `:span="24"`。
- 项目存在 `src/plugins/AppPagination`、`src/plugins/AppSearchComplex`、`src/plugins/AppExpand` 或 `src/composables/table.ts` 时，匹配其职责的页面必须复用。仅当现有 API 无法表达本次业务状态时，才允许在页面内实现替代方案，并在修改说明中写明缺口。
- `el-table-column type="expand"` 必须加 `fixed`；只有需求明确要求展开列随表格滚动时才允许取消。
- 新增列表页必须覆盖搜索、重置、loading、空数据、分页、操作反馈以及子组件成功后的刷新。

## 配置页骨架

- 配置页必须按“路由标题、配置内容”组织为单层页面。
- 项目存在 `src/components/AppConfigPage` 时必须复用；不存在时，只有至少两个配置页需要同一页面壳时才允许新增共享壳，否则在当前页面保持单层结构。
- 路由标题必须使用 `meta.icon` 和 `meta.title`，并与列表页标题位置保持一致。
- 多组策略、注册表或渠道配置必须在同一页面容器内按区块排列，使用统一间距和分隔线；禁止把连续配置区块堆成多张同构卡片。
- 已支持 `embedded` 的共享配置组件嵌入页面壳时必须启用该模式，避免重复边框和 padding。

## 允许使用卡片的页面

仪表盘、统计卡片组、详情工作台或需要并列对比的独立面板允许使用卡片；每张卡片必须对应可独立命名的信息分组。列表页和连续配置表单禁止仅为制造容器感而使用卡片。

## 验收

- 必须检查页面路径为短 kebab-case 目录加 `index.vue`，route name 与页面 name 对齐且唯一。
- 必须确认页面主文件可直接看出业务区块与刷新关系，没有无意义的 `XxxPage` 或 `XxxView` 转发壳。
- 必须按 [components/placement.md](../components/placement.md) 检查独立交互已经拆分，简单字段未被过度组件化。
- 列表页必须人工检查查询、操作、表格、分页、loading、空态和刷新；配置页必须人工检查单层页面壳和区块分隔。
- 修改布局或样式后必须检查桌面和移动端实际渲染，确认没有横向溢出或异常换行。
