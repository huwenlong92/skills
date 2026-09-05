# Rust 后端路由规范

## 路由分组

- 同一业务能力必须先建独立 `Router` group，再通过 `.nest("/xxx", group)` 挂到父路由，不把不同业务能力平铺在一个 `Router::new()` 链里。
- 每个 group 前必须有一行简短注释，说明这个 group 的职责边界和鉴权边界。
- group 命名要对应业务名，例如 `project`、`project_groups`、`project_deploy`、`project_rollback`、`nodes`、`users`、`agent`。

## 管理接口路径

- 后台管理接口使用“group + action”路径，不使用资源 id path 参数。
- 列表和详情查询使用 query 参数，例如 `/api/project/detail?key=demo`。
- 创建、更新、删除、重置、执行等写操作使用 JSON body 传参，例如 `/api/nodes/update` body `{ "key": "node-a", ... }`。
- 不写 `/api/nodes/{key}`、`/api/users/{username}`、`/api/project/groups/{id}` 这类路径。
- 业务删除动作不用 HTTP `DELETE` method，统一用 `POST /delete`，避免代理、表单、前端封装和权限审计里的特殊处理。

## 子能力路径

- 子能力按业务语义继续分 group，不把所有动作堆在父级。
- 发布相关放到 `/deploy` 下，例如 `/api/project/deploy/manual`、`/api/project/deploy/records`。
- 回滚相关放到 `/rollback` 下，例如 `/api/project/rollback/config`、`/api/project/rollback/execute`、`/api/project/rollback/records`。
- 日志相关放到 `/logs` 下，例如 `/api/project/logs/tail`、`/api/project/logs/stream`。
- 不使用 `rollback-config`、`deploy-records` 这类在父级拼业务名的路径。

## 鉴权边界

- 鉴权优先挂在 group 上，例如 `.route_layer(middleware::from_fn_with_state(state.clone(), require_admin))`。
- 多个 handler 共享同一鉴权逻辑时，抽成 middleware，并把认证后的上下文放进 request extension。
- handler 不重复实现同一套 token/session 校验，只处理业务参数和业务流程。

## 例外

- 外部系统回调、Webhook、公网可配置 URL 可以保留稳定、直观的 path 参数，例如 `/hook/{hook_type}/{project_key}`。
- 这类例外要限于公开回调入口，不扩散到后台管理 API。

## 前端 API 文件

- 前端 API 文件结构要和后端 route group 对齐。
- group 复杂时使用目录和 `index.ts` 统一导出，例如 `api/projects/manage.ts`、`groups.ts`、`deploy.ts`、`logs.ts`、`rollback.ts`、`version.ts`。
- 页面层从 group 入口导入能力，不在页面里拼装 URL。
