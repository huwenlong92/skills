---
name: dockerops
description: 管理 Docker 镜像来源及项目构建发布：创建、修改或评审 Dockerfile，生成统一的 .sdkit/docker/ 构建/推送/验证脚本、Compose/Nginx 示例和根 Makefile 快捷入口，执行已授权的业务镜像发布、Webhook 检查/配置/通知与容器更新；同时查询已配置镜像库、补同步基础镜像和发布共享 builder。环境数量不明确时询问，业务平台服从项目要求。
---

# DockerOps

Docker 构建与发布统一使用本 Skill。基础镜像库维护与业务项目构建发布按任务分流；需要新建 Docker 文件时统一放在 `.sdkit/docker/`。已有项目默认复用现有入口，只有用户要求整理或迁移时才调整文件位置与引用；禁止将一次性整理任务变成每次使用 Skill 的默认改造。禁止将动态镜像清单、真实业务项目清单或个人绑定复制进共享 Skill。

## 任务分流

| 任务 | 必须读取 |
|---|---|
| 查询镜像、选择基础镜像/builder，核对 Dockerfile 镜像引用 | [镜像选择与接入](references/selection.md) |
| 基础镜像/版本缺失、锁记录异常，或新增/升级共享 builder | [镜像选择](references/selection.md)、[镜像库同步与发布](references/publication.md) |
| 为项目生成 Dockerfile、构建发布脚本、Compose/Nginx 示例与 Make 快捷入口，或迁移旧布局 | [项目固定布局](references/project-layout.md)、[项目文件生成](references/project-generation.md)、[运行示例与快捷入口](references/runtime-examples.md)；涉及镜像再读镜像选择 |
| 业务镜像构建、推送、验证，或按授权更新/恢复容器运行环境 | [项目固定布局](references/project-layout.md)、[业务构建发布](references/project-release.md)；缺文件时追加项目文件生成 |
| Webhook 检查、配置、发送或失败补发（webhook check/setup/send） | [Webhook 子任务](references/webhook.md)、[项目固定布局](references/project-layout.md)；关联镜像发布时再读业务构建发布 |
| 绑定镜像库目录与远端 URL、迁移私有配置、Git 同步与跨会话检查 | [配置与仓库协作](references/repository.md) |

## 调用约定

`dockerops webhook check/setup/send` 表示本 Skill 的检查、配置、发送子任务；不注册全局 CLI。实际通知复用目标项目的根 Makefile 与 webhook.sh，不在 Skill 内维护第二套项目通知目标。具体边界见 Webhook 子任务 reference。

## 执行顺序

1. 判断是镜像库维护还是业务项目任务，读取目标项目最新规则、匹配 references 和实际调用链，保护已有修改。
2. 业务任务先确认技术栈、产物、服务、环境、镜像和平台；没有证据确定单环境或多环境时必须询问。缺少文件按固定布局生成，已有文件先核对兼容性，禁止顺带批量迁移。
3. 新增或修改基础镜像引用、或用户要求查询镜像库时，解析镜像库配置，用[清单工具](scripts/catalog.py)查询记录，再核验实际远端。缺少匹配镜像时进入镜像库流程；用户指定其他来源时服从其要求。执行既有构建发布不自动更换镜像来源，也不要求改造项目来接入镜像库。
4. 明确整理任务必须按固定布局的职责分类验收，不能只搬文件；按已授权范围执行生成、离线检查、构建、推送与验证；服务器更新、webhook、清理和 Git 写入分别判断授权，禁止由命令名称推导权限。
5. 分别报告文件生成、验证、镜像发布和真实运行验收；未执行阶段必须明确，禁止将静态记录或 push 成功说成已上线。

## 共同门禁

- 当前用户要求 > 目标项目显式规则 > 本 Skill > 历史实现。新业务 Docker 文件按 `.sdkit/docker/` 约定生成，默认仅本地保存、不纳入版本库；后续是否加入由用户决定，具体忽略与迁移规则见[项目固定布局](references/project-layout.md)。不要求修改既有协作规范或复制 Skill 到项目。
- 镜像库普通与回滚/唯一版本标签必须支持 linux/amd64、linux/arm64；业务镜像只构建项目要求的平台，禁止因基础镜像双架构扩大业务范围。
- 使用执行主机既有认证，禁止记录、输出或提交凭据。绑定镜像库的私人配置不代表当前业务项目、服务器或 Git 写入已获授权。
- 只生成文件不授权构建推送；“Docker 构建发布”包含该目标所需的生成、构建、推送与验证，不自动授权服务器更新、webhook、清理和 Git 提交。已明确授权的步骤禁止重复询问。
- 只修改本次所需 Docker 文件和关联入口，禁止顺带升级工具链、批量同步全库、删除旧标签、覆盖未提交修改或提交无关文件。
- 本 Skill 的自然语言调用不等于系统已注册 dockerops CLI；脚本和 make 目标必须实际存在并经核验，安装不替代真实构建与发布验收。
