---
name: sdkit-skills
description: 管理 SDKit Skills 仓库内 Skill 的发现、分类、创建、校验，以及向明确指定的本地 Agent Skills 目录安全安装和更新时使用；不用于普通业务代码开发。
---

# SDKit Skills Manager

本 Skill 只管理 Skill 本身，不替代技术或产品 Skill；路径均以 skills 仓库根目录为基准。

## 任务分流

- 查询分类、Skill 归属或新增候选：读取 [管理流程](references/workflow.md)，使用 `scripts/manager.py list`。
- 新建 Skill：读取 [管理流程](references/workflow.md)，执行 `create` 并核验 Catalog。
- 修改已有 Skill：读取目标 Skill 的 SKILL.md 与命中 references，先检查 Git 状态，再修改并运行 `validate`。
- 安装、更新到本地：读取 [安装安全](references/install.md)，明确目标路径后使用 `install` 或 `update`。
- 全仓检查：使用 `validate --all`，只执行本地静态检查，不调用外部网络。

## 共同门禁

- 创建与更新源仓库必须遵守根 AGENTS.md；不自动提交、Push、合并或部署。
- 安装与更新只允许用户明确指定目标目录；不自动猜测全局 Codex 路径或修改第三方配置。
- 已存在的未知目录、用户修改、符号链接、缺失安装记录必须停止覆盖。
- 本管理 Skill 仅使用 Python 标准库，独立安装时管理命令相对于自身目录执行。
