---
name: nuxtjs-code-base
description: Nuxt.js Vue 与 TypeScript 基础写法、import、局部状态和 composable 边界
---

# 基础代码规范

本文适用于 Nuxt.js 项目的 Vue、TypeScript、import、局部状态和 composable 修改。页面与组件命名分别以 [page.md](page.md) 和 [placement.md](../components/placement.md) 为唯一权威。

## 基础写法

- 新 Vue 代码必须使用 `<script setup lang="ts">`，props 和 emits 必须声明类型。
- API 返回值和复杂对象必须有明确类型，禁止隐式 `any` 和 `Record<string, any>` 兜底。
- 仅当外部依赖类型错误且本次无法修正其 declaration 时才允许局部使用 `as any`；必须用注释写明外部缺口和移除条件。
- 禁止因单页面需求引入新的状态库、请求库、格式化器或目录组织方式。
- 简单字段必须在模板或 computed 中直接表达，禁止增加只包装一次属性读取的方法。

## import

- import 必须使用目标项目已有路径别名，例如 `/@/` 或 `@/`；同一组件内部允许相对路径。
- 标识符不冲突且导出名能够表达语义时禁止使用 import alias。
- 仅当两个导入在同一文件发生真实命名冲突、导出名与包公开名称不同，或项目对该依赖已有固定别名时允许起别名。
- 禁止为了缩短名称、强调层级或模仿历史文件增加 `Api`、`Store`、`Util`、`View` 等别名后缀。

## 局部状态与 composable

- 只服务一个页面或组件的表单、DOM、loading、筛选和一次性请求状态必须留在该页面或组件。
- 同一组合行为已有两个真实页面调用，且可以定义不含单页完整流程的稳定输入输出时，才允许放入 `src/composables`。
- 路由、导航、鉴权或缺省态已有 composable 能完整表达需求时必须复用；仅当现有 API 无法表达已确认需求时才允许扩展。
- 禁止用 composable 隐藏整个页面的数据流；页面入口必须仍可看出主请求、区块和动作协调。

## Store

- 新增 store 的门禁、命名、缓存和清理规则以 [state.md](../store/state.md) 为唯一权威。
- 只服务当前页面的状态禁止进入 store。

## 验收

- 必须对修改文件运行项目 format、ESLint 和 typecheck 中已配置的对应命令。
- 必须检查 props、emits、API 结果和复杂状态没有新增隐式 any。
- 每个 import alias 和 `as any` 必须满足本文允许条件；无法说明条件时必须移除。
- 新增 composable 必须列出至少两个真实调用页面，并确认未隐藏完整页面流程。
