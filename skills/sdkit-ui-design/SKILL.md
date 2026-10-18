---
name: sdkit-ui-design
description: 跨项目 UI 视觉设计、页面布局、交互状态、响应式设计、设计图片基线归档、设计稿复核及面向开发 Agent 的设计交接；不负责业务代码、产品仓库管理或部署。
---

# SDKit UI Design · 设计与交接 V1.1

适用于设计、修改、评审 UI 设计稿，或将已有设计稿归档并交给开发 Agent。仅业务代码、前端 Bug、原型发布或 PRD 不得作为 Primary。

## 分流

| 任务 | 读取 |
|---|---|
| 页面视觉、风格、布局、组件设计 | [视觉规范](references/visual.md) |
| 页面流程、弹窗、表单、状态 | [交互规范](references/interaction.md) |
| 多端设计、可访问性 | [响应式规范](references/responsive.md) |
| 已授权基于实际图片进行设计迭代、原型或正式开发 | [设计基线归档](references/baseline.md)、[设计交接](references/handoff.md) |
| 交给 Codex 或其他开发 Agent | [设计交接](references/handoff.md)；涉及图片归档时再读 [设计基线归档](references/baseline.md) |
| 评审设计稿、对比实现截图 | [设计复核](references/review.md) |

## 协作边界

- 纯设计任务以 sdkit-ui-design 为 Primary；Foundry 负责项目身份、Workspace、权威仓库、产品决策及原型迁移声明。不得自行实现第二套 Resolver。
- 设计图片归档协议由本 Skill 定义；正式业务实现由技术栈 Skill 负责，原型源码及发布按 Foundry 与目标仓库规范执行。Git 操作遵守共享协作协议。
- 用户明确要求基于图片开发且写入授权覆盖归档时，必须先核验并保存设计基线，再进入选定实现模式；只读讨论不得写入。图片字节不可访问时 BLOCKED，不得声称已归档。
- implementationMode 允许 production、prototype、undecided；未确定时只归档，不自动开发。归档不代表 Commit、Push、PR、Merge 或 Deploy 获授权。
- 当前 Agent 不支持图片输出时，只能交付标记清楚的文字设计方案，不得冒充已生成图片。
- 先读取既有设计基线，不擅自替换已确认风格、信息架构或真实数据来源。小改动仅增量更新。

## 完成标准

必须区分图片生成、图片归档、开发交接、视觉验收、Git 交付和部署状态；报告页面、设备、关键交互、素材来源及未验证事项。未执行浏览器测试不得声称已完成视觉实现验收。
