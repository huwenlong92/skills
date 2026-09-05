---
name: rust-sdcore
description: 为 Rust 工具型 Web 应用执行 SDKit sdcore 约定。创建、修改、评审或调试共享 core 边界、package 布局、Axum 路由、handler、middleware、命令执行、SSE、reporter、测试、本地 Web 联调和 agent-node 流程时使用。
---

# Rust sdcore

当 Rust 项目依赖 `sdcore`，或用户明确要求采用 SDKit Rust 工具架构时使用本 skill。references 中的路径以目标项目根目录或解析出的 `sdcore` checkout 为基准。

## 必须执行的流程

1. 每个任务都必须读取 [core.md](references/core.md)。
2. 修改 route、handler、middleware、auth 或前端 API 时读取 [routing.md](references/routing.md)。
3. 修改本地 Web、SSE、process、部署或 agent-node 行为时读取 [workflow.md](references/workflow.md)。
4. 新增测试前和最终验证前读取 [testing.md](references/testing.md)。
5. 必须从 `Cargo.toml`、`Cargo.lock`、workspace 配置、仓库规则或用户输入中解析共享 `sdcore` 源码；禁止假定工作站路径。

## 停止条件

- 可复用框架缺陷必须在 `sdcore` 修复，产品专属流程必须留在消费项目。所需仓库不在任务范围内时，说明边界并取得授权，确认前停止修改。
- 禁止在消费项目中重复实现命令执行、SSE、认证、数据库、静态文件、日志、配置、后台任务或进度基础设施。
