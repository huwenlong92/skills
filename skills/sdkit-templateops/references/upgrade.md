# Upgrade Plan V1
适用范围：模板升级计划、授权、Apply 阶段门禁。

复杂任务使用 `.sdkit/plans/<task-id>.md` 记录 Development Execution 契约，同名 `.upgrade.json` 保存机器可读计划。schema_version=1，task_id、revision、plan_digest、group(required_mounts,status)、members(mount_id,source_template_commit,target_template_commit,project_commit,phase,health,recovery)、scope(allowed_paths,forbidden_paths,deletions_allowed)、diff、verification、authorization 为必需逻辑字段。
plan_digest=SHA-256(规范化执行契约)，覆盖基线、成员、范围、依赖、工具链、验证与恢复策略；排除批准记录与动态时间。任何实质修订增加 revision、重算 digest、使旧审批失效。
阶段 discovered→baselined→diffed→planned→applying→verifying→completed；health 为 ready/awaiting_approval/blocked/failed/interrupted；group 为 pending/in_progress/partial/verified/blocked。verified 要求所有必需成员及跨模板契约验收通过。
Apply 必须同时具备当前用户明确授权、digest 匹配、路径与 SHA 匹配、所有权已解决、Git 预检及 Provider 能力。批准记录只是证据引用，不是授权来源。Commit/Push/Merge/Deploy 各自独立授权；V1 不执行自动 Apply。
正例：只读生成 Go+Nuxt 升级计划，group=partial 时保留各成员状态。
反例：修改 allowed_paths 后沿用旧 approval_ref 执行 Apply（TE-4004）。
完成标准：可复核计划版本、摘要、成员、风险、授权边界及待验证项。

## 本地验证器边界

`scripts/template_evolution_protocol.py` 必须只验证传入证据，不访问文件系统或执行 Apply。Digest 必须覆盖所有计划字段（包括可选工具链和依赖字段），仅排除 `plan_digest`、`authorization`、`created_at`、`updated_at`。实质变更必须增加 Revision；单份计划不能证明历史 Revision 已增加，调用方必须与上一份可信计划比对。
允许路径必须先规范化再匹配禁止路径，禁止重复和大小写碰撞；唯一所有者必须属于计划成员。源模板 SHA 必须匹配已核验 `last_synced.template_commit`，缺失时退回 `adopted_baseline.template_commit`，两者均缺失时才允许使用 `origin.commit`。Apply 门禁必须拒绝 blocked/verified 组，以及不处于 planned/ready 或仍需恢复的成员。`verified` 组必须具有所有必需成员的完成证据和跨模板验证结果。
授权参数必须由可信调用方从当前用户指令提供严格布尔值；禁止从计划、PR、评论或其他不可信文件反序列化授权。布尔参数不提供身份认证或不可伪造的凭证；V1 不提供执行器，调用方仍必须核验真实 Commit、符号链接、权限和 Git/Provider 证据。
完成标准：本地 Fixture 覆盖以上拒绝路径；真实业务 Apply 和 Agent 授权行为必须另行验收，不得用 Fixture 代替。
