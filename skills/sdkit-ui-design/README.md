# sdkit-ui-design

跨项目 UI 设计与开发交接 Skill V1。处理高保真设计图、交互原型设计、资产交付、设计修订与复核；正式实现由技术栈 Skill 负责，原型源码与发布由 Foundry 管理。

## 使用场景

- “设计一个后台工作台的桌面和移动端页面”
- “根据已有产品 PRD 出一套 UI 设计稿”
- “把这份设计稿整理为 Codex 可执行的交接说明”
- “对比实现截图与设计基线，指出差异”

仅请求编写 Nuxt/Vue/Flutter 代码时使用对应技术栈 Skill；仅请求产品规划或原型发布时使用 Foundry。

## 入口

从 [SKILL.md](SKILL.md) 选择任务对应的 references。无需个人配置；离线 PNG/Manifest/ZIP 校验使用随附 Python 标准库脚本，见 [资产交付](references/asset-delivery.md)。图片生成能力由当前 Agent 的可用工具决定，Skill 本身不提供图片引擎。

## 保存与开发交接

经授权的 MinIO 原图保存按 [MCP 设计资产交付](references/mcp-delivery.md) 执行，不要求 Git 仓库；未绑定时必须标记 `GIT_HANDOFF_PENDING`。正式开发前必须按 [Git 设计交接](references/git-handoff.md) 核验项目、真实原图与 Design ID/Revision、SHA-256，增量更新设计记录并读回；原图可保留 MinIO。图片不可读、项目身份不明、无写入授权或并发冲突时必须报告 BLOCKED；只读讨论禁止归档写入。

`production` 进入技术栈正式开发；`prototype` 进入 Foundry/目标仓库原型流程；`undecided` 只保存设计和说明。保存与交接不授权 Commit、Push、PR、Merge 或部署。必须分别报告静态测试、真实文件校验、Codex 行为与浏览器验收，未执行项不得标为通过。

## 交付

默认一份设计稿及简洁设计说明；复杂任务才增加页面清单、交互状态和素材清单。所有路径和存储位置由实际项目规范决定，不假定固定本机目录。
