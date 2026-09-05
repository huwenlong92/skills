# Rust 测试规范

## 测试文件位置

- 公共 API、集成行为、跨模块流程、命令执行、SSE、reporter、数据库连接等能力测试，默认放在 crate 根目录的 `tests/` 下。
- `src/**` 实现文件里不要长期堆大量 `#[cfg(test)] mod tests`，避免实现文件膨胀、阅读主逻辑时被测试细节打断。
- 只有测试私有纯函数、极小边界条件，且无法通过公开 API 验证时，才允许在实现文件旁边保留少量单元测试。
- 新增公共能力时，优先创建按能力命名的测试文件，例如 `tests/exec_shell.rs`、`tests/sse_hub.rs`、`tests/reporter_set.rs`。

## 测试内容边界

- 公共能力测试应覆盖对外 API 行为，而不是依赖内部私有函数。
- 业务项目测试只验证业务行为；如果测试暴露出底座能力不足，应先补 `sdcore` 测试和能力，再回到业务项目消费。
- 测试命名使用行为描述，例如 `shell_executor_times_out_long_running_commands`。
- 需要临时目录、端口、环境变量时，测试内显式隔离，不依赖开发机固定状态。

## 验证要求

- 修改 Rust 公共能力后，至少运行对应 crate 的测试，例如 `cargo test -p sdcore`。
- 修改业务项目对 `sdcore` 的消费方式后，同时运行业务项目的 `cargo check` 或相关测试。
