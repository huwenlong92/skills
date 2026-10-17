---
name: database-batch-write
description: sdkitgo 大批量导入、同步、staging、upsert 和集合式合并规则
---

# Database 批量写入规范

本文适用于数据同步、批量导入、范围生成、批量回填和其他大量记录写入。新增或修改批量抽取、staging、批量 upsert、集合式合并、watermark、同步证据或性能验收时必须读取本文。

## 基本原则

- 禁止在大数据循环中逐条执行 `First`、`Take`、`Save`、`Create` 或单行 upsert。同步流程必须批量抽取、批量落 staging，并通过数据库集合操作合并。
- 源库读取必须使用流式 rows 和可配置 fetch size，边读边组成有上限的批次；禁止把完整源数据集一次性加载进 Go 内存。
- 不需要冲突处理的普通批量写入必须使用 `CreateInBatches`；需要冲突处理时必须组合 `clause.OnConflict`。仅当使用接近验收规模的数据证明 GORM 批量写入达不到明确性能目标时，才允许改用项目已接入的数据库批量导入能力。批次大小必须按字段数量、单行大小和数据库参数限制统一配置，禁止在循环中写死不同常量。
- 大规模原始数据落地经压测确认 GORM 批量写入不足时，必须使用项目已接入的数据库批量导入能力；禁止在业务项目 `app/infra` 自行封装通用 COPY、驱动或连接池。

## Staging 与集合式合并

- 同步数据必须先写入带 `sync_run_id`、源记录键和原始哈希的 staging 或 raw 表，校验成功后再合并业务表；禁止从源系统直接逐条更新正式业务表。
- 合并使用 `INSERT ... SELECT ... ON CONFLICT DO UPDATE`、`UPDATE ... FROM`、`NOT EXISTS` 等集合 SQL，一次处理一批或一个数据集。
- 只更新源哈希或参与业务映射的字段确实变化的记录，避免无变化数据反复刷新 `updated_at`、索引和审计日志。
- 缺失检测、软失效和关系重建通过 staging 与当前数据集合比较完成，不在 Go 中逐行判断。
- 仅当维表最大行数有明确上限且在验收数据规模下内存占用符合项目预算时，才允许一次加载为映射；大事实表和关系表不得为了查外键把全量数据加载进 map，也不得逐行查询外键，必须通过 staging 字段和目标表 `JOIN` 批量解析。

## 事务、幂等与进度

- 每次同步具有稳定的 run ID；每个数据集记录抽取、写入、插入、更新、未变化、失效、拒绝数量。
- 批次重试必须幂等。唯一约束至少覆盖数据源、数据集和源记录键，重复执行不得产生重复目标记录或重复关系。
- 增量 watermark 只在该数据集校验和合并全部成功后推进；失败批次不得跳过未落地数据。
- 禁止用一个事务包住全部同步范围和全部数据集；事务必须按数据集和依赖顺序划分，同时保证未完整校验的快照不会被标记为当前有效版本。仅当多个数据集共享不可拆分的数据库约束且能在验收规模内证明锁时长符合预算时，才允许合并事务边界。
- 同一同步范围、同一数据源、同一数据集必须串行同步，并使用任务唯一性或数据库锁防止并发批次互相覆盖；仅当数据被可证明互斥的稳定分片键隔离，且并发测试确认不会竞争 watermark、唯一键或当前版本标记时，才允许并行。

## 原始证据与变更留痕

- 同步日志不能替代原始证据。每次同步必须保存当次源数据原文或可完整重建当次输入的不可变 artifact，并记录文件大小、记录数和 SHA256。
- 每个 artifact manifest 至少包含同步范围、数据源、数据集、run/attempt ID、抽取起止时间、源库时间或可用 watermark、连接器版本、查询定义哈希、源结构指纹和映射版本。重跑必须创建新的 attempt，禁止覆盖旧 artifact 或旧 manifest。
- 原始数据、标准化 staging 和正式业务数据分层保存。后续字段映射修正、人工消歧或业务合并不得修改原始记录；只能产生新的映射版本、变更记录和派生结果。
- 保存源记录首次出现、最后出现、最后变化的同步批次，并对真实变化记录保留变更前、变更后和字段差异。无变化记录不重复写行级历史，但对应同步批次必须能通过原始 artifact 和 manifest 完整核验。
- 源表、视图或接口结构变化必须保存前后 schema snapshot 和差异；源系统提供视图定义、Oracle SCN、MySQL binlog/GTID 或其他一致性位置时必须一并记录，源系统不提供时必须明确标记证据能力限制。
- 证据 artifact 必须使用对象存储版本控制、保留锁或等价的不可变策略，并加密存储。删除、下载、验证和延长保留期都必须受权限控制并写审计记录。
- 管理端必须能按源记录键查看历史、按两个同步批次生成原字段差异，并导出包含 manifest、schema、原始文件、差异、日志和校验信息的证据包。
- 证据保留时间必须按项目的数据治理和保留规则配置；到期清理必须保留审批和执行审计，禁止由普通业务接口物理删除。

## 正向典型形态

Go 只负责形成有上限的批次并落 staging；正式表合并必须使用集合 SQL：

```go
batch := make([]models.ResourceStaging, 0, batchSize)
for rows.Next() {
	var row models.ResourceStaging
	if err := rows.Scan(&row.SourceKey, &row.Name, &row.SourceHash); err != nil {
		return err
	}
	row.SyncRunID = runID
	batch = append(batch, row)
	if len(batch) == batchSize {
		if err := db.CreateInBatches(batch, batchSize).Error; err != nil {
			return err
		}
		batch = batch[:0]
	}
}
if len(batch) > 0 {
	if err := db.CreateInBatches(batch, batchSize).Error; err != nil {
		return err
	}
}
```

```sql
INSERT INTO resource (source_id, source_key, name, source_hash)
SELECT s.source_id, s.source_key, s.name, s.source_hash
FROM resource_staging AS s
WHERE s.sync_run_id = $1
ON CONFLICT (source_id, source_key) DO UPDATE
SET name = EXCLUDED.name,
    source_hash = EXCLUDED.source_hash,
    updated_at = NOW()
WHERE resource.source_hash IS DISTINCT FROM EXCLUDED.source_hash;
```

禁止在 `rows.Next()` 循环中查询正式表、解析单行外键或逐行 upsert。

## 性能验收

- 必须使用项目容量目标定义的数据量验证；项目尚未定义容量目标时，必须记录本次数据量、选择依据和不能外推的范围。验证至少记录抽取速度、批量落地速度、合并耗时、峰值内存、数据库锁等待和失败重试结果。
- 验收必须检查 SQL 数量随记录数按批次增长，而不是按单行增长；出现 N 条数据对应 N 次查询或 N 次写入即视为未通过。
- 对大表确认源记录键、run ID、当前状态和业务合并键索引有效，并通过执行计划确认合并 SQL 没有意外全表嵌套扫描。

## 完整性验收

- 必须验证重复执行不产生重复业务记录，失败批次不推进 watermark，未完整校验的快照不成为当前版本。
- 必须核对 artifact、manifest、schema snapshot、变更历史和清理审计能够由 run/attempt ID 串联，且旧证据未被覆盖。
- 必须验证同一同步范围的并发任务会被唯一性或数据库锁阻止；启用稳定分片并发时必须保留互斥性与竞争测试结果。
