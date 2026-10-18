# PR #18 · ui-design V1 最终本地验收报告

适用范围：2026-10-18 对 `huwenlong92/skills` PR #18 的隔离集成验收。静态检查、离线回归、真实模型行为分别计数。

## 结论

**最终验收 BLOCKED，尚未达到最终技术可合并条件。** 本地修复与自动化回归通过；临时 Codex Home 未登录且无可用进程认证，依用户停止条件，未复制认证、未发起模型请求。U01–U12 全部 BLOCKED，不能用文档、测试字符串或当前聊天中的 Skill 名称代替真实原生选择证据。

保持 PR Draft/Open；不合并、不切换 Ready、不部署、不主动触发 CI。用户授权的普通 Push 可能按仓库既有设置产生自动工作流；本任务不调用 Actions 触发接口。

## Git 基线与协作核验

- main：`8b22285aa2abba995e88f49718800c167c7e2413`。
- 开始及写入前 PR #18 Head：`5983179b279dcc8c75b62c43bb19962c6580e316`，Draft/Open、MERGEABLE。
- 修复 Commit：`f3a5716c7b3db16edbf788d8afc2a17f276b17c8`。
- **最终 Head SHA 定位**：包含本报告的验收提交为本轮交付 tip；在该提交执行 `git rev-parse HEAD`，或对本轮报告执行 `git log -1 --format=%H -- docs/testing/ui-design-v1/REPORT.md` 得到完整 SHA，并与 GitHub `gh pr view 18 --repo huwenlong92/skills --json headRefOid` 核对。提交不能在自身正文内嵌自身 SHA；最终推送后的完整 SHA、Draft/Open 和 mergeable 由交付时实时查询并在最终回复给出，不将起始 Head 冒充最终 Head。
- 隔离 Worktree 使用独立本地分支，普通 Fetch main 与目标分支；main 已为祖先，`git merge-base --is-ancestor <main> HEAD` 退出 0，无需 Merge。未操作主工作区的 `docs/ideas/` 或已有 Worktree。
- [GitHub 快照](github-before-write.json)包含最新 SHA、状态、时间及完整文件集。#14–#17 均 Draft/Open，文件数量分别 14、36、12、10；#18 原始文件 11。四个 PR 与 #18 原始变更及本轮修复无同路径重叠。目录未重命名，完整文件列表未截断。
- #14 涉及发现/bootstrap 协议，#15/#16 涉及 Nuxt/Vab 技术栈规范，按共享接口关联 L1 审阅，不把无路径重叠等同于证明未来合并后全部语义兼容。未引入它们任何 Commit、脚本或规范修改。未来合并顺序改变时仍须重新验收。
- Push 前须再次读取 main、目标 Head 和相关 PR 状态；远端前进时禁止覆盖，必须重新整合和测试。最终交付状态以实际 GitHub 为准。

## 规范与兼容性审计（静态）

已读取根 AGENTS、Catalog、协作感知、Skill Orchestration、Development Execution、任务/决策/交接、Foundry 入口与 prototypes、ui-design 入口/README/全部五份 references/acceptance。

| 检查 | 结果与边界 |
|---|---|
| Catalog | 21 条，21 个实际目录与有效入口；ui-design 名称唯一、product 分类 |
| Frontmatter | ui-design 只含 name/description；描述覆盖视觉、布局、交互、响应式、复核和交接，排除业务代码、产品仓库管理与部署 |
| Foundry/UI | 纯设计唯一 Primary 为 ui-design，已有确认需求可由 Foundry Supporting；文档规范管理、可操作原型和发布仍为 Foundry，不存在静态双 Primary 规则 |
| 正式实现 | Nuxt/Flutter/Vab 等已核实模板身份的技术栈 Skill 主导；不能仅凭文件后缀套用模板 |
| 职责 | ui-design 引用目标发布协议，不承担 Git、R2、Runtime、数据库或工程计划执行；设计交付不授权这些操作 |
| 独立使用 | 五份 Reference 无个人绝对路径或 Product Docs 强制读取；交接不再强制依赖未提供的 Development Execution，必要工程规则缺失只停止受影响实现 |
| Reference 质量 | 五份均有开头适用范围、正反例、结尾可核验完成标准；Token 优先规则紧接缺少 Token 的退回条件；路径放置限定目标规范/用户授权，禁止猜测目录 |
| 高风险边界 | 图片产物声明需成功结果与可访问性核验；未经核实资源保持缺失；发布/工程操作交还实际规则，不引入发布执行流程 |
| Foundry 保留能力 | 规划、PRD、研究、项目路由、初始化/导入、原型及发布分流保留；prototypes、Workspace、Git、发布 references 与原始 Head 逐字节不变 |
| 新旧入口 | Nuxt/Vab 主入口与旧兼容入口、全部既有技术栈文件与原始 Head 相同；迁移 7 项回归包含在 Manager 44 项中 |

