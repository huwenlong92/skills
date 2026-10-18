# PR #13 Codex 真实行为验收计划

- 任务 ID：pr13-codex-behavior；revision：1；原始 Git 基线：913d0db61a27b6124f4c7beddb29435fb2f6064e。
- 目标：真实执行 T01–T10，核验计划、规范、范围、恢复与安全停止；静态检查和真实行为分别报告。
- 用户已授权：通过 Codex 模型服务发送公开协议、虚构代码/需求/计划、脱敏结果；允许范围内修复、Commit 和普通 Push。禁止发送凭据、真实业务数据、私有配置、环境变量全集及无关源码。
- 允许修改：PR #13 验收文档、协议测试、必要协议修复及 .sdkit/ 记录。禁止修改 PR #12、模板仓库、全局 Skill、main；禁止合并、部署、强推或主动触发 CI。
- 命中规范：根 AGENTS、standards/engineering-protocol-acceptance.md、development-execution.md、skill-orchestration.md、project-collaboration.md、collaboration-awareness.md。夹具只使用虚构 fixture-go 及 calculation/testing references。
- A verified：实时核验 main、#12/#13、Draft、工作区；main 为 537d6dad8220d3bc05596ff8051faeb7946084eb，#12 为 e912b9df9b11da45c5cf1069ea0674286869af91。
- B verified：十个隔离 Go 夹具逐项调用真实 Codex；T03 使用原会话续接，T07 使用新会话恢复；每项保存初始状态、输入、命令、结果、文件和 Git 差异。失败保留证据，环境限制记 BLOCKED。
- C verified，依赖 B：脱敏审查并落库报告；重新运行协议测试、Manager 测试及 validate --all，相对链接检查均退出 0。不得通过删除失败项或改变标准取得通过。
- D implemented，依赖 C：定向提交，Push 前重新 Fetch/核验远端；普通 Push 并确认 Draft/Open。
- D0/D1：仅范围内修复再测；D2/D3 暂停受影响部分并取得明确授权。修订保留历史。
- 恢复：先读此计划、TASKS、DECISIONS、HANDOFF，再核对 Git、真实调用和测试，不凭交接推断成功。

## 已执行证据

10 场景最终 PASS 10 / FAIL 0 / BLOCKED 0；14 次模型调用全部成功。T09 初轮 BLOCKED 已保留，经工具审查的临时 .git/ 目录授权后真实 Fetch 成功，保留未知文件并停止快进。报告与逐项证据见 [本次报告](../../docs/testing/engineering-v1/2026-10-18-report.md)。协议测试 17、Manager 测试 37、validate 12 均退出 0。D 的材料已完成；最终 Commit/Push 和 Draft 状态必须从实际 Git/PR 核验，不以计划代替实时证据。
