# Git 设计交接与 Revision

适用范围：已保存设计资产需要进入正式项目研发、修改现有 Git 设计基线、或进行设计 Revision 审计时读取。本规范处理 Git 交接，不替代 [MCP 设计资产交付](mcp-delivery.md) 的原始图片存储和授权读取。

- 设计资产允许在没有 Git 仓库时先保存 MinIO；此时必须报告资产版本已保存、`GIT_HANDOFF_PENDING`，不得宣称仓库归档完成。
- 准备实际修改项目 Git 前，必须通过 Foundry/目标仓库规范核验唯一项目身份、权威仓库与工作区、AGENTS.md、已有 DESIGN.md/设计目录、写入授权、dirty 状态及并行 PR/Worktree。身份不明、图片不可读、权限不足或同路径并发冲突时停止写入。
- 允许位置是目标项目已有设计目录；无目录规范时才可最小新增 `docs/design/DESIGN.md`。禁止擅自写业务源码、凭据、部署目录或另一个项目仓库。
- 交接记录必须包含稳定 Project/Page/Design ID、Design Revision、MCP Asset ID、已提交文件集版本、Manifest 引用与哈希、原图 SHA-256、素材授权读取办法、设计状态、实现模式、交互与响应式验收条件，以及未确认事项。未知字段明确标待验证。
- 相同 Design ID 与相同字节 SHA-256 必须复用资源引用；设计内容变化必须登记新的 Revision，不能覆盖历史。索引更新前后读回核验；并发版本变化时停止 last-writer-wins。
- Git 记录优先引用已在 MinIO 保存并通过授权回读的原图；只有项目明确要求时才在 Git 保存第二份原字节。缺少 Git 绑定不可伪造 `source_git`，不能以 MinIO vN 代替 Design Revision 或 Git Commit。
- Git Commit、Push、PR、Merge、部署和发布是独立授权动作；仅有资产上传或设计交接任务不授权这些动作。原型源码归档、版本和发布仍由 Foundry 管理。
- `production` 由技术栈 Skill 实现实际页面；`prototype` 是可运行交互原型路径；`undecided` 只保存设计说明，不自动创建业务或原型代码。

正向形态：MinIO 已保存 → 核验项目 Git 与 AGENTS → 引用可回读原图 → 记录 Design Revision 和验收 → 读回 Git 交接记录。反例：只有聊天内图片且没有 Git 仓库，却写入假的 Commit 和本机图片路径并宣布归档完成。

## 完成标准

分别报告 MinIO 保存/原图回读、Git 绑定与交接记录状态、Design Revision、接收 Agent 看图与代码/浏览器验收状态。未实际执行的环节不得标记 PASS；仓库写入后必须提供实际路径与读回证据。
