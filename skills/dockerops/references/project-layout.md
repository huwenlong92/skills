---
name: dockerops-project-layout
description: 项目 Docker 发布文件的固定位置、环境模式与既有入口迁移。
---

# 项目 Docker 文件布局

适用范围：在业务项目生成、修改、查找或迁移 Dockerfile、构建/发布脚本和 Compose。执行这些任务前必须读取本文件。所有项目文件路径均以本次目标项目根目录为基准；本文件不改变 `.sdkit/` 原有协作状态文件。

## 使用边界

- 已有项目必须先识别并复用现有入口；只有当前任务明确要求创建、接入或整理时，才允许修改对应文件。禁止为使用 DockerOps 自动迁移目录、替换旧脚本、改写 Makefile/README/CI，或改变构建发布逻辑。
- 用户要求统一文件位置或操作入口时，必须保留原镜像名、平台、版本策略、服务范围及发布副作用，只调整已授权位置和必需引用。用户另行要求改变流程时才允许改动这些行为。
- 本文件规定新文件的位置，不是每个项目的必建清单。必须只生成当前任务所需文件，禁止额外引入管理程序、包装层或配置体系。

## 模式选择与固定位置

- 新增 Docker 构建发布文件必须统一放在 `.sdkit/docker/`；项目使用 Makefile 时，由根 Makefile 直接调用脚本。禁止在根目录、`deploy/`、`docker/` 或 `scripts/` 再生成另一套同职责实现；业务源码、普通构建产物仍按项目本身约定放置。
- 必须先读取当前用户要求、项目规则、Makefile、Compose、CI 和实际调用脚本，确定现有环境模式。单环境不创建 test/release；只有明确采用多环境时，才允许创建对应环境子目录。
- 项目没有 Docker 发布文件，或无法从证据确定环境模式时，必须询问“使用单环境，还是 test/release，或其他明确环境？”。禁止将缺文件等同于默认 test/release，也禁止默认为正式环境。
- 用户当前明确选择高于已有规范和历史模板。发现旧规范强制环境数量时必须指出差异并按当前选择实施，禁止让旧约定覆盖本次决定。

单环境的新文件按以下位置放置；列表仅说明位置，各文件均按本次需求生成：

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
  docker-compose.yml # 运行服务或静态制品提取示例
  nginx.conf.example # HTTP/静态站点的 Nginx 示例
  deploy.sh          # 已要求自动更新运行环境时才生成
  rollback.sh        # 已实现并验证回滚入口时才生成
  scripts/           # 存在实际共享实现时才生成
```

已确认 test/release 时，新文件按以下位置放置，禁止仅为补齐列表而生成文件：

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
    docker-compose.yml
    nginx.conf.example
  release/
    config.json
    build.sh
    publish.sh
    verify.sh
    webhook.sh       # 该环境有通知需求时才生成
    docker-compose.yml
    nginx.conf.example
```

- 需要生成 config.json、build.sh、publish.sh、verify.sh 时，单环境直接放在 `.sdkit/docker/`，多环境放在 `.sdkit/docker/<环境>/`；已有配置形式必须保留，禁止强制新增 config.json。其他环境名称必须来自用户或项目明确声明。
- 默认共用 `.sdkit/docker/Dockerfile`；只有环境间存在无法用公开构建参数表达的构建阶段、依赖或运行基础差异时，才允许使用 `<环境>/Dockerfile`，并在配置和 README 记录原因。禁止无差别复制 Dockerfile。
- Dockerfile 专属忽略文件必须紧邻对应 Dockerfile，命名为 `<Dockerfile文件名>.dockerignore`。已有根 `.dockerignore` 必须审计保留，禁止把秘密送入构建上下文。
- scripts/ 只允许项目自身共享实现；禁止放 Skill 安装产物、Agent 插件、私有凭据或第二套发布框架。缓存、临时日志必须放系统临时目录或项目已忽略的缓存目录，禁止写入 `.sdkit/` 的状态文件或提交到发布文件目录。

## 按职责整理与兼容边界

