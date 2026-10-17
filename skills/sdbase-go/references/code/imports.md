---
name: go-imports
description: sdkitgo Go 文件的 import 分组、显式别名、dot import 和 blank import 规则
---

# Go Import 规范

本文适用于 sdkitgo 项目中任何新增 Go 文件或被修改的 `import` block。只修改既有文件函数体且 import 完全不变时不必读取本文；import alias 的唯一权威规则在本文，其他 reference 只能链接本文。

## 默认不使用别名

- import 必须直接使用被导入 package 的声明名；没有实际冲突时禁止增加显式别名。
- 禁止仅为强调来源层级而增加 `coreconfig`、`databasefacade`、`webhandler`、`appmiddleware`、`pkgstorage` 这类前缀。
- 禁止仅因 import path 较长、package 名较短或“看起来更清楚”而增加别名。
- 当前文件新增或修改某个 import 时，必须检查该 import 是否真的需要别名；不得顺带清洗任务范围外其他文件的历史别名。

没有名称冲突时必须直接导入：

```go
import (
	"example.com/framework/core/config"
	"example.com/framework/core/database/facade"
)

func load() (facade.Config, error) {
	var cfg facade.Config
	return cfg, config.LoadRequiredKey("config.yaml", "database", &cfg)
}
```

禁止写成：

```go
import (
	coreconfig "example.com/framework/core/config"
	databasefacade "example.com/framework/core/database/facade"
)
```

## 允许显式别名的条件

仅当命中以下条件之一时允许显式别名：

1. 同一文件必须导入两个声明名相同的 package。
2. package 声明名与 import path 最后一段不同，并且显式写出声明名能够避免误读；别名必须与 package 的真实声明名一致。
3. 当前 package 名与被导入 package 名冲突，且重命名当前 package 不在任务范围内。

同名 package 冲突时，只给需要区分的 import 增加最短且稳定的领域前缀。标准库名称必须保留原名；项目或框架 package 使用能力名区分：

```go
import (
	"errors"

	apperrors "example.com/framework/core/errors"
)
```

同一文件必须使用两个 `facade` package 时允许写成：

```go
import (
	databasefacade "example.com/framework/core/database/facade"
	redisfacade "example.com/framework/core/redis/facade"
)
```

- 当冲突只来自当前文件的私有局部变量、参数或 private helper 名称时，必须先重命名该局部标识符；禁止为了保留随手起的局部名而给 package 增加别名。
- 别名必须表达被导入能力，禁止使用 `x`、`x1`、`util2`、`pkg`、`lib` 等无稳定语义的名称。
- 一个别名只解决当前文件的真实冲突；禁止为了让不同文件“看起来统一”而在没有冲突的文件中复制别名。

## Dot Import 与 Blank Import

- 生产代码和测试代码禁止 dot import。
- blank import 仅当被导入 package 的公开契约明确要求通过 import side effect 注册 driver 或 provider 时允许。
- blank import 必须位于显式的启动、构建或 driver 注册入口；handler、model、普通 infra 和测试 fixture 禁止依赖隐式注册。
- Service Provider、Router、worker task、crontab template 和 realtime event 必须显式注册；禁止用 blank import 规避它们的集中注册入口。

## 分组与格式化

- import 顺序和空行分组必须交给 `goimports`；禁止人工维持一套与 `goimports` 冲突的排序。
- 删除别名后必须同步更新当前文件中的 qualifier，禁止保留失效引用或为通过编译重新加入无必要别名。
- 禁止大范围格式化与本次修改无关的文件。

## 验收

- 对全部新增或修改的 Go 文件运行 `goimports`，并检查 diff 中每个显式别名都能对应本文的一项允许条件。
- 必须搜索本次修改文件中的显式别名和 dot import；无法说明真实冲突、声明名差异或受支持 side effect 的命中不通过。
- 必须运行覆盖修改 package 的最小 `go test` 或构建命令；无法运行时必须说明具体原因和未覆盖范围。
