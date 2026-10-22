# RANGE Retention V1.1

任务range-retention-v11-20261022，revision1，初始基线7093a0b047d805aabcbee051d2e4ad37317e80bb。仅预建daily、三组monthly策略（12/6/12月，delete/keep）、共享SQL内核、隔离真实测试、模板文档及既有Skill增量。禁止Core/YAML/集中策略表、现有数据库删除、安装/部署/CI。

Primary按仓库为sdbase-go/sdkit-skills；DBops离线安全审查、sdenv实际服务入口。原9部署/64忽略、草稿、全部Worktree、历史引用和已安装文件已外部快照保护。

共享方案：Go嵌入单一partition/retention.sql；手动psql用相对include同一SQL，事务/安全判断只有一处。组策略在原Template文件定义；数据库精确名进程确认门禁用于首次启用，flag不代替授权。

阶段C0基线保护已核验；C1实现；C2新建独立数据库验证及定向Go/race/Skill检查；C3两仓Draft或待授权成果。范围扩大、Core需求或环境身份不明须停止。中断从首个未验收阶段继续，真实证据不以静态测试替代。


C1 verified：daily预建及monthly三组清理已实现；代码常量delete/keep与12/6/12个月，首次启用精确库名门禁。单一SQL保留原Catalog/DEFAULT/活动与重试/跨月引用/RESTRICT判定，Go嵌入；手动包装相对include同一内核，容器客户端用离线渲染器展开。无Core/YAML/持久策略表修改。

C2：定向Go默认3包PASS；关键race3包34 PASS事件/5 SKIP（含子测试，真实配置门禁在独立真实测试执行）。实际标签crontab/serve构建、scripts/check-core-api.sh、go mod verify PASS。两个新建隔离PostgreSQL库分别执行真实Go清理和V1 SQL工具；SQL23/23、daily真实Handler/Ensure race、stdin渲染keep通过，13个清理场景含Run状态及提交后结果日志通过，最终精确库名夹具及13场景已全部PASS，见冻结报告。不读写旧验收库。

Skill：24校验、95项DBops unittest、376文档1244链接2锚点0错误。没有重跑无关全量/浏览器/Linux矩阵，没有等待实际日/月时钟或声称停机回放。原9部署/64忽略、草稿11文件、原8/48 Worktree登记、历史引用与464已安装文件哈希复核保留。代码源码SHA见同目录清单。

夹具偏差保留：离线五表dump不含CREATE SCHEMA，第二新库初次结构恢复失败，创建其空Schema后恢复成功；归档本就没有当前月分区，额外DROP探测报不存在而未删数据；SQL幂等夹具原来复用不含CREATE TEMP的DO，新内核包含临时表定义，改为只重建测试临时表后重跑，使用既有指纹/无已提交DDL门禁确认恢复。均不以忽略错误替代PASS，首次日志保留在受控证据目录。

C3：用户于2026-10-22明确授权本轮两仓Stage、Commit、普通Push及两个互链Draft PR；已重新核验远端main、开放PR、权限及冻结源码。本文为提交前授权检查点，最终Head/PR状态以GitHub为准；不合并、部署、安装或主动CI，不沿用旧任务审批。
