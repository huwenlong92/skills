---
name: dockerops-runtime-examples
description: 生成 Docker 方案时默认配套的 Compose、Nginx 示例及根 Makefile 发布快捷目标。
---

# 运行示例与发布快捷入口

适用范围：新建或明确补齐项目 Docker 构建发布方案，创建/修改 docker-compose.yml、nginx.conf.example 或根 Makefile 发布目标时必须读取。所有路径以目标项目根目录为基准；目录与本地忽略规则以[固定布局](project-layout.md)为准。普通查询和执行既有方案不触发本文件的生成流程。

## 默认交付与适用性

- 新建或补齐方案必须同步维护根 Makefile，并为实际运行方式生成配套示例；禁止只生成 Dockerfile/build.sh 而遗漏运行说明。根 Makefile 不存在时必须创建，存在时必须增量补充并保留原有目标。
- 单环境文件必须放在 `.sdkit/docker/docker-compose.yml`、`.sdkit/docker/nginx.conf.example`；多环境必须放在 `.sdkit/docker/<环境>/` 的同名文件。禁止生成另一份子目录 Makefile，禁止将示例写入在用服务器目录。
- 有可运行容器服务时必须提供 docker-compose.yml；只有静态制品时必须明确提取方式，已有 image-only profile/提取容器必须保留，禁止将 scratch 制品作为常驻服务。HTTP 服务或静态站点必须提供 nginx.conf.example；Worker、CLI 或编译工具镜像没有 HTTP 入口时禁止伪造反向代理。
- 只用于导出原生安装包的 Docker 镜像不创建虚假的服务 Compose；必须在交付中记录不适用原因。已有独立服务示例必须复用，只有缺失时才生成新实现。
- 原有 Compose 为权威运行配置时，固定位置允许使用相对链接，必须明确其原配置目录并给出带 `--project-directory` 的调用方式；禁止复制另一份同职责配置后宣称自动保持同步。历史 compose.yaml 允许在原位置保留兼容；规范目录只保留 docker-compose.yml，禁止再生成 compose.yaml 别名。

## Compose 与 Nginx 内容

- 必须从实际镜像、Compose、运行配置和既有 Nginx 核对镜像名、服务/实例、端口、命令、配置挂载、数据持久化、网络、静态目录及路径前缀。禁止从项目名猜端口或给单环境强加 test/release。
- 外部数据库、Redis、NATS 和既有网络必须沿用项目引用，禁止为示例自动创建第二套基础设施；真实凭据必须留在既有受控来源，示例禁止包含 Token、密码或带秘密的 URL。
- Compose 路径必须按文件所在目录或显式 `--project-directory` 解析；运行配置/挂载源缺失时必须标明部署前置条件。仅生成示例不授权执行 up/down、pull、reload 或改服务器文件。
- Nginx 必须标明宿主机或容器使用场景、真实上游端口、proxy_pass 尾斜杠/前缀语义、静态目录与 SPA 回退。涉及 WebSocket/SSE 时必须保留对应 Upgrade/Connection、超时和禁用缓冲行为。示例域名必须使用保留的 example.invalid；证书、访问范围和目录待填写项必须明确，禁止伪造已部署 HTTPS。
- 已有在用配置必须保留；新示例不替换其域名、端口、路由或访问控制。信息不足以生成可用运行目标时必须询问缺失项；可交付的占位示例必须明确标记，禁止运行或宣称部署验收通过。

正向形态（单服务，端口已核实；运行目录已有 configs）：

```yaml
services:
  api:
    image: registry.example.invalid/team/tool:${IMAGE_TAG:?set an immutable version}
    ports: ["127.0.0.1:8080:8080"]
    volumes: ["./configs:/app/configs:ro"]
```

```nginx
# 放入 Nginx http 上下文；仅 HTTP 示例，域名必须替换。
server {
    listen 80;
    server_name api.example.invalid;
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

反例：将 compose.yaml 复制到更深目录却不修正挂载基准；给无 HTTP 的 worker 生成 8080 反向代理；启动 scratch 制品镜像充当静态服务器。

## 根 Makefile 快捷目标

- 必须依据实际环境/可发布服务生成目标：单环境单服务 `publish`；多环境单服务 `publish-test`/`publish-release`；多环境多服务 `publish-test-api`、`publish-release-api` 等，单环境多服务使用 `publish-api` 等。
- 多服务必须保留通用 SERVICE 入口并提供显式 `publish-<环境>-all`（单环境为 publish-all）。快捷目标必须只选择命名服务，禁止默认扩大到全部服务或调用别的环境。
- 已有同名快捷目标必须复用并核对真实调用；缺失时必须委托已有聚合发布或按原顺序调用现有构建/推送入口，禁止复制第二套发布逻辑。原发布已含通知或清理时，外层禁止重复调用。
- 新聚合流程必须使用顺序 recipe，构建失败停止后续阶段；多服务父入口必须生成一次版本并传递给全部服务。禁止将构建/推送写为可并行 prerequisites；既有聚合行为只在当前任务明确授权调整时改变。
- 已有 `clean` 的其他职责必须保留；独立镜像清理、通知目标按[固定布局](project-layout.md#入口与迁移)命名。生成目标不授权执行发布、通知、清理或部署。

正向形态（已有 publish-test 支持 SERVICE，且其发布顺序已验证）：

```make
.PHONY: publish-test-api publish-test-worker
publish-test-api:
	$(MAKE) publish-test SERVICE=api
publish-test-worker:
	$(MAKE) publish-test SERVICE=worker
```

反例：publish-test-api 调用 publish-test-all；或新入口调用一个已经通知过的 publish.sh 后再额外发送 webhook。

## 验证与完成标准

必须检查根 Make 目标、实际委托范围及版本传递，用隔离替身验证新增快捷目标的服务/环境和失败停止；必须用 Docker Compose 配置解析检查示例（禁止启动容器）。Nginx 可用时必须在系统临时目录以独立主配置包裹示例执行 nginx -t；测试证书、日志与监听端口必须使用隔离替身，并区分语法验证与真实证书/端口验收，禁止 reload；不可用时必须明确未验证项。必须核对相对路径、静态制品形态和默认 Git 忽略，报告生成文件、适用例外和真实构建/部署未执行状态。人工检查真实域名、证书、访问范围、运行目录和外部依赖，禁止将示例语法通过等同于上线。
