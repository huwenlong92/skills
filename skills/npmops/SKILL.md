---
name: npmops
description: 为可发布 npm 包执行结构、打包与发布约定。创建新 npm 包、查找本地包，创建、修改或评审 package.json、exports、依赖、发布文件、Makefile，验证 tarball，处理 npm 认证、版本发布、dist-tag 和 GitHub 公开介绍页同步时使用；普通应用的依赖安装不触发。
---

# npmOps 包维护与发布

本 skill 维护发布到 npm-compatible registry 的 package，固定以 Makefile 编排人工发布。包结构、发布流程、认证和公开页同步各有一处权威规则，禁止复制成多套指令。

## 任务分流

| 任务 | 必须读取 |
|---|---|
| 创建新包、列出或查找本地 npm 包 | [仓库协作](references/repository.md)；初始化包结构时追加[包结构](references/package-json.md)和[Makefile](references/makefile.md) |
| metadata、exports、依赖、scripts 或发布文件 | [包结构](references/package-json.md) |
| pack、tarball 验证、首次/正式/prerelease 发布、版本或 dist-tag | [发布流程](references/workflow.md)；真实发布再读[认证](references/auth.md) |
| 创建、修改或评审 Makefile 发布入口 | [Makefile](references/makefile.md)、[发布流程](references/workflow.md)、[认证](references/auth.md) |
| npm 登录、Token 或权限失败 | [认证](references/auth.md)；失败发生在发布中时再读[发布流程](references/workflow.md) |
| GitHub 公开 README 与 demo 图片同步 | [公开介绍页](references/public-page.md) |
| 绑定本地目录与远端 URL、定位源码包、Git 同步与跨会话检查 | [仓库协作](references/repository.md) |

## 执行顺序

1. 创建或查找包时先按[仓库协作](references/repository.md)读取用户配置的包父目录；维护已有包时先验证目标源码仓库与包目录。再读取目标仓库显式规则、package.json、锁文件、Makefile 和命中说明，确定包管理器、产物与任务范围。
2. 按分流读取 references；涉及具体包结构时追加包结构 reference。模板必须按项目脚本、registry、access 和路径审计后使用，禁止直接覆盖已有自定义流程。
3. 区分维护、只读评审、本地打包、版本变更、registry 发布与公开页同步；只执行已授权动作，禁止从“整理包”推导真实发布权限。
4. 执行匹配验证并报告结果；发布任务必须分别报告检查、版本变化、registry 状态、消费验证和 Git 状态。

## 共同门禁

- 包目录、registry、repository、scope、access 和版本必须从项目声明或用户要求解析；缺少必要信息时停止依赖该信息的操作，禁止猜造地址或把模板值当目标值。
- 仅当当前用户明确授权对应动作时，允许版本变更、npm 发布、Token 创建、公开页写入与 Git commit/tag/push。日常发布已获授权时按发布 reference 的确定性版本规则执行，禁止反复索要已有授权。
- 禁止打印、持久化或提交真实 Token，禁止将认证文件或秘密打入 tarball。
- 平台认证策略、CLI 行为和 registry 权限规则必须按实际版本实时核验官方资料；reference 中的入口不代表账号具备相应权限。
