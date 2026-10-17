---
name: database-migration
description: sdkitgo PostgreSQL schema、DDL、迁移、分区和历史数据回填规则
---

# Database Migration 规范

本文适用于 sdkitgo 项目的数据库迁移、schema 创建、分区表 DDL 和历史兼容。新增或修改 migration、schema、DDL、索引、约束、分区维护或历史数据回填时必须读取本文。

开始结构开发或连接数据库前必须先遵循 [safety.md](safety.md)：先备份，再在本地开发与验收，最后按授权同步增量迁移到远端开发库。正式库只允许提供人工执行指导，本文任何执行步骤均不得作为 AI 操作正式库的例外。

## 迁移入口

- 项目根目录的 `migrations/` 负责迁移入口、执行顺序、跨表/跨领域编排、schema 与父表创建、约束/索引/触发器、历史数据回填和旧表搬迁；`command/migrate/` 只负责参数解析、配置加载和调用。
- `app/models` 负责模型结构以及与单张表自身绑定的公共能力。仅当 `EnsureXxxPartition` 需要同时被 migration、crontab 或运维入口调用时，才允许定义在对应模型文件中。
- `app/models` 不保存 `MigrateXxx`、跨表迁移流程、历史回填流程或独立 `*_migrate.go`；单表公共 helper 不读取命令参数、不加载全局配置，也不顺带操作无关模型。
- schema 创建必须早于对应 schema 下的表迁移。
- 新增 schema 时，必须同步更新 schema ensure 逻辑。
- 领域迁移 helper 不读取命令参数、不加载全局配置，也不顺带执行无关领域迁移。

## 运行模式

- 项目内直接执行的 `migrate` 命令只允许 `app.mode=dev`；空值、`test`、`prod`、`production` 和其他值全部拒绝。
- 模式校验必须发生在数据库 DDL/DML 之前，失败时返回明确错误，不允许先执行一部分迁移再拒绝。
- 非开发环境的 schema 变更必须走项目明确建设的受控发布/运维流程，不复用开发命令绕过环境门禁；正式库流程只能由人执行，AI 禁止触发发布流水线代执行。
- `seed` 不得隐式调用 migration；需要一键初始化开发环境时，另建显式 setup 编排，内部仍按 migrate 后 seed 的顺序调用。

## 在已有环境执行迁移

- 凡数据库“大动作”必须先备份再执行。这里包括 schema/表迁移、批量 seed、批量清理或回填、账号/组织体系重建、跨表数据修复、约束或索引调整，以及所有影响多表或大量行的操作。备份必须可恢复并已验证可读；同时完成目标数据库核验和对象/数据范围白名单后才能写入。
- 业务功能开发不得把无关关键 schema 的清理、重建或聚合迁移当作前置步骤。当前业务不依赖该 schema 变更时必须继续业务主线；确需变更时必须拆成独立任务，先完成可恢复且验证可读的备份，再按表、字段、索引和数据范围白名单执行。
- 只执行覆盖本次变更的最小迁移入口。业务域改动调用对应领域或业务迁移，不得为了“顺便补齐”而执行无关的全量 `AutoMigrate`、system migration 或其他 schema 迁移。
- 执行前必须列明本次允许变更的 schema、表和迁移函数；实际 SQL 或对象范围超出清单时立即停止，不把新暴露的历史问题夹带进当前需求。
- 项目只有聚合迁移入口、但本次只需其中一部分时，必须调用能覆盖本次对象的已有领域 `MigrateXxx`/`AutoMigrateXxx`。仅当不存在可单独调用的领域入口时，才允许增加窄范围命令或 helper；禁止用全量入口代替。
- 对已有数据环境执行 DDL 前先做可恢复备份，并验证备份可读；需要稳定写入视图时先停止相关 writer/worker/crontab。
- 不得假设聚合迁移整体处于一个数据库事务中。迁移中途失败后，必须审计失败前已提交的对象和数据变化，再决定继续、回滚或单独维护；不能仅凭最后一个错误宣称“数据库没有变化”。
- 迁移、回滚和补建完成后，核对对象清单、约束/索引、父表总行数和数据路由，并记录实际执行入口与结果。

## 普通表

- 仅普通、非分区 GORM model 的非破坏性创建和兼容变更允许使用 `AutoMigrate`。
- 修改已有字段、索引、默认值时，必须考虑历史数据和线上兼容。
- 禁止依赖 `AutoMigrate` 处理破坏性变更；涉及数据搬迁、类型不兼容、删改对象或多步约束切换时，必须使用显式 SQL 或受控迁移步骤。

## 分区表

- PostgreSQL 分区表不依赖 `AutoMigrate` 创建父表。
- 分区父表、默认分区、月分区、索引、注释使用显式 DDL。
- RANGE 分区使用 UTC 边界。
- 主键或唯一约束必须包含分区键。
- 保留 default 兜底分区，避免漏建月分区时写入失败。

