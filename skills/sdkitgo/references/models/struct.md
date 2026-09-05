---
name: models-struct
description: sdkitgo GORM model 的文件组织、schema、字段 tag、注册表和分区表写法
---

# Models Struct 规范

本文适用于 sdkitgo 服务中的 GORM model struct。新增或修改 model、表名、schema helper、字段类型、业务注册表或分区表 model 时必须读取本文；基础字段选择同时读取 [base.md](base.md)，model lifecycle hook 读取 [hooks.md](hooks.md)，DDL 和迁移流程同时读取 [migration.md](../database/migration.md)。

## 文件组织

- database model 必须按一张表一个 Go 文件组织。
- 文件名必须使用业务表名，例如 `item.go`、`item_option.go`。
- 单表拥有的常量必须放在该表 model 文件里。
- status 常量必须有注释说明业务含义。
- 只有真正被多张表共享的常量才允许移动到公共文件。
- 仅当基础表尚未形成独立业务域且确实跨域共享时，才允许使用 `public` schema；项目已建立对应业务 schema 时，新表必须进入该 schema，禁止继续落入 `public`。
- 仅平台或系统内部表，例如 system menus、roles、admins，允许使用 `system` schema；业务表禁止进入 `system` 或 `system_data`。

## Model 内容边界

- 普通 model 文件只允许包含该表的常量、`TableName`、持久化 struct 和符合 [hooks.md](hooks.md) 的 `BeforeCreate`；只属于该表的创建时标识前缀和默认值常量也必须留在这里。分区表仅额外允许 [database/migration.md](../database/migration.md) 规定的 model-local partition ensure、spec 和 DDL helper。
- Model 文件禁止访问全局 `database.DB` 或其他连接，禁止定义 `XxxCheckExist`、`FindXxx`、`GetXxx`、`ListXxx`、`SaveXxx`、`DeleteXxx` 等查询、CRUD 或业务编排方法。
- 存在性检查、状态读取、关联查询和普通写入必须直接放在使用它们的 handler、worker handler 或 crontab run handler；满足两个以上真实调用方和稳定共享契约时，才按 [infra/placement.md](../infra/placement.md) 提升为 capability。
- 禁止为了让 model 看起来“自包含”而把请求上下文、权限、response、realtime、queue 或外部调用放入 model receiver method。
- 数据库连接初始化、连接池、日志器和迁移聚合入口禁止放入 `app/models`；这些能力必须使用项目已经接入的 core database 与根目录 migration 入口。

## 表名与字段名简化

- schema 已经表达业务域时，表名必须使用领域内最短且不失真的局部名称，禁止重复 schema 或领域前缀。例如使用 `catalog.item`，禁止使用 `catalog.catalog_item`。
- 聚合内从表必须保留表达所属关系所需的聚合根名称，例如 `catalog.item_option`；禁止为了缩短名称写成无法判断归属的 `catalog.option`。
- model 类型已经表达当前实体时，字段名禁止重复 model 或表名。例如 `CatalogItem` 必须使用 `Code`、`Name`、`Status`，禁止使用 `ItemCode`、`ItemName`、`ItemStatus`。
- 引用其他实体的 ID 必须保留被引用实体语义，例如 `CollectionID`、`CategoryID`；禁止缩写成 `CID`，也禁止简化成含义不明的 `RefID`。
- 字段名禁止添加不表达新语义的 `Value`、`Text`、`Data`、`Info` 后缀。只有同一 struct 中确实需要区分不同表示时，才允许使用带表示语义的后缀。
- database column 默认使用 GORM 的 snake_case 映射。只有默认映射不符合既有物理字段名时，才允许添加 `column:`；禁止为每个字段重复声明可由 GORM 稳定推导的列名。

## Schema

- schema 常量必须定义在 `app/models/base.go`。
- schema 必须按稳定业务域划分，禁止按用户角色、前端页面或单个功能拆分。只有数据归属、状态机、权限边界或迁移生命周期形成独立领域时，才允许新增业务 schema。
- 必须使用现有 schema helper，禁止在每个 model 里手写 schema 前缀：
  - `publicTable(namer, table)`：普通业务表。
  - `systemTable(namer, table)`：平台或系统表。
  - `systemDataTable(namer, table)`：系统运行数据和分区日志。
