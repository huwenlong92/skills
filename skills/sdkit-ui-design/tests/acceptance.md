# sdkit-ui-design V1 · 触发与边界验收矩阵

本矩阵是静态路由与后续真实 Agent 行为测试的共同基线。不能将本文件存在视为模型隐式触发通过。

| ID | 输入 | Primary | 预期行为 |
|---|---|---|---|
| U01 | 帮我设计一个新的后台工作台 UI | sdkit-ui-design | 输出视觉稿或受支持的设计媒介，不修改代码 |
| U02 | 根据已确认 Northstar Tasks PRD 设计任务列表页面 | sdkit-ui-design | Foundry 只提供已确认需求与决策 |
| U03 | 给现有页面补移动端设计 | sdkit-ui-design | 保留现有设计系统 |
| U04 | 设计表单错误与加载状态 | sdkit-ui-design | 交付交互状态，不编造业务规则 |
| U05 | 把设计稿交给 Codex 实现 | sdkit-ui-design | 输出目标、页面、素材、状态与验收 |
| U06 | 对比设计稿和实现截图 | sdkit-ui-design | 区分设计复核与真实浏览器验收 |
| U07 | 编写 Nuxt 业务页面 | sdbase-nuxtjs-portal（模板身份已验证） | sdkit-ui-design 不接管代码 |
| U08 | 修复 Flutter 页面编译错误 | sdbase-flutter-app（模板身份已验证） | 不触发纯 UI 设计 |
| U09 | 维护 Northstar Tasks PRD | foundry | 不误触发 sdkit-ui-design |
| U10 | 发布交互原型到 R2 | foundry（按目标仓库规则） | sdkit-ui-design 不接管发布 |
| U11 | 未指定设计媒介且环境无图像工具 | sdkit-ui-design | 提供可支持的设计说明并说明限制 |
| U12 | 只给一张设计图，要求实现真实 API | 技术栈 Skill | 不能从图片推断已确认 API 契约 |

## 验收门禁

1. Catalog 中 sdkit-ui-design 唯一、SKILL.md frontmatter 仅含 name/description。
2. 五个 references 可被相对链接解析；Reference 适用范围、正反例和完成标准完整。
3. Foundry 与 Orchestration 不出现双 Primary、自动提交越权或技术栈职责漂移。
4. 全仓 Manager validate --all、Markdown 链接检查、工程协议测试必须运行并保留退出码。
5. 真实 Codex / ChatGPT Web 隐式触发与误触发单独记录 PASS/FAIL/BLOCKED；没有实际模型证据时不能标记通过。
6. 不修改业务项目、R2、Runtime 或真实 Codex 全局配置。

设计交接专项必须覆盖已有设计稿、仅文字说明、图片工具实际成功生成三种来源；未执行真实模型调用时三种场景均保留 BLOCKED，不以静态测试替代。


## 自动归档静态场景矩阵

以下 A01–A10 是规则和静态测试验收对象，状态均为 STATIC_ONLY；尚未通过真实 ChatGPT/Agent 会话验收，不可据此声称隐式执行 PASS。

| ID | 输入/前提 | 必须执行 | 当前证据 |
|---|---|---|---|
| A01 | 唯一产品身份，当前项目已有有效保存授权，项目不存在 | 复用 slug，经服务器许可注册，重新 resolve/检查写权限，进入保存链路 | STATIC_ONLY |
| A02 | 两个合理项目候选或绑定冲突 | 先询问，禁止猜测与合并 | STATIC_ONLY |
| A03 | 已识别项目，但用户未授权保存 | 先询问，禁止注册或上传 | STATIC_ONLY |
| A04 | 同项目、同已确认任务范围连续设计 | 沿用有效授权，不逐张询问 | STATIC_ONLY |
| A05 | 切换项目、撤销或超原范围 | 重新确认，不跨项目继承 | STATIC_ONLY |
| A06 | 原图引用失效/无原字节 SHA-256 | BLOCKED，不截图替代、近似重绘或填造 | STATIC_ONLY |
| A07 | MinIO 提交与回读成功，无 Git 绑定 | ASSET_SAVED + GIT_HANDOFF_PENDING | STATIC_ONLY |
| A08 | MCP 未连接或无注册工具 | 报告不可保存/服务版本不支持，交操作者处理 | STATIC_ONLY |
| A09 | 无注册权限、项目冲突或无项目写权限 | 正确报告错误，停止，不自行扩权 | STATIC_ONLY |
| A10 | 接收/提交中断，结果不明 | 复用原 upload_id，通过 status/recover 核验，不重复版本 | STATIC_ONLY |

真实行为验收必须另行观察：宿主项目定位是否实际可访问、用户授权是否可追溯、服务器是否认可注册与写权限、原生 fileParams 是否可用、原字节 SHA/Manifest/原图回读是否一致。未执行项必须保留待验证，不改变离线 ZIP 打包器、服务端 Schema 或 Git 独立授权。
