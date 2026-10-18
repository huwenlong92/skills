# PR #15 最终 Squash 前集成

适用范围：用户明确授权的专题 A 最终按序 Ready 与 Squash Merge。同步前 Head `32f9d9a9ac16221b8c760dbc77c0dc93c819d350`，本次合并前 main `a874524db55edae7bd7d9613b74a1d03ac6ff8b4`。前置 PR 已验证 Squash Merge，当前在本 PR 独立 Worktree 普通 Merge 最新 main。

## 冲突与证据

冲突仅限四个 `.sdkit/` 状态文件，各冲突段都是不同 PR 的历史决策、任务与验收段落。逐段联合，保留双方原始行序、历史 SHA、成功/失败及限制；不按整文件 ours/theirs，不把历史禁止本地合并当作本轮当前授权。当前用户已授权 Ready、精确 Head 锁定的 Squash Merge；其余真实配置/安装/业务/旧库/部署/主动 CI 禁令继续有效。

Nuxt API 环境变量、主题目录、新旧入口、409 组原始审计、原覆盖统计、audit.json SHA-256（314f6bed66360cc67291a28fb8f33c3cd9f5a9e7b7cdf86c2117df270b344ad6）及 R027–R044 补充逐字节保留。R042 仍阻塞、R043 仍部分通过，不升级外部协议验收。五组 Node 测试在原隔离模板归档实际重跑 36/36，退出 0，详见 squash-final-template.json。

双方 docs/ 的全部既有材料逐字节保留，技术栈 Reference 与相应父版本一致，新旧 Reference 除身份说明一致，共享 Orchestration/Foundry/UI 语义未变；见 [保留核验](squash-final-preservation.json)。不引入 #20/#21 或其他未合并 PR。

## 本轮验证

Python **118/118**，全部退出 0：工程协议 17、Manager/迁移 44、DockerOps 41、Markdown 7、ui-design 9。21 Skill、Markdown 相对链接/锚点、Diff、Reference 一致性及敏感/个人路径扫描通过，结果见 [本轮检查](squash-final-checks.json)。路由语义无实质变化，复用此前适用真实 Codex 证据，本轮模型调用 0。

Ready 前/后必须重新核验 Open/main/Head、main 祖先关系、权限、保护与 Rulesets、审查及检查、mergeable；只有全部通过才以 sha 与 merge_method=squash 合并。合并后必须验证 merged=true、closed、main 前进、单父为前置 main、整树等于验收 Head 后，才进入下一 PR。

完成标准：上述门禁与合并后验证全部满足；精确同步 Head/Squash Commit/最终 main 由实时 GitHub 交付记录与最终回复给出。任一步失败停止后续合并，不绕过保护或测试，不自动操作其他 PR。
