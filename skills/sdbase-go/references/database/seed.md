---
name: database-seed
description: sdkitgo 初始化数据、开发数据、演示 fixture 和 seed 命令规则
---

# Seed 与初始化数据规范

本文适用于 sdkitgo 项目的系统初始化数据、开发数据、演示 fixture 和迁移中的基线数据。新增或修改 seed 命令、初始化数据、代码托管基线、demo 账号或 data migration 分类时必须读取本文。

## 目录与依赖边界

- 项目根目录使用 `seeds/` 保存 seed 注册、分类和实现；`command/seed/` 只负责参数解析、配置加载、环境门禁和调用。
- `app/models/` 保存模型、表名、字段类型和与模型自身绑定的公共方法；不保存 seed 数据清单、跨模型 seed 聚合、seed 执行顺序或 `SeedXxx` 流程。
- seed 实现接收 `context.Context` 和明确的 `*gorm.DB`，不得依赖全局数据库变量。
- 依赖方向固定为 `command/seed -> seeds -> app/models/项目公共能力`，model 不反向依赖 seeds；seed 只消费 model 定义的能力，不把 seed 内容塞进 model。

## 数据归类

- 应用运行必需、必须随版本一致演进的协议元数据、内置注册项和系统分类，属于版本化 data migration，不属于可选 seed。
- 对既有业务行进行补齐、转换、审计记录初始化或兼容修复，属于 data migration/backfill，不使用 `SeedXxx` 命名。
- 由代码托管的系统定义必须使用独立、幂等的 system seed 或 reconciler，并明确哪些字段由代码覆盖、哪些字段允许运营修改。
- 开发身份、演示身份和演示业务数据属于 dev/demo seed，必须与系统基线数据分开。

## 运行模式与安全

- 批量 seed、测试身份及关联数据重建、会覆盖代码托管基线的 reconcile，以及其他影响多表或大量行的初始化操作，均属于数据库“大动作”：必须先完成可恢复且验证可读的备份、目标数据库核验和写入范围确认；未满足这些前置条件不得执行。
- `seed` 命令及其子命令只允许 `app.mode=dev`；空值、`test`、`prod`、`production` 和其他值全部拒绝。
- 环境门禁必须在数据库 DDL/DML 之前完成。seed 不得创建表、修改 schema 或隐式调用 `AutoMigrate`/migration。
- 执行 seed 前显式检查所需表是否存在；schema 不完整时提示先执行 migrate，并保证没有部分 seed 写入。
- 生产或共享环境的密码、token、密钥和其他真实凭据不得进入 seed、仓库、日志或命令输出。固定开发演示凭据必须明显标识为非生产用途，并受 `app.mode=dev` 门禁保护。

## 幂等与事务

- seed 必须可重复执行；使用稳定业务键和明确冲突策略，不以“表内已有任意一行”代替精确幂等判断。
- 同一组不可分割的初始化数据放在事务中；失败时不得留下无法识别的半成品。
- 代码托管数据的重命名、停用和权限迁移必须显式处理，不能只追加新行。
- demo seed 必须输出创建、跳过和冲突数量；仅当演示流程要求固定账号时才允许展示固定开发演示账号，且必须明确其仅适用于本地开发环境，不得混用真实凭据。

## 正向典型形态

具体 runner API 由目标项目已有 `seeds/` 入口决定；单个 seed 必须保留下面的依赖与事务形态，不得自行引入新的 seed framework：

```go
func SeedResourceTypes(ctx context.Context, db *gorm.DB) error {
	items := []models.ResourceType{
		{Code: "example", Name: "示例类型", Status: 1},
	}
	return db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		return tx.Clauses(clause.OnConflict{
			Columns:   []clause.Column{{Name: "code"}},
			DoNothing: true,
		}).Create(&items).Error
	})
}
```

上例只补缺失 `code`，不得在重复执行时覆盖运营可维护的 `name`、排序或状态。需要回填已有行时必须改为独立 data migration，不得把 `DoNothing` 换成无条件 update-all。

## 验收

- 至少验证：非 dev 模式被拒绝、schema 缺失时零写入、重复执行结果稳定、关键唯一键无重复。
- 涉及真实 PostgreSQL 行为、约束或事务时，使用隔离数据库验证，不复用开发共享库。
