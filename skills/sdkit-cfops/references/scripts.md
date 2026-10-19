# 脚本与构建

适用范围：生成、修改或执行项目 check/build/preview/deploy/verify 入口时必须读取。

## 布局与接入

- 允许将本 Skill 的 [cfops.py](../scripts/cfops.py) 复制至项目 `.sdkit/cloudflare/cfops.py`，公共发布计划放同目录 `release.json`；禁止写入 node_modules、框架生成目录或全局工具目录。已有入口允许包装本助手，禁止建立两套独立发布事实源。
- 助手会检查显式命令、声明的 package scripts（含 pre/post 生命周期）及可见脚本中的明显发布命令；这只是保守阻断，不能证明动态代码、插件、source 或外部程序无副作用，未知调用链必须停止并人工审阅。
- 必须先审阅 `build` 数组和它调用的脚本、package scripts、框架配置及生命周期；无 shell 拼接不能保证构建无副作用。禁止将部署、资源创建、数据迁移或远端写入藏在 build 中。
- 新增的本地结果目录 `.sdkit/cloudflare/.local/` 必须加入项目 `.gitignore`；禁止提交包含环境变量、凭据或原始日志的记录。
- 计划中的路径必须相对项目根目录；Wrangler 自身的 output/main 相对配置文件目录解析。禁止使用工作站绝对路径、越界路径、符号链接产物或非普通文件。
- 助手必须阻断根目录动态 `wrangler.ts/js/mjs/cjs` 和 `.wrangler/deploy/config.json` 重定向配置，必须在执行前和构建后重复检查，并在构建改写生效配置时停止；禁止忽略框架生成配置后发布原始配置。
- 助手支持 TOML（Python 3.11+）、JSON、JSONC 的显式配置；框架自动生成配置、动态配置与特殊 bundle 必须按锁定版本适配，禁止声称本助手已覆盖。

## 按产物分流

| 类型 | 必须执行 | 禁止行为 |
|---|---|---|
| pages-static | 调用项目确认的 Vite/静态站构建，检查首页、静态资源、构建 mode、API 地址和客户端深层路由 | 禁止把本地代理地址或开发凭据编进产物 |
| pages-nuxt | 使用项目确认的 Pages preset，检查 `_worker.js/index.js`、`_routes.json`、SSR 与所需 Binding | 禁止把 Node 开发适配、临时 R2 代理或 Node-only 依赖直接带入 Worker |
| worker | 调用项目构建，再执行锁定 CLI 的 `deploy --dry-run`，检查 bundle 和入口 | 禁止把 dry-run 称为完全无副作用，必须先审阅自定义 build hook |

- 必须按项目规则运行类型/合约检查；构建仅执行一次，deploy 助手会自行构建，禁止外层又依赖 build 造成重复。
- `required_files` 必须包含实际必要产物；Nuxt Pages 固定额外检查 Worker 与 routes。前端产物必须人工检查公开内容、开发地址及 Secrets 泄漏。
- 新目录产物必须排除旧 hash 混杂；只有确认是该构建的派生产物且本次允许清理时才能删除精确目录，禁止宽泛 rm 清场。
- 预览使用 localhost；必须排除 remote Binding 和 build hook 的未授权副作用，`pages dev` 不等于纯静态文件服务。

## 正向入口

从项目根目录运行；目标名必须显式传入，禁止默认选生产：

```sh
python3 .sdkit/cloudflare/cfops.py check --target review
python3 .sdkit/cloudflare/cfops.py build --target review
python3 .sdkit/cloudflare/cfops.py preview --target review
```

[Makefile 示例](../assets/Makefile)仅用于合并命中目标，禁止覆盖原 Makefile。命令数组正向为 `["pnpm", "run", "build:cloudflare"]`；反例为把 Token、`&& wrangler deploy` 或远端 SQL 放入构建脚本。

## 完成标准

check 不执行项目命令、不联网、不加载 dotenv；三个类型分别验证产物。人工审阅 build 调用链、Binding 副作用、打包内容及遗留发布脚本；不支持的配置明确停止，不静默退回猜测。
