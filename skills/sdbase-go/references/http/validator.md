---
name: http-validator
description: sdkitgo app/http/validator 的绑定入口、自定义 validation tag 和注册规则
---

# HTTP Validator 规范

本文定义 sdkitgo 的请求绑定入口、自定义 validation tag，以及校验与值归一化的边界。新增或修改 `app/http/validator/**`、binding tag、校验翻译或 HTTP service 的 validator 初始化时必须读取本文。

## 校验边界

- validator 只判断输入值的类型、格式、长度、取值范围和字段间静态关系。
- 数据库存在性、唯一性、权限、租户归属和状态流转必须在当前 handler 中校验。
- 能使用 go-playground validator 内置 tag 表达的规则必须直接使用内置 tag，例如 `required`、`omitempty`、`min`、`max`、`oneof`、`required_with`、`gtfield`、`gte`、`lte`、`datetime`。
- 禁止为内置规则增加 `in`、`between`、`date` 等同义 custom tag。
- 自定义 tag 仅允许表达被两个及以上 request 使用、且不依赖业务上下文的稳定字段格式，例如统一的 `mobile`、`username`、`password` 格式。

## 校验与归一化

- validator 回调只能返回字段是否合法，禁止承担会被后续写入或响应使用的值转换。规范化地址、标准化编码等 canonical value 必须由 handler 在 binding 成功后显式取得。
- 自定义 tag 允许调用纯 parser 或 normalizer 并丢弃返回值，只把 `err == nil` 转为布尔校验结果；同一个 handler 需要规范化结果时，必须在 binding 后再次显式调用该 parser，禁止从 validator 的隐式状态取值。
- 只服务 HTTP 输入格式的布尔适配必须放在 `app/http/validator/custom/{tag}.go`，禁止放在 `app/infra`。
- 可脱离 HTTP、返回规范值与结构化元数据的通用 parser、normalizer 或 masker 不属于 validator。跨项目通用时必须使用实际 sdkit 依赖中的 `pkg/` 能力；仍含项目业务规则时必须留在使用它的 handler 或服务私有 infra，禁止以 `app/http/validator` 隐藏业务转换。

## Binding 入口

- JSON 使用 `validator.BindJSON(c, &request)`。
- Query 使用 `validator.BindQuery(c, &request)`。
- Form 使用 `validator.BindForm(c, &request)`。
- 每个 HTTP service 必须在创建业务路由前调用一次 `app/http/validator.Init()`；初始化失败必须阻止 router/server 创建。
- handler 禁止直接调用 `c.ShouldBindJSON`、`c.ShouldBindQuery` 或 go-playground validator，从而绕过统一错误转换。

## 自定义规则写法

每个 custom tag 使用一个同名文件，放在 `app/http/validator/custom/{tag}.go`。规则通过现有 `Register(Rule{...})` 注册；禁止修改公共 binding 入口来硬编码单个业务 tag。

```go
package custom

import (
	"regexp"

	"github.com/go-playground/validator/v10"
)

var mobilePattern = regexp.MustCompile(`^1[3-9]\d{9}$`)

func init() {
	Register(Rule{
		Tag: "mobile",
		Validate: func(fl validator.FieldLevel) bool {
			return mobilePattern.MatchString(fl.Field().String())
		},
		Translate: "{0}手机号格式不正确",
	})
}
```

- 正则必须在 package 初始化时预编译，禁止在 `Validate` 回调中重复 `regexp.MustCompile`。
- 校验回调必须是纯函数；禁止读写数据库、Redis、文件、网络、全局业务状态或当前用户信息。
- 可空性由 request tag 的 `omitempty` 或 `required` 决定，自定义规则不得把空值同时解释为“可选”。
- 固定翻译使用 `Translate`；只有错误文本确实需要校验参数时才允许使用 `TranslateFunc`。
- tag 使用稳定小写名称，不得包含页面名、handler 名或临时版本号。
- custom tag 导入 parser 时必须遵循 [imports.md](../code/imports.md)；没有真实名称冲突时禁止为了强调“工具”语义增加显式别名。

使用示例：

```go
Phone string `json:"phone" form:"phone" binding:"omitempty,mobile"`
```

## 验收

- 必须证明新增 custom tag 无法由内置 tag 表达，并至少存在两个真实 request 调用方。
- 必须测试合法值、非法值、空值与 `required`/`omitempty` 的组合，以及中文错误翻译。
- custom tag 调用 parser 时，必须另行测试 parser 的规范化结果；validator 测试只断言通过或失败，禁止依赖 callback 保存的中间值。
- 必须运行 `rg -n 'RegisterValidation|Register\(Rule|binding:"' app/http app --glob '*.go'`，核对 tag 注册、初始化和使用位置一致。
