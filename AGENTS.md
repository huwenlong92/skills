# Repository Instructions

本仓库维护 opinionated 工程约定，并将其作为可被多个 coding agent 使用的共享 skills 分发。规则应忠实固化已经确认的代码习惯，不要擅自改写成宽泛的行业建议。

## 内容规则

- 文档使用中文；代码标识符、路径、命令和协议名保留英文。
- 每个 skill 必须自包含。不得依赖本机固定目录、全局 `AGENTS.md` 或另一个未声明的私有文档。
- `SKILL.md` 只写触发、分流、执行顺序和跨场景门禁；详细规则写入该 skill 的 `references/`。
- 只使用通用 Agent Skills frontmatter：`name` 和 `description`。不要加入某个 agent 专属的工具权限或执行字段。
- 通用共享 Skill 不记录具体业务项目清单、真实账号、真实凭据、个人目录或临时兼容方案。明确标记为专用的 Skill 可记录其必需的公开仓库定位信息与公开站点地址；仍禁止记录凭据、Token、个人本机路径、私密账户数据和随版本变化的业务项目清单。
- 已确认的个人偏好使用确定性措辞。即使其他团队可能采用不同方案，也不要擅自把“必须”改成“建议”。
- 新增或改造本仓库 Skill 的用户私有配置时，必须默认使用 `~/.config/sdkit/skills/<skill-name>/config.json`；显式指定配置文件时使用指定路径。禁止在 Skill 安装目录、源仓库或业务项目内保存个人配置，也不得为没有配置需求的 Skill 创建空配置。既有 Skill 随各自配置改造迁移，禁止因修改本约定而批量迁移未授权的 Skill 或第三方工具配置。
- 各 Skill 必须在自身 reference 与读取脚本中声明一致的配置路径，保持自包含。配置迁移必须先校验旧配置并检查目标是否存在；目标存在时停止覆盖；迁移后必须核对内容、文件权限和实际读取结果，验证前保留原配置。

## Reference 质量门禁

每个 reference 必须满足以下要求：

1. 开头定义适用范围；明确哪些修改需要读取该文件。
2. 规则使用“必须”“禁止”“仅当……时允许”表达；不得单独使用“尽量”“适当”“一般”“视情况”等无判定条件的词。
3. “优先”后必须紧跟退回次选方案的客观条件。
4. 路径以目标项目根目录为基准；不得出现工作站绝对路径。
5. 涉及放置位置时，同时写明允许位置和禁止位置。
6. 涉及危险操作、发布、数据库或凭据时，写明前置条件、停止条件和验证动作。
7. 文件末尾提供可核验的完成标准；无法自动验证的内容写明人工检查对象。
8. 涉及代码写法的 reference 必须提供经过脱敏的正向典型形态；仅靠禁止项不足以表达写法时，还必须提供最小反例。示例不得包含真实业务仓库地址、账号、凭据或只能在单一项目成立的临时名称。
9. 同一 skill 内不得有互相冲突的规则；发现冲突时先统一模型，再保留一处权威定义，其余文件链接过去。

## 维护流程

- 修改前只读取目标 skill 及命中的 references。
- 新增、删除、拆分或重命名 reference 时，同步更新该 skill 的 `SKILL.md` 分流表。
- 修改模板时同时检查引用模板的 reference；模板不得包含真实仓库地址、token 或本机路径。
- 完成后运行 skill 校验，检查 Markdown 相对链接，并搜索残留绝对路径和模糊措辞。
- 不自动执行 `git add`、`git commit` 或 `git push`。

## 跨项目协作规范

仓库维护 [SDKit 项目协作规范](standards/project-collaboration.md)，用于跨技术栈项目的 `AGENTS.md` 和 `.sdkit/` 约定。该规范不改变独立 Skill 的职责或发布授权；对规范的修改必须遵守本仓库维护流程。

## 跨会话 PR 感知

涉及并行仓库写入时，必须遵守 [按需 PR 感知与冲突处理](standards/collaboration-awareness.md)。只在任务开始、写入前及 Push/合并前检查相关远端状态；禁止为感知检查主动触发 CI。

## 知识检索与沉淀

自然语言任务隐含已有项目资料、历史技术经验或值得沉淀的知识时，按 [Knowledge Retrieval & Capture V1](standards/knowledge-retrieval-capture.md) 进行按需检索、候选分类与阶段摘要。自动识别不增加仓库写入、项目创建、发布或跨 Workspace 授权。

## Skill 场景感知与开发执行

涉及 Skill 的自动选择、跨 Skill 协作或能力降级时，必须遵守 [Skill Orchestration V1](standards/skill-orchestration.md)。涉及多阶段、跨会话或高风险开发任务时，必须遵守 [Development Execution V1](standards/development-execution.md) 的计划基线、阶段验收与偏差门禁。两份协议不取代各 Skill 自身规则，不构成额外的提交、合并、数据库写入或部署授权。

任务恢复入口：[当前状态](.sdkit/STATUS.md)、[任务与计划](.sdkit/TASKS.md)、[已确认决策](.sdkit/DECISIONS.md)、[验收交接](.sdkit/HANDOFF.md)。状态记录必须与实际 Git 和测试证据核对。

## Git Collaboration

涉及 Git 同步、Worktree、Commit、Push、PR/MR、Merge 或失败恢复时，必须遵守 [Git Collaboration V1](standards/git-collaboration.md) 的按需 Preflight、独立授权与安全降级门禁。该协议不构成额外写入或部署授权；独立安装的 Skill 必须保留自身必要安全规则。
