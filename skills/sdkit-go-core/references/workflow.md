---
name: sdkit-workflow
description: 修改 Go sdkit 框架时的范围确认、调用方检查和实施顺序
---

# sdkit 工作流

本文适用于修改 Go sdkit 框架源码的任务。新增、重构、移动或删除 sdkit package 时必须读取本文；普通 sdkitgo 业务项目修改禁止读取本文代替业务规范。

## 修改前

- 必须确认当前任务目标是 sdkit 框架仓库，不是业务项目中的 `app/infra` 或服务私有代码。
- 必须搜索现有 `core/`、`pkg/`、tests 和至少一个真实消费方，确认已有能力、调用方式和兼容面。
- 必须记录新增能力解决的真实调用需求；禁止以“以后可能用到”作为进入 sdkit 的依据。
- 新增或移动 package 前必须读取 [core-vs-pkg.md](architecture/core-vs-pkg.md)。

## 实施顺序

1. 先确定能力是否包含业务语义；包含时停止修改 sdkit，回到业务项目。
2. 再判断它是否参与 sdkit 的配置、注册、生命周期、capability 或 facade；命中时读取 [framework.md](core/framework.md)。
3. 未命中框架职责、但属于可独立消费的通用机制时读取 [library.md](pkg/library.md)。
4. 先实现最小公共契约，再实现 adapter、driver 或 runtime wiring。
5. 修改公共 API 后同步修改 sdkit tests 和真实消费方。

## 停止条件

- 任务需要改变业务 model、业务 schema、业务状态机或项目权限语义时，必须停止向 sdkit 提取。
- 无法找到真实调用方时，禁止新增公共 package；必须先由业务项目保留实现并等待形成稳定边界。
- 需要破坏已有公共 API 且用户未授权兼容策略时，必须停止并说明影响范围。

## 验收

- 能指出代码唯一归属为 `core/`、`pkg/` 或业务项目，并提供对应判定依据。
- 新增公共 API 必须存在 sdkit package test 和至少一个真实消费路径验证。
- 业务标识、业务字段、业务状态和项目路径不得进入 sdkit。
