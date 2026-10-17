---
name: vab-admin-code-base
description: Vab Admin Vue 与 TypeScript 基础写法、import、store 和局部状态边界
---

# 基础代码规范

本文适用于 Vab Admin 项目的 Vue、TypeScript、import、局部状态和 store 修改。组件放置、命名与事件以 [components/placement.md](../components/placement.md) 为唯一权威。

## 基础写法

- 必须沿用目标项目已配置的 Vue、TypeScript、ESLint、路径别名和格式化体系。
- 禁止为了减少少量重复行新增 wrapper、composable 或 helper。只有同一行为已经在两个真实调用点出现，且可以定义不含页面语义的稳定输入输出时才允许提取。
- 禁止因单页面需求修改全局配置、全局组件、布局组件或依赖版本。
- 禁止格式化或重排本次任务未修改的文件。
- 模板中可直接读取或判断的字段必须直接表达，禁止增加只包装一次属性访问的方法。

## import

- import 必须使用目标项目已有路径别名，例如 `/@/`、`/@vab/`，同一目录内允许使用相对路径。
- 标识符不冲突且导出名能够表达语义时禁止使用 import alias。
- 仅当两个导入在同一文件发生真实命名冲突、导出名与包公开名称不同，或项目对该依赖已有固定别名时允许起别名。
- 禁止为了缩短名称、强调所属层或模仿其他文件，增加 `Api`、`Store`、`Util` 等别名后缀。
- import 分组和 type-only import 必须服从项目 ESLint 的现有结果。

## 局部状态与 composable

- 只服务一个页面或一个组件的表单、弹窗、DOM、loading 和请求状态必须留在该页面或组件。
- 同一组合行为已有两个真实页面调用，且不包含某个页面的完整业务流程时，才允许放入 `src/composables` 或 `src/hooks`。
- 禁止用 composable 隐藏整页数据流；页面主文件必须仍能看出主请求、子组件和刷新关系。

## Store

- 跨页面共享状态、远程 options 缓存、pending 去重或显式刷新动作必须放在 `src/store/modules/`。
- 单页面表单状态、DOM 状态和一次性请求结果禁止放入 store；[remote-options.md](../components/remote-options.md) 定义的远端注册表缓存是明确例外，即使当前只有一个语义组件也必须由业务 store 持有。
- 新 store 必须先检查 `user`、`tabs`、`routes` 及对应业务 store，禁止建立职责重复的模块。
- store 文件名和 `defineStore` 名使用短业务域名，例如 `catalog.ts` 与 `catalog`；禁止 `catalog-item-options-cache.ts` 这类实现细节堆叠名称。
- 登录用户展示名使用 `nickname`；只有 `nickname` 为空时才退回 `username`。
- 远程 options store 的 fetch、cache、pending 与 refresh 契约以 [components/remote-options.md](../components/remote-options.md) 为准。

## 验收

- 必须检查新增封装至少有两个真实调用点；没有时保留局部实现。
- 必须检查 import alias 均能指出允许条件，且没有为缩短名称或标记分层而新增别名。
- 必须检查单页面状态未进入 store，跨页面缓存没有散落在页面或选择组件中。
- 必须对修改文件运行项目 ESLint，并确认没有新增未使用 import、隐式 any 或规则禁用注释。
