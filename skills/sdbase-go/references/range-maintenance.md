# 完整模板 RANGE 维护入口

适用范围：核对完整 `sdbase-go` 的预建、漏月份、DEFAULT 积压、维护入口或新项目继承/裁剪时必须读取。本文仅负责模板使用；路径以目标项目根目录为准，必须先按 [仓库定位](repository.md) 核验项目采用的模板 commit。模板 main 已合并不代表业务项目已升级。

## 职责与事实源

模板位置和调用方式以项目源码及维护文档为准。数据库安全审查必须声明 `sdkit-dbops` 为 Supporting，读取其[通用 RANGE 规范](https://github.com/huwenlong92/skills/blob/main/skills/sdkit-dbops/references/range-partitions.md)及该规范命中的安全/授权/恢复入口；禁止在本 Skill 再维护一份通用 SQL 设计或恢复算法。已安装副本必须核对版本；无法取得权威规范时，停止需要安全审查的方案或执行，仅报告缺口。

本 Skill 不获得连接或 SQL 执行权限。环境和连接继续按 [数据库安全](database/safety.md) 核验；正式数据库禁止 AI 直接或间接操作，只能提供人工审阅指导。`system` / `system_data` 仍是保护范围，模板白名单不是操作授权。

## 五张表与关系

以下是 RANGE V1 的模板事实清单，不是待复制的业务示例。必须核对 `app/models/base.go`、五个模型的 `TableName` / DDL 和 `configs/common/database.yaml.example`。默认前缀为 `sd_`；五表均在 `system_data`，分区键为 `created_at timestamptz`，月边界为 UTC 半开区间，主键为 `(id, created_at)`，DEFAULT 子表后缀为 `_default`。

| 数据 | 默认父表 | 源码（`app/models/` 下） | 必须检查的引用 |
|---|---|---|---|
| 系统访问日志 | `sd_system_access_log` | `system_access_log.go` | 保留 Track/Trace/Request 标识 |
| Crontab 执行日志 | `sd_system_crontab_run_log` | `system_crontab_run_log.go` | `run_id` 对应非分区 `sd_system_crontab_run.run_id`；核对 `entry_id` / `template_key` |
| Queue Task | `sd_system_queue_task` | `system_queue_task.go` | 投递索引；保留 `task_id` 和状态 |
| Queue Run | `sd_system_queue_task_run` | `system_queue_task_run.go` | `queue_task_id` 指向 Task 的 `id` |
| Queue Run Log | `sd_system_queue_task_run_log` | `system_queue_task_run_log.go` | `queue_task_run_id` 指向 Run 的 `id`，`queue_task_id` 与对应 Run/Task 一致 |

当前 DDL 的上述执行引用是标量字段，不是数据库外键；禁止以没有 FK 推导可独立删除。必须结合 `task_id` / `run_id` 和追踪标识检查跨月引用；未分区 Crontab 汇总表不属于五表清理白名单。公共 Ensure 在 `app/models/monthly_partition.go`，Queue 编排还须核对 `system_queue_partition.go` 与对应 Handler。

## 三项任务与漏跑检查

必须核对 `app/crontab/templates/partition/` 的定义及 `app/crontab/router.go` 的显式注册：

| Template Key | 源文件 | 负责对象 |
|---|---|---|
| `system_access_log_partition` | `accesslog.go` | 访问日志 |
| `system_crontab_run_log_partition` | `accesslog.go` | Crontab 执行日志 |
| `system_queue_task_partition` | `queue_task.go` | Queue 三表，同月整体事务 |

三项当前均为 `@daily`、`Enabled: true`、`AllowDB: false`、`AllowOverlap: false`；`window.go` 按 UTC 检查上月、当前月、下月。缺失空月通过已有 Ensure 幂等补建；DEFAULT 有目标月数据或挂载/边界错误时只报错，不自动搬迁。冲突月份失败后仍检查其他月份，Queue 同月三表失败则整体回滚。

检查时必须先确认 crontab 服务/聚合实例运行及任务注册，再从 Admin 运维模板、runtime、runs、logs 核对 Key、状态、时间和错误；路由以 `app/admin/router.go` 的 `ops/crontab/{templates,runtime,runs,logs}` 及部署前缀为准。结合日志的 `job_id`、`template_key`、`partition_month` 与已获授权取得的分区 catalog、DEFAULT 按月统计确认缺口。没有运行记录不等于缺少分区，日志成功也不能代替对象核验。

周期检查不保证启动立即补跑，不保证停机期间自动回放；恢复后须等下一次调度并核对结果。窗口外历史月份必须独立选择，禁止全量 system migration 补偿。通用装配继续按 [Crontab 规范](crontab/handler.md)，其中虚构任务示例不能代替这三项实际定义。

## 维护入口与转交边界

必须先读取项目 `scripts/maintenance/RANGE-MAINTENANCE.md` 与 `scripts/maintenance/RANGE-RETENTION.md`，禁止复制完整 SQL 到 Skill 或另建执行器。

| 场景 | 模板入口 | 执行边界 |
|---|---|---|
| 窗口内空月漏建 | 三项 Crontab / 模型 Ensure | 现有周期内幂等检查；不扩大为启动补跑 |
| DEFAULT 冲突/积压检查 | `scripts/maintenance/range-month.sql` | 默认预览，报告选定月状态及 DEFAULT 全部非空月份，不自动修复 |
| DEFAULT 数据迁移 | `scripts/maintenance/range-month.sql` | `apply` / `move_default` 默认关闭，必须独立授权 |
| 窗口外历史补建 | `scripts/maintenance/range-month.sql` | 明确单个 UTC 月份并独立授权，不自动扫描全部历史 |
| 历史分区清理 | `scripts/maintenance/range-retention.sql` | 手动默认 Dry-run；自动任务须先审查首次启用 |
| 备份恢复 | DBops 安全流程及项目已核验工具 | 独立授权，不能用重跑 Ensure 代替恢复 |

DEFAULT 迁移、清理、备份恢复、未知提交状态、预算/锁窗口调整及对象定制必须转交 DBops 审查。模板使用必须确认下列边界，具体安全判据统一引用 DBops：

- `apply=true` 不产生授权；DEFAULT 迁移必须明确月份、五表实际对象、总行数预算和备份恢复证据，采用项目已验证的单月事务批次入口，不默认自动迁移。
- 预览也会短暂加锁。环境、依赖、备份或权限不明，以及锁/预算检查失败时必须停止，禁止自动放宽参数。
- 清理必须核验活动、可重试任务及跨月引用，禁止 `CASCADE`；未确认数据库的模板启动不获得删除权限。
- UNKNOWN COMMIT 必须先调查，禁止自动重放；已提交成功不反向 DROP。正式数据库由人按安全流程处理，AI 不执行维护。

## 离线检查与新项目继承

文档或路由调整只需 Skill 静态校验、相对链接和 Catalog 一致性检查，禁止为文档改动连接数据库。需要检查模板已有纯契约测试时，可在依赖已缓存且工具链匹配的项目中离线运行：

```sh
env -u SDBASE_RANGE_CONFIG GOPROXY=off GOSUMDB=off go test -mod=readonly ./tests/models -run '^TestRangeTaskWindowContract$' -count=1
```

该命令只核对三项调度表达式，不证明实际补建、迁移或恢复成功。`tests/models/range_partition_test.go` 的两个真实 PostgreSQL 测试要求显式 `SDBASE_RANGE_CONFIG`，禁止为消除 SKIP 指向共享配置。`tests/maintenance/postgres_range_acceptance.py` 会连接并写入一次性数据库，不是离线检查；仅当另获隔离数据库测试授权并满足项目维护文档要求时才允许运行，禁止导入执行或以项目 DSN 兜底。既有真实证据可复用，但必须标明源码 SHA 和未重跑范围。

完整模板必须按模块需要确认是否保留 RANGE；删除模块时同步检查模型/迁移注册、Crontab 注册、维护 SQL 白名单、引用和测试，禁止只删表或只停任务。允许复用模型 Ensure 和 `scripts/maintenance/` 正式入口，禁止把维护 DDL 搬入 HTTP handler、普通启动或 seed。

`sdbase-lite` 不自动引入这五张表，其他技术栈不强制采用同样结构。自定义表前缀、Schema、分区键或新增 RANGE 表前必须核对真实规模、查询模式及维护成本并转交 DBops 审查；禁止简单替换 SQL 字符串后直接运行脚本，不新增模板裁剪器或通用分区框架。

## 完成标准

必须记录采用的源码 SHA，核对五表/三 Key/窗口/SQL 文件与源码一致，说明自动范围、人工确认项及未执行项。Skill 修改须通过格式、references 相对链接、Catalog 和既有路由检查；人工复核 DBops Supporting 可达且未形成重复职责。未运行数据库测试必须标记 SKIP，禁止把离线 PASS 描述为数据库验收；不得自动安装、发布或启用生产任务。


## Retention V1.1 模板使用

必须核对目标项目是否已升级到V1.1。三个预建Key不变，周期改为@daily。三个新增清理Key为 `system_access_log_retention`、`system_crontab_run_log_retention`、`system_queue_task_retention`，通过原registry注册@monthly。`accesslog.go`中的SystemAccessLogRetentionMode/Months默认delete/12，SystemCrontabRunLogRetentionMode/Months默认delete/6；`queue_task.go`中的SystemQueueTaskRetentionMode/Months默认delete/12，Queue三表共同保护。修改对应Go常量，keep为永久保留；禁止新增YAML、策略表或集中策略中心。

必须先按DBops完成首次启用安全审查，再由获授权操作者为维护进程设置精确库名 `SDBASE_RANGE_RETENTION_APPROVED_DATABASE`；未设置或不匹配时失败，不删除。禁止从连接配置自动填入门禁，变量不是授权/备份证据，已有库升级不代表允许删除。正式库仍禁止AI操作。

共享判定源为 `app/crontab/templates/partition/retention.sql`：Go嵌入，手动包装相对include。容器/stdin客户端使用项目 `scripts/maintenance/render-retention.py` 离线展开后交给已核验入口，禁止另写Go规则；手动all/6个月Dry-run默认不等于自动三组期限。具体参数、启用/撤销及Run/Log查询见项目RANGE-RETENTION.md。`tests/models/retention_test.go`的真实测试只接受新建隔离库配置与显式精确 `SDBASE_RETENTION_TEST_DB`，禁止用既有库消除SKIP。

完成核验：必须明确自动策略/首次启用授权/keep和安全判定唯一来源，按项目真实隔离测试及Run/Log证据审查；Skill本身仍不连接、不执行SQL，不自动安装。