- 明确整理/迁移时，必须按职责重新归位，禁止只把原目录文件整体复制到 `.sdkit/docker/`。必须保留镜像、平台、版本、服务、通知和清理行为；历史文件名和层级不得因此成为新布局的例外。
- 多环境的业务 build.sh、publish.sh、verify.sh、webhook.sh、cleanup.sh、deploy.sh、rollback.sh 必须位于各自环境目录；禁止在根目录再保留一套通用业务入口。根目录只允许共用 Dockerfile/专属 ignore、README.md、已声明环境、scripts/ 及被实际消费的既有共用配置；共用配置必须记录调用者，禁止为统一目录强制迁移配置体系。
- 单环境业务入口允许放在根目录，推送入口必须命名 publish.sh；禁止在新布局保留 push.sh、build-push.sh、build-push-all.sh 等历史别名。聚合操作与服务快捷入口必须由根 Makefile 提供。
- scripts/ 必须只保存有真实调用者的跨环境辅助实现，例如传输工具适配、制品检查/提取及共享镜像处理；辅助脚本必须有明确职责名称。共享基础镜像的辅助构建/推送脚本必须放 scripts/base/，Dockerfile.base 保留在根目录。禁止把未分类的历史命令集合整体塞进 scripts/。
- 必须在 README.md 记录环境、标准入口、共享辅助文件的用途/调用者和不适用项，禁止另建同职责 runtime-examples.md 或迁移专用管理文件。
- 旧路径仍被现有 Makefile、CI、工作区或文档调用时，允许仅在原位置保留最小转发；转发可以直接委托既有 Make 目标。禁止把多余的兼容别名复制进新的规范目录，禁止保留无调用者的中转层。旧跟踪文件的 Git 边界仍执行下文，不自动删除索引记录。
- 整理后必须核对每个已有操作均能在规范位置或已说明的原生打包入口找到。仅本地构建/离线制品项目不得伪造远端 publish；编译工具镜像必须声明原生打包调用者，不伪造服务 Compose 或 HTTP 服务。
- 必须逐个核对 Makefile/脚本引用和调用方向，禁止 Make → 脚本 → 同一 Make 目标的循环。路径替换必须一次完成并核对实际解析结果，禁止连续子串替换导致 `.sdkit/docker/.sdkit/docker/` 等重复前缀。构建 context 为项目父目录或独立 named context 时，必须审计实际上下文中的项目相对路径，确保各层 `.sdkit/` 都被忽略。

## 文件职责

| 文件 | 必须承担的职责 |
| --- | --- |
| README.md | 本项目 Docker 发布的模式、环境、服务、镜像、架构、命令、版本、副作用、配置来源与恢复说明 |
| config.json | 项目可公开的镜像、平台、Dockerfile、构建上下文和公开参数；禁止包含凭据或个人路径 |
| build.sh | 构建指定范围及明确版本；禁止推送、通知 webhook、部署和清理历史版本 |
| publish.sh | 推送已构建制品并核对远端；新脚本禁止隐式 webhook、服务器更新和本地镜像清理 |
| verify.sh | 校验明确版本、digest、平台和别名，并区分本地/远端范围；禁止重建、推送或部署 |
| webhook.sh | 该环境/服务的已授权通知；必须明确是否会引起自动更新，禁止包含真实 Token、重建镜像或隐式修改其他环境 |
| cleanup.sh（按需） | 仅清理明确版本的本地业务镜像标签；禁止隐式删除缓存、其他版本、远端镜像或使用 prune/强制删除 |
| docker-compose.yml | 该环境实际运行的服务与挂载、网络、公开参数；禁止将只用于提取文件的静态制品作为常驻服务 |
| nginx.conf.example | 已核对端口和路由的站点示例；域名/证书待替换项必须标明，禁止自动覆盖在用 Nginx 配置 |
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

## 默认本地保存与 Git 边界

- `.sdkit/docker/` 默认仅保存在本地。已有忽略规则生效时必须复用；需要补充忽略时，必须通过 `git rev-parse --git-path info/exclude` 定位本仓库的本地 exclude 文件，保留其原内容并补充 `/.sdkit/docker/`。只有用户明确要求共享忽略规则时才修改项目 `.gitignore`；禁止为此忽略整个 `.sdkit/`。无 Git 仓库时禁止仅为设置忽略而初始化 Git。
- 后续是否将该目录加入版本库由用户自行决定。DockerOps 禁止主动执行 `git add -f`、取消忽略或提交目录内容；用户后续明确要求纳入时，才允许按其指定范围调整忽略与暂存。
- 忽略规则不能取消已有跟踪。迁移前必须用 `git ls-files -- .sdkit/docker` 检查；已有跟踪文件必须保留并报告，禁止自动执行 `git rm --cached`、删除索引记录或改写历史。旧目录文件的跟踪状态必须单独核对，不能把“迁移到本地目录”当作删除旧版已跟踪文件的授权。
- 根 Makefile 和项目 `.gitignore` 按原状态保留，不因本地 Docker 文件被忽略而自动修改它们。新文件交付时必须说明 `.sdkit/docker/` 不随 Clone 获取；禁止为说明此事自动改写项目 README，或宣称 Git 同步已经分发了这些文件。

