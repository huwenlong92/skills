# Project Skill Bootstrap V1

适用范围：SDKit/SDBase 项目的 Skill 自动识别、Codex 全局入口接入，以及按需的项目 AGENTS.md 补齐。默认只读、全局优先、项目写入必须有明确授权。本协议不创建总控 Skill，不安装或卸载 Skill，不改业务代码。

## 全局优先

1. Codex 用户级入口为实际 `CODEX_HOME/AGENTS.md`；未设置 CODEX_HOME 时默认 `~/.codex/AGENTS.md`。大小写必须正确。其他 Agent 只使用自身实际支持的入口，不得假定共享 Codex 路径。
2. 全局入口只记录简短发现规则、共享协议来源和安全边界；禁止复制整份 Skill Reference 或写死本机源码绝对路径。
3. 进入项目时先读取其 AGENTS.md、锁定依赖、模板来源及原生 Skill 发现结果；已安装且适用的新主入口优先，旧入口仅作历史兼容。模板 main 不代表业务项目已升级。
4. 使用 Skill 不自动修改项目 AGENTS.md；已有全局规则且项目正常运行时无需生成任何项目文件。
5. 项目级规则和当前用户授权不可被全局入口覆盖；发现冲突必须停止受影响操作。全局入口也不赋予 Git、数据库、发布权限。
6. 共享协议来源为 `huwenlong92/skills` 的 `standards/skill-orchestration.md`、`standards/development-execution.md` 和本文件；只有通过已安装 Skill 或可用 Git Provider 解析后才可使用。来源不可访问时不得假称已经读取。

## 按需项目补齐

仅当项目要长期共享协作入口、明确要求持久化或全局入口无法满足项目级交接时，才提出最小补齐。只读任务不得写入。已有项目文件必须保留自定义规则；不生成第二套任务系统。

- 必须核验项目模板身份、版本、当前 Skill 的适用范围。仅当来源证据充分时才建议 `nuxtjs` → `sdbase-nuxtjs-portal` 或 `rust-sdcore` → `sdkit-rust-core` 等映射；不因为文件扩展名就迁移。
- 项目写入必须有针对目标项目配置的授权；缺少授权时只输出 Diff 计划。
- 只修改根目录 AGENTS.md 中明确托管的 Skill 入口，禁止全局替换旧名字、修改业务代码、依赖、数据库或 `.sdkit/`。
- 文件存在符号链接、未知修改、模板身份不明、托管标记损坏或并发哈希变化时停止。
- 变更前备份原始字节并记录哈希，写入后检查权限、内容和第二次运行零差异；备份不提交 Git。不得自动 Commit、Push、合并、部署或触发 CI。

## Codex 全局接入工具

`scripts/project_skill_global.py` 仅修改 Codex 全局 AGENTS.md 中带有独立标记的托管区块；默认 dry-run。写入必须显式传入授权标志与 dry-run 返回的原始 SHA-256。已有未托管内容逐字节保留；标记异常时拒绝修改。写入前备份，目标改变则拒绝写入；重复执行无差异。

建议的全局入口要求：识别项目真实模板来源，按 [Skill Orchestration](skill-orchestration.md) 选择唯一 Primary，按 [Development Execution](development-execution.md) 约束长任务；先遵守项目 AGENTS.md 和实际安装状态，禁止自动安装/卸载、项目批量改写和越权提交。

`scripts/project_skill_bootstrap.py` 是项目级可选辅助工具，不属于默认全局流程。其模板身份参数仅是经外部核验后的输入，不得当作工具自动完成了模板身份验证。

## 验收

- 全局入口初次写入可恢复、二次执行零差异、原有自定义规则保留。
- 无授权、SHA 变化、符号链接、错误标记、路径异常均阻止写入。
- 多个项目无需逐个修改即可依靠全局入口与原生 Skill 发现完成路由；项目级补齐仍须单独授权。
- Codex 实际发现与隐式触发必须另行行为测试；静态文件检查不能代替模型行为验证。
- 不访问业务仓库、数据库或 CI；最终报告明确哪些仅静态验证。