- 项目有业务隔离 schema 时，必须使用该 schema 对应 helper，例如 `catalogTable(namer, "item")`。
- 传入 schema helper 的 `table` 必须是未加 `TablePrefix` 的业务表名，例如传 `item`，禁止传 `sd_item`。
- 非 `public` schema 已经表达领域名称，schema 内的表必须使用领域内局部名称，禁止重复 schema 名。物理表名统一为 `<schema>.<TablePrefix><local_table>`：
  - 使用 `catalog.sd_item`、`catalog.sd_item_option`，禁止使用 `catalog.sd_catalog_item`、`catalog.sd_catalog_item_option`；
  - 使用 `content.sd_entry`、`content.sd_entry_revision`，禁止使用 `content.sd_content_entry`、`content.sd_content_entry_revision`；
  - 使用 `workflow.sd_job`、`workflow.sd_job_attempt`，禁止使用 `workflow.sd_workflow_job`、`workflow.sd_workflow_job_attempt`。
- schema helper 必须接收局部表名，例如 `catalogTable(namer, "item")`；`sd_` 等全局表前缀只允许由 GORM `TablePrefix` 产生，禁止在 helper 参数、`TableName` 返回值或迁移 DDL 中重复硬编码。
- 聚合内从表允许保留聚合根前缀来表达关系，例如 `catalog.sd_item_option`、`workflow.sd_job_attempt`；必须省略的是已经由 schema 表达的领域前缀，不是所有业务含义前缀。
- Go model 类型允许保留领域前缀以避免同一 `models` 包内重名，例如 `CatalogItem`、`ContentEntry`；Go 类型名不决定物理表必须重复领域前缀。
- 新增非 `public` schema 时，必须同步加入 `EnsureSchemas`。
- `TableName` 必须使用 `func (Xxx) TableName(namer schema.Namer) string`，并返回匹配的 schema helper。

## 业务注册表与代码枚举

- 初始由 migration 或 seed 预置、以后允许运营人员新增、改名、排序、调整适用范围或停用的数据，必须建成业务注册表并提供后台维护能力；禁止因为首期只有少量记录就写死在前后端。
- 同一份业务选项只能有一个服务端权威来源。
- 状态机状态、权限动作、协议常量、不可由运营改变的安全规则必须继续使用代码枚举；禁止把流程合法性和授权边界下放到普通数据表。
- 注册表 `code` 是稳定业务标识，创建后不可修改；被历史业务数据引用的记录禁止物理删除，必须使用 `active`、`disabled` 等状态停用。只有名称、说明、排序和明确标记为运营可维护的策略字段允许编辑。
- migration 或 seed 只允许补齐缺失编码，使用 `ON CONFLICT DO NOTHING` 或等价逻辑；禁止在每次启动时 upsert 覆盖管理员已维护的数据。一次性回填新字段时，必须以字段或列首次出现等明确条件控制，禁止重复覆盖。
- 业务写接口必须重新校验引用的注册表记录仍为启用状态，并校验类型、数据区域、组织类型等适用范围；前端下拉框过滤不能替代服务端校验。
- 停用被其他启用配置引用的注册表记录时，必须拒绝操作并返回可理解的业务错误。

## 分区表

- PostgreSQL 分区表必须显式定义 migration，禁止依赖 `AutoMigrate` 创建分区父表；父表、分区键、边界、约束和 default 分区规则以 [migration.md](../database/migration.md) 为唯一权威定义。
- 分区表 model 文件必须把 model struct、供 migration、crontab、运维入口复用的 partition ensure 函数、partition spec 或单表 DDL helper、indexes 和 comments 放在一起。
- 跨表迁移入口与执行顺序必须放在根目录 `migrations/`，禁止放入 `app/models`。
- 父表、索引、分区创建和注释必须使用 model-local helper，例如 `tableIdentWithName`、`quoteIdent`、`quoteLiteral`、`partitionTimeLiteral`。
- helper 输入必须来自代码生成的表名、分区名、索引名或注释内容；禁止把用户输入传给 DDL 字符串构造。
- 多张分区表共享迁移模式时，必须使用本地 partition spec helper，禁止在多个文件重复 parent SQL、index、comment 执行逻辑。

## 字段类型

