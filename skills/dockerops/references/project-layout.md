---
name: dockerops-project-layout
description: 项目 Docker 发布文件的固定位置、环境模式与既有入口迁移。
---

# 项目 Docker 文件布局

适用范围：在业务项目生成、修改、查找或迁移 Dockerfile、构建/发布脚本和 Compose。执行这些任务前必须读取本文件。所有项目文件路径均以本次目标项目根目录为基准；本文件不改变 `.sdkit/` 原有协作状态文件。

## 模式选择与固定位置

- 新增 Docker 构建发布文件必须统一放在 `.sdkit/docker/`，根 Makefile 直接调用脚本。禁止在根目录、`deploy/`、`docker/` 或 `scripts/` 再生成另一套同职责实现；业务源码、普通构建产物仍按项目本身约定放置。
- 必须先读取当前用户要求、项目规则、Makefile、Compose、CI 和实际调用脚本，确定现有环境模式。单环境不创建 test/release；只有明确采用多环境时，才允许创建对应环境子目录。
- 项目没有 Docker 发布文件，或无法从证据确定环境模式时，必须询问“使用单环境，还是 test/release，或其他明确环境？”。禁止将缺文件等同于默认 test/release，也禁止默认为正式环境。
- 用户当前明确选择高于已有规范和历史模板。发现旧规范强制环境数量时必须指出差异并按当前选择实施，禁止让旧约定覆盖本次决定。

单环境必须采用以下位置；标为可选的文件只能在实际需要时生成：

```text
.sdkit/docker/
  README.md
  Dockerfile
  Dockerfile.dockerignore
  config.json
  build.sh
  publish.sh
  verify.sh
  webhook.sh         # 已配置并需要发布通知时才生成
  compose.yaml       # 需要 Compose 运行时才生成
  deploy.sh          # 已要求自动更新运行环境时才生成
  rollback.sh        # 已实现并验证回滚入口时才生成
  scripts/           # 存在实际共享实现时才生成
```

已确认 test/release 时必须采用：

```text
.sdkit/docker/
  README.md
  Dockerfile
  Dockerfile.dockerignore
  scripts/           # 存在共享逻辑时才生成
  test/
    config.json
    build.sh
    publish.sh
    verify.sh
    webhook.sh       # 该环境有通知需求时才生成
    compose.yaml     # 按实际运行方式选择
  release/
    config.json
    build.sh
    publish.sh
    verify.sh
    webhook.sh       # 该环境有通知需求时才生成
    compose.yaml
```

- 单环境的 config.json、build.sh、publish.sh、verify.sh 必须直接放在 `.sdkit/docker/`；多环境必须在 `.sdkit/docker/<环境>/` 各自保留这些入口。其他环境名称必须来自用户或项目明确声明。
- 默认共用 `.sdkit/docker/Dockerfile`；只有环境间存在无法用公开构建参数表达的构建阶段、依赖或运行基础差异时，才允许使用 `<环境>/Dockerfile`，并在配置和 README 记录原因。禁止无差别复制 Dockerfile。
- Dockerfile 专属忽略文件必须紧邻对应 Dockerfile，命名为 `<Dockerfile文件名>.dockerignore`。已有根 `.dockerignore` 必须审计保留，禁止把秘密送入构建上下文。
- scripts/ 只允许项目自身共享实现；禁止放 Skill 安装产物、Agent 插件、私有凭据或第二套发布框架。缓存、临时日志必须放系统临时目录或项目已忽略的缓存目录，禁止写入 `.sdkit/` 的状态文件或提交到发布文件目录。

## 文件职责

| 文件 | 必须承担的职责 |
| --- | --- |
| README.md | 本项目 Docker 发布的模式、环境、服务、镜像、架构、命令、版本、副作用、配置来源与恢复说明 |
| config.json | 项目可公开的镜像、平台、Dockerfile、构建上下文和公开参数；禁止包含凭据或个人路径 |
| build.sh | 构建指定范围及明确版本；禁止推送、通知 webhook、部署和清理历史版本 |
| publish.sh | 推送已构建制品并核对远端；新脚本禁止隐式 webhook、服务器更新和本地镜像清理 |
| verify.sh | 校验明确版本、digest、平台和别名，并区分本地/远端范围；禁止重建、推送或部署 |
| webhook.sh | 该环境/服务的已授权通知；必须明确是否会引起自动更新，禁止包含真实 Token、重建镜像或隐式修改其他环境 |
| compose.yaml | 该环境实际运行的服务与挂载、网络、公开参数；禁止将只用于提取文件的静态制品作为常驻服务 |
| deploy.sh / rollback.sh | 已明确要求并实现的运行环境更新/恢复入口，必须独立于 build/publish |

项目配置示例仅说明结构；实际地址和架构必须来自已确认的项目目标：

```json
{
  "image": "registry.example.invalid/team/tool",
  "platform": "linux/amd64",
  "dockerfile": ".sdkit/docker/Dockerfile",
  "context": "."
}
```

config.json 中 Dockerfile 和 context 必须以项目根目录解析，禁止因配置文件位于 test/release 而改变路径含义。个人机器路径和服务器绑定不属于此项目文件；只有需要新增 Skill 私有配置时才允许使用 `~/.config/sdkit/skills/dockerops/config.json`，必须保留已有镜像库绑定，禁止创建空配置或把项目配置当私有绑定覆盖。

Webhook 的 check/setup/send、路由与执行边界必须读取 [Webhook 子任务](webhook.md)；本文件只定义其放置位置。

## 入口与迁移

Docker 的 make 目标必须统一定义在项目根 `Makefile`，直接调用 `.sdkit/docker/` 下脚本。禁止再生成 `.sdkit/docker/Makefile` 或另一份 Docker 专用 Makefile；同名目标已存在时必须先审计，不得覆盖。单环境提供 docker-build、docker-push、docker-verify、publish；多环境提供对应环境后缀，服务入口以项目真实服务名生成。有通知需求时必须增加 webhook（单环境）或 webhook-<环境>（多环境）目标，直接调用对应 webhook.sh；没有通知需求时禁止生成空脚本或占位通知地址。

```make
# 项目根 Makefile，保留其他目标。
.PHONY: docker-build
docker-build:
	bash .sdkit/docker/build.sh
```

- 必须先核对旧 Dockerfile、脚本、Makefile、CI、文档、构建上下文、Webhook 与服务器 Compose 的实际引用。只有用户要求或已授权迁移时才允许移动旧入口；仅查询或发布既有项目时禁止顺带改目录。
- 新项目按本布局生成；已有项目未授权迁移时必须复用原流程并报告布局差异。迁移必须同步更新 -f、context、COPY、脚本定位、Makefile、CI、Webhook 调用与文档；兼容旧路径只能保留薄转发并记录移除条件，禁止两套独立实现。
- 禁止为统一目录改写 `.sdkit/STATUS.md`、TASKS.md、DECISIONS.md、HANDOFF.md 的职责或覆盖已有项目状态。无需为使用本 Skill 额外改写协作规范。

正向形态：先确认单环境 → 在 `.sdkit/docker/` 生成一套入口 → 根 Makefile 调用脚本。反例：检测不到 Dockerfile 就复制 test/release 两份模板并覆盖原 deploy 目录。

## 完成标准

必须核对模式与用户选择一致、文件可在固定位置找到、入口无重复实现，旧路径引用无悬空。人工检查是否只调整已授权项目、环境和迁移范围；文件生成与构建、镜像发布、运行更新必须分别报告。
