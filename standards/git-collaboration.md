# Git Collaboration V1

适用范围：SDKit 项目中本地 Git、远端 Provider、分支、Worktree、Commit、Push、PR/MR、Review、Merge 和中断恢复。涉及 Git 状态变更时必须按任务风险读取本协议。路径以目标仓库根目录为准。此协议不是独立 Skill、常驻程序或授权来源。

## 事实源与职责
- 目标仓库 AGENTS.md、当前用户授权和实时 Git/Provider 结果是执行门禁；.sdkit/ 仅持久交接，不是锁，也不替代实时状态。
- [Skill Orchestration](skill-orchestration.md) 负责路由，[Development Execution](development-execution.md) 负责 C0–C3 阶段，[Collaboration Awareness](collaboration-awareness.md) 负责 L0–L3 并行冲突；本协议仅负责 Git 操作。
- 单人默认允许在当前分支（包括 main）开发；真实团队必须遵守保护规则与 Review；多 Agent 是附加并发维度，不自动授予写入权限。
- 不创建第二套任务数据库、自动轮询或后台 Git 服务；不为感知主动触发 CI 或部署。

## 按需 Preflight
- P0 讨论与普通只读：不强制 Git 查询。
- P1 开始本地修改：确认仓库身份、当前分支/HEAD、工作区暂存/未暂存/未跟踪文件、进行中的 Git 操作及任务文件归属。
- P2 Commit、Push、同步和创建 PR：在 P1 基础上核验 remote fetch/push URL、upstream、目标 SHA、权限、授权与相关开放 PR；本地需按需 fetch。Commit 前审查精确 Diff、敏感信息、定向测试和暂存范围。
- P3 Merge、发布前 Git 校验及高风险恢复：在 P2 基础上核验 PR/MR head/base、Draft、mergeable、必需检查、Review、保护规则、依赖及证据所对应的 SHA。
- 同一检查点复用有效证据；Push、Merge 前必须重新核验关键远端状态。检查失败标记 UNKNOWN，不得将缓存视为实时事实。

## 状态模型与同步
工作区维度：CLEAN、DIRTY、OPERATION_IN_PROGRESS、UNKNOWN。
同步维度：SYNCED、AHEAD、BEHIND、DIVERGED、UPSTREAM_MISSING、REMOTE_REWRITTEN、UNKNOWN。REMOTE_REWRITTEN 仅在有历史远端 SHA 等充分证据时判定。
门禁维度：PASS、BLOCKED、UNKNOWN；仅 PASS 可执行对应写入。
- CLEAN + BEHIND 且确认祖先关系时允许 git pull --ff-only；DIRTY 不自动 stash、reset 或 clean。
- AHEAD 必须先确认远端目标未前进及 Push 授权；DIVERGED 停止自动同步，先提出 Merge/Rebase 方案并评估已发布提交。
- UPSTREAM_MISSING 不猜测远端；远端身份变化、历史重写或 UNKNOWN 必须停止受影响写入。
- Fetch 只更新远端跟踪信息，不代表本地工作分支已同步；未 fetch 的 ahead/behind 仅是缓存。
- Push 拒绝、网络超时或响应丢失时，先查询远端实际结果再决定是否重试，禁止盲目重复写入。

## 分支与 Worktree
- 本地单人小任务不强制 PR；复杂任务可采用短期分支或独立 Worktree；Web Provider 写入默认独立分支与 PR/MR。
- Worktree 生命周期：DISCOVER → ALLOCATE → ACTIVE → INTEGRATE → RETAIN/CLEANUP。创建时核验路径、分支占用、任务归属与授权。
- 禁止自动删除其他会话的 Worktree、分支、Stash 或未知文件；PR 已合并不等于可以清理。
- 清理前核验未提交、未跟踪、未推送提交及 PR 依赖，并取得独立清理授权。工作站绝对路径不得提交到 .sdkit/。
- 多 Agent 共用工作区须检查真实工作区状态；任务计划和 PR 不是文件锁。

