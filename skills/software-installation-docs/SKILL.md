---
name: software-installation-docs
description: 创建、更新或评审精确的 Linux 软件安装与运维文档。处理 package repository 安装、源码编译、容器、静态二进制、升级、降级、回滚、卸载、systemd 集成、供应链验证和版本敏感的安装说明时使用。
---

# 软件安装文档

起草或评审安装文档前，必须完整读取 [installation.md](references/installation.md)。

## 必须执行的流程

1. 明确软件 edition、release channel、目标 Linux 发行版、架构、init system、当前安装状态和操作者权限。
2. 所有版本敏感事实、repository URL、签名密钥、checksum、支持系统和安全指引都必须查阅官方文档，并记录核验日期。
3. 必须分开编写全新安装、升级、迁移、回滚和卸载流程；禁止把全新安装流程直接用于已有安装。
4. 命令必须使用明确占位符并写明前置条件。破坏性操作必须放在单独标记的流程中，写明精确目标和恢复要求。
5. 必须满足 [installation.md](references/installation.md) 要求的全部章节和完成检查。

## 停止条件

- 禁止编造当前版本、repository 路径、package 名称、key fingerprint、service user、端口或数据目录。
- 权威来源无法确认必需事实时，必须标记为未解决并省略不安全命令。
- 未实际执行命令或验证服务时，禁止声称已经执行或验证。
