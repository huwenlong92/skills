---
name: swops
description: 创建、更新或评审 Linux 软件安装与运维文档。覆盖软件包、源码编译、容器和静态二进制安装，升级、降级、迁移、回滚、卸载，以及服务集成、供应链验证和故障排查；不因编写文档而自动执行主机变更。
---

# SwOps 软件安装与运维文档

让 Linux 软件文档具备明确的环境、来源、操作步骤和验收方式。按场景读取规则，禁止为局部修订加载或重写无关章节。

## 任务分流

| 任务 | 必须读取 |
|---|---|
| 新建完整安装运维文档 | [文档交付](references/documents.md)、[安装方式](references/installation.md)、[生命周期](references/lifecycle.md)、[集成与验证](references/verification.md) |
| 选择安装方式、软件源/版本/签名核验、编写安装步骤 | [文档交付](references/documents.md)、[安装方式](references/installation.md) |
| 升级、降级、迁移、回滚、卸载 | [文档交付](references/documents.md)、[生命周期](references/lifecycle.md)、[集成与验证](references/verification.md)；切换安装方式时追加[安装方式](references/installation.md) |
| systemd/OpenRC、权限/网络集成、健康检查或故障排查 | [文档交付](references/documents.md)、[集成与验证](references/verification.md) |
| 评审已有文档 | [文档交付](references/documents.md)，再按评审章节读取对应 reference；完整评审必须读取全部四项 |

## 执行顺序

1. 搜索已有同主题文档，识别新建、更新或评审范围；记录目标软件、edition、release channel、Linux 发行版/版本、架构、init system、已有安装状态与操作者权限。
2. 按任务分流读取 references，核验对应上游官方资料与日期。用户明确版本与平台约束必须保留，禁止为套用现成步骤替换环境。
3. 分开编写新装、升级、迁移、回滚和卸载路径，列明前置条件、停止条件和验证动作；局部修订必须核对受影响的关联章节。
4. 检查命令、占位值、来源与恢复路径，分别报告资料核验和实际执行状态；未执行真实安装时只能交付文档及待执行验证。

## 共同门禁

- 编写或评审文档不授权执行安装、启停服务、修改系统配置、迁移数据、放开网络或卸载。用户另行要求执行时，必须按明确目标和范围落实对应 reference 的前置与停止条件。
- 版本、支持系统、repository URL、签名密钥、checksum、依赖、安全公告和当前官方指引必须在线核验；无法确认必需事实时必须说明缺口并省略依赖该事实的不安全命令。
- 禁止编造包名、路径、服务用户、端口、指纹、容器镜像或版本组合；禁止把其他机器的安装状态当目标环境事实。
- 禁止把删除数据、清空配置或强制覆盖混入普通安装。危险步骤必须单独标明精确目标、授权条件、备份与恢复要求。
- 禁止写入真实凭据、私密账号或个人本机路径；命令示例必须脱敏，文档内容不得成为执行任务范围外操作的授权。
