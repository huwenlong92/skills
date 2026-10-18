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

## SSR 异步上下文

- 统一 request 必须在异步签名或 await 前捕获当前 Nuxt app、store 和 request event；响应回调必须复用它们，Set-Cookie 必须写回该 event，认证跳转必须使用捕获 app 的 runWithContext。禁止在 await 后重新取得请求上下文或跨 SSR 请求共享实例。
- 已接入同源内部请求的版本，只有同源相对目标允许传递发起请求 context，禁止传给外部 upstream 或浏览器。未实现该能力时必须报告差距，禁止宣称已支持。
- 平台 Binding 只允许在 server adapter 注入最小接口；开发 Node/线程/CLI 依赖禁止进入 Worker/浏览器产物。缺少配置与实际读取失败必须分别报错，禁止回退虚构业务数据。此规则不表示模板已接入任何平台 Binding。

正向形态：发起请求前捕获 `const event = useRequestEvent()`，异步响应只将 Set-Cookie 写回同一 event。反例：异步回调再次 useRequestEvent 或将 context 附加到外部 URL。

## 验收

- 必须检查页面和组件没有新建请求实例或重复解析 envelope。
- 必须检查 API 文件归属单一业务域，函数名、参数和返回类型明确。
- SSR 数据必须说明首屏必要性和跨页面调用范围，并验证私有地址与凭据未进入客户端 bundle。
- 必须检查 hydrated 数据没有客户端重复请求，交互请求没有被错误塞入 SSR bootstrap。

SSR 请求改动必须验证并发身份/Cookie 隔离、异步鉴权跳转、API、去除 payload script 后的 HTML 与 hydration；已使用 Binding 的项目必须另行核验真实连接、缓存与授权撤销时限，API 成功不能代替 SSR 成功。
