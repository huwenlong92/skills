---
name: dockerops-selection
description: 镜像库位置解析、动态清单查询、基础镜像与 builder 选择，以及 Dockerfile 接入验收。
---

# 镜像选择与接入

适用范围：生成、修改或评审 Dockerfile、构建脚本中的基础镜像引用，或查询可用镜像。执行这些任务前必须读取本文件。

## 镜像库绑定与只读查询

镜像库是使用 `images.txt`、`<镜像名>/<版本线>/image.conf`、`digest.lock` 和独立 builder 配方的源码库。必须从以下入口解析位置，禁止写死个人目录或真实账号到共享技能：

1. 当前用户提供的路径或消费项目显式声明；相对路径以消费项目根目录为基准。
2. 仅当上述入口没有声明时，使用 `DOCKEROPS_MIRROR_REPO`。
3. 仅当前两项没有声明时，读取 `--config <path>` 指定的 JSON；未指定时读取 `DOCKEROPS_CONFIG`，两者均未指定时必须使用 `~/.config/sdkit/skills/dockerops/config.json`。显式配置路径相对当前工作目录解析；禁止自动回退旧路径或受 `XDG_CONFIG_HOME` 改变默认路径。

机器级配置必须用 `repository.local_path` 绑定实际镜像库根目录，用 `repository.url` 声明预期 Git 远端。相对路径以该配置文件所在目录解析；离线清单查询不等于 Git 身份核验。配置的允许位置、迁移、本地绑定与 Git 门禁必须遵守[配置与仓库协作](repository.md)；禁止在多个 reference 维护另一套配置路径或迁移步骤。

```json
{"repository": {"local_path": "../../repos/image-mirror", "url": "https://code.example.invalid/team/image-mirror.git"}}
```

没有绑定时必须询问镜像库位置，禁止遍历整个主目录、猜造远端或自动修改 Git remote。指定路径无效时必须报告错误，禁止退回其他来源掩盖配置错误。

使用 Python 3.9 或以上版本，在本技能实际所在目录运行脚本；脚本只读文件，不执行配置、不访问网络、不修改锁文件。`--repo` 的相对值按当前工作目录解析，因此必须在消费项目根目录执行或传入已解析路径：

```bash
# 以下相对路径假设镜像库与消费项目同级；实际使用前必须核对。
python3 <skill-dir>/scripts/catalog.py --repo ../image-mirror
python3 <skill-dir>/scripts/catalog.py --repo ../image-mirror --search node
# 已有机器级绑定时允许省略 --repo。
python3 <skill-dir>/scripts/catalog.py --search builder
# 仅当需要覆盖默认配置文件时显式指定。
python3 <skill-dir>/scripts/catalog.py --config <private-config.json> --search node
```

输出 `recorded` 仅指本地记录完整且内部一致；`unrecorded` 表示没有成功发布锁文件；`inconsistent` 表示配置、平台或锁记录异常。`remote_verified` 始终为 `false`。查询过滤只缩小显示范围；必须检查顶层 `issues`，禁止把空结果视为全库没有异常。

官方镜像清单以 `images.txt` 为准。builder 不加入此清单，工具从独立 Dockerfile 与 `*builder*.lock` 查找候选；非标准布局必须按镜像库 README 和配方补查。禁止把有配置但无锁文件的条目描述为已发布。

## 版本、系统和阶段匹配

- 必须检查项目的工具链/运行时声明、lockfile、现有 Dockerfile 及构建参数，保留用户指定的主版本、精确版本约束和 Alpine/Bookworm/slim 等变体。禁止因为清单已有 Node 24 就替换要求 Node 22 的项目；禁止在没有兼容验证和用户授权时互换 musl 与 glibc。
- 必须优先选择满足这些约束的已发布 Mirror 引用；仅当没有匹配条目、发布未完成或远端验证失败时，进入[同步与发布](publication.md)，禁止自动退回第三方加速器或偷偷改用官方公网地址。
- 共享 builder 只允许用于工具链、基础系统与构建依赖满足项目需求的构建阶段。业务源码、模块下载、业务依赖缓存与配置必须留在消费项目；禁止为单个应用把这些内容预装进共享 builder。
- 必须识别所有外部镜像依赖：`# syntax=`、`FROM`、全局 `ARG` 的默认值、构建脚本的覆盖参数、外部 `COPY --from=<image>` 与镜像形式的 build context。`scratch`、数字阶段与已经定义的阶段别名无需同步。禁止只改默认值而遗漏实际覆盖入口。
- `FROM --platform=$BUILDPLATFORM` 和 `$TARGETPLATFORM` 的含义必须按项目编译方式保留；双架构基础镜像不会自动把 amd64 程序变为 arm64 程序。

## 发布记录与远端验证

官方镜像选定后，必须核对该目录 `image.conf` 与 `digest.lock`，并在镜像库根目录执行：

```bash
make verify IMAGE=node/22-bookworm-slim
```

示例目录不代表已存在；执行时必须使用实际清单中的目录。该检查验证配置/锁文件、远端普通和回滚标签、索引及平台/config，不能证明运行健康或业务编译成功。

builder 必须读取其 README、Dockerfile 与发布锁文件，用目录规定的远端验收入口核对唯一版本及别名的双平台索引和实际依赖。禁止把只有本地构建检查的 `verify-*builder` 当成远端发布验收；没有专用远端入口时，必须用 registry 工具检查锁定 digest、两个子 manifest 与 config。

日常消费允许使用已验证的普通标签/版本线别名；用户或项目要求不可变引用时，必须使用记录的目标**索引** digest 或已验证的回滚/唯一版本标签。禁止复制上游索引 digest、某个单平台子 digest 或历史单架构回滚标签冒充双架构目标。

以下是脱敏后的 Dockerfile 接入形态；必须把示例地址替换为本次已验证记录中的真实地址，保持项目自己的构建步骤：

```dockerfile
# syntax=registry.example.invalid/mirror/dockerfile:1.7
ARG NODE_IMAGE=registry.example.invalid/mirror/node:22-bookworm-slim
FROM ${NODE_IMAGE} AS build
WORKDIR /src
# 项目自己的依赖安装和构建步骤。
FROM ${NODE_IMAGE} AS runtime
WORKDIR /app
COPY --from=build --chown=node:node /src/dist ./dist
USER node
CMD ["node", "dist/server.js"]
```

禁止仅拼接 `registry.example.invalid/mirror/node:<版本>` 或其他猜造地址就交付为可用镜像；目标地址必须来自成功发布记录并通过远端验证。

## 接入验证与完成标准

- 必须检查 Dockerfile 所有外部引用及关联构建覆盖参数，匹配项目版本、系统、架构和凭据边界。
- 仅当任务需要业务构建且用户没有明确自行打包时，执行项目规定的构建检查；业务 amd64 时只验收对应业务平台。仅获镜像选择/接入授权时，禁止启动业务部署或完整跨架构构建；业务发布任务另按[业务构建发布](project-release.md)执行。
- 完成：每个选中引用有匹配配置、真实发布记录和远端验证结果；Dockerfile 使用真实消费地址，保留项目目标架构与版本约束。
- 受阻：必须指出未绑定、未发布或验证失败的具体依赖；允许保留明确标注的草稿，禁止把未发布地址写成可立即使用的交付。
- 交付必须列出消费地址、是否新增镜像、执行过的验证，以及业务构建已执行还是未执行；人工检查各阶段的 ABI、运行用户与产物路径是否仍符合项目。
