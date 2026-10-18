---
name: vab-admin-directories
description: Vab Admin 项目的目录职责、允许内容和禁止的新分层
---

# 目录职责

本文适用于 Vab Admin 项目中的新增文件、移动文件和新建目录。无法确定代码落点时必须先读取本文，再读取表中链接的详细规范。

## 目录总图

| 路径 | 唯一职责 | 禁止放置 |
|---|---|---|
| `src/views` | 路由页面、页面私有组件和模块内共享业务组件 | 全局基础组件、请求底座、通用工具 |
| `src/api` | 按业务域组织的请求函数、参数类型和响应类型 | 页面状态、UI 组件、store |
| `src/components` | 跨业务模块复用且 API 稳定的组件 | 单页面组件、绑定单一页面请求的组件 |
| `src/plugins/App*` | 当前项目统一安装或具有稳定协议的全局组件能力 | 普通业务组件、只为缩短 import 的转发组件 |
| `src/plugins/Vab*` | Vab 已有插件及其兼容维护 | 新增项目业务组件 |
| `src/store/modules` | 跨页面状态、缓存、pending 去重和显式刷新动作 | 单页面表单状态、DOM 状态 |
| `src/composables`、`src/hooks` | 已被多个页面复用的组合行为 | 单页面完整业务流程 |
| `src/utils` | 无状态、无页面语义的纯函数 | API 请求、组件状态、业务页面编排 |
| `src/styles/app.scss` | 当前项目跨页面复用的业务样式 | Vab 框架主题源码、单组件局部样式 |
| `src/router/modules` | 业务路由定义 | 页面实现、菜单 UI |
| `src/config`、`src/constants` | 项目级固定配置和真正跨模块的常量 | 可由后台维护的业务 options、页面临时配置 |
| `src/assets`、`src/icon` | 参与构建的图片、样式资源和自定义图标 | 不参与构建的公开文件 |
| `library` | Vab 框架本身的 layout、component、plugin、style 和 build 能力 | 普通业务需求 |

组件的页面私有、模块共享和全局落点以 [components/placement.md](../components/placement.md) 为唯一权威；页面目录与入口命名以 [code/page.md](../code/page.md) 为唯一权威。

## 新建目录门禁

- 新文件必须先归入上表已有职责，禁止为了一个需求新增 `services`、`features`、`shared`、`common`、`helpers` 或第二套 `modules` 分层。
- 同一职责已经有目录时必须沿用，禁止以个人偏好建立同义目录。
- 表中没有对应职责时，必须先检查它是否属于 Vab 框架、项目全局能力或当前业务页面；仍无法归属时停止新建目录并向用户说明缺失边界。
- 历史目录与本文不一致时，本次新增文件按本文放置；未在任务范围内的历史文件禁止批量搬迁。

## 验收

- 每个新增文件必须能对应目录总图中的一行，且内容没有命中该行的禁止项。
- 必须检查没有新增与现有职责同义的顶层源码目录。
- 新增或移动组件时必须继续通过 [components/placement.md](../components/placement.md) 的调用范围检查。
- 新增或移动页面时必须继续通过 [code/page.md](../code/page.md) 的路由与命名检查。
