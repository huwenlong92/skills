---
name: sdbase-admin-lite-repository
description: sdbase-admin-lite 模板源码定位、身份核验与项目归属规则
---

# 模板仓库与项目归属

适用范围：首次进入项目、解析模板身份、核对基础能力和准备跨仓库修改时必须读取。

- 权威模板仓库：`https://github.com/huwenlong92/sdbase-admin-lite`；默认分支目前为 `main`，使用时必须检查最新远端分支和实际提交。
- 优先从当前任务路径、Git root、origin、AGENTS.md、TEMPLATE.md 与依赖声明识别业务项目；不能把当前项目误认成模板仓库。
- 本地仓库路径动态发现，不允许硬编码用户机器路径；远端私有仓库必须使用当前已授权 Git Provider 或本地凭据，禁止绕过权限。
- 模板 README/TEMPLATE 和真实依赖用于确认基线；项目复制后的起始 commit 应记录，模板 main 更新不代表业务项目已升级。
- 普通业务任务只修改目标业务仓库；模板公共改进需要单独确认仓库与写入授权。

## 完成标准

能够给出当前项目 Git 身份、模板来源、实际版本与修改归属；缺少来源证据时报告未知，不编造兼容性。
