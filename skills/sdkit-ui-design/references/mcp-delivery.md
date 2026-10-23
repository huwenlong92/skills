# Design Delivery MCP V1 · 设计资产保存与交接

适用范围：用户授权通过 Design Delivery MCP 保存高保真原图、交互原型文件集，或将已保存资产交给 Codex 等 Agent 时读取。本文件只定义 Skill 工作流；接口 Schema、权限和存储以实际连接的 MCP 工具为准。

## 项目识别与状态

必须按以下顺序解析项目，并保留已确认的身份依据：

1. 用户明确指定的项目标识。
2. 当前会话已确认的项目身份。
3. 当前 ChatGPT 项目的唯一业务产品身份。
4. 已核验的既有项目绑定。

高优先级身份唯一且与已核验绑定不冲突时必须直接使用，不要求用户重复输入。项目身份存在多个合理候选、绑定相互冲突或无法取得唯一 slug 时必须询问，不得猜测。当前 ChatGPT 项目的身份必须来自实际可访问且已确认的产品上下文，不得假定宿主自动提供隐藏项目资料。不能仅凭相似名称、目录名称或聊天标题自动合并两个项目；只有已确认的产品名本身是合法 slug 或具有已核验的唯一名称—slug 绑定时，才允许直接复用；只有中文显示名而无唯一 slug 绑定时必须询问绑定。

| 状态 | 必须具备的证据 |
|---|---|
| PROJECT_IDENTIFIED | 项目唯一，已确认 slug，绑定不冲突 |
| REGISTRATION_AUTHORIZED | 服务器当前具体连接允许该项目注册；工具发现不等于权限 |
| SAVE_AUTHORIZED | 用户明确允许当前项目、当前已确认任务范围内保存设计资产 |
| ASSET_SAVED | 文件集已真实提交，原字节、Manifest 与授权回读已核验 |
| GIT_HANDOFF_PENDING | Git 设计交接尚未完成，不能声称 Git 已归档 |

这些状态必须独立报告。项目 Git 仓库不是 MCP 保存前提；没有 Git 绑定时允许已授权的 MinIO 保存，成功后必须提示 GIT_HANDOFF_PENDING，不得宣称完成 Git 归档。

## 保存授权与自动注册

- 未获 SAVE_AUTHORIZED 时必须先询问，禁止先注册或上传再补问。用户已授权当前项目持续保存设计资产时，必须在同一项目、同一已确认任务范围内连续使用该授权，不逐张询问；这只省略重复询问，不省略服务端每次权限验证。
- 必须保留授权目标与范围依据。切换项目、撤销授权、授权失效或明显超出原授权范围时，必须重新确认；持续保存授权不能跨项目自动继承。只读讨论不授权注册、保存或 Git 写入。
- 必须先调用 artifact_project_resolve 获取唯一 project_id；项目存在则复用。FORBIDDEN/UNAUTHORIZED 不能解释为项目不存在。已有 legacy 项目或待绑定身份必须交操作者处理，不得用注册绕过绑定或接管历史项目。
- 只有项目已唯一确认、保存授权有效且服务提供 artifact_project_register 时，才允许为缺失项目调用该工具，并依据用户有效授权填写 authorized:true；只提交当前工具实际支持的身份与操作字段，source_repository 可省略，不伪造 project_id、source_git 或注册策略。项目是否可创建、幂等及冲突以服务器真实结果为准，不将 PROJECT_BINDING_REQUIRED 本身当成已证明可以创建。
- 注册能力必须来自服务器已验证的具体授权记录及策略；通用注册可免逐项目白名单，既有精确策略仍以实际服务结果为准。注册权限不代表保存授权，不代表项目读写权限；普通 design:write、write:*、客户端 authorized=true 或列出注册工具都不能作为注册能力证据。没有权限预检工具时，不得编造已读取服务器策略；必须根据实际调用结果确认或报告权限不足。
- 注册成功必须保存真实稳定 project_id，重新 resolve 核验，并检查当前项目写权限；无写权限时必须停止上传、请求操作者另行授权，不自行扩大 Grants。注册不创建资产、版本或 Manifest。MCP 服务器必须独立校验 OAuth/Token，客户端禁止提交自报 Grants。
- 接口 Schema、注册策略、身份幂等与权限规则以实际工具和服务仓库为权威；本 Skill 不复制服务端 Schema、IAM 或配置文件，不代替服务器实现授权。

## 客户端降级

| 条件 | 必须执行 |
|---|---|
| MCP 未连接 | 报告不可保存，停止写入 |
| 缺失 artifact_project_register | 提示当前服务版本不支持自动注册，交操作者处理 |
| REGISTRATION_PERMISSION_REQUIRED（含无通用且精确策略不覆盖） | 报告注册权限不足，禁止匿名降级或自行扩权 |
| PROJECT_REGISTRATION_CONFLICT / LEGACY_BINDING_REQUIRED | 停止并询问或请求操作者处理，禁止覆盖/接管 |
| 无项目写权限 / PROJECT_AUTHORIZATION_REQUIRED | 停止上传，单独请求项目授权 |
| 原图引用失效或原字节不可访问 | BLOCKED，停止；禁止近似重绘、截图替代或虚构成功回执 |
| 用户未授权保存 | 先询问；不能以服务器能力代替用户授权 |

## 资产接收与回读

1. 每个页面必须保留独立文件，禁止以多页拼接图替代原页面资产。静态设计稿使用 high_fidelity，可运行原型使用 prototype，不能混淆。必须从已确认的页面/主稿清单形成固定计划，保留 UTF-8 页面名、ASCII `page_id` 和版本内安全相对文件路径。文件 `bytes`、`sha256`、MIME、图片尺寸均以实际原始字节为准。
2. 正式文件集按 `artifact_begin(upload_id, authorized=true, plan)` → 每文件 `artifact_receive(project_id, upload_id, path, file 或 data_base64)` → `artifact_status` → `artifact_commit` 执行。ChatGPT 原生图片必须使用宿主提供的真实 `fileParams`，不得伪造 file ID、URL 或拿回复截图代替原图；宿主不保证必然提供可用原图引用；原字节 SHA-256 或来源引用无法取得时必须停止，不得填造。接收失败不得提交。
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

正向形态：从唯一已确认产品身份复用 slug/page_id 与有效保存授权 → resolve project_id → 缺失时按服务器许可注册并重新 resolve → 核验项目写权限 → artifact_begin → artifact_receive → artifact_status → artifact_commit → artifact_list → artifact_download → 核验原图与 Manifest → 交接真实 Asset ID/哈希 → 记录 Git 待关联或实际 Design Revision。反例：只有聊天图片缩略图，填造 SHA 和 Git Commit 后报告“已归档”。

## 完成标准

逐项报告项目识别、注册权限、保存授权、资产保存、版本提交、授权原图回读、Git 交接及 Agent 实际看图的独立状态；任何未执行项不得标记 PASS。MCP 工具桥接未将回读图片嵌入 ChatGPT 回复时，不作为 V1 阻断条件，但不得声称回显已验证。禁止把测试环境成功推断为所有客户端与生产环境已通过。
