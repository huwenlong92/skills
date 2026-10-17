---
name: rust-sdcore-repository
description: sdcore Rust 框架的实际依赖来源定位、仓库身份验证与跨仓库安全边界
---

# Rust sdcore 源码定位

适用范围：使用 rust-sdcore Skill 修改公共底座、核验框架版本或判断业务项目与 sdcore 的边界时必须读取。

- 当前尚未确认 sdcore 的独立权威 GitHub 仓库地址；禁止猜测为 huwenlong92/sdcore 或其他未核实路径。
- 必须从目标项目 Cargo.toml、Cargo.lock、workspace、path/git dependency、项目 AGENTS.md 与现有 checkout 确认真实依赖和 revision。
- 只读取已经授权访问的本地或远端源码；无法确定来源时，允许完成当前业务项目内的只读分析，但不得跨仓库修改公共 sdcore。
- 本地路径动态发现，禁止写死个人本机路径；不同 revision 不能当成同一份框架源码。
- 计划的新 Skill 名称为 sdkit-rust-core；当前旧入口 rust-sdcore 保持有效，尚未切换安装或触发。

## 完成标准

能列出 Cargo 实际依赖、版本/revision、源码来源和修改授权范围；来源不明时明确报告阻塞，不编造仓库身份。
