# Design Delivery MCP → SDKit UI Design：总控协调交接

状态：**存储 PoC 已验证 / 正式契约与 Skill 对接待总控安排**。更新：2026-10-22。

本文件供 Skill 总控阅读与分派，只记录现有能力、真实证据、用户确认的范围和待办；不修改 Skill 行为、Catalog、业务代码、安装配置或发布系统。此交接不授权合并相关 PR，也不构成新的存储写入或部署授权。

## 先读实现仓库与证据

用户明确要求向总控提供实现仓库。以下链接指向 **Private 仓库**，读取者需要已有访问权限；无权限时必须报告缺口，禁止把链接存在当作已读证据。本公开交接不包含运行 Endpoint、服务器、Bucket、凭据、本机路径、原图或签名 URL。

| 内容 | 权威入口 |
|---|---|
| MCP 实现仓库 | [huwenlong92/sdkit-design-delivery](https://github.com/huwenlong92/sdkit-design-delivery) |
| 本次已交付基线 | [06f39822625b623d3c3fc2827a83b13e5e951c20](https://github.com/huwenlong92/sdkit-design-delivery/commit/06f39822625b623d3c3fc2827a83b13e5e951c20) |
| 当前能力说明 | [固定基线 README](https://github.com/huwenlong92/sdkit-design-delivery/blob/06f39822625b623d3c3fc2827a83b13e5e951c20/README.md) |
| ChatGPT/Codex 接入 | [固定基线接入手册](https://github.com/huwenlong92/sdkit-design-delivery/blob/06f39822625b623d3c3fc2827a83b13e5e951c20/docs/client-setup.md) |
| 图片与客户端验收 | [固定基线测试记录](https://github.com/huwenlong92/sdkit-design-delivery/blob/06f39822625b623d3c3fc2827a83b13e5e951c20/docs/testing.md) |
| 分层 manifest / 中文 / 原型落存储验证 | [artifact-layout-poc.md](https://github.com/huwenlong92/sdkit-design-delivery/blob/06f39822625b623d3c3fc2827a83b13e5e951c20/docs/artifact-layout-poc.md) |
| 可复现真实 S3 验证脚本 | [artifact-layout.integration.ts](https://github.com/huwenlong92/sdkit-design-delivery/blob/06f39822625b623d3c3fc2827a83b13e5e951c20/test/artifact-layout.integration.ts) |

以上为当时真实提交；开始后续实现时必须重新核验该仓库最新 main、AGENTS.md、工作区与相关 PR，不能直接覆盖后续变更。MinIO 是已验证的首个后端，代码使用 AWS S3 SDK；SeaweedFS 接入尚未实测，不标 PASS。

## 用户已确认的目标和本轮边界

- 本服务只保存 **UI 设计稿与 UI 交互原型产物**，维护项目编号、文件清单和版本索引；不管理 PRD、业务源码开发任务或产品权限体系。
- 一个可配置的私有 S3 兼容 Bucket，多项目通过目录分类；每个项目有稳定、唯一的 project_id。编号生成方式与正式字段格式尚未冻结，不把试验 UUID 当作强制规则。
- 项目外层有总目录；项目内部设计稿与原型分别维护版本总索引，各版本有独立明细 manifest；历史版本保留，默认版本显式指定。
- 中文目录与中文内容必须有明确编码策略和回读验证，禁止默默转码或猜测名称。
- `ui.sdkit.cn` 是后续消费展示方，**本轮暂不接入，也不作为当前验收条件**。
- 用户当前要求先验证按规则落 MinIO。该存储 PoC 已完成；后续正式 MCP / Skill 对接由总控分派，不在本 PR 偷跑实现。

以下为结构示例，`example-app` 不是实际业务项目，路径均相对配置的 catalog 根：

```text
manifest.json
example-app/
├─ manifest.json
├─ 设计稿/
│  ├─ manifest.json
│  └─ v1/
│     ├─ manifest.json
│     └─ 图片文件
└─ 原型/
   ├─ manifest.json
   └─ v1/
      ├─ manifest.json
      ├─ index.html
      └─ assets/
```

正式 catalog 根是否直接位于 Bucket 根，或使用可配置前缀，仍须总控与 MCP 实现侧确定；已通过的试验是在全新隔离前缀模拟 Bucket 根，没有修改真实根索引。不能将试验写入范围当成正式部署权限。

## MCP 现在真实具备的能力

当前正式代码契约仍是图片工具；以下“已实现”指实现与已记录测试事实，不宣称所有宿主/历史图片都成功。

| MCP Tool | 当前输入与行为 |
|---|---|
| design_upload | 明确 project、page、用户上传授权；PNG/JPEG/WebP；file 或 data_base64 二选一；返回稳定 Asset ID、页面递增版本、尺寸/字节数/SHA-256 和授权读取方法 |
| design_list | 按 project、可选 page 分页查询图片版本 |
| design_get | 按 project、asset_id 获取元数据 |
| design_download | 返回元数据及原始 MCP image 字节，Codex 能实际看图，不只是获取 URL |

其他已实现内容：Streamable HTTP、OAuth、ChatGPT 文件参数 openai/fileParams、私有 S3、服务端凭据隔离、路径/MIME/大小校验、原字节与哈希校验、不可覆盖图片历史；连接授权记录、撤销与失效记录删除。没有设计资产删除工具，也没有原型上传/发布工具。

实际已验证：13 组本地测试及检查/构建；真实隔离 MinIO 图片上传回读；ChatGPT 原生生成图和单张历史原图直传；独立 Codex OAuth 登录并实际读取图片。用户附件直接 fileParams 曾失败，任意历史图恢复未保证；新版无密码 ChatGPT 授权 UI 与撤销后的宿主即时重新授权提示仍有待验证项，详情以测试记录为准。

**兼容性缺口**：当前图片工具使用旧图片存储布局和逐页面版本，尚未使用上面的项目/产物全局版本目录。它要求明确 project/page，不能把 project_id 注册、catalog 注册或 v1 全产品版本视为已有接口。后续必须设计兼容或迁移策略，禁止重排旧对象、破坏已有 Asset ID 或让旧图片凭据失效。

## MinIO PoC 证明了什么

真实 SDK 集成已验证 14 个对象：项目总索引、项目入口、两类产物索引、设计稿 v1/v2/v3、静态原型 v1（HTML/CSS/JS）及版本明细。

- 正常读取只沿 manifest 定位到文件；最后一次限定前缀 LIST 仅作审计，不作为每次查询的前置步骤。
- 中文 S3 键、中文文件名、UTF-8 JSON/HTML/JS 回读完整，Content-Type 与 SHA-256 一致；不经过 ZIP。
- 相同 ETag 的并发索引更新恰有一个先成功；另一个显式冲突，重读合并再试后保留两个版本。旧 ETag 与覆盖原文件被拒，匿名读取被拒。
- 同一 project_id 贯穿各层；设计和原型版本分别维护，原型明细记录入口及关联设计版本。

**未证明**：正式 MCP 能接收原型、ChatGPT 能直接交接原型包、Skill 已调用新接口、浏览器原型行为、UI 站可展示、ZIP 中文路径、SeaweedFS、崩溃恢复、跨项目注册竞争或自动索引修复。schema_version 为 artifact-layout-poc/1，属于试验，不是已冻结生产协议。

## 与现有 UI Design PR 的衔接

2026-10-22 实时读到以下两个 OPEN Draft；总控接手必须重新核对状态和 head。本交接不修改、合并或替代它们。

| PR | 已读 head 与范围 | 总控需要协调 |
|---|---|---|
| [#22：设计基线归档与 Codex 交接](https://github.com/huwenlong92/skills/pull/22) | ca3fb209ea8a19853bcca4b16d927b0fb0cfb347；baseline、handoff、review 及静态检查 | 本地设计基线/修订与远程 Asset ID、产物版本如何关联；避免重复权威 |
| [#33：高保真与原型工作流、资产交付](https://github.com/huwenlong92/skills/pull/33) | 4913e44f1399b795a3da9ce3aa51d06ce639186b；高保真、原型、资产 reference 与离线打包器 | 复用离线资产清单、page_id、主稿状态；不能把现有 PNG/ZIP 打包器当作原型构建或 MCP 上传器 |

需要显式处理的契约差异：

1. #33 使用 high_fidelity、assets、path_base 等离线资产字段，PoC 使用 files/产物目录与分层索引；总控须确定规范化模型或映射，不让两边各自生成不一致的 manifest。
2. #33 约束 ZIP 内路径为 ASCII，中文名称保存在 UTF-8 JSON；存储 PoC 验证的是中文 S3 目录与文件键。两者不是同一层规则，禁止把 S3 中文成功推导为任意 ZIP 中文路径兼容。若保留可携带 ASCII 文件包，需要明确包路径到存储前缀的映射。
3. #22 的项目内归档、Foundry 的源码/Git/发布职责与远程对象存储职责要分别保留。MCP 保存原型产物不等于接管产品源码或部署；sdkit-ui-design 不因对接 MCP 而获得业务仓库写入或存储写入授权。
4. 当前通用 Skill 禁止硬编码业务仓库、个人路径或凭据。正式接入时服务连接由客户端 MCP 配置提供，本交接的仓库定位信息不复制进通用 Skill reference。

## 建议总控安排的最小下一轮

以下是待总控确认的分派建议，不表示已执行，也不授权 UI 站改造。

### 1. 冻结最小交付契约

共同确定 project_id/slug/page_id、设计稿版本与原型版本、入口文件、相对路径、文件哈希与大小、状态/默认版本、设计与原型关联，以及各层 manifest 的单一权威。明确元数据输入来自设计交接，真实路径/字节/哈希由服务核验；不能让模型伪造文件 ID、签名 URL 或 SHA-256。

### 2. MCP 仓库补齐正式能力

在实现仓库安排原型文件集接收、项目与版本索引、条件更新、完整性检查和兼容旧图片接口。正式工具名称、输入输出及幂等/失败恢复先定契约；当前不存在的工具禁止提前写成可调用。检查路径穿越、文件数量/大小/MIME、包结构、项目权限、原型入口相对资源、并发冲突与不完整版本不可见。原型上传只保存产物，不执行上传的脚本，不借此公开 Bucket 或部署 UI。

### 3. 再更新 sdkit-ui-design 并联调

在可调用接口和能力发现已实测后，增量接入已确认契约；需要明确项目编号、目标产物/版本和用户写入授权，沿用真实文件引用。sdkit-ui-design 负责视觉/交互定义、主稿与交接约束，原型代码实现仍服从目标技术栈；Foundry 与目标仓库保留源码归档/Git/发布职责。真实联调分别验证设计稿与原型交接，不用 SDK 成功代替 ChatGPT 成功。

### 4. 当前明确延后

ui.sdkit.cn、门户消费、生产部署、全量旧资产迁移、多租户、无关管理能力均不作为这一轮目标。SeaweedFS 仅保留 S3 兼容方向，实际版本需独立验收。

## 总控接收与完成标准

- 能定位 MCP 仓库、固定证据与当前接口，并区分图片已实现、SDK PoC PASS、正式 MCP/Skill 待实现、宿主待验证。
- 重新核验 #22/#33 及 MCP 最新状态，输出各自责任、契约差异与实施顺序；不得重复开发另一套打包器或目录索引。
- 本 PR 仅文档交接，保持 Draft，不合并、不安装/更新本地 Skill、不更改业务仓库或执行存储/部署操作。
- 后续实现必须分别提交真实测试证据；UI 站继续延后，未验证的链路不得标 PASS。

Collaboration-Affects: sdkit-ui-design, foundry, design-delivery-mcp
Collaboration-Protocol: design-delivery-handoff-draft
