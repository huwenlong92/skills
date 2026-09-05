---
name: nuxtjs-store-state
description: Nuxt.js Pinia store 的新增门禁、目录、命名、缓存、SSR hydrate 和清理规则
---

# Store 与状态规范

本文适用于新增、修改或删除 Pinia store、跨页面状态、业务缓存、SSR hydrate 和 legacy store。

## 目录与新增门禁

- framework 的 theme、layout 和 route 状态放在 `layers/core/stores`；业务用户态、站点配置和业务缓存放在 `src/store/modules`。
- 页面或组件局部的表单、DOM、loading 和一次性请求结果必须使用局部 `ref`、`useState` 或 `useAsyncData`，禁止进入 store。
- 状态满足以下至少一项时才允许新增 store：被两个真实页面共享；需要跨路由保留；需要 pending 去重；具有明确全局生命周期与清理动作。
- 新增前必须检查 `user`、`routes`、`settings`、`system` 及同业务域 store，禁止建立职责重复模块。

## 命名与职责

- 业务 store 放在 `src/store/modules/<name>.ts`，文件名与 store id 必须使用同一短业务语义。
- 禁止用 `user-profile-navigation-cache.ts` 一类名称堆叠状态细节。
- store action 负责请求、状态更新、cache、pending 和清理；页面负责 toast、导航、DOM 和交互展示。
- core store 禁止依赖业务 API 或保存页面状态；业务 store 允许调用 `src/api`。

## 缓存与 SSR

- 同一请求可能并发触发时必须用 pending promise 合并，并在成功或失败后清理 pending。
- 缓存必须定义有效条件、强制刷新入口和清理时机，禁止永久缓存没有版本或过期规则的数据。
- SSR bootstrap store 只允许接收 server plugin 的 hydrate/set 数据，禁止把 private upstream 请求暴露成客户端 action。
- 可维护注册表的缓存、pending、SSR hydrate 与刷新契约以 [remote-options.md](../components/remote-options.md) 为唯一权威。
- logout 必须清理 user、permission、token/session 和与身份绑定的业务缓存。
- 服务端请求临时状态禁止写入浏览器 localStorage；持久化 key 必须含稳定项目语义。

## Legacy Store

- `legacy*` store 只允许维持已有兼容行为，新代码禁止增加其接口或调用点。
- 只有确认没有模板、plugin、layout 或旧页面依赖后才允许删除 legacy store。
- 新需求必须进入当前语义明确的 store；不得继续包装 legacy API。

## 验收

- 新 store 必须列出满足的新增门禁和真实调用页面。
- 必须检查局部 UI 状态没有进入 store，core store 没有依赖业务 API。
- 缓存必须验证并发去重、失败清理、force refresh、logout 清理和 SSR/client 边界。
- legacy 修改必须证明没有新增调用；删除时必须提供全仓依赖搜索结果。
