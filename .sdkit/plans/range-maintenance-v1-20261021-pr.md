# sdkit-dbops：补齐RANGE分区维护与安全恢复规范

为既有sdkit-dbops补充分区预建、漏跑、DEFAULT迁移、清理和恢复的离线审查规则，新增reference并链接主入口/快照/恢复。保持V1不连接、不执行SQL；不新增重复Skill或执行器，不安装或发布。

明确自动有限窗口空月预建与人工DEFAULT搬迁/清理/恢复的边界，要求精确目标、catalog/OID/UTC、备份恢复证明、有界批次和单月事务、父表及直接DEFAULT写入保护、标量引用/整行/路由检查；未知COMMIT必须调查，禁止自动重放。通用reference不包含业务项目清单、账号、机器路径或凭据。

验证：24 Skill校验、全仓Markdown链接及95项DBOps现有测试通过。配套sdbase-go项目工具独立真实PostgreSQL23/23、备份恢复、实际提交修复及模型/Handler race证据另在其PR；这些结果不代表本Skill获得SQL执行权限或通过跨Agent行为验收。

配套：huwenlong92/sdbase-go 同名range-maintenance-v1分支；两个Draft PR创建后正文互相链接。原main及未知docs/ideas、所有Worktree保留；PR22文件集无重叠。本地成果已验收，用户于2026-10-22明确授权本轮两仓Stage/Commit/Push及互相引用的Draft PR；最终交付状态以GitHub为准。保持Draft，不合并、不发布、不安装、不部署、不主动CI。
