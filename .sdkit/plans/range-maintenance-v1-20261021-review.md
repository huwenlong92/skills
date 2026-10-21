# RANGE维护规范V1验收

基线1575135d961fcd1adc3f7f29ba26345167ea01ea，独立任务Worktree；原main、未知docs/ideas及所有旧Worktree登记保留。开放PR22仅涉及sdkit-ui-design及其测试，已分页核验文件集，无本轮重叠（L0）。

变更限于既有sdkit-dbops：新增RANGE维护reference，更新主入口分流及快照/恢复链接。未增加Skill、数据库执行器或授权令牌，没有安装到Agent目录；V1仍不连接数据库、不执行SQL。规范包含catalog/OID/UTC、有限窗口补偿、DEFAULT冲突、同月事务内批次迁移、父子写入锁保护、行数/内容/引用/路由、Dry-run清理、已回滚/已提交/未知提交状态和独立备份恢复门禁。

本地校验：24个Skill全量validate通过；Markdown相对链接/锚点检查通过；既有DBOps95项测试通过。未执行跨Agent模型行为或生产操作；不把文档级检查说成Skill工具已具备执行能力。

配套sdbase-go在独立PostgreSQL测试/恢复库完成23/23 SQL矩阵、五模型Ensure与真实Crontab Handler race、11条样本完整备份恢复、两个月份显式提交DEFAULT修复及重复幂等。结果是配套项目维护工具的验证，不是本Skill执行了SQL。样本指纹保持不变、DEFAULT归零；旧验收库未修改。配套项目保留原8/8历史清理SQL，未重开发或开启生产清理。

源码在本地冻结；两仓独立Draft PR正文准备互相引用，用户于2026-10-22明确授权本轮两仓Stage/Commit/Push/Create-PR；最终状态以GitHub为准，未沿用旧P0审批。禁止合并、发布、安装Skill、部署及主动CI。完成一次后不扩张Schema治理。
