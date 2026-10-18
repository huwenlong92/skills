---
name: crontab-handler
description: sdkitgo crontab 的目录、template、显式注册、job handler 和调度边界
---

# Crontab 规范

本文定义 sdkitgo 的 crontab service、template、显式注册、job handler、目录分类和 infra 边界。新增或修改 `app/crontab/**`、DB job、payload、调度 handler、store、lock 或错过调度补偿时必须读取本文。

## 目录职责

```text
app/crontab/
  config/                 service config
  infra/                  crontab 私有 adapter 和 capability wiring
    capability/
    lock/
    store/
  templates/              template 与 run handler
    partition/
    queue/
    report/
  operations.go           对外 operations facade 构造
  provider.go             runtime service 注册
  router.go               template 集中注册
  server.go               manager、runner、scheduler 装配与生命周期
```

- `app/crontab` 根目录只放 service 入口、registry、manager 装配和生命周期；禁止放具体任务业务文件。
- Template 和对应 run handler 必须放在 `app/crontab/templates`。
- 正式任务按稳定业务域或能力放入 `templates/{domain}`，例如 `partition`、`queue`、`report`；禁止按 `daily`、`hourly`、`monthly` 等执行频率分类。
- 一个目录表示一类任务，不得为每个任务创建同名目录。一个任务必须使用一个 `.go` 文件，并把 template、payload 和 run handler 放在同一文件；仅当两个 template 共享同一个不可分割的 handler 或 payload contract 时，才允许放在同一文件。
- `infra` 只放 store、lock、realtime adapter 和 capability wiring；禁止放 job 业务逻辑。

## 两层注册

Crontab service 和 crontab template 是两种不同注册。

1. Service 注册：`app/crontab/provider.go` 定义 `crontab.Provider()`；单服务入口 `cmd/crontab/main.go` 和多服务入口 `cmd/serve/main.go` 必须显式列出该 Provider。
2. Template 注册：所有 template 必须在 `app/crontab/router.go` 的 registry 构造函数中显式 `RegisterAll(...)`。

目录分类不能代替 template 注册。禁止通过 template package 的 `init()`、全局 side effect 或文件扫描自动注册任务。

```go
func NewRegistry() (*crontab.Registry, error) {
	r := crontab.NewRegistry()
	if err := r.RegisterAll(
		partition.ResourcePartitionTemplate,
		report.DailySummaryTemplate,
	); err != nil {
		return nil, err
	}
	return r, nil
}
```

## Template

- Template key 是稳定协议，必须定义为 constant，不得从 UI 文案、函数名或 cron 表达式推导。
- Template 必须明确 `Key`、`Name`、`Desc`、`Spec`、`Enabled`、`AllowDB`、`AllowOverlap`、`Timeout` 和 `Handler`。
- Handler 接受 payload 时还必须定义 `DefaultPayload`、`PayloadFormat`；需要管理端编辑或校验结构时必须定义 `PayloadSchema`。
- `AllowDB: true` 表示允许数据库任务实例引用该代码 template；数据库只能保存实例名称、spec、payload、启用状态等允许字段，不能保存或替换 Go handler。
- 只允许代码内固定运行的系统任务必须设置 `AllowDB: false`。
- Handler 需要 runtime dependency 时，使用 `NewXxxTemplate(resolveDependency)` 构造 template；没有依赖注入时使用 package-level `var XxxTemplate`，禁止无意义 constructor。

## Run Handler

普通 run handler 固定使用：

```go
func runResourcePartition(ctx context.Context, job crontab.Job) error
```

并通过以下方式绑定：

```go
Handler: crontab.RunHandlerFromFunc(runResourcePartition),
```

- Handler 必须使用传入的 `ctx` 执行数据库和下游调用。
- Handler 必须从 `crontab.JobLoggerFromContext(ctx)` 获取运行日志，记录任务开始、失败和完成；日志必须包含 `job_id`、`template_key` 和本任务关键范围。
- 失败必须返回 `error`；禁止只记录错误后返回 `nil`。
- 有界、任务专属的 GORM 查询、更新和 transaction 直接写在 run handler，禁止为单个任务创建 operation/service 或一组转发小方法。
- 简单 payload 解析和默认值直接写在 run handler。只有两个及以上 handler 复用同一解析契约，或解析本身具有需要独立测试的复杂格式协议时，才允许提取 parser。
- Handler 禁止自行创建 ticker、cron scheduler、无限 goroutine、timeout wrapper、overlap lock 或 panic recovery；这些行为由 core crontab runtime 统一负责。
- 任务需要长时间执行、queue retry、并发消费或可靠投递时，crontab handler 只创建并投递 queue task，具体执行进入 [worker/handler.md](../worker/handler.md)。

## 正向形态

```go
const ResourcePartitionKey = "resource_partition"

var ResourcePartitionTemplate = crontab.Template{
	Key:          ResourcePartitionKey,
	Name:         "资源月分区预创建",
	Desc:         "每月预创建下个月资源分区",
	Spec:         "0 5 25 * *",
	Enabled:      true,
	AllowDB:      false,
	AllowOverlap: false,
	Timeout:      2 * time.Minute,
	Handler:      crontab.RunHandlerFromFunc(runResourcePartition),
}

func runResourcePartition(ctx context.Context, job crontab.Job) error {
	jobLog := crontab.JobLoggerFromContext(ctx)
	partitionMonth := time.Now().UTC().AddDate(0, 1, 0)
	jobLog.Info("resource partition ensure started",
		"job_id", job.ID,
		"template_key", job.Name,
		"partition_month", partitionMonth.Format("2006-01"),
	)
	if database.DB == nil {
		err := errors.New("database not initialized")
		jobLog.Error("resource partition ensure failed", "err", err.Error())
		return err
	}
	if err := models.EnsureResourcePartition(ctx, database.DB, partitionMonth); err != nil {
		jobLog.Error("resource partition ensure failed",
			"partition_month", partitionMonth.Format("2006-01"),
			"err", err.Error(),
		)
		return err
	}
	jobLog.Info("resource partition ensure completed",
		"partition_month", partitionMonth.Format("2006-01"),
	)
	return nil
}
```

禁止在 run handler 中复制 `EnsureResourcePartition` 的 DDL；单表分区 Ensure 的位置以 [database/migration.md](../database/migration.md) 为准。

## 错过调度与补偿

- 内置任务只在调度服务运行时触发；core 未定义 catch-up 时禁止假设停机期间任务会自动补跑。
- 分区等运维任务必须通过运行历史、目标对象和 default 数据共同确认缺口，再按 [database/migration.md](../database/migration.md) 使用窄范围入口补偿。
- 人工补偿只调用目标 template 背后的现有 handler、Ensure 或领域 operation；禁止运行无关聚合迁移或伪造成功记录。
- 生产要求自动恢复错过周期时，必须在 core crontab 定义统一 misfire/catch-up 策略；禁止在单个项目 handler 中加入启动即补跑。

## 验收

- 必须核对新 template 文件位于正确业务域目录，并在 `app/crontab/router.go` 显式注册且 key 唯一。
- 必须核对 `AllowDB`、payload、overlap 和 timeout 与任务契约一致。
- 必须测试 template 注册、payload 合法/非法输入、run handler 成功/失败、timeout、overlap 和运行日志；没有 package 测试时至少完成包含目标 package 的构建。
- 必须检查 run handler 没有自建 scheduler、ticker、goroutine、lock 或只有一个调用方的业务 wrapper。