本仓库本地 exclude 的典型规则（保留其他规则）：

```gitignore
/.sdkit/docker/
```

必须以 `git check-ignore -v --no-index -- .sdkit/docker/Dockerfile` 核对最终规则，并以 `git ls-files -- .sdkit/docker` 区分已跟踪内容。存在后续反向规则导致忽略失效时必须修正本目录规则；禁止使用强制暂存绕过。反例：忽略整个 `.sdkit/`，或追加忽略规则后宣称原来已跟踪的 Docker 文件已退出版本库。

## 入口与迁移

为项目新建或明确补齐 Docker 构建发布方案时，必须同时维护根 Makefile；不存在时必须创建，存在时增量补充，禁止覆盖原目标。仅查询或执行既有方案时，缺少 Makefile 必须报告，不得因此改造项目。已有 Makefile 引用的本地脚本缺失时，必须区分本次已授权补齐与无关缺失，禁止为消除告警补无关文件。Compose/Nginx 示例与发布快捷目标的默认生成规则统一见[运行示例与快捷入口](runtime-examples.md)。

用户要求新增独立通知或清理入口时，脚本放在本环境目录，Make 目标放在根 Makefile：单环境使用 webhook、docker-clean，多环境使用 webhook-<环境>、docker-clean-<环境>。已有一键发布必须保留原用法，禁止仅为职责拆分而改写其顺序或副作用。新建包含已授权通知与清理的聚合流程时，按构建 → 推送 → 验证 → 已配置通知 → 清理本次本地镜像顺序调用，通知失败停止清理。新建清理入口必须核对本次明确版本，别名只有仍指向本次版本时才允许删除。以上入口定义不构成实际通知或清理的授权。

当前任务要求维护或生成 Docker make 目标时，必须统一定义在项目根 Makefile，调用实际脚本。禁止再生成 `.sdkit/docker/Makefile` 或另一份 Docker 专用 Makefile；同名目标已存在时必须先审计，不得覆盖。生成方案默认包含实际支持的构建、推送和 publish 快捷入口；通知与清理仍按实际需求生成。其他新增目标按需要选择 docker-build、docker-push、docker-verify、publish、webhook 或 docker-clean，多环境使用对应后缀；禁止生成未实现的目标或在普通查询/执行中改造现有 Makefile。

```make
# 项目根 Makefile，保留其他目标。
.PHONY: docker-build
docker-build:
	bash .sdkit/docker/build.sh
```

- 必须先核对旧 Dockerfile、脚本、Makefile、CI、文档、构建上下文、Webhook 与服务器 Compose 的实际引用。只有用户要求或已授权迁移时才允许移动旧入口；仅查询或发布既有项目时禁止顺带改目录。
- 需要创建新文件时按本布局生成；已有项目未授权迁移时必须复用原流程。已授权迁移必须核对 -f、context、COPY、脚本定位及实际调用者，仅修改受影响引用；原项目入口不能因使用 Skill 自动替换为薄转发。确需兼容旧路径时才允许保留薄转发，禁止两套独立实现。
- 禁止为统一目录改写 `.sdkit/STATUS.md`、TASKS.md、DECISIONS.md、HANDOFF.md 的职责或覆盖已有项目状态。无需为使用本 Skill 额外改写协作规范。

正向形态：用户要求新增单环境 Docker 构建 → 只在 `.sdkit/docker/` 创建所需文件 → 同步创建或增量维护根 Makefile 与实际服务的发布快捷目标。反例：构建现有项目时替换其脚本，或检测不到 Dockerfile 就复制 test/release 两份模板并覆盖原 deploy 目录。

## 完成标准

必须核对模式与用户选择一致，并运行[只读布局检查](../scripts/check_layout.py)验证根目录/环境职责、能力文件和字面路径引用；还必须用隔离调用验证变量路径与无循环。文件必须可在固定位置找到、入口无重复实现，旧路径引用无悬空；必须验证默认 Git 忽略规则生效，并报告已有跟踪文件是否保留。人工检查是否只调整已授权项目、环境和迁移范围；文件生成与构建、镜像发布、运行更新必须分别报告。
