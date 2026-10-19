---
name: rust-sdcore-testing
description: sdcore 与消费项目的测试落点、公开行为验证、隔离边界和变更后的验收范围。
---

# 测试与验收

适用范围：新增或修改 Rust 测试，以及任何匹配任务的最终验证。能力归属以[core](core.md)为准，真实 Web/agent 链路以[workflow](workflow.md)为准。

## 测试位置与内容

- 公共 API、跨模块、命令执行、SSE、reporter、数据库连接测试必须放在对应 crate 根目录 tests/；禁止在 src 实现文件中长期堆集成测试。
- 仅当测试对象是无法通过公共 API 验证的私有纯函数或极小边界时，才允许 src 中保留小型 cfg(test) 单元测试；规模扩大到公共行为时必须迁到 tests/。
- 测试文件必须按能力命名，如 tests/exec_shell.rs、tests/sse_hub.rs、tests/reporter_set.rs；测试名必须描述行为，禁止绑定私有实现细节或只复述代码。
- 业务测试必须验证领域行为，公共机制缺陷必须先在 sdcore 添加对应公开行为回归并修复，再由消费方验证接入；禁止靠业务测试和局部绕过掩盖底座问题。
- 临时目录、端口、配置和数据库必须隔离到本次 fixture；禁止依赖个人目录、真实凭据或修改共享开发库。无写入的固定命令测试允许使用测试 crate 工作目录，禁止用真实部署命令作为 fixture。

以下测试片段只适用于当前提供这些公共 API 且有 sh 的环境；它验证外部可见输出，不依赖私有函数：

```rust
use std::{path::Path, time::Duration};
use sdcore::exec::{ExecRequest, ShellExecutor};

#[test]
fn captures_fixed_command_output() {
    let request = ExecRequest::new(Path::new("."), "printf 'fixture-ready\n'")
        .with_timeout(Duration::from_secs(2));
    let output = ShellExecutor.run_capture(request).expect("fixture command");
    assert!(output.success);
    assert_eq!(output.stdout, "fixture-ready");
}
```

反例：为测试 runner 直接调用生产部署、真实消息流或远端数据库，或只断言内部 helper 的实现步骤。

## 依赖与版本升级验收

- 来源、固定 tag、锁文件及升级边界必须遵守[源码与固定版本](repository.md)，本文件只规定匹配的验收，不另维护版本号或仓库地址。
- 依赖迁移或升级后，必须使用 Cargo 实际解析结果核对 sdcore 的完整 Git commit、features 与源码路径，并运行消费方的 `cargo check --locked` 和相关 `cargo test --locked`；只修改声明或底座测试通过不能代替消费方验证。
- 修改底座 feature 行为时，必须覆盖受影响的默认、最小或组合 features，并验证实际消费方所用组合。修改 CI/Docker 依赖获取方式时，必须验证相应构建入口不依赖本机 SDK 或额外凭据；未执行的入口必须明确标记待验证。

## 验证范围

- 修改共享底座必须运行对应 crate 的测试，并至少验证一个实际消费方的 cargo check 或相关测试。消费方源码或构建环境不可用时必须报告缺口，禁止声称已完成消费验收。
- 修改业务对 sdcore 的依赖、features 或消费方式时必须运行业务 cargo check 或相关测试；必须核对锁定 revision/features 已实际生效。
- 后端业务先编译检查再执行相关模型、handler 或 runner 测试；UI 改动使用项目静态检查与本地交互验证。涉及前后端联动、SSE、agent 或部署时，必须使用本地真实服务链路，禁止只用模拟输出交付。
- 格式和静态检查必须使用项目规定入口。没有额外约定的 Rust 变更必须检查 cargo fmt --check；只有新增修改、失败或未解决问题需要时才扩大或重复验证，禁止为纯文档调整运行无关业务部署。

```bash
# 在已经确认的 sdcore workspace 根目录执行，包名从 Cargo.toml 解析。
cargo test -p sdcore --locked
# 在实际消费方根目录执行。
cargo check --locked
```

## 完成标准

- 测试落点正确且覆盖本次公开行为/领域行为，fixture 不污染个人或共享环境。
- 共享底座与实际消费方结果分别记录，已执行/未执行清楚；失败时必须报告失败阶段而非只给“测试不通过”。
- 人工检查鉴权、事件顺序、取消、节点重连等本次受影响的真实链路；编译或 mock 通过不能代替链路验收。
- 提交前必须审查差异和本次验证范围，禁止自动纳入无关文件、发布或线上变更。
