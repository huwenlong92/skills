---
name: vab-admin-router-menu
description: Vab Admin 路由、后端菜单字段、标签页、菜单高亮和权限规则
---

# 路由与菜单约定

本文适用于修改 `src/router/`、后端菜单数据、布局标签页、菜单高亮、面包屑或权限守卫。

## 路由组织

- 业务路由放在 `src/router/modules/`
- 新业务域必须建立独立路由模块；同一业务域的新页面必须加入现有对应模块，禁止塞进无关模块
- 个人中心这类登录用户自服务页面应独立为 account 模块
- 系统管理使用 system，系统配置使用 configure，个人设置使用 account

## 路由组件

- 组件路径必须使用 Vite 能正确解析的项目别名或相对路径
- 不要生成浏览器无法加载的本地绝对路径
- 动态 import 需要指向真实存在的 `.vue` 文件

## 后端菜单路由字段

- `name` 首字母大写，必须与对应 vue 文件导出的 `name` 对齐，且全局不可重复。该字段用于 `noKeepAlive` 缓存控制，新增页面时重点检查。
- `path` 规则：
  - 根路由第一条数据使用 `/`
  - 一级路由必须以 `/` 开头
  - 二级及以下路由不能以 `/` 开头
  - `path` 不可重复，框架会自动拼接父子级
  - `path` 只写一个单词，不写 `/a/b/c` 这种多段路径
- `component` 规则：
  - 后端路由里是字符串
  - 前端本地路由里是 import function
  - 一级路由使用 `Layout`
  - 其他层级使用 `views` 下的相对路径，不写 `/@/views/` 前缀，不写 `.vue` 后缀，例如 `system/menu/index`
  - 后续动态路由接入时再统一拼接 `/@/views/` 和 `.vue`
- `redirect` 如需配置，按从一级路由开始拼接后的路径填写。
- `children` 用于子菜单树。

## Meta 字段

- `hidden`：菜单隐藏
- `levelHidden`：隐藏一级路由
- `title`：菜单、面包屑、多标签显示名
- `icon`：新版图标
- `isCustomSvg`：自定义 svg 图标，开启后需要把 svg 放到 icon 目录，`icon` 填图标名
- `noKeepAlive`：不缓存当前路由
- `noClosable`：多标签页不可关闭
- `noColumn`：隐藏分栏，仅当分栏布局中的二级路由明确不显示分栏时允许开启
- `badge`：子级 badge 文案
- `tabHidden`：不显示多标签页，仅当页面是 redirect、过渡页或需求明确禁止产生 tab 时允许开启
- `target`：新标签打开，仅用于外部地址或需求明确要求浏览器新标签的页面，禁止用于分栏左侧 tab
- `activeMenu`：隐藏页高亮菜单，必须从根路由 path 开始拼接
- `dot`：小圆点
- `dynamicNewTab`：动态参数路由新开标签页
- `breadcrumbHidden`：隐藏面包屑
- `guard`：角色控制，可为角色数组，也可为 `{ role: [], mode: "allOf" | "oneOf" | "except" }`

## 菜单与标签页

- 隐藏页面需要设置 `hidden`
- 详情、个人中心等页面需要关注 `activeMenu`、标签页高亮和面包屑表现
- 动态参数详情页需要设置 `dynamicNewTab`，避免不同 `:id` 共用同一个多标签页。
- 动态详情页的返回按钮必须使用项目已有 `useBack().goRoute({ name: 'XxxList' })` 按路由 `name` 返回并关闭当前详情标签页；只有目标项目没有该能力时才允许使用 router API 实现同等行为。
- 动态详情页加载到业务标题后，应按当前 tab path 精确更新标签标题；不要只按路由 `name` 批量改 meta，避免同一详情组件打开多个 id 时互相覆盖标题。
- 个人中心从首页入口打开且需求要求高亮首页时，必须使用已有布局支持的 active tab/menu 字段；只有该字段无法表达时才允许修改布局逻辑
- 修改布局高亮逻辑时必须确认不会影响其他菜单和标签页

## 权限

- 路由权限必须复用现有 `permissions.ts` 和 store 逻辑；只有现有权限模型无法表达已确认的新语义时才允许扩展
- 不要在页面里硬编码权限判断
- 后端菜单接口尚未具备项目所需字段时，允许保留本地路由汇总；本地数据必须使用同一菜单类型和字段，禁止建立无法迁移到后端菜单的第二套模型

## 验收

- 必须检查 route name 与页面 name 对齐且全局唯一，动态 import 指向真实文件。
- 必须校验后端菜单的 path 层级、component 字符串、redirect 和 children 拼接结果。
- 隐藏页和动态详情页必须人工检查 activeMenu、面包屑、tab 标题、返回关闭和多 id 并存行为。
- 权限修改必须验证允许、拒绝和登录态变化三条路径，页面中不得新增硬编码权限判断。
