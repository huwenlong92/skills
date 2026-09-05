# npm 包发布流程规范

## 目录和入口

- 所有路径以目标 npm 包仓库根目录为基准；不得假定包位于某个工作站目录。
- 发布入口统一使用项目根目录 `Makefile`，不要把正式发布流程散落在 README、shell 片段或一次性脚本里。
- 项目应保留发布文档，统一路径为 `deploy/DEPLOY.md`，不要在根目录保留 `DEPLOY.md`。文档只说明如何调用 `make`，不要重复维护另一套命令。

## 发布前检查

正式发布前必须至少执行：

```bash
make preflight
```

`preflight` 必须覆盖：

- 类型检查或等价静态检查，例如 `pnpm typecheck`。
- 生产构建，例如 `pnpm build`。
- 本地 tarball 生成，例如 `pnpm pack`。

如果包没有 TypeScript，也要提供等价的 `check` 目标，不能让 `preflight` 只做打包。

## 本地 tarball 验证

发布前优先用 `pnpm pack` 生成 `.tgz`，在真实业务项目中安装验证：

```bash
pnpm add /absolute/path/to/<package-name>-<version>.tgz
```

tarball 验证重点：

- `dist/` 文件是否齐全。
- `exports`、`main`、`module`、`types` 是否能被业务项目正常解析。
- CSS、静态资源、类型声明是否能按公开路径导入。
- peer dependencies 是否由业务项目提供，不能被错误打包成重复运行时。

`make preflight` 和 `make pack` 必须保留本地 `dist/` 和 `.tgz`，方便发布前检查和业务项目安装验证。真实 `npm publish` 成功后，发布入口必须自动清理 `dist/` 和 `*.tgz`，避免发布产物长期留在源码目录或被误提交。

## dry-run

正式发布前建议执行：

```bash
make publish-dry-run
```

`publish-dry-run` 必须使用和正式发布一致的 `npm publish` 参数，只额外加 `--dry-run`。

`publish-dry-run` 不升级版本，只验证当前版本的包内容和发布参数。

## 首次发布

首次发布只发布当前 `package.json` 里的版本，不自动升级版本号。初始版本还没有发布过，直接发布当前版本即可；日常更新才需要自动升级版本。

首次发布前必须确认：

- `name`：npm 包名正确，scoped 包使用 `@scope/name`。
- `version`：是要首次发布的初始版本。
- `license`：与 `LICENSE` 文件一致。
- `repository`、`homepage`、`bugs`：指向当前源码仓库。
- `files`：只发布稳定产物目录，默认是 `dist`。
- `publishConfig.access`：public scoped 包必须是 `public`。

首次发布前必须确认 npm 登录账号：

```bash
make whoami
```

如果未登录：

```bash
make login
```

如果 npm 默认 web 登录要求通信密钥、指纹、Face ID、Windows Hello 或外置安全密钥，而当前设备不可用，改用：

```bash
make login-legacy
```

`login-legacy` 走用户名/密码提示。npm 当前 2FA 主流程是 security-key/WebAuthn，也就是通行密钥、Touch ID、Face ID、Windows Hello 或外置安全密钥；传统“扫码绑定验证码 App”的入口不一定会出现。npm 也可能在网页登录时发送邮箱一次性验证码；这只是登录校验步骤，不应把邮箱验证码当作可复用发布凭据。登录成功后 npm 会把本机凭据写入 `.npmrc`，认证信息不得提交到 Git。

如果希望发布时不再触发通行密钥或指纹，使用 npm granular access token：

- token 权限选择 `Read and write`。
- token 只授权需要发布的 package、scope 或组织。
- token 设置明确过期时间。
- 如果账号或包要求发布 2FA，发布自动化 token 需要开启 `Bypass 2FA`。
- token 明文只放在本机环境变量、密码管理器或 CI secret，不写入 Git。

生成 token 的推荐配置：

- 从 npmjs.com 右上角头像进入 `Access Tokens`。
- 选择 `Generate New Token`。
- 权限选择 `Read and write`。
- 只授权当前包、当前 scope 或必要组织。
- 设置明确过期时间。
- 如果这个 token 用于发布，并且账号或包要求 2FA，勾选 `Bypass 2FA`。
- 生成后只复制一次，保存到密码管理器。

本地发布：

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

Makefile 只允许自动生成本地忽略文件 `.npmrc.token`，文件内容引用 `${NPM_TOKEN}`，不得写入真实 token。不要为 token 增加单独发布入口；`NPM_TOKEN` 只是同一套 `make whoami`、`make publish-current`、`make publish` 的认证来源。

所有真实发布目标必须在发布前执行 npm 登录检查。自动升级版本的目标必须先确认 npm 登录有效，再执行 `npm version`，避免版本号已经升级但发布失败。

如果旧流程或手工命令已经先升级版本、随后因为 npm 登录失败或权限失败而发布中断，修复登录或权限后必须使用：

```bash
make publish-current
```

不要继续执行 `make publish`，避免再次升级 patch 版本。

