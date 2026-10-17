---
name: sdkit-skills-workflow
description: Skill 分类、创建、源文件更新与静态校验的执行规则
---

# Skill 管理流程

适用范围：发现、创建、修改和验证本仓库 Skill。

## 流程

1. 先读取根 AGENTS.md 和 catalog.json，核对真实 skills/ 目录；Catalog 不是替代源码的事实源。
2. 创建前必须检查名称仅包含小写字母、数字、连字符，且目标目录和 Catalog 中均不存在同名条目；使用 `create NAME --category CATEGORY`。源码父目录和 Catalog 禁止为符号链接。
3. 新 Skill 必须有仅含 name、description 的 SKILL.md frontmatter；详细规则在 references/，禁止复制其他 Skill 的未授权规则。
4. 修改现有 Skill 必须读取命中的 references，保护未提交修改，不因 update 命令覆盖源码；源文件修改使用正常 Git 流程。
5. 修改后运行 validate --all；链接、目录名、frontmatter、Catalog 不一致时禁止发布。
6. Create 必须通过仓库根目录的 `.sdkit-catalog.lock` 排他执行，Catalog 必须使用同目录临时文件与原子替换发布；写入或替换失败时必须清理本次新建目录和临时文件，禁止通过原位重写 Catalog 回滚。已有锁必须停止；异常退出后必须人工确认写入进程已结束并核对 Catalog 与目录，才允许移除该精确锁文件。禁止绕过锁并发修改 Catalog；该锁不提供进程强制终止后的跨目录事务恢复。

## 完成标准

Catalog 与 Skill 目录一一对应；创建不覆盖旧文件；静态校验可报告具体文件及失败原因；未执行的运行测试必须明确标注。