- 每个持久化业务字段必须在 `gorm` tag 中包含准确的 `comment:`；comment 必须描述字段业务含义，禁止只重复 Go 字段名或数据库类型。
- 主键、外部标识、状态、时间、金额、数量和关联 ID 也必须带 `comment:`，不得因名称看似明确而省略。
- PostgreSQL array 字段必须显式设置 GORM type，包括 `pq.Int64Array`、`pq.StringArray`、`pq.Int32Array` 等类似类型。
- model 或 GORM-parsed projection struct 中的 `datatypes.JSON`、`datatypes.JSONMap` 必须显式设置 `gorm:"type:jsonb"`。
- 必须使用真实 PostgreSQL 类型，例如 `bigint[]`、`integer[]`、`text[]`、`_varchar`。
- 禁止依赖 GORM 推断上述类型。

## 禁止外键与 ORM 关联

- model struct 禁止定义 GORM association 字段，禁止使用 `foreignKey:`、`references:`、`constraint:` 或级联删除、级联更新 tag。
- migration 禁止创建数据库 foreign key constraint。
- 表间关系必须使用 `XxxID`、`XxxIDs` 等标量字段表达，并按查询路径添加普通 index 或 unique index。
- 关联读取必须在 query 或 handler 中显式使用 `JOIN`、子查询或独立查询；禁止依赖 `Preload` 隐式装载 model association。
- 删除或更新父记录时，业务一致性必须由显式事务、存在性检查和状态检查保证，禁止依赖数据库级联动作。

```go
type Article struct {
	CategoryIDs pq.Int64Array  `json:"category_ids" gorm:"type:bigint[];comment:文章分类内部ID列表"`
	Categories  datatypes.JSON `json:"categories" gorm:"type:jsonb;comment:分类查询投影"`
	TagIDs      pq.Int64Array  `json:"tag_ids" gorm:"type:bigint[];comment:文章标签内部ID列表"`
	Tags        pq.StringArray `json:"tags" gorm:"type:_varchar;comment:文章标签名称列表"`
}
```

## 正向典型形态：`app/models/xxx.go`

一个 model 文件必须同时表达状态常量、`TableName`、字段 GORM 约束和末尾的 `BaseFullModel`：

```go
package models

import "gorm.io/gorm/schema"

const (
	// ResourceStatusDisabled 表示资源已停用。
	ResourceStatusDisabled int16 = 0
	// ResourceStatusEnabled 表示资源已启用。
	ResourceStatusEnabled int16 = 1
)

func (CatalogItem) TableName(namer schema.Namer) string {
	return catalogTable(namer, "item")
}

type CatalogItem struct {
	ID             int64  `gorm:"primaryKey;comment:内部主键" json:"-"`
	CollectionID   int64  `gorm:"type:int8;not null;index;comment:所属集合内部ID" json:"-"`
	Code           string `gorm:"type:varchar(64);not null;default:'';uniqueIndex;comment:条目稳定编码" json:"code"`
	Name           string `gorm:"type:varchar(128);not null;default:'';comment:条目名称" json:"name"`
	Description    string `gorm:"type:varchar(512);not null;default:'';comment:条目说明" json:"description"`
	Status         int16  `gorm:"type:int2;not null;default:1;index;comment:条目状态" json:"status"`
	BaseFullModel
}
```

如果项目尚未建立独立 `catalog` schema 且该表符合 `public` 条件，`TableName` 必须改用 `publicTable(namer, "item")`；禁止直接返回 `"catalog.item"` 或手写 `sd_` 前缀。

## 验收

- 必须核对一张表对应一个 model 文件，表名由匹配 schema 的 helper 生成，且 helper 参数不包含全局 `TablePrefix`。
- 必须核对表名未重复 schema 领域，字段名未重复当前 model 名；关联 ID 保留被引用实体语义。
- 必须按 [base.md](base.md) 核对基础 model 选择与嵌入位置。
- 每个持久化业务字段的 GORM tag 必须包含业务含义准确的 `comment:`。
- model、migration 和数据库 schema 中不得出现 foreign key constraint；model 不得出现 GORM association 字段或关联 tag。
- `app/models` 不得出现全局数据库访问、普通查询、CRUD 或业务编排方法；分区 ensure 和符合规则的 `BeforeCreate` 必须逐项核对其限定边界。
- array、`datatypes.JSON` 和 `datatypes.JSONMap` 字段必须具有明确 GORM PostgreSQL type。
- 分区表修改必须继续通过 [migration.md](../database/migration.md) 的 DDL 与数据路由验证。
- 注册表修改必须验证 `code` 不可改、被引用记录不可物理删除、停用依赖检查和 options 唯一来源。
- model 创建时标识修改必须核对常量与 hook 位于对应 model 文件，并检查 unique index、数据库约束和不触发 hook 的写入入口保持同一契约。
