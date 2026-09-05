---
name: sdkit
description: 开发、重构或评审 Go sdkit 框架仓库时使用，约束框架能力归属以及 core、pkg、facade、driver 和 runtime 的边界。普通 sdkitgo 业务项目 CRUD 不使用本 skill。
---

# sdkit

本 skill 只处理 Go sdkit 框架仓库。普通业务项目必须使用 `sdkitgo`，只有任务明确修改 sdkit 框架源码时才使用本 skill。

## 执行顺序

1. 读取 [workflow.md](references/workflow.md)，确认任务范围和实际调用方。
2. 新增或移动 package 时读取 [core-vs-pkg.md](references/architecture/core-vs-pkg.md)。
3. 目标属于 `core/` 时读取 [framework.md](references/core/framework.md)。
4. 目标属于 `pkg/` 时读取 [library.md](references/pkg/library.md)。
5. 完成后读取 [testing.md](references/testing.md)，验证 package 和真实消费路径。

## 门禁

- reference 中的 capability、provider 和 driver 名称必须是虚构或通用示例，只用于表达框架结构；禁止把业务项目中的真实名称和代码片段复制进本 skill。
- 禁止因为代码“可能复用”就放入 sdkit。
- 包含业务项目的 model、schema、状态机、权限名称、route 或页面语义时，必须留在业务项目。
- 无法确定 `core/` 或 `pkg/` 时，必须先按 [core-vs-pkg.md](references/architecture/core-vs-pkg.md) 完成依赖与生命周期判定，禁止先建目录再补理由。
- 修改公共 API 时必须检查真实消费方；禁止只让 sdkit 自身编译通过。
