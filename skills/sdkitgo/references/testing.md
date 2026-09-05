---
name: sdkitgo-testing
description: sdkitgo 代码、配置、迁移和 runtime 修改后的分层验证规则
---

# 测试与验证规范

本文适用于 sdkitgo 项目的完成前测试和验证。任何代码、配置、迁移或模板修改在交付前都必须读取本文。

## 目录与 Package

- 所有 Go 测试文件必须统一放在项目根目录 `tests/` 下；`app/`、`cmd/`、`bootstrap/`、`migrations/`、`seeds/` 和其他生产代码目录禁止出现 `_test.go`。
- 目标行为已经在 `tests/` 中具有对应目录时，新增测试必须进入该目录。尚无对应目录时，必须在 `tests/` 下按生产源码的相对目录建立测试目录，例如 `app/catalog/handler` 对应 `tests/app/catalog/handler`；禁止在根目录散放无法判断归属的测试文件。
- 根目录测试必须使用外部测试 package，例如生产 package 为 `catalog` 时测试 package 使用 `catalog_test`，并显式 import 被测 package。禁止为了测试未导出小方法而把测试移回生产目录，也禁止仅为测试暴露没有业务契约的导出 wrapper。

## 基本规则

- `_test.go` 与生产代码遵循同一套 Go 代码质量要求：命名清晰、导入分组正确、通过 `gofmt`，不得把测试当作规范例外。
- 同一行为存在多个输入、边界或错误分支时，必须使用带 `name` 字段的 `[]struct` 表驱动测试和 `t.Run`；仅当各用例需要不同 fixture 生命周期或不同测试并发策略时，才允许拆成独立测试函数。禁止用无序 `map` 代替测试用例表。
- 测试必须校验真正的业务契约。HTTP 测试不能只判断“成功/失败”，必须覆盖本次修改涉及的状态码、业务错误码及关键响应字段；错误断言必须包含实际值和期望值。
- 不共享可变测试状态的纯单元测试可使用 `t.Parallel()`；修改进程环境、工作目录、全局变量或依赖固定外部资源的测试必须保持串行。并行子测试不得捕获会被后续迭代修改的变量。
- 测试辅助函数在内部调用 `t.Fatal`、`t.Error` 等方法时必须调用 `t.Helper()`；资源使用 `t.TempDir()`、`t.Cleanup()` 等测试生命周期能力回收。
- 能由固定时钟、内存实现、stub、`httptest`、channel 或显式同步条件验证的行为，必须使用这些可控依赖。仅当验收目标就是外部系统或真实数据库集成时，才允许连接隔离的测试资源；禁止依赖公网、真实账号或用不稳定的 `time.Sleep` 代替同步条件。
- 类型断言、切片索引和指针解引用必须先校验前置条件，禁止用 panic 代替可读的测试失败信息。
- 测试数据必须使用明显的虚构值，不得写入真实凭据、真实用户目录、生产地址或可识别的业务数据。脱敏逻辑测试可使用专门构造的假敏感值。
- 能跑测试时，至少跑与改动最相关的 `go test`。
- 只有修改跨 package 契约、runtime 启动链或共享数据库行为时才要求扩大测试范围；其他修改必须选择与风险匹配的最小有效测试。
- 如果没有运行测试，必须说明原因。

## 验收账号与凭据

- 仅限隔离的本地开发和验收环境：测试过程中通过注册、邀请或测试脚本新创建的普通账号，密码统一使用 `123456`。
- 不得为了方便验收而修改共享 demo、固定基线或其他协作者正在使用的账号密码。
- 必须覆盖密码找回、密码重置等流程时，必须新建可丢弃的一次性测试账号；仅当系统不能创建一次性账号且用户已确认影响范围时，才允许临时使用固定测试账号，并必须在本轮验收结束前恢复。禁止使用共享账号承担未声明的破坏性凭据测试。
- 如果业务场景无法避免修改固定测试账号密码，必须事先明确记录影响范围，并在本轮验收结束前恢复约定密码、通过真实登录流程验证成功。
- `123456` 不得用于生产、对公网开放的测试环境或任何真实用户账号；管理员密码、会话 Cookie、验证码和一次性链接不得写入仓库。

## 按改动类型验证

- handler/request/response 改动：跑 `tests/` 下对应 service 或源码映射目录的 Go test；没有测试时至少确认编译或构建命令。
- model/query/projection 改动：跑 `tests/` 下相关 model/query 测试；涉及 DDL 时验证数据库迁移。
- worker 改动：必须跑命中的 worker task、queue runtime 或 event handler 测试；目标 package 没有测试时必须至少执行其编译或包含它的最小构建命令。
- crontab 改动：必须跑命中的 template、store、lock 或 run handler 测试；目标 package 没有测试时必须至少执行其编译或包含它的最小构建命令。
- realtime event 改动：必须跑命中的 event definition、gateway、transport 或 subscription 测试；目标 package 没有测试时必须至少执行其编译或包含它的最小构建命令。
- provider/config/capability 改动：跑 service 启动或 provider 构建相关测试。
- core 改动：在实际解析出的 core checkout 中运行对应 package 测试。

## 正向典型形态

同一行为有多个输入或边界时，测试必须使用有序表格、稳定名称和包含实际值的错误信息。下面的测试位于 `tests/http/form/sort_test.go`，通过 import 测试生产 package 的公开契约：

```go
package form_test

func TestSortRequestOrderBy(t *testing.T) {
	tests := []struct {
		name   string
		column string
		dir    string
		want   string
	}{
		{name: "default", want: "item.id DESC"},
		{name: "allowed", column: "name", dir: "asc", want: "item.name asc,item.id DESC"},
		{name: "unknown", column: "raw_sql", dir: "desc", want: "item.id DESC"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			request := form.SortRequest{OrderColumn: tt.column, SortType: tt.dir}
			got := request.OrderBy("item.id DESC", map[string]string{"name": "item.name"})
			if got != tt.want {
				t.Fatalf("OrderBy(%q, %q) = %q, want %q", tt.column, tt.dir, got, tt.want)
			}
		})
	}
}
```

禁止使用 `map[string]struct{...}` 作为用例表，也禁止只输出“结果错误”而不包含 `got` 与 `want`。

## 验收

- 必须运行 `rg --files -g '*_test.go' | rg -v '^tests/'`；该命令必须没有输出。
- 最终回复必须说明运行过的命令。未运行测试时，必须说明具体原因和未覆盖范围，禁止只写“未测试”。
