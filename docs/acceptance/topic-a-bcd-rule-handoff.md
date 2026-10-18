# 专题 A → B/C/D：全局规则承接交接（只读协议任务）

状态：**待专题领取 / Draft**。本文件只分派规则归属审计与证据验收，不修改任何 Skill、真实 Codex 配置或业务仓库。基线：skills/main `a79003e5a8ab5fc3ba7fa344de886bf8316b391a`；执行时重新核验最新 main 与 PR。

## 当前边界

- 专题 A：Project Skill Bootstrap、Codex 全局 AGENTS 极简入口、旧 standards-bootstrap 退出、engineering-standards 迁移收尾；统一审核规则是否可以从全局退出。
- 专题 B：Git Collaboration V1，关联 Draft PR #20；负责 Git 初始化、remote、暂存、提交、Push、PR、冲突、权限及授权门禁。
- 专题 C：Database Schema Collaboration V1，关联 Draft PR #21；负责 Schema、Migration、Baseline、DDL、恢复和协作授权；实际环境发现与操作仍由 sdenv 承担。
- 专题 D：Template Evolution V1（sdkit-templateops 尚须按实际仓库确认状态）；负责模板身份、来源、锁定版本、升级计划及兼容性，不替代 Go/Nuxt/Vab/Rust 技术 Skill。

## 规则承接矩阵

| 现有全局规则 | 主责任 | 协作/边界 | 当前处理 | 退出条件 |
|---|---|---|---|---|
| Git 初始化、remote、暂存/提交、Push 与危险操作限制 | B | A 保留用户明确授权兜底；不得放宽 | 待 B 审计 | PR #20 或后续正式协议承接、安装/可访问、静态及真实行为验证，用户授权语义不变 |
| 跨会话 PR 感知、冲突及合并门禁 | B | 根 collaboration-awareness 与项目规则 | 待 B 审计 | 无双重权威、失败安全降级且可复现 |
| Docker context home、sd help db、pg18 个人默认 | sdenv；C 审计 | 不把用户环境默认硬塞进 DBOps | 暂留全局 | 实际安装配置能读取同等默认并完成真实发现验证 |
| PostgreSQL system/system_data 基础设施保护 | C + sdenv + Go 技术 Skill | C 负责 Schema 变更协作，sdenv 负责环境操作 | 暂留全局兜底 | 所有受影响数据库路径均有等价保护、拒绝测试及授权门禁 |
| Go/Nuxt/Vab/Rust 模板来源、版本、身份 | D + 对应技术 Skill | 不按语言扩展名推断模板 | 待 D 审计 | 真实锁定依赖、来源与模板身份可解析；新旧入口兼容测试通过 |
| Rust sdcore 共享 core、消费方与个人源码线索 | Rust 技术 Skill；D 仅负责模板身份 | 个人路径不能直接删除，须证明 Cargo/Workspace 定位等价 | 暂留个人规则 | 消费方发现和 core 归属实际验证，原有用户行为不丢失 |
| 工程规范沉淀与 Skill 路由 | A + sdkit-skills + Orchestration | 唯一 Primary；写入仍需授权 | 已由现行协议部分承接 | 实际模型路由和沉淀目标验证，不重复维护技术栈清单 |
| WikiOps、Foundry Workspace 与本地路径 | 对应 Skill | 已有 config.json 的按实际读取器处理 | A 单独收口 | 用户配置、原生发现、发布偏好验证 |
| GitNexus --index-only、localhost、Superpowers | 工具原生能力或个人偏好 | 不强行塞入 B/C/D | 暂留全局 | 有等价原生配置或已验证行为后再移除 |
| 旧 standards-bootstrap | A | 禁用/恢复属于本地配置事务 | 待本地结果 | 原生禁用有效，新版路由可发现，旧目录及备份完整 |

## 专题领取与交付要求

### B：Git Collaboration

核验最新 skills/main、PR #20 与当前 Git 规范，逐条映射 Git 初始化、remote、暂存、提交、Push、PR、权限、冲突与并发。提交 **已承接 / 待实现 / 必须留全局** 的证据矩阵；尤其验证“不得未经当前用户授权执行写入”与禁止粗放暂存。此任务只读，不得顺带修改 #20。

### C：Database Schema Collaboration

核验最新 skills/main、PR #21、sdenv、sdbase-go、sdkit-go-core；分离环境发现、个人默认、基础设施 Schema 保护与 Migration/Baseline/DDL/恢复职责。返回可替代的准确条款、缺口、测试证据及退出条件。不得连接数据库、修改 #21 或执行 DDL。

### D：Template Evolution

核验最新 skills/main、sdkit-templateops 实际状态及冻结设计，检查 Go/Nuxt/Vab/Rust 身份、锁定依赖、消费方和升级边界；明确个人 Rust 源码线索的保留/替代条件。返回责任矩阵、接口证据、未实现事项与退出门禁。不得创建或修改模板仓库。

各专题只读领取，不得因为本交接 PR 而自动提交、合并、部署或触发 CI。各专题结果回传 A 后，A 再形成全局 AGENTS 精简的单一结论。

## 与本地正在执行的收尾隔离

用户已在本地执行 WikiOps 版本分叉处理、原生禁用旧 standards-bootstrap、以及 9,523 → 7,903 字节的 AGENTS 过渡精简。**本 PR 不修改、阻断、覆盖或声称完成该本地任务**。候选 SHA `80a6de41d1ab7b9e3c013e8c7ed026698d9d0a00f9755b749b7cf94c8930f7ca` 仅作为历史设计指纹，是否实际写入以本地结果为准。

R036、R041–R044 的外部协议缺口仍保留；engineering-standards 不具备删除条件。任何全局规则退出必须以对应能力实际交付和行为验证为门禁。

## 验收

- 只新增交接文档；不修改现有 Skill、协议、Catalog 或全局配置。
- B/C/D 分别报告规则来源、承接位置、证据、缺口、退出条件及是否影响个人授权。
- 本交接 PR 保持 Draft，不合并、不部署、不主动触发 CI。
