---
name: sdkit-testing
description: sdkit core 与 pkg 修改后的 package、集成、兼容和真实消费方验证规则
---

# sdkit 测试规范

本文适用于所有 sdkit 框架修改。实现完成后必须读取本文；只修改业务项目且未修改 sdkit 源码时禁止用本文替代项目测试规则。

## Pkg 验证

- 必须运行目标 `pkg/` package tests。
- 必须验证 package 不启动 sdkit runtime 也能构造和测试。
- driver 必须测试成功、配置错误、外部错误和资源关闭路径。

## Core 验证

- 必须运行目标 `core/` package tests。
- 修改 config、binding、registry、facade 或 lifecycle 时，必须测试注册、启动、停止、重复调用和错误传播。
- core 组装 pkg driver 时，必须至少验证一个真实 driver，不得只测试 mock。

## 消费方验证

- 修改公共 API、配置字段、默认行为或 capability 时，必须选择至少一个真实 sdkitgo 项目验证编译或目标测试。
- 无法访问消费方时必须停止宣称兼容，只能报告 sdkit 自身验证结果和未验证范围。
- 禁止为了让消费方临时通过，在业务项目复制 core 或 pkg 实现。

## 验收

- 目标 package tests 必须通过。
- `core/` 变更必须完成 runtime 集成验证，`pkg/` 变更必须完成独立构造验证。
- 公共 API 或默认行为变化必须记录真实消费方验证结果。
