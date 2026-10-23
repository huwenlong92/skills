# UI-AUTO-ARCHIVE · revision 1

- 原始基线：skills b2626326db37ddae931ca091db3aad42bd4208ce；GitHub/origin/main 已核验，无开放 PR。主工作区未知 docs/ideas/ 原样保留，新建独立 Worktree/分支 feat/ui-design-auto-archive，不清理既有 Worktree。
- Primary：sdkit-skills；目标仅 sdkit-ui-design 入口、MCP Reference、必要交接/测试/验收文档。不修改 Foundry、业务项目、安装目录或服务端 Schema。
- 依赖：MCP main 96ddaa53 的通用注册补丁先完成，服务端新增 allowAnyProject 配置但不新增接口/权限自动授予。两仓分别普通 Commit/Push、独立 Draft PR 并交叉引用，不合并、部署、重启、主动CI或真实存储/OAuth修改。
- 已确认行为：身份唯一直接复用；模糊时询问；同项目同任务范围持续保存授权可复用，切换/撤销/越界需重确认；注册不代表保存授权或资源读写；无原图 BLOCKED；MinIO/Git交接独立。
- C0 verified。C1：Skill manager validate --all、Markdown链接、工程协议、ui-design打包与交接静态回归及新增场景矩阵；明确不代表真实ChatGPT/模型隐式触发通过。C2/C3：保护原主工作区与未知文件，审阅精确Diff，独立Draft互引、核验Head。

- C1 verified：manager 24 Skill；全仓Markdown 382文件/1262链接/2锚点/0错误（新增本交接前），Skill自身35项与UI/工程协议26项共61项静态通过。A01–A10未执行真实模型，保留STATIC_ONLY。无安装或远端验收。
