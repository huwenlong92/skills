---
name: npm-package
description: 为可发布 npm 包执行 SDKit 约定。创建、修改、验证或发布 package metadata、exports、files、依赖、构建检查、tarball、Makefile target、npm 认证、版本、dist-tag 和公开 README 同步时使用。
---

# npm Package

本 skill 适用于发布到 npm-compatible registry 的 package。发布、版本修改、token 创建、Git commit、tag 和 push 都是外部变更；仅当用户明确要求对应操作时才允许执行。

## 必须执行的流程

1. 任何 release、version、pack 或 registry 任务都必须读取 [workflow.md](references/workflow.md)。
2. 修改 metadata、入口、依赖、scripts 或发布文件时读取 [package-json.md](references/package-json.md)。
3. 创建或修改命令入口时读取 [makefile.md](references/makefile.md)。
4. `references/templates/` 下的文件只能作为起始模板；使用前必须替换占位符并逐项审计目标值。
5. 只读评审在报告发现后停止。用户明确要求发布时，必须满足 [workflow.md](references/workflow.md) 的全部前置条件和停止条件。

## 停止条件

- 禁止推断 package 目录、registry、repository URL、npm scope、access level、dist-tag 或版本升级类型；必须从目标仓库读取或由用户提供。
- 禁止打印、持久化或提交真实 npm token；package 中不得包含带凭据的 npm 配置文件。
- 用户未明确要求对应变更时，禁止运行 `npm publish`、修改版本、创建 tag、commit 或 push。
