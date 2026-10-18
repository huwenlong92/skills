---
name: http-foundation
description: sdkitgo app/http 公共协议层的职责、允许目录和禁止边界
---

# `app/http` 公共层规范

本文定义 `app/http` 的职责和允许目录。新增、移动或评审 `app/http/**`，或判断 HTTP 公共代码应放 handler、middleware、infra 还是 core 时必须读取本文。

## 职责

`app/http` 只保存多个 HTTP service 共同使用的传输协议约定。代码必须同时满足：依赖 HTTP/Gin 语义，并且已被两个及以上 HTTP service 使用或属于固定 HTTP 契约。

| 目录 | 允许内容 | 禁止内容 |
|---|---|---|
| `app/http/form` | [form.md](form.md) 规定的分页、排序等稳定公共请求片段 | 单个资源或单个接口的 request struct |
| `app/http/response` | JSON envelope、成功/失败输出、统一错误转换 | 业务判断、数据库查询、权限逻辑 |
| `app/http/validator` | Gin binding 入口、错误翻译、自定义 validation tag 注册 | 数据库存在性、权限、状态流转、外部调用 |

`app/http` 不新增其他一级目录，除非用户明确确认新的跨 HTTP 服务协议契约。

## 与其他目录的边界

- 只属于一个 endpoint 的 request、projection、查询和 CRUD 必须放在 `app/{service}/handler/{module}`。
- 公共 HTTP middleware 放在现有 `app/middleware`；服务私有 middleware 放在 `app/{service}/middleware`，具体边界读取 [service/middleware.md](../service/middleware.md)。禁止同时创建语义重复的 `app/http/middleware`。
- 离开 HTTP 后仍成立的 database、Redis、storage、queue、realtime 或业务 capability 必须按 [infra/placement.md](../infra/placement.md) 放置，禁止放入 `app/http`。
- Gin binding、response 或 middleware 的通用框架行为属于 sdkit 时，必须按 [framework/boundary.md](../framework/boundary.md) 判断框架归属，禁止在 `app/http` 复制框架实现。

## 验收

- 必须逐个核对新增符号是否依赖 HTTP/Gin，并证明它属于多个 HTTP service 或固定 HTTP 契约。
- `app/http/form` 不得出现业务资源名；`app/http/validator` 不得访问数据库、Redis、网络或运行时 capability；`app/http/response` 不得包含业务分支。
- 必须搜索是否已经存在同义 middleware、validator、response helper 或 core 能力；存在时禁止重复新增。
