---
name: vab-admin-ui-style
description: Vab Admin 局部与项目级样式、列表操作列、页面容器和标准抽屉规则
---

# UI 与样式规范

本文适用于页面样式、全局业务样式、表格操作列和标准抽屉。

## 项目级 SCSS

- 同一业务样式已经有两个真实页面调用时，必须抽到项目级 SCSS。
- 项目级业务样式统一写到 `src/styles/app.scss`。
- `src/styles/app.scss` 用于当前项目复用的业务样式，例如表格操作列、标准抽屉、统一局部查询区、通用状态布局。
- 不要在多个页面 scoped 样式里重复写同一套 class。
- 当前项目业务样式禁止写入 Vab 框架层 `library/styles/*`；只有修改框架主题或布局协议时才允许写入。
- 抽到 `src/styles/app.scss` 后，页面使用稳定 class，不再用 scoped `:global` 重复命中 Element Plus teleport 结构。
- 抽取完成后必须删除页面里旧的重复 scoped 样式，新旧样式不能并存。

## 样式

- 只服务当前组件的样式必须使用局部 scoped。
- 跨页面复用的业务样式放在 `src/styles/app.scss`，例如表格操作列、标准抽屉。
- 相同业务样式出现第二个真实页面调用时，必须抽到 `src/styles/app.scss`，禁止继续复制到页面 scoped 样式。
- 项目使用全局样式入口时，`src/styles/app.scss` 必须从应用入口或现有全局样式入口导入，不要让页面单独补全局样式依赖。
- 只有本次需求改变全局视觉协议、主题或布局时才允许修改对应全局文件。
- 不要引入新的色彩体系或大面积重写 UI 风格。
- 修改布局组件时必须考虑标签页、菜单、面包屑和移动端影响。
- 业务列表页和配置页默认由框架页面根容器提供白色背景、边框、圆角和内边距，不要再套一层整页 `vab-card`、`el-card`，也不要用负 margin 抵消卡片间距。
- 卡片只用于具有独立信息分组语义的仪表盘、统计块或并列面板；查询列表和连续配置表单不以卡片作为默认页面骨架。

## 表格操作列

表格操作列包含多个 `el-link`、按钮或下拉触发器时，统一使用 `app-table-actions` 包裹。

```vue
<template #default="{ row }">
  <span class="app-table-actions">
    <el-link type="primary" underline="never" @click="editRef?.open(row)">编辑</el-link>
    <el-dropdown trigger="click">
      <span class="app-table-action-more">更多</span>
    </el-dropdown>
  </span>
</template>
```

- 行内操作容器使用 `app-table-actions`。
- 下拉触发器使用 `app-table-action-more`。
- 对齐、间距、垂直居中由共享 class 控制，不在页面里补 `margin-left` 或局部对齐样式。

## 标准抽屉

业务抽屉必须同时使用全局基础 class 和当前模块自己的 class，例如：

```vue
<el-drawer class="app-drawer system-admin-drawer">
  ...
</el-drawer>
```

紧凑抽屉同时使用 `app-drawer` 和 `app-drawer--compact`。

```vue
<el-drawer class="app-drawer app-drawer--compact">
  ...
</el-drawer>
```

- `app-drawer` 控制通用 header、body、footer 间距。
- 当前模块自己的 drawer class 只用于当前业务的特殊样式。
- 通用 header/body/footer 不要再用 scoped `:global(.xxx-drawer .el-drawer__header)` 重复写。
- header 默认样式：`padding: 14px 20px`、`margin-bottom: 0`、`border-bottom: 1px solid rgba(31, 35, 41, 0.15)`。
- body 默认样式：`padding: 16px 20px 20px`。
- 表单需要更舒服的左右间距时，在表单根 class 加 `padding: 0 12px`。
- 字段不超过五个且标签能在 `80px` 内完整显示时使用 `label-position="left"` 和 `label-width="80px"`；不满足时使用 `label-position="top"`。

## 验收

- 必须检查局部样式使用 scoped，跨两个以上页面的业务样式位于 `src/styles/app.scss`，框架主题样式没有混入业务规则。
- 必须搜索被抽取 class 的旧 scoped 实现，确认新旧样式没有并存。
- 列表操作列必须人工检查按钮、link 和 dropdown 的间距、垂直对齐与窄屏表现。
- drawer 必须人工检查 header、body、footer、滚动、表单标签和移动端宽度。
- 页面容器与卡片使用必须继续通过 [page.md](../code/page.md) 的页面骨架检查。
