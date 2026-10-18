---
name: dockerops-project-generation
description: 识别业务项目并生成 Dockerfile、构建/推送/验证脚本和 Makefile 入口。
---

# 生成项目 Docker 能力

适用范围：用户要求为当前项目补齐 Docker 构建发布、生成 Dockerfile/build.sh，或迁移既有 Docker 入口。修改前必须读取[固定布局](project-layout.md)；生成运行示例或 Make 入口时必须读取[运行示例与快捷入口](runtime-examples.md)；涉及基础镜像必须同时读取[镜像选择](selection.md)。所有路径以目标项目根目录为基准。

## 识别与澄清

本文件仅在当前任务要求新增文件或明确整理/迁移时执行。普通构建、推送、查询与检查必须复用现有项目，不自动修改 Makefile、README、CI、配置形式或发布逻辑；禁止为统一目录引入新的管理程序和包装层。

1. 必须读取当前项目 AGENTS.md、技术栈声明、依赖锁文件、构建配置、入口程序及现有 Docker/Make/CI 文件；多仓工作区必须确定实际生成文件的仓库和构建上下文，禁止直接选工作区父目录。
2. 必须从实际代码确认产物和运行方式：Go/Rust 二进制、Node SSR 服务、静态制品或已有其他形态。禁止将 dist 静态包当 Node 服务，也禁止从目录名猜测启动命令。
3. 环境模式按布局 reference 确认；registry、镜像名、目标架构、服务范围或公开构建参数缺失时，必须只询问影响当前步骤的信息，禁止猜造可发布目标。仅生成规则/草稿时允许标注缺失项，禁止执行占位值。
4. 必须遵守已确认的本地 path、Git 或发布版本依赖边界；容器必须消费与当前代码兼容的共享 core，禁止默默切换旧版本、复制 core 或顺带升级项目工具链。
5. 必须按[仓库协作](repository.md)检查本地 Git 状态并保护本任务之前的修改；纯本地整理不以 PR/MR 查询为前置，涉及远端写入时再执行对应协作检查。已有同名文件必须先比较内容与调用者，禁止整目录覆盖或重新初始化仓库。

## Dockerfile 与构建上下文

- 必须按匹配技术栈生成真实可用的构建与运行阶段，镜像和 builder 按[镜像选择](selection.md)实时核验。用户指定来源时必须遵守，镜像库双架构不构成业务多架构构建授权。
- Dockerfile 必须使用实际锁文件和项目已有构建命令；必须审计 COPY、外部 build context、依赖下载和本地共享源码。禁止复制宿主机 node_modules、认证文件、私钥、.git、真实 .env 或不相关项目数据。
- runtime 必须只包含所需制品和依赖，运行用户、端口、启动参数及健康检查必须符合真实应用。静态制品可以用 scratch 打包再提取，禁止为其伪造长期运行进程。
- Dockerfile 的 -f 路径必须来自固定布局，context 必须独立指定为实际源码根目录；禁止把 `.sdkit/docker/` 直接当 context 导致 COPY 不到业务代码。

以下仅为二进制项目的阶段形态；镜像、源码入口和命令必须按项目生成，不能直接作为通用成品：

```dockerfile
ARG BUILDER_IMAGE
ARG RUNTIME_IMAGE
FROM ${BUILDER_IMAGE} AS build
WORKDIR /src
COPY . .
# 此处必须使用本项目真实命令，产物统一到已确认路径。
RUN make build
FROM ${RUNTIME_IMAGE} AS runtime
WORKDIR /app
COPY --from=build /src/dist/tool /usr/local/bin/tool
USER 10001:10001
ENTRYPOINT ["/usr/local/bin/tool"]
```

反例：只修改 FROM，保留不存在的 `/src/dist/tool`，然后声称 Dockerfile 已可用。

## 脚本与 Makefile