## 授权与 Git 写入
- 修改文件、Stage、Commit、Push、创建 PR/MR、切 Ready、Review、Merge、Deploy 各自按当前任务和已核验工作流授权判断；前一步授权不自动推导后一步。
- 只暂存明确属于任务范围的路径，禁止无范围 git add .、git add -A、git commit .；不得提交凭据或未知文件。
- Provider 更新单文件时使用当前 blob SHA 等条件；多文件更新保留无关树项并检查预期父提交。条件写入能力缺失时报告竞态风险，不得声称原子安全。
- 禁止未经明确授权的 force push、reset --hard、clean、历史重写及绕过分支保护。
- 提交、Push、PR、合并、部署和真实访问状态必须分别核验报告。

## PR/MR 与 Merge
- PR/MR 创建前核验分支、目标、Diff 和权限；Draft/Ready、Review 和 Merge 均按独立操作门禁执行。
- Merge 前必须重新核验目标 PR 的 Head SHA、Base、Draft、Review、必需 Checks、保护规则、Mergeable、相关 PR L0–L3 风险及合并授权；缺少必要证据为 UNKNOWN，停止。
- 仅使用目标 Provider 和仓库允许的 Merge 方法；不因 Provider 不支持某项能力就模拟成功或通过直接 Push 绕过。
- 合并后核验目标分支最终 SHA；本地同步和部署属于后续独立步骤。

## 冲突与失败恢复
- 流程：DETECT → SNAPSHOT → DIAGNOSE → RESOLVE → VALIDATE → CONTINUE/ABORT。Snapshot 是保存证据，不自动 Commit 或 Stash。
- Merge/Rebase/Cherry-pick 中断时识别操作状态、冲突路径、原始提交及未提交修改；不得无条件采用 ours/theirs、rebase --skip 或删除未知锁文件。
- Abort 也会改变工作区，必须确认操作来源、修改归属和可能损失；不能证明安全时保留现场并停止。
- 冲突解决后必须运行相关测试、复核 Diff 与远端状态；网络或 Agent 中断恢复时先核验是否已经完成写入，禁止重复执行。
- 失败时保留工作区、分支、证据及任务交接，不能用 reset --hard 或 force push 消除问题。

## Provider 能力与降级
- GitHub、Gitee、GitLab 的能力分别发现，字段不能假定等价。
- 每项能力声明 SUPPORTED、UNSUPPORTED 或 UNKNOWN；每项操作门禁独立返回 PASS、BLOCKED 或 UNKNOWN。能力存在不等于账号有权限或当前对象已满足检查。
- Draft、Review、Checks、Branch Protection、Merge、Conditional Write 不可查询时，不得假称通过；影响必要门禁时停止，保留可审阅结果。
- Provider 不支持 PR/MR 或安全 Merge 时，报告限制，不得绕过保护直接推主分支。

## 发布前 Git 事实核验
只核验目标 Commit、分支同步、相关 PR 合并状态、测试/CI 证据所对应 SHA 与冲突状态；不得执行部署，也不得将本地测试通过等同远端已合并或线上已部署。

## 正向与反例
正向：确认仓库及授权 → 检查工作区 → fetch 并比较 SHA → 仅暂存任务文件 → 定向测试 → Commit → Push 前重新核验 → 远端验证。
反例：发现远端前进后执行 reset --hard 或 force push，或者把 GitHub mergeable=true 当作 Review/CI/授权全部通过。

## 完成标准
- P0 不误触发全量 Git 检查，P1–P3 的必要证据与 UNKNOWN 阻断可追溯。
- 本地领先、落后、分叉、脏工作区、远端重写及 Worktree 并行不会静默覆盖修改。
- Commit、Push、PR、Merge、Deploy 授权隔离；Provider 缺失能力安全降级。
- 静态协议测试、隔离真实 Git CLI 测试与真实 Agent 行为测试分别报告；未运行的类别标记待验证。
