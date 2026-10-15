---
name: npmops-package-json
description: 可发布 npm 包的元数据、公开入口、发布文件、scripts 与依赖边界。
---

# package.json 与发布内容

适用范围：创建、修改或评审 npm 包 metadata、exports、scripts、依赖及打包文件。字段必须位于目标包根目录的 package.json；禁止放进消费应用或其他 workspace 包替代本包配置。

## 元数据

- 必须维护 name、semver version、description、license、packageManager、repository、bugs、homepage 与 keywords。license 必须和 LICENSE 一致；packageManager 必须固定项目实际版本，禁止套用示例工具版本。
- repository 必须指向真实源码；私有源码不得伪装成公开介绍页。homepage 允许指向公开页，bugs 必须指向真实问题入口，禁止填写不存在的占位地址。
- scoped public 包必须显式声明 publishConfig.access 为 public，registry/access 必须和[发布流程](workflow.md)一致；restricted 包禁止沿用 public 模板参数。

以下是脱敏形态；包名与 URL 必须替换为真实声明，并补齐项目 packageManager：

```json
{
  "name": "@example/atlas",
  "version": "0.1.0",
  "description": "Atlas components",
  "license": "MIT",
  "repository": {"type": "git", "url": "https://code.example.invalid/team/atlas.git"},
  "bugs": {"url": "https://code.example.invalid/team/atlas/issues"},
  "homepage": "https://docs.example.invalid/atlas",
  "keywords": ["components"],
  "publishConfig": {"access": "public"}
}
```

## 公开入口与文件

- 必须只发布稳定产物；files 以 dist 为允许范围，禁止包含 playground、测试 fixture、本地脚本、私密配置和临时产物。README、LICENSE、package.json 的实际包含情况必须通过 pack 清单核对，禁止仅凭 files 推断 tarball 安全。
- exports 必须覆盖真实公开入口；types、import、require、main、module 必须对应实际构建输出。仅当支持对应格式时允许声明，禁止为凑齐字段填写不存在的 CJS/ESM/类型路径。
- CSS 和公开资源必须提供稳定路径；副作用文件必须在 sideEffects 声明对应模式，禁止被 tree-shaking 误删。

以下仅适用于确实输出 ESM、CJS、类型与 CSS 的包，单格式包必须移除不支持的入口：

```json
{
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {"types": "./dist/index.d.ts", "import": "./dist/index.js", "require": "./dist/index.cjs"},
    "./style.css": "./dist/style.css"
  },
  "files": ["dist"],
  "sideEffects": ["**/*.css"]
}
```

## scripts 与依赖

- 必须提供 dev、静态检查、build、check；check 必须顺序检查和构建。非 TypeScript 包允许保留 typecheck 目标调用等价检查，禁止以空命令伪造成功。
- 必须提供 prepublishOnly 调用 check，使常规直接发布也经过检查；不能阻止主动禁用生命周期脚本，禁止描述为不可绕过的保护。
- 允许提供 pack:local 给工具调用，人工正式发布必须走 Makefile。[Makefile](makefile.md)定义编排入口。
- 随包安装的运行时依赖必须放 dependencies；宿主提供且禁止重复打包的运行时必须放 peerDependencies，并在 devDependencies 配置开发所需版本。仅构建、检查、playground 使用的依赖必须放 devDependencies。
- Vue、React、编辑器内核作为宿主运行时时必须遵守 peer 边界，禁止只因依赖名称相同就机械套用；独立运行包必须按真实所有权分类。

以下 scripts 只适用于 Vite/vue-tsc 包，其他包必须使用已有工具链，禁止为了套用示例引入 Vue：

```json
{
  "scripts": {
    "dev": "vite",
    "typecheck": "vue-tsc --noEmit",
    "build": "vite build && vue-tsc -p tsconfig.build.json",
    "check": "pnpm typecheck && pnpm build",
    "pack:local": "pnpm check && pnpm pack",
    "prepublishOnly": "pnpm check"
  }
}
```

## 完成标准

- metadata 与真实项目一致，工具版本和 URL 未被模板值替代。
- pack 清单只有允许产物与必要元数据，无秘密或开发目录。
- 全部公开路径存在于 tarball 并通过[消费验证](workflow.md)。
- 人工检查依赖所有权、资源副作用及模块格式与入口的一致性。
