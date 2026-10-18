# PR #20 最终本地集成验收契约

任务 ID：pr20-final-integration；Revision 1；日期：2026-10-18。

## 基线与授权

原始 PR Head：`d406eedfaf52f72dd1652dc566518f74c95aaf31`；main：`226465e5f951cc1f1394a1c91e4c3f682f822b83`；共同祖先：`77e0664fcbb0943f9bd4aa8cad96ab0d14fa4c3a`；初始 main/PR 独有提交 5/11。
用户明确授权独立 Worktree、普通 Merge、范围内修复、必要测试与证据、Commit 和普通 Push。禁止 PR Merge、Ready、部署、主动 CI、历史重写、未知文件或其他 Worktree 清理、真实配置和业务仓库写入。

## 范围与规范

Primary：sdkit-skills；命中管理流程、Foundry publishing、WikiOps repository 和用户指定的根协议。允许修改 PR 原有八个文件、必要 scripts 测试、docs/testing/git-collaboration-v1 证据及本任务 .sdkit 记录。其他 main 内容必须逐字节保留。D0/D1 范围内处理；D2/D3 停止受影响修改并取得批准。

## 阶段与验收

1. C0 已核验：仓库身份、Fetch/Push URL、ADMIN、远端实际 SHA、开放 #20/#21/#22、分支规则为空、原工作区仅未知 docs/ideas、不存在当前进行中操作、其他 Worktree 与 Stash 清单。#21/#22 无目标路径重叠，L0；本次 main 集成入口冲突 L2。
2. 集成 implemented：从远端 Head 创建新 Worktree；普通 Merge main，AGENTS 唯一文本冲突。审查 Base/Ours/Theirs，保留两个入口；验证所有未授权路径相对 main 未变后才可 verified。
3. 本地验证 verified：全仓现有 Python 测试、Manager、链接锚点、Catalog、Reference/安全/协议审查及 G01–G20 真实 CLI。命令/退出码/数量以报告和 JSON 为准。
4. 真实 Agent blocked：全新隔离 home 登录检查退出 1，Not logged in；按用户停止条件不调用模型，不复制认证。16 项逐项保留 BLOCKED；不能用 CLI/静态证据冲抵。
5. C2/C3 implemented（交付前检查已执行，Push/远端读回待执行）：再次 Fetch，确认 PR Head/main、Diff 与权限，普通 Commit/Push 后读回。保持 Draft，技术总验收因 Agent 阶段阻塞不得标记 verified。

## 恢复

读取本计划、报告与四份状态文件，重新核对工作区、Merge 状态和远端。恢复模型测试必须具备隔离正常认证及文件/网络边界验证；只发送公开协议和虚构材料，禁止读取或复制用户认证内容。

本地最终：263 unittest 全通过、21 Skill、G01–G20 CLI 20/20；初次 Foundry 路径差异通过规范化 TMPDIR 消除，失败历史保留。Reference 完成标准顺序调整属 D1。#24 新增 Orchestration L2 交集，审查后不引入，未来须联合重测。整体阶段保留 blocked（真实 Agent），不以静态和 CLI 冲抵。

## Revision 2：真实 Agent 续验（2026-10-18）

当前用户明确授权解决隔离登录、真实 A01–A16、必要测试修复与普通 Commit/Push。基线 dbf71b252cefe799625cb7b81bde95b2beb783ab；main 226465e5f951cc1f1394a1c91e4c3f682f822b83。用户自行完成独立 home 官方登录，状态命令退出 0，未读取/复制认证内容。用户授权在外网连接失败时执行 proxy auto。

离线权限探针通过：夹具内读写与 Git Commit 允许；夹具外合成文件读写、真实用户配置可读性检查均拒绝；工具网络关闭。首次发现 CLI 自动注入四个系统 Skill，在隔离配置中逐项禁用后重新离线检查，模型输入无 SKILL.md 或用户目录。不修改真实配置。

A01–A16 使用独立虚构仓库，原始 JSONL/会话标识只留本地。脚本断言和模型自述均不能代替人工工具审查。A05 若缺真实 Provider 创建能力，必须 BLOCKED；不使用模拟 Provider 冒称 PR 已创建。后续阶段以新报告和逐项证据为准，禁止 Ready/Merge/部署/主动 CI。

Revision 2 阶段记录：真实模型 19 次均退出 0 且完成；最终 15 PASS/0 FAIL/1 BLOCKED（A05 Provider）。A02/A03/A04 首轮环境阻塞保留，新夹具精确权限重测通过。main 前进到 8777b036311349fef7a99cdf094c36fd7011c15c，普通 Merge 无冲突；共享 Git 语义未改。真实行为阶段 implemented，A05 条件缺失，不得标整体 verified；Commit/Push 最终状态以交付读回为准。

Revision 2 · 并发 main 第二次前进：#24 合入到 957c5e49a53acc8343b09a4a875a430db57deac2。先保存 #21/真实证据 Merge Commit 938d61662452044e3b421f2e4e072ce9d5331c04，再普通合入新 main。三份状态文件冲突审查 Base/Ours/Theirs 后保留双方；Orchestration 校验为新 main 原文加原 Git 入口。只重跑受影响静态/模板/Catalog 检查；Git 场景模型证据不因无关模板路由增量失效，不重复模型调用。

## Revision 3：A05 真实 Provider 最终验收

用户明确同意专用私有测试仓库创建，并授权证据/脚本普通 Commit/Push。A05 一次真实隔离调用，实际官方 gh 创建 Draft PR #1 并独立读回，通过；16/0/0。完整命令与前后状态见 cases/A05.json，旧 Provider BLOCKED 原证据保留。main 新增 DBOps 离线功能已普通 Merge，无冲突；共享 Git 语义未变，不重复无关模型调用。完成定向回归/保全/安全扫描与 Push 读回后，本任务可报告受控 Ready 技术条件；仍禁止实际 Ready/合并/部署/主动 CI。专题 A 全局规则退出单独裁定。
