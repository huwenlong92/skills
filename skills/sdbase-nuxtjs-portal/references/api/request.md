---
name: nuxtjs-api-request
description: Nuxt.js 请求 wrapper、API 文件与函数、返回类型和 SSR 初始化数据边界
---

# 请求规范

本文适用于 Nuxt.js 门户的 HTTP 请求、API 文件、请求与响应类型、客户端交互请求和 SSR 初始化请求。

## 请求入口

- 客户端与 universal 代码必须复用项目已有 `useAppRequest()`，禁止直接新建 `$fetch`、axios 或第三方请求实例。
- 页面和组件禁止重复处理统一 request 已覆盖的成功码、登录过期、token/cookie 清理和全局错误提示。
- API 函数只负责请求、参数和返回类型，禁止持有组件 loading、toast、router 或 DOM 状态。
- 统一 request 已支持 `err_code`、`code`、`msg`、`data` envelope 时，调用方必须使用归一化结果。

## API 文件

- 客户端可调用的业务接口放在 `src/api/<domain>.ts`；同一业务域出现两个以上明确子职责时允许改为 `src/api/<domain>/<resource>.ts`。
- 目录已经表达业务域时，子文件使用短资源或流程名，禁止重复父目录名称。
- 跨角色合同完全相同的资源放在资源业务域；角色专属动作放在对应角色域。禁止用 `common`、`business`、`workspace` 混装多个业务域。
- 只服务端调用且含私有 upstream 或凭据的接口必须放在 Nuxt 实际隔离的 `server/` 目录或服务端 plugin 中，禁止进入通用 `src/api`；任意目录中自行加 `.server.ts` 后缀不能替代服务端导入边界检查。
- 页面 `.vue` 文件禁止定义可复用 API 函数。

## 类型与命名

- 请求参数和响应必须定义明确 interface 或 type，字段名必须与真实 API 一致。
- 查询列表使用 `getXxxList`，详情使用 `getXxxDetail`，预览使用 `getXxxPreview`，新增使用 `createXxx`，编辑使用 `updateXxx`，删除使用 `deleteXxx`。
- 禁止用 `saveXxx` 合并新增和编辑语义。
- 禁止使用 `Record<string, any>` 覆盖已知字段；只有服务端明确允许任意动态筛选键时才允许索引签名。

## SSR 初始化数据

- 只有站点配置、全局导航或首屏渲染前必须存在且跨页面复用的参考数据，才允许在 Nuxt 服务端初始化并 hydrate store。
- 服务端 upstream、token 和凭据必须放在 private runtime config，禁止进入 `runtimeConfig.public` 或客户端 bundle。
- 服务端初始化请求必须放在 `.server.ts` plugin 或 `server` 专用 adapter；客户端 store 只接收 hydrate/set 结果。
- 已由 SSR 注入且缓存仍有效的数据，页面和客户端 plugin 禁止在 `onMounted` 重复请求。
- 非关键初始化项失败时必须返回明确空态或本地安全缺省值，禁止使整个 SSR 页面返回 500；鉴权或页面主数据失败不得用缺省值掩盖。
- 表单选择器使用的可维护注册表不自动归入 SSR 初始化；其版本化 API、缓存、SSR hydrate 和刷新以 [remote-options.md](../components/remote-options.md) 为准。

## 验收

- 必须检查页面和组件没有新建请求实例或重复解析 envelope。
- 必须检查 API 文件归属单一业务域，函数名、参数和返回类型明确。
- SSR 数据必须说明首屏必要性和跨页面调用范围，并验证私有地址与凭据未进入客户端 bundle。
- 必须检查 hydrated 数据没有客户端重复请求，交互请求没有被错误塞入 SSR bootstrap。
