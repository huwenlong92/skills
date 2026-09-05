---
name: vab-admin
description: 为基于 Vab Shop Vite、Vue 3 和 Element Plus 的后台应用执行 SDKit Vab Admin 约定。创建、修改、评审或调试页面、组件、store、API 调用、路由、菜单、权限、样式、上传流程、业务选项和 UI 验证时使用。
---

# Vab Admin

本 skill 仅适用于基于 Vab 的 Vue 后台仓库，不适用于 Nuxt 门户。所有 reference 路径均以目标项目根目录为基准。

## 必须执行的流程

1. 读取 [workflow.md](references/workflow.md)。
2. 读取分流表中与本次修改匹配的每一份 reference；新增或移动文件、目录时必须额外读取 [structure/directories.md](references/structure/directories.md)，禁止加载无关 reference。
3. 在目标仓库中查找一个同类页面或组件，用它确认 API 和本地命名；历史写法不得覆盖本 skill 的显式规则。
4. 完成实现，并对每个修改过的 Vue/TypeScript 文件运行 ESLint；同时执行命中 references 要求的其他检查。

## Reference 分流

| 修改内容 | 读取 |
|---|---|
| 新增、移动文件或目录，判断目录职责 | [structure/directories.md](references/structure/directories.md) |
| `library`、layout、全局 plugin、router core、构建或框架行为 | [framework.md](references/framework.md) |
| Vue/TypeScript 基础、import、store 命名、组件事件 | [code/base.md](references/code/base.md) |
| 页面结构、列表/配置页、页面私有组件 | [code/page.md](references/code/page.md) |
| 组件落点、提取、提升到 module/global 范围 | [components/placement.md](references/components/placement.md) |
| 判定 options 属于固定枚举、远端注册表还是展示模型 | [components/business-options.md](references/components/business-options.md) |
| 固定 enum/status/type 的 options、展示、输入或 `useStatusRender` | [components/enum-components.md](references/components/enum-components.md) |
| 后台可维护注册表 options 组件、版本化 API、store、pending、缓存和刷新 | [components/remote-options.md](references/components/remote-options.md) |
| 上传或上传凭据协议 | [components/app-upload.md](references/components/app-upload.md) |
| HTTP 请求、API 函数、响应 envelope、登录状态、API 环境 | [api/request.md](references/api/request.md) |
| 嵌套展示模型或 options 数据职责 | [api/display-model.md](references/api/display-model.md) |
| 路由、菜单、tab、权限、动态菜单字段 | [router/menu.md](references/router/menu.md) |
| 页面样式、共享 SCSS、表格操作、drawer | [ui/style.md](references/ui/style.md) |

## 停止条件

- 禁止猜测 Vab 参考 checkout 或共享 npm 组件仓库的位置；必须从项目文档、依赖元数据、workspace 配置或用户输入中解析。
- 仅页面需求未满足命中 reference 的提升条件时，禁止修改框架级文件。
- 未取得用户明确授权时，禁止引入第二套 UI 框架、请求客户端、状态系统或格式化系统。
