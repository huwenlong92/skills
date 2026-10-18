# Recovery V1
适用范围：升级中断、构建失败、恢复和补偿。

发生中断时保留工作区、补丁、基线 SHA、修改路径、命令退出码与证据；health=interrupted，recovery=required。恢复前重新核验 Git、相关 PR、其他 Agent 新修改；禁止 reset --hard、force push、盲目反向覆盖或清理未知文件。
恢复结果为 restored/partially_restored/unresolved。restored 必须内容比对原始基线通过；partially_restored 保留原始基线并生成新计划 Revision；recovered 不自动意味着 completed。跨仓库多模板不承诺原子事务，使用补偿计划。
正例：隔离 Worktree 中止后保存补丁，重新核验差异再恢复。
反例：升级失败时直接 reset --hard 丢弃并行开发修改。
完成标准：记录恢复前后 SHA、保留的业务修改、验证证据及残余风险。
