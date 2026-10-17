---
name: models-hooks
description: sdkitgo GORM BeforeCreate 的标识生成、创建默认值、行内校验和其他 lifecycle hook 边界
---

# Models Hooks 规范

本文适用于 sdkitgo model 的 GORM lifecycle hook。新增或修改 `BeforeCreate`，或评审其他 lifecycle hook 时必须读取本文；修改 model 字段同时读取 [struct.md](struct.md)。

## 放置位置

- hook 必须定义在对应 model 的同一个 `app/models/{table}.go` 文件中，并紧跟在 model struct 后面。
- 禁止建立通用 hooks 目录，禁止把单表 hook 放入 handler、`app/http` 或 `app/infra`。
- 多个 model 需要相同的稳定标识生成或纯值校验时，只有已经存在两个以上 model 调用方且语义完全一致，才允许提取为 `app/models` 包内 private helper；否则必须直接写在各自 `BeforeCreate` 中。

## 只使用 BeforeCreate

- 新业务 model 只允许新增 `BeforeCreate`。
- `BeforeCreate` 允许生成创建时稳定标识、填充创建专属默认值、归一化当前 row 字段，以及验证只在创建时成立的行内不变量。
- 除 `BeforeCreate` 外，其他 lifecycle hook 不属于 sdkitgo 的常规写法，禁止自行新增。只有用户在当前任务中明确指定某个 hook 时才允许实现，并必须重新确认其触发路径、事务和批量写入行为。
- 既有 model 已存在其他 lifecycle hook 时，本次任务未修改该 hook 或其依赖字段就不得顺带重构；任务命中时必须先说明实际行为和调用入口，不能把历史存在当作新代码依据。
- create 与 update 都需要执行的业务逻辑必须由各自 handler 的显式写入流程承担；禁止为了复用而新增覆盖多个写入阶段的隐式 hook。

## 行为边界

- `BeforeCreate` 必须使用 GORM 规定的 `func (row *Xxx) BeforeCreate(tx *gorm.DB) error` 签名，并通过返回 error 阻止创建。
- `BeforeCreate` 只允许读取或修改当前 row，禁止查询或写入其他表，禁止引用全局 `database.DB` 或开启 transaction。
- `BeforeCreate` 禁止发送 realtime event、投递 queue、写文件、调用 HTTP、发送邮件或调用第三方服务。
- `BeforeCreate` 禁止承担权限、Session、请求参数、response、状态流转或跨表一致性逻辑；这些逻辑必须在 handler 的显式流程中可见。
- `BeforeCreate` 禁止依赖 association；model 不定义 association 的规则以 [struct.md](struct.md) 为准。
- 依赖 `BeforeCreate` 的创建入口必须使用 model struct 执行 GORM `Create`/`CreateInBatches`。使用 map、原生 SQL、COPY 或其他不保证触发 model hook 的入口时，必须在写入前显式生成并校验相同字段，禁止假设 hook 会执行。
- 只属于当前 model 的创建时标识、前缀和默认值必须直接放在该 model 文件及其 `BeforeCreate` 中；禁止仅为共享几行生成代码建立项目级 infra 注册表。
- 标识的格式、长度和字符集必须沿用目标项目已经确认的公开契约。实际 sdkit 依赖已有满足要求的随机或编码能力时必须直接复用；没有满足要求的能力时必须按 [framework/boundary.md](../framework/boundary.md) 判断归属，禁止复制参考项目的具体格式或临时建立项目 wrapper。
- 只有两个以上 model 已经使用完全相同、且不包含实体前缀或业务枚举的生成机制时，才允许提取 `app/models` 包内 private helper；跨项目通用的纯生成机制必须按 [framework/boundary.md](../framework/boundary.md) 判断为 sdkit `pkg/` 候选。

## 正向示例

```go
func (row *Resource) BeforeCreate(_ *gorm.DB) error {
	row.Name = strings.TrimSpace(row.Name)
	if row.Name == "" {
		return errors.New("resource name is required")
	}
	if row.Status == "" {
		row.Status = ResourceStatusDraft
	}
	return nil
}
```

创建时稳定标识必须使用同样的空值判断直接写入 `BeforeCreate`，并保持调用方预先传入的合法值。唯一性必须由 unique index 和 handler 的错误映射保证，禁止在 `BeforeCreate` 中先查询数据库。

## 验收

- `BeforeCreate` 必须位于对应 model 文件并紧跟 struct，只读取或修改当前 row。
- hook 生成稳定标识时必须测试空标识自动生成、预设合法标识保持不变、非法格式和 unique constraint；其他 hook 必须测试默认值、归一化与非法行零写入。
- 存在 batch、map、原生 SQL 或 COPY 创建入口时，必须逐个核对是否触发 hook；不触发时必须测试显式生成和校验路径。
- 必须运行 `rg -n 'func \([^)]*\) (Before|After)[A-Z][A-Za-z]+\(' app/models --glob '*.go'`；新增 hook 不是 `BeforeCreate` 且没有用户当前任务的明确要求时即不通过。
