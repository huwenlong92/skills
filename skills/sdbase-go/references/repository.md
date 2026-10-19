---
name: sdbase-go-repository
description: sdbase-go 主入口的权威源码定位、模板版本核验与写入边界
---

# 权威源码与项目身份

适用范围：使用 `sdbase-go` 开始项目开发、模板能力核对或跨仓库修改前必须读取。本文件是 `sdbase-go` 主入口的源码定位依据；`sdkitgo` 仅保留历史兼容用途。

- 权威源码：`https://github.com/huwenlong92/sdbase-go`；访问时检查实际默认分支和当前 SHA，不把历史版本当成最新实现。
- 定位边界：完整 Go 应用模板；SQLite 单 Web 项目应使用 sdbase-lite。
- 先根据当前工作目录、Git root、origin、项目 AGENTS.md、TEMPLATE.md 与依赖确认目标业务仓库。项目名称或语言本身不能证明采用该模板。
- 若项目由模板复制创建，应核对并记录项目采用的模板 commit；模板最新 main 不代表业务项目已升级。
- 本地路径必须从现有工作区和 Git 身份动态发现，禁止写死个人本机路径。私有仓库访问依赖当前 Git 授权。
- 业务开发只修改获授权的目标仓库；修改模板或框架仓库需要明确授权，禁止把模板维护与业务变更混为一谈。

## 共享 Go 底座

- 当前模板使用公开模块 `github.com/huwenlong92/sdkit-go`，权威源码为 `https://github.com/huwenlong92/sdkit-go`；当前迁移基线为 `v0.1.28`。必须从实际 go.mod 和模块解析结果核对项目已采用的版本，禁止把模板 main 或本基线当成项目已升级的证据。
- 正常开发和交付必须使用明确的已发布版本及匹配的 go.sum，不使用浮动 main、@latest、go.work 或本地 replace 替代发布依赖。依赖升级必须有本次授权，使用 `go list -m -json` 核对实际版本及 Replace，并按项目声明的 build tags 验证 `go build -mod=readonly` 和定向测试。
- 公开 SDK 不需要为其额外配置 GitHub 凭据；私有模板和其他私有依赖仍按各自权限处理。识别到旧 `github.com/huwenlong92/sdkit` 时必须报告真实来源，不能自动修改旧仓库或替用户迁移。

## 完成标准

能够说明目标 Git 仓库身份、模板或框架来源、版本证据、适用规则和实际修改范围；无法定位时停止跨仓库写入并报告缺失信息。