首次发布前必须执行：

```bash
make preflight
make publish-dry-run
```

`publish-dry-run` 输出必须检查：

- 包名和版本正确。
- tarball 文件清单只包含预期发布内容。
- scoped public 包发布参数包含 `--access public`。
- `dist`、类型声明、CSS 公开入口都在 tarball 中。

首次发布执行：

```bash
make publish-current
```

`make publish-current` 发布成功后必须自动执行清理，删除本地 `dist/` 和 `*.tgz`。如果发布失败，不要清理产物，方便排查 dry-run、build 或 npm publish 输出。

不要用 `make publish` 做首次发布，因为 `make publish` 会自动执行 patch 升级。

首次发布后必须检查：

```bash
npm view <package-name> version
npm view <package-name> dist-tags
```

然后在真实业务项目安装验证：

```bash
pnpm add <package-name>@latest
```

如果包有 peer dependencies，业务项目安装命令必须显式带上必要 peer dependency 版本，避免 npm tag 异常导致装错主版本。

发布成功后再按需提交版本和发布流程文件。不要使用 `git add .`，只暂存本次发布相关文件。

## 日常正式版本发布

日常正式发布默认使用：

```bash
make publish
```

`make publish` 必须自动执行 patch 版本升级，然后发布到 `latest`。如果要指定版本升级类型，使用：

```bash
make release-patch
make release-minor
make release-major
```

语义：

- `release-patch`：小修复。
- `release-minor`：向后兼容的新功能。
- `release-major`：破坏性变更。

版本升级使用 `npm version <patch|minor|major> --no-git-tag-version`。Makefile 不自动 commit 或 tag，发布成功后由维护者按本次变更范围提交。

首次发布或已经手动改好版本号时，使用：

```bash
make publish-current
```

`publish`、`publish-beta`、`release-*` 最终都必须复用 `publish-current`，因此真实发布成功后统一清理本地 `dist/` 和 `*.tgz`。

## prerelease 发布

测试版发布使用 prerelease 版本号和独立 npm dist-tag：

```bash
make publish-beta
```

默认：

- `PREID=beta`
- `PRERELEASE_TAG=beta`

发布 rc 时同时指定 prerelease id 和 npm dist-tag：

```bash
make release-beta PREID=rc PRERELEASE_TAG=rc
```

不要把 prerelease 发布到 `latest`。

## clean tree guard

`release-*` 目标默认必须检查 Git 工作区是否干净：

```bash
git status --short
```

只有明确知道风险时才允许：

```bash
make release-patch ALLOW_DIRTY=1
```

允许 dirty tree 发布时，必须在最终回复或发布记录里说明当时存在的未提交改动。

## npm cache

Makefile 的 npm 命令默认使用项目内 `.npm-cache/`：

```make
NPM_CACHE ?= $(CURDIR)/.npm-cache
NPM_RUN := npm_config_cache=$(NPM_CACHE) npm
```

这样可以避免全局 `~/.npm` 权限问题。`.npm-cache/` 必须加入 `.gitignore`。

## 发布后检查

发布成功后至少检查：

```bash
npm view <package-name> version
npm view <package-name> dist-tags
```

业务项目升级正式版：

```bash
pnpm add <package-name>@latest
```

业务项目安装 prerelease：

```bash
pnpm add <package-name>@beta
```

## GitHub 公开介绍页

如果源码仓库不希望开源到 GitHub，可以采用“源码仓库 + GitHub 公开介绍页”分离模式：

- `origin` 指向真实源码仓库，例如 Gitee、私有 GitLab 或私有 GitHub。
- `package.json.repository` 指向真实源码仓库。
- `package.json.homepage` 可以指向 GitHub 公开介绍页。
- GitHub 公开仓库只放 `README.public.md` 渲染后的 `README.md`、demo 截图、安装说明、release 说明等公开材料。
- 不要把 `src/`、`playground/`、`package.json`、锁文件、内部脚本同步到 GitHub 公开仓库。

公开同步脚本必须使用白名单复制，并在同步前清空临时克隆里的非 `.git` 内容，避免旧源码继续留在公开仓库：

```bash
DRY_RUN=1 make sync-github-public
make sync-github-public
```

推荐入口：

```make
sync-github-public:
	bash deploy/release/sync-github-public

publish-readme: sync-github-public
```

同步脚本默认复制：

- `README.public.md` -> `README.md`
- `docs/public/images/` -> `docs/images/`
- 兼容已有项目把 `docs/assets/` -> `docs/images/`

脚本必须支持：

- `GITHUB_PUBLIC_REPO_URL=git@github.com:owner/repo.git` 覆盖公开仓库。
- `GITHUB_PUBLIC_BRANCH=main` 覆盖公开分支。
- `DRY_RUN=1` 只显示将提交的公开文件，不 commit、不 push。

新包可复制 `templates/deploy/release/sync-github-public`，然后把脚本里的默认 `GITHUB_PUBLIC_REPO_URL` 改成该包的 GitHub 公开仓库地址。
