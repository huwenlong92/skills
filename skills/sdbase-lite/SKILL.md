---
name: sdbase-lite
description: 用于基于 SDBase Lite 的单 Web Go 工具项目的开发、调试、测试与评审；识别 SQLite、Cookie Session、app/web 和嵌入前端，不适用于 PostgreSQL 多服务 sdbase-go。
---

# sdbase-lite

本 Skill 仅用于已核实采用对应 SDBase 模板的项目。不得仅凭编程语言或目录名推断模板身份。

## 执行顺序

1. 读取 [仓库定位与模板边界](references/repository.md)，通过项目 AGENTS.md、TEMPLATE.md、依赖与实际代码确定模板身份和版本。
2. 核验目标项目 Git 根目录、当前分支、未提交修改与相关开放 PR；遵守项目显式授权及协作规则。
3. 按项目真实源码和 README 执行最小范围修改；框架公共能力与业务项目职责分开。
4. 完成后执行 [工作流与验收](references/workflow.md)，明确已验证与待验证内容。

## 停止条件

- 无法证明目标采用本模板时，不得套用专有目录和认证契约。
- 不得因为模板仓库存在而擅自修改模板或其他业务仓库。
- 禁止硬编码个人本机路径、密钥、令牌或未经验证的远端版本。
