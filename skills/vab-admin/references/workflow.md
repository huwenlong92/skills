---
name: vab-admin-workflow
description: Vab Admin 需求从定位同类实现到代码验证的执行顺序
---

# 执行流程

本文适用于所有 Vab Admin 创建、修改、重构、评审和调试任务。本文只定义执行顺序；目录、页面、组件和 API 的具体规则由对应 reference 唯一定义。

## 动手前

1. 根据 `SKILL.md` 分流表读取所有命中的 references；新增或移动文件时必须读取 [structure/directories.md](structure/directories.md)。
2. 在目标项目中检查包管理器、scripts、路径别名和一个同类页面或组件。历史实现只用于确认项目 API；与本 skill 冲突时必须执行本 skill。
3. 涉及 `library`、layout、全局 plugin、router core、权限守卫、全局样式或构建配置时，必须读取 [framework.md](framework.md) 并逐项通过其框架层门禁。
4. 页面任务必须先判断页面类型，再读取 [code/page.md](code/page.md) 和 [components/placement.md](components/placement.md)。
5. 上传、业务 options、展示模型、路由或权限任务必须分别读取对应 reference，禁止凭现有单页写法推断共享规则。

## 实现中

- 文件必须放入 [structure/directories.md](structure/directories.md) 已定义的目录；禁止为单次需求建立同义分层。
- 页面必须保留页面级组合与刷新关系；独立交互必须按 [components/placement.md](components/placement.md) 拆分。
- 单页面需求禁止修改框架层、全局主题或全局布局。发现确需新增跨项目或全局能力时，必须先确认其真实调用范围和稳定 API。
- 重构为共享组件、store、项目级样式或上传能力后，必须删除被替代的旧实现，禁止新旧路径并存。
- 修改必须限制在本次任务范围，禁止顺手格式化或搬迁无关历史文件。

## 验证顺序

1. 对每个修改过的 Vue/TypeScript 文件执行项目 ESLint 命令；可自动修复的问题处理后必须重新运行。
2. 执行与风险最接近的项目检查：类型变化运行 typecheck，请求或构建配置变化运行 build，已有相关测试时运行对应测试。
3. 页面布局、交互或样式变化必须在浏览器中检查实际渲染；至少覆盖目标桌面宽度和移动端宽度。
4. 检查 loading、空数据、搜索、重置、分页、提交反馈、失败反馈以及 create/update/delete 后的刷新路径。
5. 修改路由、菜单、权限或详情标签页时，检查菜单高亮、面包屑、tab 行为、route name 唯一性和动态参数页面。
6. 无法执行某项验证时，交付说明必须写明未执行项、原因和需要人工检查的对象。

## 验收

- 必须能从分流表列出本次读取的 references，并确认新增文件均通过目录门禁。
- 必须提供实际执行的 lint、typecheck、test、build 或浏览器检查结果；未执行项必须明确说明。
- 必须确认没有遗留被替代的旧组件、重复请求、重复 scoped 样式或临时验证文件。
- 必须确认没有修改任务范围外的框架文件、全局配置或历史目录。
