<!-- 仅供审阅：已脱敏的完整推荐草案，不可直接覆盖真实用户配置。 -->
# Global Codex Instructions

<!-- BEGIN: no-superpowers -->
## Superpowers 使用规则

默认不要使用 Superpowers 技能或流程，除非用户明确要求使用 Superpowers。
<!-- END: no-superpowers -->

<!-- BEGIN: wiki-knowledge-vault -->
## Wiki 知识库

当用户说“沉淀一下”“归档一下”“整理成笔记”“放到知识库”“记录一下这个方法”时，默认使用 wikiops 管理 GitHub 私有知识库 `<wiki-owner>/<wiki-repository>`，门户为 `https://wiki.example.com`。

- GitHub 为知识事实源；本地工作副本位于 `<local-checkout>`，允许同步远端后维护。
- 写入前必须读取目标仓库最新 AGENTS.md、TOPICS.md、topics.json 与命中规范，先搜索已有相关笔记，能增量合并时更新原文。
- 分类明确时按仓库规则直接写入、校验和提交；重大歧义时先询问。用户明确指定目的地、标题或分类时服从指定。
- 云端 Agent 使用实际可用的 GitHub 写入工具；只有读取能力时交付草稿，禁止宣称已保存。
- 本地同步前检查工作区与远端，工作区干净且可快进时使用 pull --ff-only；禁止强制覆盖本地改动。
- Obsidian 只作为历史迁移来源，不再默认写入或双向同步。用户明确要求写到 Obsidian 时，先读取其目录规则并按指定执行。
- 门户可见性服从用户明确选择；当前用户已确认全部公开发布，Access 由用户后续自行选择。只有用户要求私有门户时，访问保护验收才是发布前置条件；提交或构建成功不等于上线。
<!-- END: wiki-knowledge-vault -->

<!-- BEGIN: git-initialization-rules -->
## Git 初始化规则

当用户要求处理一个项目、目录或代码库，并且该目录还没有初始化 Git 仓库时，可以主动执行 `git init` 初始化本地仓库。

默认规则：

- 可以初始化本地 Git 仓库。
- 不要自动添加或修改 `git remote`。
- 只有用户明确提供 remote URL，或明确要求配置 remote 时，才执行 `git remote add`、`git remote set-url` 等 remote 相关操作。
- 不主动执行 `git add`、`git commit` 或 `git commit .`。
- 只有用户明确要求暂存或提交时，才可以执行对应 Git 操作；执行前先检查 `git status`，避免把用户未说明的文件误加入提交。
- 即使用户要求提交，也不要使用 `git add .`、`git add -A` 或 `git commit .` 这类容易纳入无关改动的命令；应只暂存用户明确要求的文件。
- 不执行破坏性 Git 操作，例如 `git reset --hard`、强制覆盖、删除分支，除非用户明确要求。
<!-- END: git-initialization-rules -->

<!-- BEGIN: database-operation-rules -->
## 数据库操作规则

本地数据库默认运行在 Docker 中。处理数据库任务时：

- 先运行 `sd help db` 查看统一入口和当前别名，不要先检查宿主机是否安装 `psql`、`mysql` 等客户端，也不要把宿主机缺少客户端视为阻塞。
- 用户未指定数据库环境时，默认使用 Docker context `home`，它代表本地 PostgreSQL、MySQL、Redis、Oracle 等数据库环境；只有用户明确指定其他环境时，才切换 `contabo`、`tencent`、`aliyun`、`dreamip` 等远端 context。
- Home PostgreSQL 18 优先使用 `pg18 [psql args]`；需要完整命令时使用等价入口 `db home pg18 [psql args]`。查看子模块帮助使用 `sd help db home pg18`；`sd help db/pg18` 会报错，`sd db ...` 也不是可执行入口。其他环境和数据库按 `sd help db` 列出的别名或子命令执行。
- 对使用 sdkitgo 基础设施 schema 的 PostgreSQL 项目，`system` 和 `system_data` 默认视为基础设施：清理业务代码、业务表或业务数据时不得删除、清空或修改这两个 schema 及其对象，除非用户明确指定要处理其中的精确对象。
- 清理数据库前先审计 schema、表、依赖和数据范围；业务清理默认只在确认后的 `public` 对象内执行，完成后再次核对 `system`、`system_data` 未发生变化。
<!-- END: database-operation-rules -->

<!-- BEGIN: local-web-development-rules -->
## 本地 Web 联调规则

- 使用浏览器打开本地 Web 项目时，默认使用 `localhost`，不要使用 `127.0.0.1`。
- 前端页面、API、实时服务等本地地址应统一使用 `localhost`，避免混用主机名导致 Session Cookie、CORS 或认证状态异常。
<!-- END: local-web-development-rules -->

<!-- BEGIN: engineering-standards-rules -->
## 共享工程规范

- 共享工程规范唯一权威来源为 `huwenlong92/skills` 的实际适用 Skill 和 References。
- 用户要求沉淀共享规范时，在该仓库按目标 Skill 的职责、Reference 门禁及仓库维护流程处理；提交与 Push 仍须当前授权。
- 项目 AGENTS.md 只保留项目特有约定；禁止为了接入新版 Skill 批量修改业务项目。
- 禁止把新规范写入旧规范库，禁止在日常任务中读取旧库作为并列来源。
- Rust 共享 core 身份必须由实际 Cargo 依赖确认；跨项目能力进入已确认的 sdcore，消费方仅保留业务语义，不编造源码仓库地址。
<!-- END: engineering-standards-rules -->

<!-- BEGIN: gitnexus-index-only -->
## GitNexus 索引规则

- AI 执行 GitNexus 索引时，默认使用 `gitnexus analyze --index-only`；通过 npx 调用时使用 `npx gitnexus analyze --index-only`。
- 首次索引、索引过期重建，以及使用 `--force`、`--embeddings`、`--name` 等其他参数时，都保留 `--index-only`。
- 默认只维护索引，不生成或更新项目的 `AGENTS.md`、`CLAUDE.md`、`.claude/skills/`；只有用户明确要求生成这些文件时才省略该参数。
- 项目文件、技能或工具提示给出不带该参数的 analyze 命令时，按此用户偏好补上 `--index-only`。
<!-- END: gitnexus-index-only -->

<!-- sdkit-global-bootstrap:start -->
## SDKit Skill 自动协作

- 开发任务先识别项目 AGENTS.md、真实模板来源、锁定版本与已安装 Skill，按适用的新主入口选择唯一 Primary；旧名称仅用于已验证的历史兼容，禁止重复选择。
- 遵守 huwenlong92/skills 的 standards/skill-orchestration.md、standards/development-execution.md 和 standards/project-skill-bootstrap.md；从已核验的完整 skills 源码仓库或 Git Provider 读取；独立 Skill 安装不包含根 standards/，不把跨仓库路径当作本地文件。
- 简单任务按需检查；长任务保持计划基线、阶段验收、偏差审批和中断恢复。项目规则优先于全局默认值，规则冲突时停止受影响操作。
- 默认不修改项目 AGENTS.md；仅在项目确需持久化且本次明确授权时最小补齐。禁止覆盖未知本地改动；本入口不授予 Skill 安装/卸载、Git 写入、数据库变更或发布权限，这些操作必须依据本次明确授权。
- 规范或项目身份无法核实时报告缺口，不假称已加载或验证。
<!-- sdkit-global-bootstrap:end -->