## 缺失分区维护

- 先通过 `pg_inherits`/`pg_partition_tree`、定时任务运行历史和 default 分区按月行数确认确实缺失的父表与月份；已经存在的分区不得重复处理。
- 缺少少量分区时，使用一次性、窄范围维护命令调用对应 model 已有的 `EnsureXxxPartition`，只传明确的表和月份；禁止通过全量 system migration 间接补建。
- 定时任务错过执行不等于缺少 Ensure 方法。先判断服务在计划时间是否运行、任务是否有成功/失败记录，再决定补跑命令或修调度能力。
- 如果 default 分区已经包含目标范围数据，直接 `CREATE TABLE ... PARTITION OF` 或简单调用 Ensure 会被 PostgreSQL 拒绝。此时必须：
  1. 备份并停止相关 writer；
  2. 在单一事务中锁定父表；
  3. 把目标时间范围行复制到事务级临时表并从 default 删除，复制数和删除数必须一致；
  4. 调用已有 `EnsureXxxPartition` 创建明确月份分区；
  5. 通过父表重新写入暂存行，让 PostgreSQL 自动路由；
  6. 核对恢复数、父表迁移前后总行数和 `tableoid` 路由；任何一步不一致都整体回滚。
- 一次性维护命令必须写死或白名单限制允许操作的父表和月份，执行前验证 default 与目标分区的挂载关系；不得接受未经校验的用户表名或任意 DDL。
- 仅用于一次单环境修复的维护命令只允许放在仓库外的隔离临时工作目录，并必须保留执行内容与结果记录；需要第二次执行、进入版本管理或交由其他操作者运行时，必须改造成仓库内受权限、审计和幂等保护的正式 ops command。禁止把一次性维护脚本放入 `app/models`、普通 migration 或业务 handler。

## DDL 安全

- DDL helper 只接收代码生成的表名、分区名、索引名和注释内容。
- 不把用户输入传入 DDL 字符串构造。
- SQL 标识符使用 `quoteIdent` 或项目已有 helper。
- SQL 字符串字面量使用 `quoteLiteral` 或项目已有 helper。
- 常规 `migrate up` 必须保持非破坏性：禁止删表、删 schema、清表以及隐式删列；历史结构切换应拆成独立受控运维入口，不得放进每次开发都会运行的领域 migration。
- PostgreSQL 单个 migration domain 必须在事务中执行；仅当目标 DDL 被 PostgreSQL 明确禁止在事务中运行，或项目 migration runner 不支持事务且本次任务不允许修改 runner 时，才允许拆成受控步骤，并必须写明已提交步骤、停止条件和补偿动作。提交前必须比较迁移前后的已有表身份；已有表消失或被删后重建时必须回滚。承载账号、组织等关键数据的 schema 还必须校验迁移后行数不得减少。
- 仓库外临时脚本不得加载项目共享配置后执行破坏性 DDL。只读取证脚本连接共享数据库后必须先启用只读事务；临时写脚本只能操作明确核验名称的一次性数据库，或改造成仓库内受测试、受审计的窄范围命令。
- 集成测试中的 `DROP DATABASE`、`DROP SCHEMA`、`DROP TABLE` 和 `TRUNCATE` 只能针对测试刚创建且名称经过前缀和随机后缀核验的一次性数据库；不得把项目配置 DSN 作为测试数据库兜底。

## 正向典型形态

根目录 `migrations/` 必须显式注册迁移顺序。普通表通过 model 指针注册，分区表通过窄范围 `Ensure` 入口注册：

```go
type Migration struct {
	Name  string
	Model any
	Up    func(ctx context.Context, db *gorm.DB) error
	Index func(ctx context.Context, db *gorm.DB) error
}

func All() []Migration {
	return []Migration{
		gormMigration("resource", &models.Resource{}, "Code", "DeletedAt"),
		resourceLogMigration(),
	}
}

func resourceLogMigration() Migration {
	model := &models.ResourceLog{}
	return Migration{
		Name:  "resource_log",
		Model: model,
		Up: func(ctx context.Context, db *gorm.DB) error {
			return models.EnsureResourceLogTable(ctx, db)
		},
		Index: func(ctx context.Context, db *gorm.DB) error {
			return models.EnsureResourceLogTable(ctx, db)
		},
	}
}
```

`All` 只表达顺序与注册；单表 Ensure 只操作所属表；跨表回填与旧表搬迁必须在 `migrations/` 的领域 migration 中编排。禁止把全量 `All()` 当成单表修改的验收入口。

## 验收

- DDL、分区表、索引和 schema 变更必须在真实 PostgreSQL 或项目已有的隔离数据库测试环境验证。
- 分区补建至少验证：目标分区存在且边界正确、default 仍挂载、父表总行数不变、目标月份数据不再落入 default、重复检查不会扩大操作范围。
- 如果不能验证，必须说明未验证原因和风险。
