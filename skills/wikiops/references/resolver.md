---
name: wikiops-resolver
description: 本地优先的 Git 仓库发现与 Provider 适配
---

# Repository Resolver

适用范围：所有涉及本地工作区或远端 Git 仓库读写的任务。

## 解析顺序

1. 按 [Workspace](workspace.md) 确定唯一仓库身份，优先检查当前工作区及其父目录。
2. 若有 `local_path`，检查该路径是否为可访问的 Git 仓库；必须规范化 URL 并使用 `git remote get-url --all origin` 与 `git remote get-url --push --all origin` 验证全部 Fetch/Push URL 均与 Workspace 目标一致；当前工作区或配置路径发现匹配仓库但含冲突 URL、或匹配仓库只有非 `origin` Remote 时，必须停止本地解析，禁止静默降级。禁止只按目录名匹配。
3. 本地匹配成功时使用本地 Git，返回分支、dirty、upstream 和可取得的 ahead/behind（未 fetch 时只是缓存状态）；若无本地访问能力、目录不存在或没有匹配仓库，才使用已授权的 Provider API/Connector 或 Git CLI。
4. 本地存在匹配仓库但有未提交修改、分叉或身份冲突时，必须停止危险写入并报告；禁止悄悄改用远端绕过冲突。
5. Provider 能力必须分别检测：读取、提交、推送、PR/MR、CI 和部署；无能力时不得假称已完成。

## 双阶段同步

- Resolver 默认只读；`python3 skills/wikiops/scripts/workspace.py sync-check [workspace] --fetch` 仅在工作区干净、非 Detached HEAD 且已配置上游时于已验证本地仓库执行 `git fetch origin` 并报告状态，不执行 Pull、Commit 或 Push。无 `--fetch` 时只报告缓存状态，`can_push` 必须为 `false`；即使 Fetch 后 `can_push` 为 `true`，也仅表示同步状态满足条件，不能代替权限、分支保护和授权核验。
- 本地修改前与 Push 前分别检查远端状态；必须按 [仓库协作](repository.md) 的双阶段同步门禁执行。禁止自动 Rebase、Reset、Stash 或 Force Push。

## 本地协作

- 必须尊重当前检出分支；禁止自动 checkout、reset、stash、clean 或覆盖未提交内容。
- 修改前检查工作区、远端分叉和任务文件所有权。修改后按目标仓库规范测试、提交。
- 推送前必须核对远端 HEAD、分支保护、权限与用户授权。禁止 force push；若远端要求 PR/MR，必须遵循该规则，不能以本地开发为由绕过。
- 不得因本地优先而忽略目标仓库最新 `AGENTS.md`、`TOPICS.md` 或适用子规范。

## 远端协作

- Web 默认使用独立任务分支和 PR/MR，Base Branch 从目标仓库发现并遵循其规范。
- 普通 Git 远端可能不支持 PR/MR、CI；不支持时停止相应交付步骤并报告，不得自动直接推主分支。
- 仅在用户授权范围内使用可用 Connector/API；URL 本身不提供权限。

正向形态：身份全部匹配 → `sync-check --fetch` → 检查同步状态、权限与授权 → 按仓库规范提交和推送。反例：只校验第一个 Push URL，或将未 Fetch 的缓存 ahead/behind 当成推送许可。

## 完成标准

必须说明实际选用 Local 或 Remote、仓库身份校验结果、分支与远端状态、变更及交付证据；未能运行的本地或 Provider 检查标为待验证。
