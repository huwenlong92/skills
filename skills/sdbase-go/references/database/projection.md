---
name: database-projection
description: sdkitgo list 与 detail 查询的本地 projection、关联展示和 JSON 聚合规则
---

# Database Projection 规范

本文适用于 list/detail 响应 projection 和关联展示数据。新增或修改读接口字段、GORM projection、关联对象、聚合 JSON 或查询结果转换时必须读取本文。

## 本地 Projection

- list 和 detail handler 禁止返回完整 GORM model；只有写入、状态迁移、模型钩子或业务校验需要实体当前状态时才允许查询完整 model，且响应仍必须使用接口 projection。
- 使用 handler 内的本地匿名 projection struct。只有树形响应需要 `Children []Xxx` 自引用时，才允许在当前 handler 内定义 named response type；禁止因此创建 package-level 通用 View。
- detail handler 使用 `var detail struct { ... }`。
- 只 select 前端实际消费的字段。
- 一次性 handler projection 不定义 named response struct。
- 单条 projection 使用 `Take`，由 `gorm.ErrRecordNotFound` 表达未命中；只有业务明确需要按主键取首条的排序语义时才使用 `First`。多条 projection、分组和聚合结果使用 `Scan`。禁止为了投影先查 model 再手写 loop 转换。
- 不同 HTTP 入口必须分别维护自己的 projection；即使底层表相同，也禁止为了复用而返回包含多个入口字段并集的通用 View。
- 当前结果行的关联对象或关联数组能通过 `JOIN`、`LEFT JOIN LATERAL`、相关子查询或聚合得到时，必须直接在当前 handler 的 SQL projection 中完成；单条用 `Select + Take`，多条用 `Select + Scan`。禁止先加载 model，再按行补查关联或调用一层完整的 projection service。
- 禁止扫描扁平结果后使用 Go `for range` 查询关联、建立临时映射、把关联字段写回 struct 或拼装 JSON object/array。循环只允许处理数据库无法表达的非关系型业务计算，并且必须说明 SQL 无法表达的具体输入或规则。
- Detail 同时包含两个及以上相互独立的一对多集合，并且放入同一查询会形成集合间笛卡尔积或需要额外去重时，必须在同一 handler 中按集合分别执行有界查询，最后直接组合 response。禁止为了追求单条 SQL 把无关集合交叉 Join，也禁止把这些查询包装成单调用方 service/helper。
- 长查询必须先构造 `model`，筛选条件按业务分支追加到 `model`；最后只把短执行语句放入 `if err := model.Take/Scan(...).Error; err != nil`。该错误分支先处理 `gorm.ErrRecordNotFound`，随后直接处理剩余错误，不再重复判断 `err != nil`。禁止把整个查询构造链压缩进错误判断。

示例：

```go
list := make([]struct {
	ID     int64  `json:"id"`
	Name   string `json:"name"`
	Status int32  `json:"status"`
}, 0)
```

## 关联展示数据

- 关联展示数据默认必须返回嵌套 JSON object 或 array，禁止返回展开的扁平字段。没有命中下述例外时直接采用嵌套结构，不得把常规 projection 选择交还给用户。
- 只有目标 API 已有无法在本次任务中变更的公开兼容契约，或用户明确指定当前接口属于特殊扁平场景时，才允许保留旧扁平字段；实现和验收记录必须写明命中的例外，且不得给新字段延续该形态。
- Category 关联必须返回 `category: {"id":1,"code":"...","name":"..."}`，禁止新增 `category_name`、`category_code` 等扁平字段。
- Collection 关联必须返回 `collection: {"id":1,"name":"...","code":"..."}`，禁止新增 `collection_name`、`collection_code` 等扁平字段。
- 单个关联对象使用 `datatypes.JSONMap` 并设置 `gorm:"type:jsonb"`。
- 关联数组、聚合子项、options 子列表使用 `datatypes.JSON` 并设置 `gorm:"type:jsonb"`。
- 后续给关联对象加字段时，只更新 SQL `jsonb_build_object`；禁止继续增加扁平字段。
- 展示模型能在一次 SQL 查询构造时，使用 `jsonb_build_object`、`jsonb_agg` 或 `LEFT JOIN LATERAL`。
- 可空单个关联必须使用 `CASE WHEN relation.id IS NULL THEN NULL ELSE jsonb_build_object(...) END`，禁止返回所有属性均为 `null` 的伪对象；关联数组无记录时必须通过 `COALESCE(..., '[]'::jsonb)` 返回空数组。
- Projection struct 中同一关联对象的字段必须聚合成一个 JSON 字段；关联对象字段集中排列，随后列出当前资源自己的标量字段。禁止把同一关联的 `id`、`code`、`name` 分散到顶层。

