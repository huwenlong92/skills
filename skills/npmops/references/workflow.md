---
name: npmops-workflow
description: npm 包打包与消费验证、首次和日常发布、prerelease、失败恢复及发布后验收。
---

# 打包与发布流程

适用范围：pack、release、version、dist-tag 或 registry 发布任务。真实发布必须同时读取[认证](auth.md)；新增或修改发布入口必须同时读取[Makefile](makefile.md)。

源码身份、双阶段 Git 同步与跨会话检查必须执行[仓库协作](repository.md)。同步状态检查不构成版本变更或发布授权。

## 入口与前置条件

- 发布必须从目标包根目录的 Makefile 进入；发布说明必须放在 `deploy/DEPLOY.md`，禁止在根目录 `DEPLOY.md` 或零散 shell 片段维护另一套正式流程。
- 必须确认 name/version、registry、access、版本渠道及本次授权。scope registry、publishConfig 与实际发布参数必须一致，冲突时停止，禁止向其他 registry 试发。
- 版本发布必须先检查 Git 工作区干净和认证有效，再修改版本。ALLOW_DIRTY=1 仅当用户明确允许带未提交改动发布时使用，交付必须记录差异；禁止自动 stash、清理或提交来绕过检查。
- Git commit/tag/push 与 npm 发布分别判断授权，Makefile 禁止自动执行这些 Git 写操作。

## 打包与消费验证

```bash
make preflight
make publish-dry-run
```

- preflight 必须顺序执行静态检查、构建与本地 tarball 生成；非 TypeScript 包必须提供等价静态检查，禁止只打包而跳过检查。
- 必须检查 tarball 中的 dist、类型、CSS/资源和公开入口，验证 peer 边界且无秘密。[包结构](package-json.md)是字段与文件范围的权威定义。
- 必须在已确认的消费项目或等价隔离 fixture 安装当前生成的真实 tarball，验证 import/require、类型与公开资源路径。仅当真实消费项目有不可替代的集成要求时必须使用该项目；禁止未经授权修改其他项目。
- dry-run 必须与真实发布使用相同 registry、access 和 dist-tag，只增加 --dry-run，禁止升级版本。必须先审计生命周期脚本；dry-run 仍可能执行这些脚本，成功不证明发布权限或真实发布成功。
- preflight、pack、dry-run 必须保留 dist 与 tgz；真实发布失败必须保留产物，真实发布成功后才允许清理当前包的 dist 与本地 tgz，禁止清理其他项目。

正向形态：生成 tarball，在隔离消费者安装并导入公开入口，再核对 dry-run 清单和参数。反例：只运行 playground 就声称打包产物可以使用。

## 版本与发布入口

| 情形 | 入口与行为 |
|---|---|
| 首次发布，或版本已经改好 | make publish-current：发布当前版本，禁止再次 bump |
| 日常正式更新，无其他升级类型要求 | make publish → release-patch → patch bump → publish-current TAG=latest |
| 明确 minor/major 更新 | make release-minor / make release-major |
| 新测试版本 | make publish-beta → prerelease bump → publish-current TAG=<PRERELEASE_TAG> |
| 已有测试版本，只发布当前版本 | make publish-current-beta，禁止再次 bump |
| rc | make release-beta PREID=rc PRERELEASE_TAG=rc |

- 版本修改必须使用 npm version ... --no-git-tag-version；release-* 必须复用 publish-current，禁止回调 publish 导致二次升级。
- 正式默认渠道为 latest，测试默认 PREID 与 PRERELEASE_TAG 为 beta；项目指定其他测试渠道时使用声明值。禁止将 prerelease 发布到 latest。
- 首次发布前必须确认当前版本未发布；日常发布必须核对现有版本与 dist-tags，禁止把网络、认证或 registry 错误当成“版本不存在”。

## 失败与恢复

- 检查、认证或构建失败必须停止后续步骤；禁止继续发布或清理失败产物。
- 已 bump 但发布失败时，修复后必须使用 publish-current 或 publish-current-beta，禁止重新执行会 bump 的入口。
- 发布请求结果不确定时，必须查询目标 registry 的精确版本与 dist-tags；禁止盲目重发、再次 bump、删除版本或覆盖发布。
- 发布成功但清理、消费验证或 Git 失败时，必须分别报告 registry 已发布与后续失败，禁止重新发布以掩盖错误。

## 完成标准

```bash
# 占位值必须替换为本次已核对的值。
npm view <package>@<version> version --registry=<registry>
npm view <package> dist-tags --registry=<registry>
```

- 真实发布必须核对精确版本存在、目标 tag 指向该版本，再在消费项目或隔离 fixture 安装精确版本验证；tag 安装必须检查实际版本与必要 peer 版本。
- 完成：打包清单、公开入口和消费验证通过；真实发布时 registry、精确版本、tag 与清理状态均有证据。
- 受阻：报告失败阶段、版本是否改变、远端能否确认及产物是否保留；禁止把 dry-run 或登录成功描述为已发布。
- 人工检查包名/registry/access、版本选择、文件清单、消费范围与 Git 差异是否属于本次授权。
