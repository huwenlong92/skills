# 专题 A → B/C/D：全局规则承接交接（只读协议任务）

状态：**B/C/D 审计已交接 / Draft 待归档**。本文件只分派规则归属审计与证据验收，不修改任何 Skill、真实 Codex 配置或业务仓库。基线：skills/main `a79003e5a8ab5fc3ba7fa344de886bf8316b391a`；执行时重新核验最新 main 与 PR。

## 当前边界

- 专题 A：Project Skill Bootstrap、Codex 全局 AGENTS 极简入口、旧 standards-bootstrap 退出、engineering-standards 迁移收尾；统一审核规则是否可以从全局退出。
- 专题 B：Git Collaboration V1，关联 Draft PR #20；负责 Git 初始化、remote、暂存、提交、Push、PR、冲突、权限及授权门禁。
- 专题 C：Database Schema Collaboration V1，关联 Draft PR #21；负责 Schema、Migration、Baseline、DDL、恢复和协作授权；实际环境发现与操作仍由 sdenv 承担。
- 专题 D：Template Evolution V1（sdkit-templateops 尚须按实际仓库确认状态）；负责模板身份、来源、锁定版本、升级计划及兼容性，不替代 Go/Nuxt/Vab/Rust 技术 Skill。

## 规则承接矩阵

| 现有全局规则 | 主责任 | 协作/边界 | 当前处理 | 退出条件 |
|---|---|---|---|---|
| Git 初始化、remote、暂存/提交、Push 与危险操作限制 | B | A 保留用户明确授权兜底；不得放宽 | B 已审：Stage/Commit/Push/PR 已承接；GAP-B01/B02 阻塞 | PR #20 或后续正式协议承接、安装/可访问、静态及真实行为验证，用户授权语义不变 |
| 跨会话 PR 感知、冲突及合并门禁 | B | 根 collaboration-awareness 与项目规则 | 待 B 审计 | 无双重权威、失败安全降级且可复现 |
| Docker context home、sd help db、pg18 个人默认 | sdenv；C 审计 | 不把用户环境默认硬塞进 DBOps | 暂留全局 | 实际安装配置能读取同等默认并完成真实发现验证 |
| PostgreSQL system/system_data 基础设施保护 | C + sdenv + Go 技术 Skill | C 负责 Schema 变更协作，sdenv 负责环境操作 | 暂留全局兜底 | 所有受影响数据库路径均有等价保护、拒绝测试及授权门禁 |
| Go/Nuxt/Vab/Rust 模板来源、版本、身份 | D + 对应技术 Skill | 不按语言扩展名推断模板 | D 已审：技术 Skill 部分承接；Template Evolution 未实现 | 真实锁定依赖、来源与模板身份可解析；新旧入口兼容测试通过 |
| Rust sdcore 共享 core、消费方与个人源码线索 | Rust 技术 Skill；D 仅负责模板身份 | 个人路径不能直接删除，须证明 Cargo/Workspace 定位等价 | 暂留个人规则 | 消费方发现和 core 归属实际验证，原有用户行为不丢失 |
| 工程规范沉淀与 Skill 路由 | A + sdkit-skills + Orchestration | 唯一 Primary；写入仍需授权 | 已由现行协议部分承接 | 实际模型路由和沉淀目标验证，不重复维护技术栈清单 |
| WikiOps、Foundry Workspace 与本地路径 | 对应 Skill | 已有 config.json 的按实际读取器处理 | A 单独收口 | 用户配置、原生发现、发布偏好验证 |
| GitNexus --index-only、localhost、Superpowers | 工具原生能力或个人偏好 | 不强行塞入 B/C/D | 暂留全局 | 有等价原生配置或已验证行为后再移除 |
| 旧 standards-bootstrap | A | 禁用/恢复属于本地配置事务 | 本地已原生禁用，旧目录保留、备份可恢复 | 原生禁用有效，新版路由可发现，旧目录及备份完整 |

## 专题领取与交付要求

### B：Git Collaboration

核验最新 skills/main、PR #20 与当前 Git 规范，逐条映射 Git 初始化、remote、暂存、提交、Push、PR、权限、冲突与并发。提交 **已承接 / 待实现 / 必须留全局** 的证据矩阵；尤其验证“不得未经当前用户授权执行写入”与禁止粗放暂存。此任务只读，不得顺带修改 #20。

### C：Database Schema Collaboration

核验最新 skills/main、PR #21、sdenv、sdbase-go、sdkit-go-core；分离环境发现、个人默认、基础设施 Schema 保护与 Migration/Baseline/DDL/恢复职责。返回可替代的准确条款、缺口、测试证据及退出条件。不得连接数据库、修改 #21 或执行 DDL。

### D：Template Evolution

核验最新 skills/main、sdkit-templateops 实际状态及冻结设计，检查 Go/Nuxt/Vab/Rust 身份、锁定依赖、消费方和升级边界；明确个人 Rust 源码线索的保留/替代条件。返回责任矩阵、接口证据、未实现事项与退出门禁。不得创建或修改模板仓库。