接口正向结构如下；`author` 和 `category` 是完整关联对象，`name`、`age`、`sex` 属于当前资源：

```json
{
  "author": {
    "id": 18,
    "name": "示例作者"
  },
  "category": {
    "id": 6,
    "name": "示例分类"
  },
  "name": "示例条目",
  "age": 3,
  "sex": 1
}
```

禁止改成 `author_id`、`author_name`、`category_id`、`category_name` 与当前资源字段混排。

关联数组同样由数据库直接返回 JSON array：

```json
{
  "authors": [
    {"id": 18, "name": "示例作者甲"},
    {"id": 27, "name": "示例作者乙"}
  ],
  "category": {"id": 6, "name": "示例分类"},
  "name": "示例条目"
}
```

## SQL 直接构造 JSON object 与 array

- 单个关联对象的 projection 字段使用 `datatypes.JSONMap`；SQL 使用 `jsonb_build_object`，可空关联外层使用 `CASE`。
- 关联对象数组的 projection 字段使用 `datatypes.JSON`；SQL 使用带稳定 `ORDER BY` 的 `jsonb_agg(jsonb_build_object(...))`，并在外层使用 `COALESCE(..., '[]'::jsonb)`。
- 一对多数组必须通过相关子查询或 `LEFT JOIN LATERAL` 在当前行范围内聚合；禁止直接 Join 后由 Go 按行归组。
- JSON object 和 array 中只放接口实际消费字段；禁止把完整 model 转成 JSON 后塞入 projection。

下面的虚构列表同时返回一个 `category` object 和一个 `authors` array：

```go
list := make([]struct {
	Authors  datatypes.JSON    `json:"authors" gorm:"type:jsonb"`
	Category datatypes.JSONMap `json:"category" gorm:"type:jsonb"`
	ID       int64             `json:"id"`
	Name     string            `json:"name"`
}, 0)

model = model.
	Joins(`LEFT JOIN LATERAL (
		SELECT jsonb_agg(
			jsonb_build_object('id', author.public_id, 'name', author.name)
			ORDER BY link.sort ASC, link.id ASC
		) AS authors
		FROM ` + database.Table(&models.CatalogItemAuthor{}) + ` AS link
		INNER JOIN ` + database.Table(&models.CatalogAuthor{}) + ` AS author
			ON author.id = link.author_id AND author.deleted_at IS NULL
		WHERE link.item_id = item.id AND link.deleted_at IS NULL
	) AS item_authors ON TRUE`).
	Select([]string{
		"item.id",
		"item.name",
		`CASE
			WHEN category.id IS NULL THEN NULL
			ELSE jsonb_build_object('id', category.id, 'name', category.name)
		END AS category`,
		`COALESCE(item_authors.authors, '[]'::jsonb) AS authors`,
	})
if err := model.Scan(&list).Error; err != nil {
	response.Error(c, errors.ErrInternalServer)
	return
}
```

## 独立集合与整棵树

