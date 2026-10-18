# Skill Orchestration V1

适用范围：SDKit 项目中自然语言任务的 Skill 发现、选择、组合与安全降级。修改 Skill 入口或跨 Skill 任务路由时必须读取本协议。它是仓库级约定，不是独立 Skill、运行时调度器或授权来源。

## 事实源与边界

- 当前用户意图决定任务目标；已核验的目标仓库 AGENTS.md、项目身份和实际代码决定适用规则；已安装 Skill 的 SKILL.md 和命中 references 决定实现约束。
- 只有 `name`、`description` 属于通用 Skill frontmatter；Catalog 用于源码发现与维护，不得假定独立安装的 Skill 能读取 Catalog。
- 不创建总控 Skill、常驻服务、全局状态数据库或自动轮询；不得自动安装未授权 Skill。
- 用户明确指定 Skill 时先验证适用性；不适用时说明冲突，不得因明确指定而越过仓库或安全边界。
- 未指定时依据任务语义、已验证的仓库身份和技术证据选择；不得仅根据文件扩展名推断模板身份。

## 选择与组合

1. 将任务划分为讨论、只读检查、代码修改、数据变更、Git 集成或部署；跨仓库任务拆成可验收子任务。
2. 每个子任务确定唯一 Primary 责任能力。Supporting 只处理命中范围，Guardrail 是共同安全约束而不是另一业务执行者。
3. 优先使用当前 Agent 原生已发现且适用的 Skill；不可用时读取可访问的权威 Skill 源码及命中 references。必要规范不可取得时停止受影响操作。
4. 只加载任务命中的 references；新的修改范围、Skill 更新或会话恢复时重新核验。
5. 不重复执行同一写入：Model/业务代码由技术栈 Skill 负责；数据库迁移由项目现有规范与已验证的能力负责，不得依赖尚未实现的 dbops；Git 交付遵守协作规范。
6. 候选的 gitops、dbops、Template Evolution 在实际安装与验证前不能当作已具备执行能力；沿用现有项目与技术栈规则安全降级。

规则优先级为：当前用户明确指令 > 目标项目显式规则 > 命中 Skill > 历史实现。协议只规定协作流程，不得以路由结果覆盖项目规范；存在无法同时满足的规则时，必须说明冲突并停止受影响修改。

## 新旧入口选择

- 必须先核验项目来源、锁定版本与已发现 Skill 的适用范围；模板 main 不是业务项目已升级的证据。
- 已安装且适用的新主入口必须作为正常开发 Primary：`sdkit-go-core`、`sdkit-rust-core`、`sdbase-go`、`sdbase-vab-admin`、`sdbase-nuxtjs-portal`；对应旧入口 `sdkit`、`rust-sdcore`、`sdkitgo`、`vab-admin`、`nuxtjs` 仅用于其当前 description 允许的历史兼容或迁移任务，不得与新入口重复承担同一子任务。
- 只有旧版 Skill 可访问、且其 description 仍允许当前开发任务时，允许以 Degraded 使用旧版；若已收窄为显式兼容用途，必须停止正常开发路由或读取可访问且适用的新入口源码，不得静默越过触发边界。不得为解决选择问题自动安装、删除或覆盖旧入口。
- `sdbase-lite`、`sdbase-admin-lite`、`sdbase-flutter-app` 必须按其各自模板身份单独选择；禁止给 lite 套用完整 Go 多服务/PostgreSQL 或 Vab 动态菜单/RBAC 规则，禁止把 Flutter 未接入 SDK 描述成已实现。Rust core 身份必须从实际 Cargo 依赖解析，不得推测仓库地址。

## 隐式知识检索与沉淀

