# sdkit-templateops

Template Evolution V1：Solo-first / Team-ready / Multi-stack / Agent-compatible。

用于识别 Git 模板来源、审计 Node/Go/Rust/Python/Flutter 工具链和依赖锁、比较 BASE/TARGET/PROJECT 三方差异、生成带摘要的升级计划，并在独立授权下执行或恢复。首版只交付协议与只读工作流，不内置自动修改业务项目的 CLI。

## 使用
- “这个项目来自哪个模板？”：读取项目声明、Git 证据；未知来源保持 unknown。
- “模板更新了什么？”：锁定两个模板 Commit，只读比较。
- “升级到最新版”：先生成计划与风险，不自动 Apply。
- “Node 版本不对”：报告声明/实际/CI 差异，不安装工具链。

项目身份约定：`.sdkit/template.json`；复杂任务计划：`.sdkit/plans/<task-id>.md` 与同名 `.upgrade.json`。这些文件是建议协议，不因安装本 Skill 自动创建。参考 [身份](references/identity.md)、[升级计划](references/upgrade.md) 和 [测试](references/testing.md)。

本 Skill 可独立安装；不依赖其他 Skill 的安装目录或个人固定路径。Git、数据库和部署的实际操作必须遵守目标仓库规范与用户授权。
