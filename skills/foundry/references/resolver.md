---
name: foundry-resolver
description: 本地优先的 Git 仓库发现与 Provider 适配
---

# Repository Resolver

适用范围：所有涉及本地工作区或远端 Git 仓库读写的任务。

## 解析顺序

1. 按 [Workspace](workspace.md) 确定唯一仓库身份，优先检查当前工作区及其父目录。
2. 若有 `local_path`，检查该路径是否为可访问的 Git 仓库；必须规范化 URL 并验证其 remote 与 Workspace 目标一致。禁止只按目录名匹配。
3. 本地匹配成功时使用本地 Git；解析器返回工作分支、dirty、上游分支与可获得的 ahead/behind 计数（不自动 fetch，可能是缓存状态）；若无本地访问能力、目录不存在或没有匹配仓库，才使用已授权的 Provider API/Connector 或 Git CLI。
4. 本地存在匹配仓库但有未提交修改、分叉或身份冲突时，必须停止危险写入并报告；禁止悄悄改用远端绕过冲突。
5. Provider 能力必须分别检测：读取、提交、推送、PR/MR、CI 和部署；无能力时不得假称已完成。

## 本地同步边界

- Resolver 是只读定位与状态查询工具，不能将本地缓存的 ahead/behind 当作远端实时状态。
- 本地 Git 双阶段同步按 [提交与发布验收](publishing.md) 执行：修改前 Fetch/安全 Fast-forward，Push 前再次 Fetch/核对上游；不自动执行 Rebase、Reset、Stash 或 Force Push。
- 本地当前分支通常为 main，但必须尊重实际检出的分支，不自动创建任务分支；Web 默认独立分支与 PR/MR。

## 本地协作

- 默认尊重当前检出分支，通常为 `main`；禁止自动 checkout、reset、stash、clean 或覆盖未提交内容。
- 修改前检查工作区、远端分叉和任务文件所有权。修改后按目标仓库规范测试、提交。
- 推送前必须核对远端 HEAD、分支保护、权限与用户授权。禁止 force push；若远端要求 PR/MR，必须遵循该规则，不能以本地开发为由绕过。
- 不得因本地优先而忽略目标仓库最新 `AGENTS.md`、`PROJECTS.md` 或适用子规范。

## 远端协作

- Web 默认使用独立任务分支和 PR/MR，Base Branch 从目标仓库发现并遵循其规范。
- 普通 Git 远端可能不支持 PR/MR、CI；不支持时停止相应交付步骤并报告，不得自动直接推主分支。
- 仅在用户授权范围内使用可用 Connector/API；URL 本身不提供权限。

## 完成标准

必须说明解析器只定位仓库，不执行 GitHub/GitLab API 操作或自动同步；必须说明实际选用 Local 或 Remote、仓库身份校验结果、分支与远端状态、变更及交付证据；未能运行的本地或 Provider 检查标为待验证。