- 自然语言任务依赖已存在产品项目的 PRD、设计、技术决策或进度时，必须按需路由 Foundry 检索权威产品文档；涉及已有个人技术经验、可复用排障或专题时，必须按需路由 WikiOps 检索知识库。两类证据均必要时可组合，但每个写入子任务仍只有唯一 Primary。
- 检索与候选捕获遵守 [Knowledge Retrieval & Capture V1](knowledge-retrieval-capture.md)：索引优先、正文按需、当前会话去重、阶段性摘要、写入授权独立。普通无历史关联问答不强制检索私有仓库。
- 仅有 Skill 描述和协议不能保证所有 Agent 都自动发现或监听其他会话；不得把静态规范测试当成跨模型真实触发验证。

## 场景与反例

| 场景 | Primary | 条件性辅助 | 禁止误触发 |
|---|---|---|---|
| Nuxt 页面 | 已验证的 sdbase-nuxtjs-portal；旧版按兼容规则 | 写入前 Git 预检 | 不连接数据库 |
| Vab 后台 | 已验证的 sdbase-vab-admin；旧版按兼容规则 | 写入前 Git 预检 | 不应用 Nuxt 规则 |
| Go 业务 | 已验证的 sdbase-go / sdbase-lite，按项目身份区分 | DDL 时数据库规范 | 不自动修改 sdkit core |
| 框架源码 | 已验证的 sdkit-go-core / sdkit-rust-core | Git 协作 | 不按普通 CRUD 处理 |
| 查询开发数据库 | sdenv 或已验证连接入口 | Schema 比对时数据库协作规范 | 不执行 DDL |
| Git 同步 | 项目 Git 协作规范 | 相关 PR 感知 | 不丢弃本地改动 |
| 老项目模板演进 | 已验证技术栈 Skill | 模板差异与 Git 协作 | 不整体覆盖业务代码 |
| 产品文档 | foundry | 必要时 Git 协作 | 不开发正式业务代码 |
| Wiki | wikiops | 必要时 Git 协作 | 不覆盖 PRD 事实源 |
| Skill 维护 | sdkit-skills | Git 协作 | 不接管业务开发 |

只讨论方案时允许读取相关规范，但不得将讨论视为写入、合并或部署授权。

## 能力、授权与降级

- 能力状态为 Ready、Degraded、Blocked；授权另行按操作、目标与范围核验。Ready 不等于获准 Push、合并、部署或数据库写入。
- Git 写入前遵守 [跨会话协作感知](collaboration-awareness.md)，按需检查最新 SHA 和相关 PR；不得为感知主动触发 CI。
- 必须先按项目与 Skill 规则解析显式环境或已声明的默认环境；解析后数据库环境仍不明时禁止试连；正式数据库沿用对应 Skill 的禁止 AI 直接或间接操作规则。
- 缺少本地 CLI 时可以只读分析或使用已验证的等价 Provider；不能把远端检查称作本地已同步。
- 必要实时证据缺失时将相关写入标记 Blocked，保留已有工作，不以缓存代替验证。

## 执行生命周期

Discover → Resolve → Preflight → Execute → Verify → Handoff。

- 简单只读任务不强制全量预检；修改前检查必要状态，Push/合并前再次核验。
- 长任务和多阶段代码修改遵守 [开发执行约束](development-execution.md)。
- 任务结果分别报告已分析、已修改、已测试、已提交、已推送、已合并、已部署、已验证；不得混淆。

## 跨 Agent 兼容

- 必须先使用适用的原生 Agent Skills；仅在 Agent 不支持原生发现时通过目标仓库 AGENTS.md 的简短入口发现权威规则，禁止复制第二份可漂移的业务规范。
- Skill 保持独立可安装；不得依赖未声明的个人路径、私有配置或其他未安装 Skill。
- 当前环境不支持自动发现时如实说明，不宣称已验证 Codex、Claude 或 ChatGPT Web 的行为。

## 完成标准

同一任务能够确定主责任与命中规范；无关 Skill 不加载；写入遵守授权；工具缺失时安全降级；结果可核验。人工验收至少覆盖跨 Agent 隐式触发与误触发场景。
