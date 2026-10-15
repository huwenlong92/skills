---
name: rust-sdcore
description: 为依赖 sdcore 的 Rust 工具型 Web 应用执行 SDKit 约定。创建、修改、评审或调试共享 core 边界、领域能力包、Axum 路由与鉴权、命令执行、SSE/reporter、本地 Web、agent-node 和测试时使用；普通未采用 sdcore 的 Rust 项目不触发。
---

# Rust sdcore

用于依赖 sdcore 或明确采用 SDKit Rust 工具架构的任务。通用机制由共享 sdcore 承载，业务项目保留领域行为；路径以目标项目根目录或已经解析的 sdcore checkout 为基准。

## 任务分流

| 任务 | 必须读取 |
|---|---|
| 所有匹配任务：确认共享能力与业务边界 | [能力归属与结构](references/core.md) |
| route、handler、middleware、auth、前端 API | [能力归属与结构](references/core.md)、[路由与鉴权](references/routing.md) |
| 本地 Web、process、SSE/reporter 联调、agent-node、部署验收 | [能力归属与结构](references/core.md)、[本地联调](references/workflow.md) |
| 新增/修改测试及最终验证 | [测试与验收](references/testing.md)，按修改内容追加上面命中的 reference |

## 执行顺序

1. 读取目标项目规则与 Cargo.toml/Cargo.lock，解析 workspace、path/git dependency、features、实际 sdcore 源码与版本；禁止假定工作站路径或将不同 revision 的源码当作当前依赖。
2. 按任务分流读取 references，先判定通用机制和业务语义，再修改权威归属处。实际 API、模块与依赖版本必须从当前源码解析，示例不是永久兼容承诺。
3. 在已授权范围实施修改；公共能力缺口必须在 sdcore 修复，业务项目通过已有依赖消费，禁止复制局部 core 来绕过边界。
4. 按测试 reference 完成匹配验证；共享底座变化必须验证实际消费方，分别报告源码、依赖接入、编译/测试与本地链路结果。

## 共同门禁

- 当前用户要求 > 目标项目显式规则 > 本 skill > 历史写法；禁止顺带改造无关历史代码或未经要求升级工具链。
- 涉及额外仓库时必须检查现有授权。所需 sdcore checkout 无法定位或不在授权范围时，停止越界修改，完成范围内分析并说明缺口；禁止擅自 clone、切换依赖或发布来补齐。
- 命令执行、SSE、认证、数据库、静态资源、日志、配置、后台任务与进度分发的通用机制只能由共享底座维护，具体归属以 core reference 为唯一权威定义。
- 联调、数据库变更、发布和部署分别服从当前任务授权；禁止因修复底座或页面而自动操作线上服务或数据。
