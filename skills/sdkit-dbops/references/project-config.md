# 项目配置 V1

适用于 `database/database.yaml` 的定义、读取和检查。路径相对于业务项目根目录。

允许单方言目录 `database/schema/baseline.sql`、`database/migrations/`；多方言必须显式使用 `database/<dialect>/schema/` 与 `migrations/`。禁止在 Skill 安装目录保存项目配置。

示例：
```yaml
apiVersion: sdkit.dev/schema/v1
project:
  id: example-app
database:
  dialect: postgres
  layout: single
migration:
  driver: sql
  directory: database/migrations
  baseline: database/schema/baseline.sql
safety:
  defaultMode: read-only
```

- 方言必须显式声明为 postgres、mysql、oracle、sqlite；不能从 SQL 内容猜测。
- `layout=multi` 时按方言分目录；`driver=external/observe` 时不允许 dbops 接管 SQL 执行。
- 配置中禁止 DSN、Token、密码及真实个人目录；环境身份须由独立已确认入口解析。
- V1 静态工具尚不读取 YAML 或 JSON 项目配置；当前 CLI 仅接受显式 `--dialect` 与 `--layout`，调用者必须先从已确认的项目配置人工核对参数。JSON Schema 只定义未来配置契约，不能视为已实现配置解析。
- 配置 schema 位于 `schemas/project-config.schema.json`。

完成标准：方言、路径、驱动和只读模式可核验；未知配置必须拒绝或标记 Unsupported。
