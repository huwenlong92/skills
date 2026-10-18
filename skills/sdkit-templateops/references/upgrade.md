# Upgrade Plan V1
适用范围：模板升级计划、授权、Apply 阶段门禁。

复杂任务使用 `.sdkit/plans/<task-id>.md` 记录 Development Execution 契约，同名 `.upgrade.json` 保存机器可读计划。schema_version=1，task_id、revision、plan_digest、group(required_mounts,status)、members(mount_id,source_template_commit,target_template_commit,project_commit,phase,health,recovery)、scope(allowed_paths,forbidden_paths,deletions_allowed)、diff、verification、authorization 为必需逻辑字段。
plan_digest=SHA-256(规范化执行契约)，覆盖基线、成员、范围、依赖、工具链、验证与恢复策略；排除批准记录与动态时间。任何实质修订增加 revision、重算 digest、使旧审批失效。
阶段 discovered→baselined→diffed→planned→applying→verifying→completed；health 为 ready/awaiting_approval/blocked/failed/interrupted；group 为 pending/in_progress/partial/verified/blocked。verified 要求所有必需成员及跨模板契约验收通过。
Apply 必须同时具备当前用户明确授权、digest 匹配、路径与 SHA 匹配、所有权已解决、Git 预检及 Provider 能力。批准记录只是证据引用，不是授权来源。Commit/Push/Merge/Deploy 各自独立授权；V1 不执行自动 Apply。
正例：只读生成 Go+Nuxt 升级计划，group=partial 时保留各成员状态。
反例：修改 allowed_paths 后沿用旧 approval_ref 执行 Apply（TE-4004）。
完成标准：可复核计划版本、摘要、成员、风险、授权边界及待验证项。
