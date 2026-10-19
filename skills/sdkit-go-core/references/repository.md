---
name: sdkit-go-core-repository
description: sdkit-go 公开模块的源码定位、固定版本与跨仓库写入边界
---

# Go sdkit-go 源码与固定版本

适用范围：定位共享 Go 框架、维护框架源码、修改依赖或升级消费方时必须读取。本文件是 `sdkit-go-core` 的权威源码与版本依据。

## 权威来源与项目身份

- 权威公开仓库为 `https://github.com/huwenlong92/sdkit-go`，Go module 为 `github.com/huwenlong92/sdkit-go`；源码模块根目录包含 `go.mod`、`core/` 和 `pkg/`。禁止把 Skill 名 `sdkit-go-core` 当作 module path，禁止指向 `core/` 子目录作为独立模块。
- 必须从当前 Git root、origin、项目 AGENTS.md、TEMPLATE.md 和真实依赖识别目标。只有修改框架源码时使用本 Skill；完整 Go 模板业务使用 `sdbase-go`，SQLite 单 Web 模板使用 `sdbase-lite`。
- 必须核对消费项目的 `go.mod`、现有 `go.work`、`replace` 和实际模块解析结果。已知新仓库不代表项目已迁移；旧模块、工作区和本地覆盖必须如实识别，禁止未经授权自动切换。
- 公开底座模块不需要为其新增 GitHub 账号、SSH key 或 CI secret；其他私有依赖与私有模板仍按各自权限处理，禁止批量删除认证配置。
- 本地 checkout 必须动态发现并核对 remote 与 module 声明；禁止写死工作站路径或直接修改 Go module cache 中的源码。普通业务任务不自动修改框架或模板仓库。

## 消费方固定依赖

- 正式依赖必须在 `go.mod` 使用已发布的明确版本，版本来自项目锁定值或本次已授权的升级目标；禁止使用 `@latest`、浮动 main 或本机 checkout 代替发布版本。当前已确认的迁移基线为 `v0.1.28`，不代表以后每个项目都必须升级到该版本。
- 必须提交与依赖解析一致的 `go.mod`、`go.sum`。`go.sum` 校验内容完整性，不是版本锁文件；必须核对 `go list -m -json` 的 Path、Version、Dir、Sum 和 Replace，确认实际选中版本与目标一致。
- API 核验必须读取实际选中版本的源码；禁止把框架 main 的新 API 当成消费项目已经具备的能力。构建、测试与容器必须使用同一发布版本，验证命令必须使用 `-mod=readonly` 防止隐式修改依赖。
- 本地 replace 仅允许用于已明确授权的联调，必须指向已核验的 module 根目录；交付前必须移除临时覆盖并重新核验正常命令和 `GOWORK=off` 的解析结果。禁止用 `GOWORK=off` 掩盖正常构建仍生效的旧 SDK 工作区。
- Go 模块路径更名只调整依赖与 import；禁止顺带重命名 package、修改业务模型、升级无关依赖或改造 Docker 文件布局。

以下是脱敏形态；实际 module 和版本必须替换为已核验的发布值：

```sh
go get example.com/shared/framework@vX.Y.Z
go mod tidy
go list -m -json example.com/shared/framework
GOWORK=off go list -m -json example.com/shared/framework
go build -mod=readonly ./...
```

反例：require 声明固定版本，但实际仍由 go.work 或 replace 选中另一个本机源码；或只根据 go.sum 中存在某版本就宣称实际使用该版本。

## 版本发布与旧仓库边界

- 已发布 tag 禁止移动、删除或覆盖；框架修复与新增能力必须使用新版本发布。源码提交、tag 发布、消费方升级与部署分别核对授权。
- 框架发布成功不等于消费方已升级；必须显式更新 require，审查 go.mod/go.sum 差异，并按[测试规范](testing.md)验证真实消费路径及项目声明的 build tags。
- 旧仓库 `https://github.com/huwenlong92/sdkit` 与旧 module `github.com/huwenlong92/sdkit` 保留历史用途；禁止自动修改、镜像同步、删除或覆盖其 tag。旧 Skill 名 `sdkit` 也只用于其 description 允许的历史兼容任务，禁止与新入口重复选择。

## 完成标准

- 能列出目标 Git 身份、实际 module、版本、源码目录、校验和及生效覆盖，依赖声明和实际解析一致。
- 已发布 tag 保持不变；go.mod/go.sum、声明 build tags 与定向验收结果可核验，编译检查与实际测试必须分别报告。
- 人工检查构建和交付没有遗留本机 SDK 前提；未授权的旧仓库、业务、认证、工具链与线上状态保持不变。