- 主对象附带多个独立事件流、历史集合或回执集合时，每个集合使用自己的匿名 slice 和一条集合查询；查询、排序和错误处理直接保留在当前 detail handler。
- 每条集合查询内部仍必须用 SQL 构造其单个关联 object 或 array，禁止对集合结果逐行补查。
- 全部查询成功后使用一个 `response.Success(c, gin.H{...})` 组合主对象和各集合；任一查询失败时立即返回错误，禁止返回缺少部分集合的伪成功响应。
- 同一数据库父子关系需要直接返回完整树形 JSON，并且节点内容、过滤和排序都能由 SQL 表达时，必须使用 CTE、`jsonb_build_object` 和 `jsonb_agg` 在 PostgreSQL 中组装最终数组，再通过 PGX `QueryRow` 扫描原始 JSON。只有树节点还必须合并非数据库来源，或包含无法由 SQL 表达的项目业务计算时，才允许在 Go 中组树；普通平面列表禁止为了炫技改用整段原生 SQL。

树形响应需要自引用类型，因此允许在 handler 内定义 named type；数据库必须直接返回有序 JSON array，空树固定为 `[]`：

```go
func GetCatalogTree(c *gin.Context) {
	type nodeResponse struct {
		ID       int64          `json:"id"`
		Name     string         `json:"name"`
		Children []nodeResponse `json:"children"`
	}

	ctx := c.Request.Context()
	pool := database.PGX(ctx)
	if pool == nil {
		response.Error(c, errors.ErrInternalServer)
		return
	}

	table := database.Table(&models.CatalogNode{})
	sql := `
		WITH nodes AS (
			SELECT id, parent_id, name, sort
			FROM ` + table + `
			WHERE deleted_at IS NULL
		), child_nodes AS (
			SELECT id, parent_id, sort,
				jsonb_build_object(
					'id', id,
					'name', name,
					'children', '[]'::jsonb
				) AS node
			FROM nodes
		), root_nodes AS (
			SELECT root.id, root.sort,
				jsonb_build_object(
					'id', root.id,
					'name', root.name,
					'children', COALESCE((
						SELECT jsonb_agg(child.node ORDER BY child.sort ASC, child.id ASC)
						FROM child_nodes AS child
						WHERE child.parent_id = root.id
					), '[]'::jsonb)
				) AS node
			FROM nodes AS root
			WHERE root.parent_id = 0
		)
		SELECT COALESCE(
			jsonb_agg(node ORDER BY sort ASC, id ASC),
			'[]'::jsonb
		)
		FROM root_nodes`

	var raw []byte
	if err := pool.QueryRow(ctx, sql).Scan(&raw); err != nil {
		response.Error(c, errors.ErrInternalServer)
		return
	}
	tree := make([]nodeResponse, 0)
	if len(raw) > 0 {
		if err := json.Unmarshal(raw, &tree); err != nil {
			response.Error(c, errors.ErrInternalServer)
			return
		}
	}
	response.Success(c, tree)
}
```

上例展示两层树；支持更深层级时必须在 CTE 中逐层或递归构造 `children`。没有命中非数据库来源或 SQL 无法表达的例外时，禁止查询全部行后在 Go 中按 `parent_id` 二次拼树。

## 验收

- 必须核对 projection 只包含当前接口消费字段，一次性 projection 位于 handler 内，且不同入口没有共享字段并集 View。
- 存在扁平关联字段时必须核对并记录兼容契约或用户明确指定的特殊场景；没有例外依据即不通过。
- 单条详情必须验证未命中分支；列表和聚合必须验证空集合以及至少一条含关联数据的结果。
- 必须通过 SQL 日志、查询计数测试或代码检查确认不存在逐行补查；JSON 关联字段必须核对 `gorm:"type:jsonb"`，无单个关联时返回 `null`，无关联数组时返回 `[]`，数组元素顺序稳定。
- 必须搜索本次 handler 中处理查询结果的 `for`/`range`；用于关联查询、临时映射或 JSON 组装时即不通过，命中明确的非数据库计算例外时必须人工核对说明。
- Detail 包含多个独立集合时，必须确认查询数按集合数量固定，不随主对象或集合行数增长；禁止出现多个一对多 Join 形成的重复行。
- 树形 SQL 必须验证空树、单层和最大支持层级，核对每层 `children` 都是数组且排序稳定；JSON 反序列化失败必须返回内部错误。
