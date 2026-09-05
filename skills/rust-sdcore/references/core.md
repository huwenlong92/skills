# Rust 工程规范

## 适用场景

- 修改 Rust 后端项目的目录骨架、能力包、路由、handler、middleware、config、models、pkg 等结构时，先读本文件。
- 新增跨项目可复用能力时必须沉淀到实际解析出的 `sdcore` crate；只有业务项目特有能力才留在项目内 `src/pkg/<ability>`。从 `Cargo.toml`、workspace、path/git dependency、仓库说明或用户输入解析 `sdcore` 源码位置，禁止假定本机目录。

## 分流

- 修改 HTTP 路由、API path、handler 鉴权边界或前端 API 文件组织时，先读 `routing.md`。
- 调试带 Web UI、后端服务和 agent 的 Rust 工具型项目时，先读 `workflow.md`。
- 新增或调整 Rust 测试时，先读 `testing.md`。

## `sdcore` 公共能力边界

- Rust 工具型 Web 应用的公共运行时和基础设施能力必须进入实际解析出的 `sdcore` crate。
- 公共能力包括但不限于命令执行、SSE 推送、reporter、认证、数据库连接、静态资源、日志、配置、后台任务、长任务进度、文件/系统操作辅助等。
- 如果业务项目发现现有 `sdcore` 能力不够用，应优先扩展 `sdcore` 的通用 API，再由业务项目消费。
- 业务项目只保留领域模型、业务路由、业务 handler、业务 runner、业务前端页面和产品特有流程。
- 不要在业务项目里复制一套局部可用的 framework/core 能力。

## `pkg` 能力包结构

- `src/pkg/<ability>` 只用于当前项目特有的领域能力；跨项目公共能力按上一节沉淀到 `sdcore`。
- `src/pkg/<ability>/mod.rs` 只负责声明子模块和导出门面，例如 `mod client;`、`mod types;`、`pub use client::HttpClient;`。
- 具体实现必须放到同级职责文件中，按职责命名，例如 `client.rs`、`types.rs`、`runner.rs`、`guard.rs`、`sender.rs`、`registry.rs`。
- 不要把请求构建、响应类型、执行器、reporter、校验逻辑、注册表等不同职责混在一个 `mod.rs` 里。
- 如果一个能力内还有子能力目录，子目录的 `mod.rs` 也遵守同样规则：只声明和导出，注册表或集合逻辑放到 `registry.rs` 等职责文件。
- `src/pkg/mod.rs` 是全局能力入口，只声明和导出能力包，不承载实现。

## 请求和响应边界

- `src/pkg/response` 表示本服务对外输出的 HTTP 响应能力，负责统一 JSON、文本、静态资源等响应格式。
- `src/pkg/request` 表示本服务访问外部 URL 的出站请求能力，可以有自己的 `HttpRequest`、`HttpResponse` 类型。
- 出站请求的响应不能套用本服务固定响应格式；外部服务响应应保留状态码、响应头、原始 body 等通用字段。

## 日志能力

- 基础日志能力目录统一叫 `src/pkg/logger`，对齐 `core/logger` 的命名，不使用 `logstore` 这类只描述存储方式的名字。
- `pkg/logger` 应提供初始化和常用 level 方法，例如 `init`、`named`、`debug`、`info`、`warn`、`error`、`sync`。
- 运行日志由 `pkg/logger` 统一写入日志根目录，例如 `logs/app/app.log`；启动后不要在业务路径里直接用 `println!` / `eprintln!` 记录运行日志。
- 项目部署日志这类按业务对象落文件的日志，不放在 `pkg/logger` 下；它属于部署 runner 能力，应放在 `src/pkg/deployrunner/log.rs`，提供 `append_deploy_log`、`read_deploy_log_tail`、`deploy_log_dir`。
- CLI 帮助信息、安装进度、启动前 logger 尚未初始化的 fatal 错误，可以保留标准输出或标准错误。

## 可复用过程输出

- 执行过程日志、SSE 推送、数据库记录、文件日志等输出通道应抽成 `pkg` 下的公共能力，例如 `src/pkg/reporter`。
- 业务 runner 只负责业务流程编排，不把通用 reporter 实现写在自己的目录里。
- `reporter` 只负责通用过程事件分发；部署专用的 file/db reporter 应放在 `pkg/deployrunner` 下，由 runner 自己组合。`pkg/logger` 不依赖 `reporter`，也不承载部署日志存储。
- 新增 reporter 时按职责拆文件：通用事件类型放 `pkg/reporter/event.rs`，集合和 trait 放 `pkg/reporter/set.rs`；业务专用输出通道放回对应能力包，例如部署 file/db reporter 放在 `pkg/deployrunner/file_reporter.rs`、`pkg/deployrunner/record_reporter.rs`。
