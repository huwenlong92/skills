# package.json 规范

## 必备元数据

可发布 npm 包必须维护这些字段：

- `name`：npm 包名。scoped 包使用 `@scope/name`。
- `version`：发布版本号，遵循 semver。
- `description`：一句话说明包能力。
- `license`：与 `LICENSE` 文件一致，例如 `MIT`。
- `packageManager`：锁定包管理器，例如 `pnpm@11.1.2`。
- `repository`：源码仓库地址。
- `bugs`：issue 地址。
- `homepage`：README 或项目主页。
- `keywords`：便于 npm 搜索的关键词。

如果源码仓库不公开到 GitHub，`repository` 仍然必须指向真实源码仓库，例如 Gitee 或私有 GitLab；`homepage` 可以指向只放介绍和 demo 图的 GitHub 公开页。

示例：

```json
{
  "name": "@scope/package-name",
  "version": "0.1.0",
  "description": "Short package description.",
  "license": "MIT",
  "packageManager": "pnpm@11.1.2",
  "repository": {
    "type": "git",
    "url": "git+ssh://git@github.com/owner/repo.git"
  },
  "bugs": {
    "url": "https://github.com/owner/repo/issues"
  },
  "homepage": "https://github.com/owner/repo#readme"
}
```

## 发布配置

scoped public 包必须显式声明：

```json
{
  "publishConfig": {
    "access": "public"
  }
}
```

Makefile 里的 `npm publish --access public` 仍然保留，`publishConfig` 是第二层保护。

## 产物导出

包只发布稳定产物，不发布源码临时文件：

```json
{
  "main": "./dist/package.umd.cjs",
  "module": "./dist/package.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/package.js",
      "require": "./dist/package.umd.cjs"
    },
    "./style.css": "./dist/style.css"
  },
  "files": [
    "dist"
  ]
}
```

规则：

- `exports` 必须覆盖业务项目实际需要导入的公开入口。
- CSS 如果需要公开导入，必须给稳定路径，例如 `./style.css`。
- `files` 默认只包含 `dist`；README、LICENSE、package.json 会由 npm 自动包含。
- 不要把 `playground/`、测试 fixture、本地脚本、临时产物发布到 npm。

## scripts

推荐脚本：

```json
{
  "scripts": {
    "dev": "vite --host 0.0.0.0",
    "typecheck": "vue-tsc --noEmit",
    "build": "vite build && vue-tsc -p tsconfig.build.json",
    "check": "pnpm typecheck && pnpm build",
    "pack:local": "pnpm check && pnpm pack",
    "prepublishOnly": "pnpm check"
  }
}
```

规则：

- `check` 是发布前最小质量门禁。
- `prepublishOnly` 必须存在，用来防止维护者绕过 Makefile 直接 `npm publish`。
- `pack:local` 可以保留给不使用 Makefile 的工具调用，但人工发布仍以 `make` 为入口。

## dependencies

- 运行时必须随包安装的依赖放 `dependencies`。
- 宿主项目必须提供且不能重复打包的依赖放 `peerDependencies`。
- 构建、类型检查、playground 使用的依赖放 `devDependencies`。
- Vue、React、编辑器内核等宿主级运行时一般应放 `peerDependencies`，并在 `devDependencies` 再放一份用于本包开发。

## sideEffects

包包含 CSS 或会被 tree-shaking 误删的副作用文件时，必须声明：

```json
{
  "sideEffects": [
    "*.css"
  ]
}
```