Foundry 的原有 PRD/路由/原型/发布能力仅通过规则与文件完整性审阅；真实执行兼容性仍未验证。普通项目不接 Product Docs 的能力同样仅完成静态独立性检查。既有 Foundry README 根仓库导航限制并非本轮新增，未借此重构。

## 自动化命令与结果（真实本地执行，非模型）

所有命令从隔离 Worktree 根执行。完整命令数组、退出码、数量和输出见 [最终本地结果](local-results.json)；初始结果见 [基线结果](baseline-results.json)。

| 实际命令 | 测试数 | 通过 | 失败 | 退出码 |
|---|---:|---:|---:|---:|
| `python3 -m unittest discover -s scripts -p 'test_engineering_protocols.py' -v` | 17 | 17 | 0 | 0 |
| `python3 -m unittest discover -s skills/sdkit-skills/scripts -p 'test_*.py' -v` | 44 | 44 | 0 | 0 |
| `python3 -m unittest discover -s skills/dockerops/scripts -p 'test_*.py' -v` | 41 | 41 | 0 | 0 |
| `python3 -m unittest discover -s scripts -p 'test_markdown_links.py' -v` | 7 | 7 | 0 | 0 |
| `python3 -m unittest discover -s scripts -p 'test_ui_design.py' -v` | 8 | 8 | 0 | 0 |
| 合计（不重复计迁移子集） | 117 | 117 | 0 | 0 |
| `python3 skills/sdkit-skills/scripts/manager.py validate --all` | 21 Skill | 21 | 0 | 0 |
| `python3 scripts/check_markdown_links.py` | Markdown | Markdown: 265 files, 918 relative links, 2 anchors, 0 errors | 0 | 0 |
| `git diff --check` | 差异格式 | 通过 | 0 | 0 |

Manager 的 `test_migration.py` 七项确由 discover 实际执行，覆盖新旧入口、详细规则保留、独立安装/更新和互不覆盖；不作为额外七项重复计数。未使用不存在的入口。

四个候选 Skill（ui-design、foundry、sdbase-nuxtjs-portal、sdbase-flutter-app）仅安装到临时 home 的 skills 目录；[安装证据](isolated-install.json)记录命令初次因目标父目录不存在退出 1，显式创建该专用父目录后四次均退出 0，未覆盖任何既有目录。ui-design 独立安装/更新哈希与目录一致性还由定向回归验证。

## 修复与失败证据

- 明确完整交接十项信息、缺失项标记、三种设计来源及实际图片工具成功验证；规定允许/禁止的交接落点。
- 将未声明工程协议依赖改成按目标项目实际可用协议执行；规则缺失不得继续受影响实现。
- 两处“应”改成“必须”，验收矩阵示例统一为虚构 Northstar Tasks，保留全部 12 场景和原有判定标准。
- 新增 8 项离线契约回归。同一测试集指向原始 Git 对象导出的隔离源码时：8 项中 4 通过、4 失败（15 个失败子断言，0 errors），退出 1；修复后 8/8 通过。见 [修复前证据](regression-before.json)。没有删除失败场景或降低断言；这些是文档契约失败，不能描述成真实模型失败。

## 隔离与认证预检

临时目录结构：`<temp>/codex-home`、`fixtures`、`outputs`、`evidence`；独立 Worktree 不在真实业务项目。CLI 为 0.163.0。

实际 `CODEX_HOME=<temp>/codex-home codex login status` 退出 1，stderr 为 `Not logged in`；OPENAI_API_KEY、CODEX_API_KEY、CODEX_ACCESS_TOKEN 均不存在。仅检查宿主配置的认证机制字段并输出布尔值/机制类别，未输出配置内容或复制到夹具/证据。内置 provider、默认存储未给临时 home 提供可用登录。见 [认证预检](auth-preflight.json)。

**模型调用 0，成功 0，模型服务连接尝试 0；没有虚构模型型号或网络失败。** 阻塞发生于认证前置条件，不是模型拒绝，也不是审批拒绝。没有读取/复制真实认证文件，没有发起登录或要求用户交出密钥。

