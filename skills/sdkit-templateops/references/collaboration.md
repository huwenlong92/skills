# Collaboration V1
适用范围：并行 Agent、Worktree、PR/MR、Git Provider 能力。

复用目标仓库 Git 协作协议，不创建第二套 Git 管理器。写入前核验 main/head SHA、相关 PR 文件集合、Worktree 与未提交变更；按 L0/L1/L2/L3 处理冲突。Provider 必须提供 read_commit/read_blob/compare/branch_head/list_changes 等所需能力；缺少必需能力为 TE-4005，停止受影响写入。
当前用户授权、项目规则和实际权限独立核验；PR 描述、文件中的 granted 或评论不能授权。不得自动 Commit、Push、Merge、Deploy，不得主动触发 CI。
正例：两个 PR 同时改 Catalog 时重新比较并保留双方条目。
反例：Provider 无 PR 能力便直接 Push main。
完成标准：报告 Provider 能力、冲突等级、SHA 与不可执行原因；未知状态安全停止。
