---
name: vab-admin-framework
description: Vab Admin 项目代码、Vab framework、项目级扩展和共享组件包的边界
---

# Vab 框架规范

本文适用于修改 `library`、layout、全局 plugin、router core、权限守卫、构建配置、主题或共享组件包的任务。普通业务页面不得读取本文后自动扩大到框架修改。

## 框架参考源

“Vab 参考源码”指目标项目文档、workspace 配置、依赖元数据或用户输入明确给出的 Vab Shop Vite checkout。未解析出 checkout 时不得猜测路径；先基于目标项目内现有 `library` 实现工作，只有必须确认上游行为时才向用户索取源码位置。

修改 `library`、布局、全局插件、构建配置、路由框架、主题样式或模板生成逻辑前，必须同时检查目标项目当前实现；已经解析出 Vab 参考源码时，再比较对应上游实现和本地差异。

## 先查框架源码

涉及以下内容时，必须检查目标项目中的对应实现；存在 Vab 参考源码时同时对照它：

- `library/layouts`：整体布局、菜单、标签页、面包屑、移动端布局。
- `library/styles`：主题变量、暗色模式、全局样式、Vab 基础样式。
- `library/plugins`：全局插件、directive、错误日志、Vab install 入口。
- `library/build`：构建插件、UnoCSS、Vite 集成。
- `src/router`：路由组织、权限守卫、动态路由处理。
- `src/plugins/Vab*`：Vab 原生插件组件。
- `plop-template`：模板生成规则。

不要在不了解原始框架实现的情况下重写 layout、router、global style、build plugin 或 Vab plugin。

## 项目扩展边界

- `src/views` 放业务页面。
- `src/api` 放请求方法。
- `src/store/modules` 放业务 store。
- `src/plugins/App*` 只放当前项目需要统一安装或具有稳定协议的通用插件组件。
- `src/styles/app.scss` 只放当前项目跨页面复用的业务样式。
- `library/*` 只允许承载框架行为。普通业务需求禁止修改该目录。

## 共享 npm 组件

- terminal 展示、代码格式化、语法高亮、复制、空态、命令渲染等通用能力统一维护在 `@zixinit/vue-terminal` 包。其源码位置必须从 workspace、依赖元数据、仓库说明或用户输入解析，禁止假定本机目录。
- Vue admin 业务项目需要 terminal 能力时，消费 `@zixinit/vue-terminal` 并引入 `@zixinit/vue-terminal/style.css`；不要在业务项目里复制或新建本地 `components/terminal` 组件。
- 需要新增 terminal 支持语言、格式化规则、token 样式或交互能力时，先改 `@zixinit/vue-terminal`，通过包内 playground 和 `make preflight` 验证后，再升级或接入业务项目。
- `@zixinit/vue-terminal` 的职责边界是展示外部传入的 `content`：包内不封装 SSE、WebSocket、轮询等连接能力，也不绑定业务事件协议；业务项目的 realtime/API 层负责连接、订阅和消息归一化，再更新传给 terminal 的字符串内容。
- terminal 包本体禁止依赖 Element Plus、Vab 或其他业务 UI 框架；demo/playground 只有用于演示宿主集成时才允许使用业务 UI 库，发布包的 peer dependency 必须保持为 Vue。

## 修改框架层代码

修改 `library/*`、全局布局、全局主题、router core、权限守卫或 Vite build 配置时：

- 先确认原始 Vab 源码的写法和当前项目差异。
- 只改必要位置，不大范围重写框架结构。
- 保持 Vab 既有命名、目录、插件注册和布局习惯。
- 必须考虑菜单、标签页、面包屑、权限、移动端和多布局模式影响。
- 业务页面需求必须落在业务页面或业务组件；只有能力需要全局安装或具有跨模块稳定协议时才允许放入 `src/plugins/App*`，两者都禁止修改 `library/*`。

## 依赖和升级

- 不主动升级 Vab、Vue、Element Plus、Vite、Pinia、router、构建插件等依赖。
- 只有当前依赖存在已确认的功能缺口、安全问题或兼容阻塞时才允许升级；升级前必须说明原因、影响范围和与原始框架源码的差异。
- 不为了单个页面效果引入新的 UI 框架或全局视觉体系。

## 验收

- 必须列出修改属于业务页面、项目扩展、Vab framework 或共享组件包中的哪一层。
- 修改 `library`、router core、layout、全局主题或构建配置时，必须提供本地实现检查结果；存在已解析的上游 checkout 时必须同时记录差异。
- 必须检查业务组件没有进入 `library`，单模块组件没有包装成 `App*`，共享包没有依赖宿主 UI 框架或业务协议。
- 依赖升级必须提供功能缺口、安全问题或兼容阻塞的证据以及验证结果；否则禁止升级。
