# Makefile 发布入口规范

## 基本原则

- npm 包项目根目录必须提供 `Makefile`。
- 人工发布统一从 `make` 入口执行，避免每个项目复制散乱命令。
- Makefile 只编排流程，不把包名、业务路径、构建逻辑硬编码到通用目标里。
- 真正构建逻辑优先放在 `package.json` scripts，Makefile 调用 `pnpm` 和 `npm`。

## 必备变量

```make
PNPM ?= pnpm
NPM ?= npm
NPM_CACHE ?= $(CURDIR)/.npm-cache
TOKEN_NPMRC ?= $(CURDIR)/.npmrc.token
ifneq ($(strip $(NPM_TOKEN)),)
NPM_USERCONFIG ?= $(TOKEN_NPMRC)
else
NPM_USERCONFIG ?=
endif
TAG ?= latest
PREID ?= beta
PRERELEASE_TAG ?= beta
```

说明：

- `NPM_CACHE` 默认指向项目内 `.npm-cache/`，避免全局 npm cache 权限问题。
- `NPM_USERCONFIG` 用于指定发布时的 npm config 文件；token 发布时指向 `.npmrc.token`。
- `TOKEN_NPMRC` 是本地 token config 文件路径，必须加入 `.gitignore`。
- `TAG` 用于正式发布或自定义 dist-tag。
- `PREID` 用于 semver prerelease 标识。
- `PRERELEASE_TAG` 用于 prerelease npm dist-tag。

## 必备目标

开发和检查：

- `help`：列出可用命令和变量。
- `install`：安装依赖。
- `dev`：启动开发或 playground。
- `typecheck`：类型检查或等价静态检查。
- `build`：生产构建。
- `check`：按顺序执行 `typecheck` 和 `build`。

打包：

- `pack`：执行 `check` 后 `pnpm pack`。
- `preflight`：发布前预检，默认等价于 `pack`。
- `clean`：清理 `dist` 和本地 `.tgz`。

发布：

- `login`：npm 登录。
- `login-legacy`：npm 用户名/密码登录；当 web 登录要求通信密钥但当前设备不可用时使用。
- `whoami`：查看 npm 登录账号；如果存在 `NPM_TOKEN`，自动使用 token。
- `publish`：检查 Git 工作区干净，自动升级 patch 版本，然后发布到 `latest`。
- `publish-beta`：检查 Git 工作区干净，自动升级 prerelease 版本，然后发布到 prerelease tag。
- `publish-current`：执行 `check` 后发布当前版本；如果存在 `NPM_TOKEN`，自动使用 token；真实发布成功后执行 `clean`。
- `publish-current-beta`：发布当前版本到 prerelease tag。
- `publish-dry-run`：执行正式发布 dry-run。
- `publish-beta-dry-run`：执行 prerelease 发布 dry-run。
- `check-npm-auth`：发布前检查 npm 登录是否有效。

可选公开页：

- `sync-github-public`：只同步公开 README 和 demo 图到 GitHub，不同步源码。
- `publish-readme`：`sync-github-public` 的别名。

版本发布：

- `release-patch`
- `release-minor`
- `release-major`
- `release-beta`

## 顺序执行

`check` 和 `pack` 必须在 recipe 内显式顺序调用，避免用户执行并行 make 时类型检查和构建并行：

```make
check:
	$(MAKE) typecheck
	$(MAKE) build

pack:
	$(MAKE) check
	$(PNPM) pack
```

`pack`、`preflight`、`publish-dry-run` 必须保留本地 `dist/` 和 `.tgz`，方便发布前验证。`publish-current` 必须在真实 `npm publish` 成功后执行 `clean`：

```make
publish-current:
	$(MAKE) check-npm-auth
	$(MAKE) check
	$(NPM_RUN) publish --access public --tag $(TAG)
	$(MAKE) clean
```

## clean tree guard

`release-*` 必须先执行：

```make
check-clean:
	@if [ "$(ALLOW_DIRTY)" != "1" ] && [ -n "$$(git status --short)" ]; then \
		printf "%s\n" "Working tree is not clean. Commit/stash changes first, or rerun with ALLOW_DIRTY=1."; \
		git status --short; \
		exit 1; \
	fi
```

## npm 登录检查

所有会真实发布或自动升级版本的目标，都必须先检查 npm 登录状态：

```make
check-npm-auth:
	@if ! $(NPM_RUN) whoami >/dev/null 2>&1; then \
		printf "%s\n" "npm auth is invalid. If using a token, export NPM_TOKEN and run 'make whoami'. Otherwise run 'make login' or 'make login-legacy'. If the version was already bumped, retry with 'make publish-current'."; \
		exit 1; \
	fi
```

`release-*` 必须在 `version-*` 前执行 `check-npm-auth`，避免先升级版本后才发现 npm 未登录。

