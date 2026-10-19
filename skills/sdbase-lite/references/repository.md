---
name: sdbase-lite-repository
description: sdbase-lite 模板源码定位、身份核验与项目归属规则
---

# 模板仓库与项目归属

适用范围：首次进入项目、解析模板身份、核对基础能力和准备跨仓库修改时必须读取。

- 权威模板仓库：`https://github.com/huwenlong92/sdbase-lite`；默认分支目前为 `main`，使用时必须检查最新远端分支和实际提交。
- 必须从当前任务路径、Git root、origin、AGENTS.md、TEMPLATE.md 与依赖声明识别业务项目；不能把当前项目误认成模板仓库。
- 本地仓库路径动态发现，不允许硬编码用户机器路径；远端私有仓库必须使用当前已授权 Git Provider 或本地凭据，禁止绕过权限。
- 模板 README/TEMPLATE 和真实依赖用于确认基线；项目复制后的起始 commit 应记录，模板 main 更新不代表业务项目已升级。
- 普通业务任务只修改目标业务仓库；模板公共改进需要单独确认仓库与写入授权。

## 共享 Go 底座

- 当前模板使用公开模块 `github.com/huwenlong92/sdkit-go`，权威源码为 `https://github.com/huwenlong92/sdkit-go`；当前迁移基线为 `v0.1.28`。必须从实际 go.mod 和模块解析结果核对项目已采用的版本，禁止把模板 main 或本基线当成项目已升级的证据。
- 正常开发和交付必须使用明确的已发布版本及匹配的 go.sum，不使用浮动 main、@latest、go.work 或本地 replace 替代发布依赖。依赖升级必须有本次授权，使用 `go list -m -json` 核对实际版本及 Replace，并按项目声明的 build tags 验证 `go build -mod=readonly` 和定向测试。
- 公开 SDK 不需要为其额外配置 GitHub 凭据；私有模板和其他私有依赖仍按各自权限处理。识别到旧 `github.com/huwenlong92/sdkit` 时必须报告真实来源，不能自动修改旧仓库或替用户迁移。

## 完成标准

能够给出当前项目 Git 身份、模板来源、实际版本与修改归属；缺少来源证据时报告未知，不编造兼容性。
