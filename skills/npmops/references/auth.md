---
name: npmops-auth
description: npm 登录态、Token 注入、registry 一致性与认证失败处理。
---

# 认证与凭据

适用范围：登录、Token、权限失败与真实发布。本文件是本 skill 唯一认证规则；其他 reference 必须链接本文件，禁止复制平台教程。

## 前置条件与来源

- 必须使用目标 registry 既有认证；存在 NPM_TOKEN 时通过 NPM_USERCONFIG 指向受控 npmrc，否则使用本机登录态。Token 只改变认证来源，禁止新增另一套发布流程。
- whoami、login、dry-run 与 publish 必须指向同一已确认 registry；whoami 只证明身份，不证明包写权限或 2FA 满足。
- 真实发布与自动 bump 前必须检查认证；失败必须停止版本与发布步骤。已 bump 的恢复见[发布流程](workflow.md)。
- npmjs 登录/2FA/Token 策略必须在操作时核验[官方认证说明](https://docs.npmjs.com/accessing-npm-using-2fa/)和[Token 说明](https://docs.npmjs.com/about-access-tokens/)，并记录日期。其他 registry 必须读取对应官方说明，禁止直接套用 npmjs 策略。
- 项目已有 CI 认证机制时必须保留并核验对应文档，禁止未经要求迁移认证架构。本地 Token 模板不能替代所有 CI 策略。

## 登录与 Token

- 登录必须走 make login；仅当前 CLI 与 registry 支持且交互流程需要时，允许 make login-legacy。必须按[当前 login 文档](https://docs.npmjs.com/cli/commands/npm-login/)核验参数，禁止承诺绕过 2FA、通行密钥或组织策略。
- 创建 Token 必须有用户授权，权限只覆盖必需包/scope并设置明确有效期。2FA bypass 仅当自动化需要、平台及包/组织策略允许时启用，禁止作为默认要求。
- Token 只能通过既有环境、密码管理器或 CI secret 注入，禁止要求用户贴入会话，禁止输出真实值、使用泄密调试或持久化到项目。
- .npmrc.token 只允许包含环境变量引用，必须被 Git 忽略且排除 tarball；禁止写真实 Token。公共 npmjs 的正向形态如下，其他 registry 必须按实际 host/path 配置：

```ini
//registry.npmjs.org/:_authToken=${NPM_TOKEN}
```

- 模板只允许自动生成公共 npmjs 的上述文件。其他 registry 或自定义 NPM_USERCONFIG 必须使用既有匹配配置，缺失时停止；禁止跨 registry 复制 npmjs 认证或覆盖用户已有配置。
- 必须由用户环境完成 Token 注入后调用 make whoami / make publish-current，禁止把真实 export 命令写入文档、脚本或 Git。

## 完成标准

- 身份、registry 和包授权匹配，认证失败停止后续步骤。
- 认证文件只引用变量、被 Git 忽略且不在 tarball，输出与差异不含秘密。
- 人工核对操作时官方文档日期、Token scope/有效期与包组织策略；权限或交互缺失时准确报告，禁止降低策略或无授权创建凭据。