依据 [OpenAI 认证文档](https://learn.chatgpt.com/docs/auth)和[安全文档](https://learn.chatgpt.com/docs/security)核对机制；临时 CODEX_HOME 仅隔离配置，不等同于限制全部文件读取。夹具有禁止外部文件、环境、认证、网络、MCP、Git 远端与发布的规则；认证预检停止后未启动模型，OS 读取边界探针及真实模型文件访问边界尚未验证。恢复时必须先建立可验证的只读隔离边界并检查不加载宿主 Skill/插件，再运行模型；不得凭临时 home 存在就声称隔离通过。

## U01–U12 真实模型结果

[场景材料](scenarios.json)保存每项完整实际准备输入、夹具内容、预期 Primary/Reference、运行状态、选择观察字段。**这些输入尚未发送给模型。** 以下 Primary 均是预期，非实际选择。所有场景模型成功运行为否，实际 Primary/Supporting、适用文件加载、输出符合性、无关 Skill、越权行为均为“未执行，无法判断”；不是 PASS，也没有可声称的原生加载记录。

| ID | 准备输入摘要 | 预期 Primary / Supporting | 结果 |
|---|---|---|---|
| U01 | 虚构 SaaS 后台工作台 | ui-design | BLOCKED：认证 |
| U02 | 按本地虚构 PRD 设计页面 | ui-design；Foundry 仅上下文 | BLOCKED：认证 |
| U03 | 现有页面移动端设计 | ui-design；保留设计系统 | BLOCKED：认证 |
| U04 | 表单加载/错误/成功等状态 | ui-design；未知业务规则待确认 | BLOCKED：认证 |
| U05 | Northstar Tasks 完整开发交接 | ui-design；工程实现交技术栈 | BLOCKED：认证 |
| U06 | 设计与实现截图差异 | ui-design；仅有证据的差异 | BLOCKED：认证；目前为合成 SVG 源，实际截图及视觉工具读取尚未验证 |
| U07 | 直接开发 Nuxt 页面 | 经身份核验的技术栈 Skill | BLOCKED：认证；最小夹具不是完整模板克隆 |
| U08 | 修复 Flutter 编译错误 | 经身份核验的技术栈 Skill | BLOCKED：认证；未运行 Flutter 编译 |
| U09 | 维护产品 PRD | foundry | BLOCKED：认证 |
| U10 | 发布已有交互原型 | foundry / 目标仓库发布协议 | BLOCKED：认证；目标协议缺失应停止，禁止真实发布 |
| U11 | 无图像生成工具 | ui-design；文本媒介明确 | BLOCKED：认证 |
| U12 | 仅设计图要求真实 API | 技术栈 Skill；缺契约停止 | BLOCKED：认证 |

总计 **PASS 0 / FAIL 0 / BLOCKED 12**。实际模型加载 SKILL/Reference 记录不存在，不能由输出中出现名称推断原生发现。恢复时必须组合模型工具记录、真实读取文件与输出约束核验，保留未观察到的内部选择机制局限。此次没有模拟模型输出。

## U05 设计交接专项

虚构产品 Northstar Tasks，模块 tasks，TASK-LIST/TASK-CREATE，文本 PRD v0.1；标题/状态仅展示需求，权限、状态枚举、API、验证与并发均待确认。交付目标正式前端，不强制先写 HTML 原型。

静态规范已覆盖项目模块、交付类型、设计来源版本、页面 ID、交互状态、桌面手机、素材与未验证资源、已确认/未确认事项、实现边界、可执行验收十项；离线回归已核验。**实际模型生成交接及逐项内容验收全部未执行。**

| 子场景 | 实际准备材料 | 模型验收 |
|---|---|---|
| U05-A 已有设计稿 | 合成 `design.svg`，fixture-v1；需真实读取验证，不编造来源 SHA、Commit、Release、URL | BLOCKED |
| U05-B 仅文字 | 本地 design-reference.md；明确“尚无视觉稿” | BLOCKED |
| U05-C 实际图片生成 | 未提供假工具成功记录、未生成图片；恢复时须调用真实可用工具并核验可访问产物 | BLOCKED |

## 未验证项与恢复条件

真实 Codex 原生发现/隐式触发、12 场景路由与越权行为、完整三类交接、真实截图视觉对照、实际图片工具生成、Flutter/Nuxt 产品构建、操作系统文件读取边界、跨 Agent 行为以及 #14–#17 合并后的联合行为均未验证。没有真实业务 API、数据库或部署验证。

本轮交付仅为“本地回归通过、范围内修复已提交并按授权普通推送；模型验收被安全前置条件阻塞”。恢复必须具备不复制认证文件的已授权认证机制，并重新核验远端/文件隔离后执行原有全部场景，失败保留证据，不改变预期制造 PASS。保持 Draft/Open，等待后续验收与最终合并授权。
