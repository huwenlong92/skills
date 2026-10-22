# sdkit-dbops / sdbase-go：RANGE Retention V1.1职责增量

仅更新现有两份RANGE reference：模板负责daily/monthly、代码策略、启用与维护入口；DBops负责自动删除首次审查、授权、备份/事务/引用/恢复边界。V1继续不连接、不执行SQL，不新增/安装Skill或执行器。

# RANGE Retention V1.1 — daily预建与monthly安全保留

现有RANGE V1有窄范围手动清理SQL，但没有模板内置按组清理。本轮将三项预建改为@daily，新增三项@monthly清理，默认delete：访问日志12个月、Crontab日志6个月、Queue Task/Run/Run Log关联组12个月；keep永久保留。策略直接在对应Go Template文件，不新增YAML/集中策略表/Core修改。

Go嵌入与手动psql包装共用一份SQL内核，不在Go复制删除判据。内核按真实Catalog边界，保留DEFAULT/无限/嵌套分区，活动/重试/跨月引用保守保护整个Queue组，Run Log→Run→Task，RESTRICT无CASCADE；有界锁与整组事务回滚。Go只在提交成功后写结果日志，正式Runner的Run/Log真实持久化已验证。

首次启用必须独立审查并由操作者设置精确库名SDBASE_RANGE_RETENTION_APPROVED_DATABASE；未设置/库名不匹配时失败且不删除。该门禁不是授权或备份证明。现有开发/原验收库本轮不启用；正式库禁止AI执行。手动默认all/6个月/Dry-run，与自动三组策略分别说明；容器入口用离线render-retention.py展开同一内核。输出列改为parent_name/qualified_name/action/reason，旧外部解析器须适配。

验证：两个本轮新建隔离PostgreSQL库，Go 13项真实清理/race场景、daily漏月/DEFAULT/幂等实际Handler/Ensure、V1 SQL23/23与stdin共享渲染keep；Go定向3包、关键race34 PASS事件/5离线门禁SKIP、实际标签crontab/serve构建、Core API与模块校验PASS。24 Skill/95 DBops测试/376文档1244相对链接2锚点0错误。既有验收数据未连接，真实原文件未删除。不等待实际日/月触发，不重复无关全量/race/browser/Linux矩阵。

保护：原main继续正常检出，9部署/64忽略文件、Skills11草稿、原8 Go/48 Skills Worktree登记、全部旧引用及464已安装Skill文件哈希保留。只在独立分支开发，不安装Skill、不部署、不主动CI。

限制：Queue保护为原SQL的保守全组策略，持续活动可使清理持续跳过；keep不恢复已删除数据，UNKNOWN COMMIT先调查，禁止自动重放。无生产启用或安全备份已验证的暗示。

配套仓库同名分支codex/range-retention-v11-20261022；两仓Draft创建后正文互相引用，最终Head与链接以GitHub为准。基线、文件清单、实际命令、夹具首错修正和冻结源码哈希见本计划及清单。用户于2026-10-22明确授权本轮两仓Stage、Commit、普通Push及两个互链Draft PR；最终Head/PR状态以GitHub为准，不沿用旧任务审批。
