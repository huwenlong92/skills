# 发布目标与配置

适用范围：首次接入、发布预检、配置或目标迁移、发错项目排查时必须读取。

## 唯一目标

- 必须同时核对账户、Pages/Worker 项目标识、生效配置、Preview/Production、Pages 生产分支或 Worker env、域名与本次授权。禁止用文件夹名、门户展示名或历史文档推导云端目标。
- 必须比较项目规则、Wrangler 配置、创建/部署脚本和 Provider 实时结果；发生冲突时停止部署并展示差异。历史阶段授权不能替代本次发布授权。
- Pages 的 `--branch` 表示部署分支；必须查询云端 production branch 后判断环境，禁止假设只有 main 是生产。Pages 的 preview/production 配置与 Worker 命名 env 必须分别处理。
- 允许保留具有明确用途的多配置；禁止同时把不同配置称为唯一事实源。脚本离线检查发现多个配置时会停止，必须先明确实际范围并经审阅消除歧义，禁止为绕过检查删除未知配置。
- 必须检查工作区是否处于 Merge/Rebase/Cherry-pick 等中断状态；存在中断操作时停止发布。禁止自动 reset、clean、stash 或切换分支清场。

## 存放位置与工具

- 新发布计划允许放在项目根目录下 `.sdkit/cloudflare/release.json`，示例见 [release.example.json](../assets/release.example.json)；既有 `deploy/cloudflare/` 必须先复用，禁止无授权批量迁移。
- Pages 必须使用项目根目录标准 `wrangler.toml`、`wrangler.json` 或 `wrangler.jsonc` 自动发现，禁止向 Pages dev/deploy 传 `--config`；Worker 配置允许放在项目已确认的根目录或框架规定目录；禁止在 Skill 安装目录保存项目配置，禁止为个人账户或 Token 新增项目内配置。
- 第一版没有个人配置读取需求，因此禁止创建空的个人 config。后续引入时必须默认使用 `~/.config/sdkit/skills/sdkit-cfops/config.json`，显式路径覆盖默认值；迁移必须验证旧内容、目标不存在、权限和实际读取结果，验证前保留原件。
- 必须使用项目安装并锁定的 Wrangler，核对 lockfile 与 `--version`；脚本按计划的精确版本阻断漂移。禁止自动安装或升级 latest；缺工具时报告缺口。
- 必须保留项目已验证的 TOML/JSON/JSONC 格式及 compatibility_date，禁止为发布顺手转换格式或推进兼容日期。字段语义必须查询项目 schema 和 [官方配置](https://developers.cloudflare.com/workers/wrangler/configuration/)。

## 正向形态与反例

正向：计划、根配置与发布参数均指向 `example-portal`；云端确认 production branch 为 `release`；上传 `review` 分支属于 Preview。

反例：配置为 `example-portal`，创建脚本仍为 `template-web`，直接执行脚本。必须先修正已授权文件并复核，禁止默许创建或覆盖另一个项目。

## 完成标准

离线报告标明本地检查范围；人工检查项目规则和所有既有发布入口；云端账户、分支、环境与配置一致后才能进入发布。只有离线结果时必须写明云端待核验。