- build.sh、publish.sh、verify.sh 必须使用确定的解释器和失败即停止设置，并从脚本自身位置计算项目根目录。禁止依赖调用者恰好在某个子目录，或在脚本写死个人目录。
- 配置必须沿用项目已声明的形式并选中正确环境，禁止为使用 Skill 强制新增配置文件或迁移配置体系。确需新增 config.json 时只允许声明式公开数据，禁止 eval 参数或执行 JSON 中的 shell 文本；秘密必须沿用受控环境，不能写入配置、镜像层、命令输出或示例。
- Docker context 必须使用用户或项目选定的引擎环境，不得自动切换远端主机。Dockerfile 路径、平台、构建参数、版本和服务必须显式传递并在调用链中保持一致。
- 聚合发布必须先构建成功再推送、再校验，使用顺序 recipe；禁止并列 prerequisites 造成 make -j 并发推送未完成镜像。多服务必须在父入口生成一次版本并传递，不能在每个子进程重复生成不同版本。

```make
# 项目根 Makefile；已确认采用 test 环境。
.PHONY: docker-build-test docker-push-test docker-verify-test publish-test

docker-build-test:
	bash .sdkit/docker/test/build.sh

docker-push-test:
	bash .sdkit/docker/test/publish.sh

docker-verify-test:
	bash .sdkit/docker/test/verify.sh

publish-test:
	$(MAKE) docker-build-test
	$(MAKE) docker-push-test
	$(MAKE) docker-verify-test
```

当前任务要求新增通知能力时，必须按 [Webhook 子任务](webhook.md) 的 setup 生成与验证所需入口；通知授权、路由、凭据与副作用以该文件为唯一权威定义。已有通知实现默认复用，禁止仅因使用 Skill 就拆分或替换脚本。

新建或明确补齐 Docker 方案时，必须同步生成/维护根 Makefile、适用的 docker-compose.yml 与 nginx.conf.example，并按已确认服务提供 publish 快捷入口；命名、示例适用性和已有入口复用统一见[运行示例与快捷入口](runtime-examples.md)。单环境使用无 test 后缀的同职责目标；多服务项目必须按已确认服务生成 -<service> 快捷目标，并提供显式 -all 入口；单服务项目禁止伪造多服务目标。只添加当前任务所需目标，禁止将未指定范围的调用默认扩展为全部服务。

## 验证与完成标准

- 必须依据已确认模式执行[只读布局检查](../scripts/check_layout.py)，显式传 mode、环境及实际 operation/require；禁止仅凭测试数量或文件复制成功宣布整理完成。例如多环境构建/推送项目执行 `python3 <skill>/scripts/check_layout.py . --mode multi --env test --env release --operation build --operation publish --require compose --require nginx`，其中 `<skill>` 必须解析为本次实际 Skill 目录；其他项目只选择其真实能力。
- 必须覆盖本次改动的每个 Make/脚本入口；仅核对 Dockerfile 内容不足以证明 -f/context 正确。隔离替身必须检查实际传给 Docker 的 Dockerfile 路径存在、构建 context 正确，以及搬迁后的直接调用、旧调用者、服务/环境、版本和通知/清理顺序一致；必须检查失败停止和无递归调用。

- 必须执行本次新增或修改脚本对应的 bash -n/sh -n，并检查涉及的配置、Makefile 调用、路径与参数。Makefile 若有 `$(shell ...)`、include、递归 make 或隐藏副作用，必须先静态审计；禁止将 make -n 一概当作无副作用检查。
- 必须按[固定布局的 Git 边界](project-layout.md#默认本地保存与-git-边界)核验 `.sdkit/docker/` 默认被忽略及已有跟踪状态。Makefile 或其引用脚本缺失时，按固定布局区分生成/补齐任务和普通执行任务，禁止超出当前授权补文件、执行发布或声称 Clone 后入口完整可用。
- 新增脚本或改变流程控制时，必须用项目已有检查或隔离 fixture 验证相关执行顺序、失败中断、环境选择与版本传递；只移动文件和修正路径时核对语法、引用及逻辑未变。只有已获授权时才执行实际业务构建/推送；静态校验不能声称镜像已可构建。
- 本次需要新增或修改使用说明时，必须准确记录所选模式、服务、镜像、架构、入口、参数、副作用及未验证项；已有说明无相关变化时禁止仅为套用 Skill 模板而改写。
- 完成必须区分“已生成”“静态/离线验证通过”“实际构建通过”“已发布”“已上线”。人工检查命令是否真实匹配项目、基础镜像是否已验证、是否留下可执行占位值，以及是否误迁移既有流程。
