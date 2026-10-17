---
name: rust-sdcore-core
description: sdcore 共享机制与业务语义的唯一归属定义，领域 pkg 结构及日志、请求响应和 reporter 边界。
---

# 能力归属与结构

适用范围：所有匹配本 skill 的任务，尤其目录骨架、能力包、共享 API、日志、命令执行与 reporter 调整。路由、联调、测试分别读取对应 reference，禁止在其他文件重复定义归属。

## 解析源码与归属

- 必须从 Cargo.toml、Cargo.lock、workspace、path/git dependency、项目说明或用户输入定位 sdcore；必须核对实际 revision 与 features，禁止把本机同名仓库自动当成已消费版本。
- Rust 工具应用的公共运行时和基础设施机制必须放入解析出的 sdcore crate。业务项目只允许保留领域模型、业务路由/handler、业务 runner、前端与产品专属适配，禁止复制 framework/core 或通过换目录名掩盖重复实现。
- 公共机制缺口必须先扩展 sdcore，再通过依赖接入。仅当新增逻辑具有本产品独有的领域规则或输出语义时，才允许放在业务 src/pkg/<ability>；调用方暂时只有一个不构成把通用机制留在业务中的理由。
- sdcore 公开 API 与 feature 行为必须从实际导出与实现读取；禁止为了套用示例假造不存在的方法、模块或依赖版本。

| 能力 | 允许位置 | 禁止位置 |
|---|---|---|
| 命令执行、process 生命周期、SSE、认证、连接管理、静态资源、配置、日志、后台任务/进度 | sdcore 当前对应公共模块 | 业务项目的第二套 core、通用 executor/logger/reporter 等实现 |
| 通用 reporter 事件、trait、集合和分发 | sdcore reporter 模块，按 event/set 等职责拆分 | 业务 runner 中复制通用分发器 |
| 统一入站 HTTP 响应与通用出站传输机制 | sdcore 当前对应公共模块 | 业务 pkg/response 或 pkg/request 中重建通用协议层 |
| 目录导入、产品执行步骤、领域第三方客户端、专属文件/数据库输出 | 业务 src/pkg/<ability> 的职责文件 | sdcore 中硬编码产品字段、表名、路径与流程 |

## 领域 pkg 形态

- src/pkg/mod.rs 与 src/pkg/<ability>/mod.rs 必须只声明模块与导出门面，实现必须放在同级 runner.rs、client.rs、types.rs、guard.rs、log.rs 或 registry.rs 等职责文件。子能力目录遵守同一规则，禁止把多种职责堆进 mod.rs。
- 仅创建当前确实需要的职责文件，禁止为了目录完整性创建空模块或无调用方封装。

以下是虚构目录导入能力的形态；通用执行器直接消费 sdcore，不在业务目录实现：

```rust
// src/pkg/catalogrunner/mod.rs
mod runner;
pub use runner::inspect_catalog_input;
```

```rust
// src/pkg/catalogrunner/runner.rs
use std::{path::Path, time::Duration};
use sdcore::exec::{ExecOutput, ExecRequest, ShellExecutor};

pub fn inspect_catalog_input(working_dir: &Path) -> Result<ExecOutput, String> {
    let request = ExecRequest::new(working_dir, "printf 'fixture-ready\n'")
        .with_timeout(Duration::from_secs(2));
    ShellExecutor.run_capture(request)
}
```

该片段仅演示调用边界，业务必须核对实际工作目录和输入。禁止把用户文本直接拼接进 shell 命令；工作目录、环境、超时与取消必须使用已确认的底座契约，缺口必须回到底座修复。

## 请求响应、日志与过程输出

- 入站响应必须复用 sdcore 已有 HTTP 能力；出站适配必须保留外部响应状态、头和原始 body 等通用信息，禁止套用本服务固定响应格式掩盖外部协议。
- 基础日志必须使用 sdcore 的 logger 公共模块，命名禁止退回只描述存储的 logstore。初始化、named/level 输出与 flush 等能力必须按实际 API 使用，禁止在业务 src/pkg/logger 复制实现。
- 日志根目录必须由配置解析。logger 初始化后禁止在业务路径使用 println!/eprintln! 替代运行日志；CLI 帮助、明确的终端进度及 logger 初始化前的 fatal 错误允许标准输出/错误。
- 按业务对象保存的执行日志必须放在所属能力包，例如 src/pkg/catalogrunner/log.rs，不得塞进通用 logger；其读取/追加接口必须表达领域含义。
- 通用 reporter 事件与分发必须在 sdcore，业务 file/db reporter 必须放在所属领域包，由 runner 组合。logger 禁止依赖业务 reporter 或承载业务记录存储。

反例：业务 src/pkg/reporter 重写通用事件集合，或 sdcore logger 直接写本产品的导入记录表。

## 完成标准

- 实际 sdcore 路径、revision、features 与消费声明一致，公共机制和领域逻辑各有唯一实现位置。
- mod.rs 只声明/导出，正向调用形态采用真实 API，没有空模块或为单项目复制的 framework。
- 人工检查 logger/reporter、请求响应与 runner 的依赖方向，没有产品数据流入通用底座。
- 数据库迁移或清理必须另有精确范围授权、备份与恢复验证；缺少前提时必须停止对应数据操作，禁止把代码修改视为数据授权。
- 修改后的编译、公共行为与消费验证必须满足[测试与验收](testing.md)。
