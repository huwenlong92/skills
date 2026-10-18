# ui-design V1 · 触发与边界验收矩阵

本矩阵是静态路由与后续真实 Agent 行为测试的共同基线。不能将本文件存在视为模型隐式触发通过。

| ID | 输入 | Primary | 预期行为 |
|---|---|---|---|
| U01 | 帮我设计一个新的后台工作台 UI | ui-design | 输出视觉稿或受支持的设计媒介，不修改代码 |
| U02 | 根据已确认 Storyra PRD 设计创作页面 | ui-design | Foundry 只提供已确认需求与决策 |
| U03 | 给现有页面补移动端设计 | ui-design | 保留现有设计系统 |
| U04 | 设计表单错误与加载状态 | ui-design | 交付交互状态，不编造业务规则 |
| U05 | 把设计稿交给 Codex 实现 | ui-design | 输出目标、页面、素材、状态与验收 |
| U06 | 对比设计稿和实现截图 | ui-design | 区分设计复核与真实浏览器验收 |
| U07 | 编写 Nuxt 业务页面 | sdbase-nuxtjs-portal（模板身份已验证） | ui-design 不接管代码 |
| U08 | 修复 Flutter 页面编译错误 | sdbase-flutter-app（模板身份已验证） | 不触发纯 UI 设计 |
| U09 | 维护 Oranzy PRD | foundry | 不误触发 ui-design |
| U10 | 发布交互原型到 R2 | foundry（按目标仓库规则） | ui-design 不接管发布 |
| U11 | 未指定设计媒介且环境无图像工具 | ui-design | 提供可支持的设计说明并说明限制 |
| U12 | 只给一张设计图，要求实现真实 API | 技术栈 Skill | 不能从图片推断已确认 API 契约 |

## 验收门禁

1. Catalog 中 ui-design 唯一、SKILL.md frontmatter 仅含 name/description。
2. 五个 references 可被相对链接解析；Reference 适用范围、正反例和完成标准完整。
3. Foundry 与 Orchestration 不出现双 Primary、自动提交越权或技术栈职责漂移。
4. 全仓 Manager validate --all、Markdown 链接检查、工程协议测试必须运行并保留退出码。
5. 真实 Codex / ChatGPT Web 隐式触发与误触发单独记录 PASS/FAIL/BLOCKED；没有实际模型证据时不能标记通过。
6. 不修改业务项目、R2、Runtime 或真实 Codex 全局配置。
