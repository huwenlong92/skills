---
name: cfops
description: 为 Cloudflare Pages 静态站、Nuxt Pages SSR 和独立 Worker 核对发布目标，维护构建发布脚本，执行已授权部署、上线验收与回滚检查；不负责业务代码、R2 内容版本、数据库操作或 DNS/Access 管理。
---

# Cloudflare 发布协作

## 分流

| 任务 | 必须读取 |
|---|---|
| 检查目标、排查发错项目或配置冲突 | [目标与配置](references/target.md) |
| 新增或调整构建、预览、发布入口 | [脚本与构建](references/scripts.md) |
| 部署、CI 发布或认证排查 | [发布流程](references/release.md) |
| 判断是否上线、验收域名或 Binding | [上线验收](references/verification.md) |
| 发布失败、回退或恢复中断 | [失败与回滚](references/rollback.md) |

## 执行顺序

1. 读取目标项目规则及实际配置，确定 Pages 静态、Pages Nuxt SSR 或 Worker；框架生成配置时必须先明确生效配置及构建入口，禁止自动改换平台。
2. 按命中 reference 核实目标、工具链和本次授权。只讨论或只读检查时禁止执行构建、云端写入及安装。
3. 先运行离线 `scripts/cfops.py check`；通过仅代表本地一致性，云端账户、生产分支、资源绑定、访问策略与权限必须另行核验。
4. 对已授权目标执行构建、部署、Provider 读回和实网验收，分别记录源码、产物、部署及访问证据。
5. 按任务报告已检查、已构建、已部署、已验证及未完成项；禁止以 CLI 退出 0 代替上线验收。

## 边界

- 本 Skill 自包含。存在已安装且适用的 `wrangler` Skill 时读取其命中规则；不存在时使用本 Skill 的官方文档入口及项目锁定 CLI/schema，禁止把外部 Skill 当作硬依赖。
- 应用代码由实际技术栈能力负责；R2 内容发布由项目内容发布入口负责。禁止因部署前端覆盖 Latest、迁移 Bucket、改写数据库或触发业务写接口。
- 发布、回滚、Git 提交/Push/PR、资源创建、域名和访问策略修改分别核对当前授权；安装 Skill 不授予这些权限。
- 正式数据库禁止 AI 直接或通过 CI 间接操作；探针必须排除会触达正式数据库的接口。远端开发数据操作必须另行核实身份与授权。
- 项目可见性服从用户明确选择，禁止统一强制公开或强制 Access；保持已有 CI/Git 自动部署开关，除非本次明确授权改变。
