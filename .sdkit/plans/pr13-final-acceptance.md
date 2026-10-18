# PR #13 最终本地验收计划

- 任务 ID：pr13-final-acceptance；revision：1；用户已授权验收、范围内修复、Commit 与普通 Push。
- 原始 Git 基线：6b519574bb2fe63a595be84a4e054c3080e92b82；main 基线：537d6dad8220d3bc05596ff8051faeb7946084eb。
- 允许范围：PR #13 的协议、协议测试、根协议入口和本次验收/交接记录；禁止修改 PR #12、模板仓库、全局 Skill、main，禁止合并、部署、强推或触发 CI。
- 命中规则：AGENTS.md、standards/project-collaboration.md、standards/collaboration-awareness.md、standards/skill-orchestration.md、standards/development-execution.md；管理检查使用 sdkit-skills 及 references/workflow.md。
- 阶段 A：核验实时 Git/PR 与范围，比较 PR #12；状态 verified，远端 Head 与文件集已读取，无重叠，L1 显式依赖。
- 阶段 B：修复范围内语义与测试，运行协议测试、Manager 校验、Markdown 链接与隔离集成；状态 verified。协议测试 17/17、Manager 测试 37/37、单独 validate 12/12 与叠加 PR #12 后 validate 20/20 均退出 0；链接检查通过。实际命令见 STATUS.md。
- 阶段 C：独立 Codex 行为验证；状态 blocked。沙箱启动后模型路由连接失败，退出 1；网络重试被自动审批拒绝，等待验收材料发送授权。禁止把静态测试标作行为通过。
- 阶段 D：审查差异、定向 Commit、Push 前重新核验 Head，普通 Push 并检查 Draft/Open；依赖 B，状态 in_progress。行为验证阻塞允许交付 Draft 修复，但不能宣称最终行为验收通过。
- 偏差门禁：范围内遗漏为 D1；扩大模块或改变架构为 D2/D3，先停止受影响工作并取得授权；计划变更增加 revision，保留历史。
- 恢复：读取本文件、TASKS/DECISIONS/HANDOFF，再核对实际 Git、PR 与测试证据；禁止只凭本计划认定完成。

## revision 2（2026-10-18，新增授权后续验收）

保留 revision 1 和原始 Git 基线作为历史。先前阶段 D 的修复已普通 Push，实际提交为 913d0db61a27b6124f4c7beddb29435fb2f6064e；本次用户明确授权脱敏模型调用，阶段 C 已由 [真实行为计划](pr13-codex-behavior.md) 完成，10 场景最终通过。上文网络与审批阻塞为历史记录，不能当作当前状态；最新验收见 STATUS.md 与实际 PR。
