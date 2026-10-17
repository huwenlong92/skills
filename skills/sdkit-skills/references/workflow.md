---
name: sdkit-skills-workflow
description: Skill 分类、创建、源文件更新与静态校验的执行规则
---

# Skill 管理流程

适用范围：发现、创建、修改和验证本仓库 Skill。

## 流程

1. 先读取根 AGENTS.md 和 catalog.json，核对真实 skills/ 目录；Catalog 不是替代源码的事实源。
2. 创建前检查名称仅包含小写字母、数字、连字符，且目标目录和 Catalog 中均不存在同名条目；使用 create --name NAME --category CATEGORY。
3. 新 Skill 必须有仅含 name、description 的 SKILL.md frontmatter；详细规则在 references/，禁止复制其他 Skill 的未授权规则。
4. 修改现有 Skill 必须读取命中的 references，保护未提交修改，不因 update 命令覆盖源码；源文件修改使用正常 Git 流程。
5. 修改后运行 validate --all；链接、目录名、frontmatter、Catalog 不一致时禁止发布。

## 完成标准

Catalog 与 Skill 目录一一对应；创建不覆盖旧文件；静态校验可报告具体文件及失败原因；未执行的运行测试必须明确标注。
