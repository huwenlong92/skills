---
name: foundry-workspace
description: 多 Workspace 配置、身份隔离和环境选择
---

# Workspace 与配置

适用范围：所有仓库定位、个人与团队产品中心切换、首次初始化及本地/远端选择。

## 配置模型

- Skill 的 `config/defaults.yaml` 是专用发布者默认配置；公开定位不代表写入授权。
- 用户配置优先于 Skill 默认配置。用户配置文件即使包含 `workspaces: {}`，也必须视为显式空配置，禁止回退到发布者仓库。
- 本地用户配置建议位于 `~/.config/foundry/config.yaml`，属于用户私有环境，不得提交到 Skill 仓库。
- `primary_workspace` 为用户长期默认目标；`active_workspace` 仅是当前任务或会话选择，禁止因临时切换自动修改 Primary。
- Workspace 的仓库使用 `provider`、标准 Git `url` 和可选 `local_path`；默认分支从目标远端发现。不得将仓库名、目录名或历史会话当成已验证身份。
- Provider 可以为 `github`、`gitlab`、`gitee` 或 `git`；自建实例必须用完整 URL 识别主机。Provider 仅决定平台适配能力，不能代表已获授权。
- 每个 Workspace 必须拥有唯一 ID；项目身份为 `workspace_id + project_slug`。同名项目跨 Workspace 不得自动合并或迁移。

## 目标选择

1. 当前指令明确指定的 Workspace 优先。
2. 已确认的当前项目归属优先于 Primary；“整理到产品中心”“我的产品中心”这类明确默认目标的表述使用 Primary。
3. 没有明确项目归属或目标时使用 Primary；无 Primary 时要求用户绑定。
4. 多个 Workspace 命中同一项目且当前任务无法唯一判定时，必须询问，禁止写入。
5. 跨 Workspace 复制、迁移和共享必须核对来源权限与目标授权，保留可追踪声明；不得隐式复制团队私有资料。

## 首次初始化与清空

- 本地用户可以通过手动创建配置文件完成初始化；未实现的命令不得声称可执行。
- 初始化默认生成 `version: 1`、`primary_workspace: null`、`workspaces: {}`；已存在配置时禁止覆盖，除非用户明确要求重置。
- 本地配置允许添加多个 Workspace 和各自本机路径；路径仅在实际有本地文件访问能力的环境生效。
- ChatGPT Web 无法读取本机配置；使用 Skill 内置默认配置或用户明确提供、且当前环境可访问的配置。不得假定跨会话私人配置会自动持久化。
- 其他用户未完成绑定时，即使 Skill 有发布者默认仓库，也必须确认目标身份及写入授权，不得默认写入发布者仓库。

## 完成标准

能够报告目标 Workspace、仓库 URL、Provider、实际访问方式、Primary/Active 来源及授权状态；无法验证的配置或路径必须标记未验证。
