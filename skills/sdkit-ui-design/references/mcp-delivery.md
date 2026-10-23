# Design Delivery MCP V1 · 设计资产保存与交接

适用范围：用户授权通过 Design Delivery MCP 保存高保真原图、交互原型文件集，或将已保存资产交给 Codex 等 Agent 时读取。本文件只定义 Skill 工作流；接口 Schema、权限和存储以实际连接的 MCP 工具为准。

## 身份与授权

- 必须先确认项目 slug、稳定 page_id、artifact_type（high_fidelity/prototype）、设计身份及用户本次写入授权；不得从中文显示名猜测 ID，不得自动创建项目或授予权限。
- 必须先调用 `artifact_project_resolve` 获取唯一 `project_id`；返回 `PROJECT_BINDING_REQUIRED` 时停止上传并明确提示操作者登记项目。**项目 Git 仓库不是 MCP 保存前提**；没有 Git 绑定时允许已授权的 MinIO 保存，但必须提示 `GIT_HANDOFF_PENDING`，不得宣称完成 Git 归档。
- MCP 服务器必须独立校验 OAuth/Token 的项目读写权限；客户端 `authorized=true` 不代表权限已授予。未连接 MCP、缺原始图片引用、授权失败时停止，不制造 Asset ID、URL、SHA 或成功回执。

## 资产接收与回读

1. 必须从已确认的页面/主稿清单形成固定计划，保留 UTF-8 页面名、ASCII `page_id` 和版本内安全相对文件路径。文件 `bytes`、`sha256`、MIME、图片尺寸均以实际原始字节为准。
2. 正式文件集按 `artifact_begin(upload_id, authorized=true, plan)` → 每文件 `artifact_receive(project_id, upload_id, path, file 或 data_base64)` → `artifact_status` → `artifact_commit` 执行。ChatGPT 原生图片必须使用宿主提供的真实 `fileParams`，不得伪造 file ID、URL 或拿回复截图代替原图；接收失败不得提交。
3. 中断或提交结果不明时必须复用原 `upload_id`，通过 `artifact_status`、`artifact_recover` 核验，不另开上传制造重复版本。
4. 提交成功后调用 `artifact_list(project_id, artifact_type, version)` 取得完整 Manifest 与每文件 `access`；再使用其 `artifact_download` 参数在授权连接下读取。`mcp_url` 和 `catalog_path` 不是匿名公开下载地址。Codex 必须实际查看原图；仅看路径或自然语言描述不算读图验收。
5. 必须交接 `project_id`、`page_id`、`asset_id`、`artifact_type`、已提交 `version`、原图 `sha256`、Manifest 的可验证引用及哈希（若返回）、设计 `design_id/design_revision`、文件访问参数、已确认/待确认交互状态。无法取得的字段标记待核验，不得填占位值冒充事实。

`design_upload/list/get/download` 是旧单张图片接口，可用于单图保存与查询；其数字图片版本不等同于 `artifact_*` 文件集版本。正式设计版本/原型文件集使用 `artifact_*`。未接收 ZIP 的文件集接口不能直接上传 ZIP；离线 ZIP 由 [资产交付](asset-delivery.md) 的现有打包器处理，逐文件接收应另有明确文件清单。

## Git 与开发交接

- `ASSET_SAVED` 仅表示 MinIO 已提交不可变版本且字节、Manifest 可核验；不得由此推出 Git、PRD、代码或原型已归档。
- `GIT_HANDOFF_PENDING` 表示项目 Git 交接记录尚未完成。进行正式实现前必须通过 Foundry/目标仓库规则核验唯一项目位置、AGENTS.md、已有设计记录和写入权限，保存真实资产引用、Design Revision、交互及验收项；Git 的 Commit/Push/PR/Merge 各自独立授权，不要求把原图重复复制入 Git。
- `HANDOFF_VERIFIED` 必须有接收 Agent 对实际原图、设计身份及交接约束的读回证据；只看到 MinIO Manifest 不构成图像视觉验收。
- `production` 由技术栈 Skill 实现真实业务页面；`prototype` 由 Foundry 管理原型源码、版本和发布；`undecided` 只交付设计说明。静态设计图不能冒充可运行原型，MCP 文件集保存成功不等于原型行为通过。
- 设计稿版本、MCP Asset ID、MCP vN、Design Revision 和 Git Commit 必须独立标识。没有真实 `source_git` 时省略，禁止伪造仓库与 Commit。

正向形态：确认 slug/page_id 和授权 → resolve project_id → 原图接收并提交 vN → 列出版本 Manifest → 授权回读校验 → 交接真实 Asset ID/哈希 → 记录 Git 待关联或实际 Design Revision。反例：只有聊天图片缩略图，填造 SHA 和 Git Commit 后报告“已归档”。

## 完成标准

逐项报告资产保存、版本提交、授权原图回读、Git 交接及 Agent 实际看图的独立状态；任何未执行项不得标记 PASS。MCP 工具桥接未将回读图片嵌入 ChatGPT 回复时，不作为 V1 阻断条件，但不得声称回显已验证。禁止把测试环境成功推断为所有客户端与生产环境已通过。
