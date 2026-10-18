# PR #19 本地验收报告

日期：2026-10-18。结果：**16/16 真实行为场景通过；首轮 15/16，修复后定向回归 3/3，另完成十轮沙箱继承补测**。

## 基线、安全与并行修改

- 原始 Head：`5f4734606f68402941e17b1bac01f0a239171152`；main：`8b22285aa2abba995e88f49718800c167c7e2413`，已经是 Head 祖先，无需合入 main。
- 在新建的独立 detached Worktree 中操作；原工作区的既有未跟踪 `docs/ideas/` 保留。未修改其他 Worktree 或真实产品、知识仓库。
- 已读取 main/Head 的 AGENTS.md、Skill Orchestration、Knowledge Retrieval & Capture、Development Execution、协作感知，以及命中 Skill/references。
- #14 Head `50ba0de9d26d1b471068607ec4a5e11ce6274b9e`：与 #19 同改 AGENTS.md，属于 L2。Bootstrap 与知识路由入口职责兼容；只读 merge-tree 未发现文本冲突。没有合入 #14。
- #18 初检 Head `5bb812edb747d1afc716c12f25a7a776cb66c8cd`；Push 前发现前进到 `ad8914562ebf2b9228c43b35b4f8383414609234`，已重读其 changed files 与共享文件差异：仅验收证据/交接前进，Foundry SKILL.md 与 skill-orchestration.md 未变。以新 Head 再次只读三路核验，结论如下：与 #19 同改 Foundry SKILL.md 和 skill-orchestration.md，属于 L2。UI Primary 与知识检索 Supporting 职责可共存，但 Foundry description 同一行存在真实文本冲突；选路协议只读分析可自动合并。基于当前本地文件再次用 merge-file --stdout 只读比较，还发现 STATUS/HANDOFF/TASKS/DECISIONS 四份共享交接文件存在文本冲突。没有将 #18 的 UI 路由或新 Skill 放入 #19；将来二者集成时必须保留两任务记录、处理 description 并复验。

## 静态检查

实际执行以下命令，完整退出状态与最终统计见 [结果数据](results.json)：

```sh
python3 skills/sdkit-skills/scripts/manager.py validate --all
python3 -m unittest discover -s skills/sdkit-skills/scripts -p 'test_*.py' -v
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/check_markdown_links.py
git diff --check
```

首次检查：20 Skill；44 项管理/迁移测试；24 项协议/Markdown 工具测试全部通过。首次全仓 Markdown：259 文件、915 相对链接、2 锚点、0 错误，包含 `.sdkit/`。Catalog、目录与 frontmatter 身份一致，且 Skill frontmatter 仅含 name/description。最终复测同样通过：20 Skill、44+24=68 项单元测试；261 Markdown 文件、945 相对链接、2 锚点、0 错误；diff --check 退出 0。

敏感信息检查覆盖全仓已跟踪文本及本次新增证据，另人工核对变更与模型命令。个人绝对路径、私钥头、GitHub Token/OpenAI Key 模式无真实命中；检查不能证明任意未知格式秘密均可被自动识别。公开专用 Skill 原有仓库定位不属于凭据，未添加业务文档或个人配置。

## 真实 Codex 行为

CLI `0.163.0`；请求模型与隔离会话 `turn_context.model` 均为 `gpt-6.1-sol`。服务未提供不可变模型修订号，不推断后台版本。

使用脚本生成的 LumaNote/星笺产品资料、缓存笔记和虚构 Git 仓库；未检索真实 product-docs/Wiki，也未将真实私有正文送往模型。两个 Skill 从本次源码复制到夹具原生 `.agents/skills/`，场景提示不点名 Skill。项目 AGENTS 提供协议入口和显式虚构 Active Workspace；实际加载按 SKILL/reference 的读取命令认定，不能仅凭模型自述。

首轮 16 个场景共 25 轮真实调用，使用只读沙箱。第 7 项主要结论正确，但重复拉取三份有效正文，综合判失败，首轮 **15/16**。保留全部 [首轮证据](first-run/C07.json)。修复后定向重测 7/13/16 均通过，但最终元数据审查发现原第 13 项续接九轮实际回退 read-only，不能算完整可写环境验收。修正运行器，为 exec resume 的父命令也显式传 --sandbox，再从新会话完整补跑十轮。补测每轮 turn_context 都为 workspace-write，新增用户确认的登录提示决策；第 2–10 轮零工具调用，最后只输出一个合并候选摘要。C07/C16 也已核实实际为 workspace-write。

共 47 个场景模型调用退出 0 且 turn.completed；另有一次连通探针。实际运行元数据：read-only 34 轮、workspace-write 13 轮。全部夹具文件和内部 Git 状态未改动，无写入/PR/部署尝试。C15 的缺失目录检查非零属于预期受阻证据，并非模型运行失败。

