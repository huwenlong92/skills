---
name: rust-sdcore-routing
description: Axum 按业务分组的 action 路径、group 鉴权、公开回调例外与前端 API 对齐。
---

# 路由与鉴权

适用范围：修改 route、handler、middleware、auth 边界或前端 API 组织。共享 HTTP/认证机制归属以[能力归属](core.md)为准。

## 分组与路径

- 同一业务能力必须先构建独立 Router group，再通过 nest 挂载父路由，禁止在一个 Router::new 链中平铺无关能力。每个 group 前必须用简短注释说明业务职责与鉴权边界。
- 管理 API 必须使用 group + action，查询通过 query 传参，创建、更新、删除、重置、执行通过 JSON body 传参；禁止在管理 API 使用资源 ID path 参数。
- 业务删除必须使用 POST /delete，禁止 HTTP DELETE。子能力必须继续按语义分组，例如 /api/catalog/import/execute、/api/catalog/logs/stream，禁止在父级拼 import-records、rollback-config 等复合动作名。
- handler 必须只处理参数和业务流程；多个 handler 共用的 token/session 校验必须由 group middleware 完成，并通过 request extension 传递认证上下文。

## 鉴权与回调例外

- 鉴权必须先挂在 group；仅当同组个别动作具有不同权限边界时，才允许再拆子 group 或对该独立路由施加匹配 middleware。禁止为方便把全组鉴权重复粘进 handler。
- 外部回调、Webhook 与公开可配置 URL 允许保留协议所需的稳定 path 参数，该例外禁止扩散到管理 API。公开路由仍必须遵守对应协议的验签/访问控制，禁止把路径例外当成免认证授权。
- route_layer 必须覆盖已声明的目标路由；新增路由和 nest 顺序必须按当前 Axum 版本核对，并验证管理组与公开回调没有错误共享认证边界。

以下片段展示边界与路径形态，handler 和 middleware 必须由目标项目实现，禁止复制空鉴权实现：

```rust
use sdcore::axum::{middleware, routing::{get, post}, Router};
use crate::http::{handler::{detail, delete, notify}, middleware::require_admin};

pub fn routes() -> Router {
    // 目录管理：需要管理会话，资源 key 由 query/JSON 提供。
    let catalog = Router::new()
        .route("/detail", get(detail))
        .route("/delete", post(delete))
        .route_layer(middleware::from_fn(require_admin));

    // 外部通知：按回调协议校验，不复用管理会话入口。
    let hooks = Router::new().route("/notify/{catalog_key}", post(notify));
    Router::new().nest("/api/catalog", catalog).nest("/hook", hooks)
}
```

路径参数写法必须匹配项目实际 Axum 版本，示例不授权升级依赖。反例：管理 API 使用 /api/catalog/{key} 或 DELETE /api/catalog/delete，并在每个 handler 内复制 token 检查。

## 前端 API

- 前端 API 模块必须与后端 group 对齐；一个文件无法保持单一 group 职责时必须按子 group 建文件，并由 index.ts 导出，例如 api/catalog/manage.ts、import.ts、logs.ts 与 index.ts。
- 页面必须从对应 group 入口导入，禁止在页面拼 URL。API 文件只允许位于目标前端已有 API 层，禁止放入 sdcore、业务后端 pkg 或复制到多个页面。

## 完成标准

- group 职责和鉴权注释明确，管理查询/写入分别通过 query/JSON，删除使用 POST /delete。
- 真实回调协议的稳定路径保留；无管理路径参数扩散、重复鉴权或公开回调被管理会话错误拦截。
- 必须验证未认证、无权限和合法请求的结果；仅编译通过不证明鉴权正确。
- 人工检查前端 API 导出与后端路径/方法对齐，管理组与回调各自执行正确校验。
