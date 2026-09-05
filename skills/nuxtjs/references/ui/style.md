---
name: nuxtjs-ui-style
description: Nuxt.js 局部样式、framework theme、业务主题、layout 和响应式视觉规则
---

# 样式与主题规范

本文适用于修改页面或组件样式、framework theme、业务主题、layout、Element Plus 覆盖和响应式视觉。页面所有权以 [page.md](../code/page.md) 为唯一权威。

## 样式边界

- 只服务当前 Vue 组件的样式必须使用 scoped。
- 跨项目设计 token、framework theme、全局样式入口和 Element Plus 覆盖必须放在 `layers/core/assets/styles`。
- 只属于当前产品品牌的主题必须放在 `src/assets/styles/themes/<theme-name>`，禁止把品牌值写回 core。
- 页面禁止直接覆盖 Element Plus 全局样式；确认需要全项目统一时才允许修改集中覆盖文件。
- 已有 CSS variable 或 token 能表达的值必须复用；只有组件特有的栅格、媒体比例、图标尺寸和装饰几何值才允许局部写值。

## Layout 与页面

- 被多个路由共享的 header、footer、sidebar、background 和主内容容器必须由 Nuxt layout 承担。
- 当前产品需要覆盖 core layout 时放在 `src/layouts`；单页面内容区块禁止新增 layout。
- 页面 layout、theme、pageClass 和 wrapClass 必须通过 `definePageMeta` 使用已有能力；只有现有 layout API 无法表达两个以上页面的共同外壳时才允许新增 layout。
- 普通组件承载可复用内容区块、表单控件或独立业务单元，不能代替 layout，也不能隐藏整个页面；页面组合规则见 [page.md](../code/page.md)。

## 业务主题

- 一个业务主题必须使用单一 `index.scss` 入口，并拆分 `_tokens.scss` 与 `_base.scss`。
- `_tokens.scss` 统一定义颜色、字体、字阶、字重、行高、字距、间距、圆角、阴影、动效和 Element Plus bridge variables。
- `_base.scss` 只负责页面底色、默认字体渲染、表单字体继承和文字选中态等基础行为。
- 页面和业务组件禁止重复定义主题已有的字体、文字颜色、字重、行高或字距。
- 同一主题覆盖公开页、认证页和登录后工作台时必须复用同一入口。

## 图标与响应式

- Remix Icon 能表达语义时必须使用 `VabIcon`；没有对应语义时才允许在 `src/icon` 新增 kebab-case SVG。
- 门户内容可以使用较强视觉表达，但每个区块必须服务真实内容或操作，禁止纯装饰堆叠。
- 操作型页面必须保持可扫描的信息层级；核心文字和操作禁止依赖图片传达。
- 响应式修改必须检查移动端文字换行、按钮宽度、触控区域、图片裁切和横向溢出。

## 验收

- 必须检查局部、产品主题和 core framework 样式分别落在正确目录，没有重复 token 或跨层污染。
- 新增 layout 必须列出至少两个真实路由和现有 API 缺口；不满足时必须改为页面或组件。
- 必须搜索页面中的固定主题值，确认已有 token 均被复用。
- 必须人工检查目标桌面宽度、移动端宽度、主题切换、文字换行、触控与图片裁切。