| # | 实际加载 Skill | 实际来源与响应核验 | 结果与证据 |
| --- | --- | --- | --- |
| 1 | Foundry | 项目索引、profile、登录决策及 Git 版本；说明已确认方案不等于实现 | 通过，[证据](first-run/C01.json) |
| 2 | WikiOps | 主题注册表、隔离测试笔记与旧草稿；明确历史范围 | 通过，[证据](first-run/C02.json) |
| 3 | Foundry + WikiOps | 项目会话/缓存约束与历史隔离记录；建议与决策分开，不建第二份 PRD | 通过，[证据](first-run/C03.json) |
| 4 | 无 | 仅两份公共协议；解释 computed/watch，不访问资料仓库 | 通过，[证据](first-run/C04.json) |
| 5 | Foundry | 项目索引未收录后查 profile 别名，定位星笺，不误判不存在 | 通过，[证据](first-run/C05.json) |
| 6 | WikiOps | 空/过期注册表后核对 notes 目录与正文，找到记录 | 通过，[证据](first-run/C06.json) |
| 7 | Foundry + WikiOps | 并列草稿/测试/项目决策范围，项目约束优先；重复读取修复后复验 | 通过，[首轮失败](first-run/C07.json) / [修复后](regression/C07.json) |
| 8 | Foundry | Skill 捕获规则；只作为 Idea，未创建项目 | 通过，[证据](first-run/C08.json) |
| 9 | Foundry | 产品索引及捕获规则；目标用户/问题/交付物形成项目候选，不分配 slug | 通过，[证据](first-run/C09.json) |
| 10 | Foundry | 既有登录决策与用户确认；技术方案候选，未描述成已开发 | 通过，[证据](first-run/C10.json) |
| 11 | WikiOps | 已有缓存隔离文章；用户提供 2/2 测试证据，建议增量补根因，未谎称独立运行 | 通过，[证据](first-run/C11.json) |
| 12 | WikiOps | 已有对象存储主题、历史测试与用户陈述；专题候选，另外两点未核验 | 通过，[证据](first-run/C12.json) |
| 13 | Foundry | 同会话真实十轮；首轮之后零重复检索；增强场景增加一条待归档决策 | 通过，[首轮](first-run/C13.json) / [早期功能重测](regression/C13.json) / [逐轮可写补测](sandbox-regression/C13.json) |
| 14 | 无 | 无工具调用、无固定沉淀摘要 | 通过，[证据](first-run/C14.json) |
| 15 | Foundry | 仅公开规则及缺失目录检查；明确无法核实，不冒充已读正文 | 通过，[证据](first-run/C15.json) |
| 16 | Foundry | 只读核对既有登录决策与版本；未写文件/项目/PR/部署 | 通过，[首轮](first-run/C16.json) / [可写沙箱](regression/C16.json) |

完整输入、逐轮响应、实际命令、来源、退出码、文件未改动检查和原始日志 SHA-256 均在各 JSON。重复的公开 Skill 正文不再次入库，命令输出仅保存 SHA-256 与字节数。实际送入各场景的 Skill/协议文件版本见 [源码快照](source-snapshots.json)，不同修复阶段不混称同一个不可变 Head。

## 本次修复

- Foundry/WikiOps 的独立 reference 明确复用已读全文与版本；身份核验、补引用和连续回答不得附带重复拉取，只有来源变化、截断或缺少关键段落才允许补读。
- 新增捕获规则明确同主题增量更新、允许新建的条件与单一问题/专题晋升边界，消除无回退条件的“优先”。
- 选路协议补齐个人知识语境条件，与知识检索协议一致，避免将通用排障一概导向私有检索。
- 协议及场景中的项目名替换为明确虚构的 LumaNote；验收说明禁止发送真实私有正文、配置和凭据。
- 补充真实行为运行脚本、脱敏证据与阶段交接；修复续接命令未显式携带沙箱参数的验收工具缺陷，并逐轮存档实际模型/沙箱元数据。未引入其他 PR 尚未进入 main 的内容。

## 限制与交付

本次仅验证配置了项目协议入口、两个 Skill 与显式虚构 Workspace 的 Codex 环境；没有验证无入口配置时的全局自动发现、ChatGPT/Claude、真实 GitHub 权限或私有仓库同步。部分场景会先枚举小型夹具目录；增强第 13 项还读取了另一虚构 Workspace 的规则入口，但未读取其知识正文。大库检索请求量与长期会话漂移尚未量化。

本地验收已达到相对当前 main 的合并准备条件。提交前再次 Fetch/查询确认：main、#19、#14 Head 未变化，#18 前进后已按新 Head 完成兼容性复核；#19 为 Draft/Open，GitHub 返回 MERGEABLE/CLEAN。没有借检查触发 Actions。报告保存于修复提交前，Commit/Push 的最终 SHA 与结果必须以最终回复和远端 Head 为准；报告不能替代实时 Git 证据。保持 Draft，不合并、不部署；不修改产品仓库、知识库或其他 PR。