当 npm 默认 web 登录要求通信密钥、指纹、Face ID、Windows Hello 或外置安全密钥，而当前设备不可用时，提供 legacy 登录入口：

```make
login-legacy:
	$(NPM_RUN) login --auth-type=legacy --registry=https://registry.npmjs.org/
```

npm 当前 2FA 主流程是 security-key/WebAuthn，也就是通行密钥、Touch ID、Face ID、Windows Hello 或外置安全密钥；传统“扫码绑定验证码 App”的入口不一定会出现。不要把 npm token 或 `.npmrc` 中的认证信息提交到 Git。

## token 发布

需要避免每次发布都触发通行密钥或指纹时，使用 npm granular access token。token 必须按最小权限生成：

- 权限选择 `Read and write`。
- 只授权需要发布的 package、scope 或组织。
- 设置明确过期时间。
- 账号或包要求发布 2FA 时，只有发布自动化 token 可以开启 `Bypass 2FA`。
- 不要把 token 明文写入仓库。

生成 token 的推荐配置：

- 从 npmjs.com 右上角头像进入 `Access Tokens`。
- 选择 `Generate New Token`。
- 权限选择 `Read and write`。
- 只授权当前包、当前 scope 或必要组织。
- 设置明确过期时间。
- 如果这个 token 用于发布，并且账号或包要求 2FA，勾选 `Bypass 2FA`。
- 生成后只复制一次，保存到密码管理器。

Makefile 必须自动选择认证来源：存在 `NPM_TOKEN` 时使用本地 `.npmrc.token`，否则使用本机 npm 登录态。token 不应引入单独的发布命令。

```make
TOKEN_NPMRC ?= $(CURDIR)/.npmrc.token

ifneq ($(strip $(NPM_TOKEN)),)
NPM_USERCONFIG ?= $(TOKEN_NPMRC)
else
NPM_USERCONFIG ?=
endif

ifdef NPM_USERCONFIG
NPM_RUN := npm_config_cache=$(NPM_CACHE) npm_config_userconfig=$(NPM_USERCONFIG) $(NPM)
else
NPM_RUN := npm_config_cache=$(NPM_CACHE) $(NPM)
endif

prepare-npm-auth:
	@if [ -n "$$NPM_TOKEN" ]; then \
		printf "%s\n" '//registry.npmjs.org/:_authToken=$${NPM_TOKEN}' > "$(TOKEN_NPMRC)"; \
	fi
```

本地使用：

```bash
export NPM_TOKEN="npm_xxx"
make whoami
make publish-current
```

日常自动 patch 发布：

```bash
export NPM_TOKEN="npm_xxx"
make publish
```

`.npmrc.token` 必须加入 `.gitignore`。如果项目选择提交 `.npmrc`，只能提交 `//registry.npmjs.org/:_authToken=${NPM_TOKEN}` 这种环境变量引用，不能提交真实 token。

## 版本升级

日常正式发布入口使用自动 patch：

```make
publish:
	$(MAKE) release-patch
```

版本升级目标使用 `--no-git-tag-version`：

```make
version-patch:
	$(NPM_RUN) version patch --no-git-tag-version
```

`release-*` 目标升级版本后必须调用 `publish-current`，不能调用 `publish`，避免重复升级版本。

Makefile 不自动 commit 或 tag，避免把未审查改动带进版本提交。首次发布或手动改好版本号后，使用 `publish-current` 发布当前版本。

## GitHub 公开页同步

需要 GitHub 公开介绍页的 npm 包，Makefile 必须提供：

```make
sync-github-public:
	bash deploy/release/sync-github-public

publish-readme: sync-github-public
```

同步脚本的统一约定：

- 目标仓库使用 `GITHUB_PUBLIC_REPO_URL`，项目可设置默认值，例如 `git@github.com:<owner>/<package>.git`。
- 默认分支使用 `GITHUB_PUBLIC_BRANCH`，默认值 `main`。
- 只复制 `README.public.md` 到公开仓库 `README.md`。
- demo 图优先从 `docs/public/images/` 复制到公开仓库 `docs/images/`；兼容已有项目从 `docs/assets/` 复制。
- 每次同步前清空公开仓库工作区中除 `.git` 以外的顶层内容，确保 GitHub 不混入源码文件。
- 必须支持 `DRY_RUN=1`，只展示 `git status --short`，不 commit、不 push。

## 模板

新 npm 包可以复制 `templates/Makefile` 到项目根目录，然后按项目实际脚本调整 `typecheck`、`build`、`dev`。如果需要 GitHub 公开页，同步复制 `templates/deploy/release/sync-github-public` 到项目根目录对应路径，并设置脚本里的默认 `GITHUB_PUBLIC_REPO_URL`。
