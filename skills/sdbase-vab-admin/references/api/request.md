---
name: vab-admin-api-request
description: Vab Admin 请求封装、API 函数命名、响应 envelope、登录态和 API 环境规则
---

# 请求规范

本文适用于 HTTP 请求封装、接口方法命名、响应格式、登录态和环境配置。

## 请求封装

- 统一复用 `src/utils/request.ts`。
- 不要在页面里直接新建 axios 实例。
- 不要绕过统一错误处理、登录过期处理和响应归一化。
- 新增接口必须放到 `src/api/` 对应业务文件；只有框架自身请求明确已有其他入口时才沿用该入口。

## 接口方法命名

- 新增和编辑分别使用 `createXxx`、`updateXxx`。
- 不使用 `saveXxx` 表达新增/编辑合并语义。
- 删除使用 `deleteXxx`，请求仍按后端约定走 POST `/delete`。

## 响应格式

- 需要兼容后端 `err_code`、`msg`、`data` 格式。
- 前端判断成功时需要兼容 `err_code: 0` 和项目已有成功码。
- 后端业务错误通常 HTTP status 仍为 200，前端必须通过业务错误码和响应体判断。
- 后端返回非空 `msg` 时必须显示该信息；`msg` 为空时才使用前端定义的通用错误文案。

## 登录态

- 前台需要兼容 session cookie 和 JWT 两种登录方式。
- 项目存在 `is_login` cookie 契约时，本地登录判断必须读取该 cookie；不存在时必须使用项目当前 session/token 状态源。
- 有 token 时继续兼容 Authorization Bearer 逻辑。
- 不要强行把 session 登录改造成 JWT 登录。
- 退出登录时需要同时清理前端本地状态和登录态 cookie/token。

## 环境配置

- 项目已经定义 `VITE_APP_API_URL` 时必须使用它；仅当目标项目使用其他已存在的 API base 约定时才沿用该约定。
- 只有本次需求改变部署入口或代理拓扑时才允许修改 `.env.development`、`.env.production` 或 Vite proxy。
- 已存在表达相同 API base 的环境变量时禁止重复增加代理配置。

## 验收

- 必须检查页面和组件没有新建 axios 实例或绕过 `src/utils/request.ts`。
- 必须检查 API 函数位于对应业务文件，create、update、delete 命名与后端路由语义一致。
- 必须验证业务错误码、`msg`、登录过期以及 session/JWT 清理路径。
- 环境配置有改动时必须记录部署入口变化并执行对应环境的构建或启动检查。
