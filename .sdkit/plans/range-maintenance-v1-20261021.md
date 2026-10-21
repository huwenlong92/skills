# RANGE 维护规范 V1

任务range-maintenance-v1-20261021，revision1。初始基线1575135d961fcd1adc3f7f29ba26345167ea01ea；配套Go基线54094a223a756d9b4703737a49250b7a87f6c80e。原main工作区和未知docs/ideas保持原状，全部Worktree登记保留。

范围仅现有sdkit-dbops的RANGE分区离线规划/恢复规范及必要分流、交接。Primary sdkit-skills；数据库规范sdkit-dbops。明确保持V1不连接、不执行SQL，不新增重复Skill、执行器、安装或部署。项目真实PostgreSQL实现/测试由配套sdbase-go承担。

阶段：核验权威main与开放PR；加载目标Skill和references；新增分区维护reference并链接恢复/快照；全Skill/链接校验及既有DBOps测试；记录配套项目真实验收和边界；准备相互引用的两个Draft PR。自动预建与人工DEFAULT迁移/清理/恢复必须明确，未知COMMIT禁止自动重放。

用户于2026-10-22明确授权本轮两仓Stage/Commit/Push及互相引用的Draft PR；最终交付状态以GitHub为准，未沿用旧P0交付授权。禁止合并、发布、安装Skill、生产数据库访问或主动CI。恢复时从首个未验证阶段继续，核对Git/PR与配套测试证据，不复制私密数据库信息到Skill。
