---
name: npmops-makefile
description: Makefile 编排 npm 包检查、打包、认证、版本升级与发布的入口契约。
---

# Makefile 入口

适用范围：创建、修改或评审目标 npm 包 Makefile。版本和失败恢复以[发布流程](workflow.md)为准，凭据以[认证](auth.md)为准，禁止重复维护平台教程。

## 放置与模板

- Makefile 必须放在包根目录，构建逻辑必须放 package.json scripts；只有项目 scripts 无法表达必要适配时，才允许在 recipe 编写适配，禁止复制业务构建逻辑。
- [Makefile 模板](templates/Makefile)必须按实际 dev、typecheck、build、registry/access 与清理范围调整，禁止覆盖未经审计的项目自定义目标。
- npm 命令必须复用 NPM_RUN，登录复用 NPM_LOGIN_RUN；registry 必须统一使用 NPM_REGISTRY。模板默认值只表示公共 npmjs/public 包，必须从项目或用户确认目标值。

## 目标契约

| 类型 | 必须提供的入口与行为 |
|---|---|
| 开发 | help、install、dev、typecheck、build、check；顺序检查再构建 |
| 打包 | pack、preflight；check 后 pack，保留产物 |
| 认证 | login、login-legacy、whoami、prepare-npm-auth、check-npm-auth；条件见认证 reference |
| 当前版本 | publish-current、publish-current-beta、check-publish-channel；认证、渠道检查、构建、发布成功后 clean |
| 预览 | publish-dry-run、publish-beta-dry-run；不 bump、不清理、不写 registry |
| 版本 | publish、publish-beta、release-patch/minor/major/beta、version-patch/minor/major/beta、check-clean |
| 清理 | clean；只清当前包 dist 和 tgz，不清其他项目或认证文件 |
| 公开页（仅需要时） | sync-github-public、publish-readme；执行[公开页规则](public-page.md)，禁止混入 npm 发布目标 |

## 顺序与变量

- check-clean、认证、bump、发布必须在 recipe 中顺序调用，禁止声明为可并行 prerequisites。
- 必须保留 PNPM、NPM、NPM_CACHE、TOKEN_NPMRC、NPM_USERCONFIG、NPM_REGISTRY、NPM_ACCESS、TAG、PREID、PRERELEASE_TAG 入口。缓存默认 .npm-cache/，Token 配置默认 .npmrc.token；二者必须位于包根目录、被 Git 忽略且排除打包。
- TAG 表示 dist-tag，PREID 表示 semver prerelease id；版本目标必须带 --no-git-tag-version，禁止自动 commit/tag/push。
- ALLOW_DIRTY 与清理规则以[发布流程](workflow.md)为准，禁止在模板放宽。

```make
check:
	$(MAKE) typecheck
	$(MAKE) build

pack:
	$(MAKE) check
	$(PNPM) pack

publish-current:
	$(MAKE) check-npm-auth
	$(MAKE) check
	$(NPM_RUN) publish --registry="$(NPM_REGISTRY)" --access="$(NPM_ACCESS)" --tag="$(TAG)"
	$(MAKE) clean
```

反例：release-patch 用并行 prerequisites 编排认证、version 与 publish，不能保证先后顺序。

## 完成标准

- make help 可读取，变量符合项目，无真实账号、凭据或无关仓库地址。
- 模板修改必须在临时 fixture 用替身 npm/pnpm 验证认证/检查失败不发布、重试不再 bump、成功才清理、并行 make 顺序不变；禁止真实发布或修改业务版本。
- 修改模板必须核对本文件、认证和发布 reference；涉及公开页时必须核对公开页 reference。
- 人工检查 registry/access、生命周期脚本与清理范围。