各专题只读领取，不得因为本交接 PR 而自动提交、合并、部署或触发 CI。各专题结果回传 A 后，A 再形成全局 AGENTS 精简的单一结论。

## 与本地正在执行的收尾隔离

用户已报告本地完成 WikiOps 版本分叉安全同步、原生禁用旧 standards-bootstrap（旧文件仍保留），以及 9,523 → 7,903 字节的 AGENTS 原子精简；最终 AGENTS SHA 为 `80a6de41d1ab7b9e3c013e8c7ed026698d9d0a00f9755b749b7cf94c8930f7ca`。本地报告 148 项测试通过，模型唯一 Primary 探针 45 秒超时、**待验证**。以上是本地验收报告而非本 PR 执行结果；本 PR 不修改本地配置、安装或恢复备份。

R036、R041–R044 的外部协议缺口仍保留；engineering-standards 不具备删除条件。任何全局规则退出必须以对应能力实际交付和行为验证为门禁。


## 正式交接结论（2026-10-18）

### B · Git Collaboration — BLOCKED，不退出全局 Git 规则

- 已有规范：Draft PR #20 覆盖 Stage/Commit/Push 分别授权、PR/MR/Review/Merge、同步与 Worktree、并行冲突与恢复、危险操作限制及 Provider 降级。
- **GAP-B01**：git init 触发条件、已有仓库与嵌套仓库保护待补。
- **GAP-B02**：git remote add/set-url 等 Remote 变更的独立授权待补。
- PR #20 未合并，独立安装/发现、真实 Agent 行为及全局规则删除回归未完成。
- 退出门禁：补齐 B01/B02，正式合并并可用，验证实际模型与 Git 授权等价后，才重新评估移除 `git-initialization-rules`；目前必须保留。

### C · Database Schema Collaboration — BLOCKED，不退出数据库全局兜底

| 规则 | 权威责任 | 状态 |
|---|---|---|
| Docker context、home、sd help db、pg18、连接查询与备份恢复 | sdenv 实际安装配置 | 已有实现；本次真实发现行为未全部验证 |
| Go Model/GORM/现有 Migration | sdbase-go | 已有规范；不是版本化 SQL Runner |
| Go 框架数据库基础设施 | sdkit-go-core | 已有职责 |
| SQL Migration 文件规范、静态检查 | Draft PR #21 sdkit-dbops | 源码已提交，未完成正式交付/行为验收 |
| Baseline、Migration History、Snapshot、Drift、同步计划、恢复 | sdkit-dbops 后续阶段 | 待实现 |
| system/system_data、DDL 安全及拒绝规则 | Go Skill + sdenv + 未来 dbops | 部分承接，跨栈真实行为待验 |

- sdbase-go 现有 Migration 命令的 `app.mode=dev` 显式门禁仍有缺口，不属于 PR #21 已修复内容。
- 正式数据库禁止 AI 直接或间接操作（含只读、备份及 CI/CD 代执行）；未知环境禁止试连；远端共享开发库必须逐次明确授权。以上安全兜底不得因已有 SQL 静态检查而删除。
- 退出门禁：实际安装配置与命令发现、跨 Go/非 Go 的 Schema 保护、拒绝/恢复测试、Provider 集成及真实 Agent 行为全部验证，且授权语义不降级。

### D · Template Evolution — BLOCKED，不退出模板与 Rust 个人规则

- Template Evolution V1 FC2 已设计冻结；`sdkit-templateops` 尚未实现、安装或通过真实行为验收。
- Go/Nuxt/Vab 技术 Skill 已有模板来源识别规范，但统一身份、版本锁定、三方升级和恢复未具备已验证能力。
- Rust Skill 通过 Cargo/Workspace/依赖动态发现 sdcore；真实消费方定位尚待验收。个人 Rust 源码与消费方线索保留，不能直接删除或硬编码到通用 Skill。
- Git 由 B、Schema 由 C 承接；D 不重复实现。只有新 Skill 正式交付、安装、静态及真实 Agent 行为验证后才逐项评估退出。

### 专题 A 本地迁移与剩余风险

- #14–#17 已合并；本地源码与 Skill 安装 A+B 已完成；全局 AGENTS 双区块迁移 C 已完成。
- 用户本地报告：WikiOps 用户级三个文件受控更新，旧 standards-bootstrap 已由 Codex 原生配置禁用且原文件保留；全局 AGENTS 已精简为 7,903 字节、SHA 如上，备份/journal 正常。
- Catalog 21 Skill（16 主入口、5 兼容入口）；模型唯一 Primary **未通过真实行为验收**（探针超时）。
- R036、R041–R044 仍有外部协议缺口，R042 阻塞、R043 部分通过；`engineering-standards` **不具备删除条件**。
- Git、数据库、模板与 Rust 个人安全规则均暂留全局；本 PR 只记录责任和门禁，不授权修改真实 AGENTS 或各专题 PR。

## 验收

- 只新增交接文档；不修改现有 Skill、协议、Catalog 或全局配置。
- B/C/D 分别报告规则来源、承接位置、证据、缺口、退出条件及是否影响个人授权。
- 本交接 PR 保持 Draft，不合并、不部署、不主动触发 CI。
