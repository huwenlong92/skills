# SDKit Skills

Opinionated SDKit 工程约定，以可升级 Agent Skills 的形式分发。它们用于把已经确认的个人代码习惯固化为不同 agent 都能理解、模仿和验证的明确写法，不是框架 API 手册，也不是面向所有团队的通用最佳实践合集。

每个技术栈都是独立 skill：入口只负责识别任务和分流，具体代码习惯放在该 skill 的 `references/` 中。

## Skills

| Skill | 适用范围 |
|---|---|
| `sdkit` | Go sdkit 框架自身的 `core`、`pkg`、facade、driver 与 runtime |
| `sdkitgo` | 使用 sdkitgo、Gin、GORM、PostgreSQL 的 Go 后端 |
| `vab-admin` | 基于 Vue 3、Vab Shop Vite、Element Plus 的后台管理前端 |
| `nuxtjs` | 基于 Nuxt 4、Vue 3、Element Plus 的门户前端 |
| `rust-sdcore` | 基于 sdcore 的 Rust 工具型 Web 应用 |
| `npm-package` | 可发布 npm 包的结构、校验与发布流程 |
| `software-installation-docs` | Linux 软件安装、升级、回滚与运维文档 |

## 安装

仓库遵循通用 Agent Skills 目录结构，不需要发布为 npm 包。下面使用 `pnpx`；未使用 pnpm 的环境可以把 `pnpx` 换成 `npx`。命令参数以 [skills CLI 官方说明](https://github.com/vercel-labs/skills#readme) 为依据。

### 先选来源和 skill

GitHub 安装只能取得已经推送的内容；本地尚未发布的修改必须从本地目录安装。业务后端选择 `sdkitgo`，后台选择 `vab-admin`，Nuxt 门户选择 `nuxtjs`；`sdkit` 只用于框架仓库本身，不要求业务后端同时安装。

```bash
# 查看可安装的 skills
pnpx skills add huwenlong92/skills --list
```

### 项目级安装（默认）

先进入实际开发的子项目根目录，再执行命令；**不加 `-g` 就是项目级安装**。下面三条分别在各自项目执行，不是在每个项目里全部执行：

```bash
# Go 后端根目录
pnpx skills add huwenlong92/skills --skill sdkitgo -a codex

# Vab 管理端根目录
pnpx skills add huwenlong92/skills --skill vab-admin -a codex

# Nuxt 门户根目录
pnpx skills add huwenlong92/skills --skill nuxtjs -a codex
```

Codex 的项目级位置为 `.agents/skills/<skill-name>/`。同一工作区包含后端、admin 和 portal 时，必须分别进入对应子目录安装；从工作区父目录启动的会话不能据此假定已经发现所有子项目技能，必须检查当前会话的技能列表。

### 全局安装

只有希望当前用户的多个项目都能使用时才加 `-g`：

```bash
# 全局安装一个 skill
pnpx skills add huwenlong92/skills --skill sdkitgo -a codex -g

# 全局安装本仓库全部 skills
pnpx skills add huwenlong92/skills --skill '*' -a codex -g
```

禁止仅为方便而同时维护项目级和全局的同名不同版本；安装前先检查已有入口。全部安装不意味着每项任务都应读取全部 skills。

### 非 Codex 或多个 agent

换掉 `-a` 后面的 agent 名称即可；安装范围仍由是否带 `-g` 决定：

```bash
# Claude Code：项目级；全局时在末尾加 -g
pnpx skills add huwenlong92/skills --skill sdkitgo -a claude-code

# Kimi Code CLI：项目级；全局时在末尾加 -g
pnpx skills add huwenlong92/skills --skill sdkitgo -a kimi-code-cli

# 同一个项目同时供多个 agent 使用
pnpx skills add huwenlong92/skills --skill sdkitgo \
  -a codex -a claude-code -a kimi-code-cli
```

CLI 当前安装位置如下；其他 agent 名称和路径查看其官方支持表，不要自行猜测：

| Agent | `-a` 名称 | 项目级 | 全局 |
|---|---|---|---|
| Codex | `codex` | `.agents/skills/` | `~/.codex/skills/` |
| Claude Code | `claude-code` | `.claude/skills/` | `~/.claude/skills/` |
| Kimi Code CLI | `kimi-code-cli` | `.agents/skills/` | `~/.agents/skills/` |

CLI 的 symlink 模式是让 agent 入口引用安装后的 canonical copy，不等于实时链接开发中的源仓库。需要独立副本时使用 `--copy`。未列入 CLI 的 agent（例如 DSH），必须先核对该工具实际支持的 skill 搜索路径；支持 `.agents/skills` 时可以复用该目录，禁止假定它一定读取 Codex 或 Claude 的专属目录。

### 本地未发布版本

在目标项目根目录执行，把来源换成本地技能仓库路径。以下假设源仓库位于目标项目的同级目录；不满足时替换为实际路径：

```bash
pnpx skills add ../sdkit-skills --skill sdkitgo -a codex
```

`--skill`、`-a` 和 `-g` 的用法与 GitHub 来源相同。本地安装后修改源文件，不代表已安装副本自动更新；必须重新从本地来源安装，并核对覆盖预览。已经手工复制到 `.agents/skills` 的版本没有 CLI 安装记录，不能假定 `skills update` 会替它同步；迁入 CLI 管理前必须先备份并核对旧副本，禁止直接覆盖项目自有修改。

### 查看与更新

在对应项目根目录查看和更新项目技能；全局更新必须显式使用 `-g`：

```bash
# 查看已安装技能（输出可能同时包含项目级和全局，必须核对 scope）
pnpx skills list -a codex

# 只更新当前项目的 sdkitgo
pnpx skills update sdkitgo -p

# 更新当前项目全部已记录的技能
pnpx skills update -p

# 更新全局已记录的技能
pnpx skills update -g
```

更新前必须检查目标 skill 是否被手动修改；有修改时先保留差异并确认取舍。不得使用全量更新命令处理只获准更新一个 skill 的任务，也不得在目标项目内直接修改共享 skill 副本来代替源仓库维护。

### 安装完成检查

1. 确认安装位置、skill 名称和来源符合预期，`SKILL.md` 与 `references/` 完整存在。
2. 在对应项目的新一轮对话中检查技能是否可见；未发现时重开会话或重启 agent。Codex 的发现方式见 [官方技能说明](https://developers.openai.com/codex/skills)。
3. 检查项目 `AGENTS.md` 是否仍引用旧规范或存在相反约定。安装技能不会自动修改它；发现冲突必须先确认项目规则是否迁移，不能假定 skill 会覆盖项目显式规则。
4. 需要团队共享时，检查实际副本、链接和 CLI 锁文件是否可移植，再由用户决定提交范围；禁止提交只在某台机器有效的外部绝对路径符号链接。

## 仓库结构

```text
skills/
└── <skill-name>/
    ├── SKILL.md
    └── references/
        ├── <topic>.md
        └── <area>/<topic>.md
```

- `SKILL.md`：触发条件、任务分流、执行顺序和共同门禁。
- `references/`：按修改区域建立一级目录，例如 `service/handler.md`、`models/struct.md`、`worker/handler.md`、`crontab/handler.md`。每份 reference 都包含独立的 `name` 和 `description`，只有任务命中的文件需要读取。
- `templates/`：确实需要逐字复用的模板或脚本；它们不是解释性规范。

## 仓库内测试

本仓库使用 `.agents/skills/` 提供项目级测试入口。测试入口必须使用符号链接指向 `skills/<skill-name>`，禁止复制第二份 skill 内容；这样修改源文件后，当前仓库中的 Codex 会直接读取同一份草稿。

项目级入口只用于本仓库开发和验证，不等于全局安装。只有明确执行安装命令后，skill 才会进入用户级 agent 目录。

## 维护原则

- 已确认的个人偏好直接写成硬规则，不用“最佳实践”“灵活处理”等措辞弱化。
- 涉及具体代码写法时，同时提供脱敏的正向典型形态；只写禁止项不能让 agent 学会目标风格。
- reference 的代码和业务说明必须使用统一的虚构领域，不得复制真实项目的表名、schema、事件、权限、账号、route 或业务文案。
- 历史代码只用于发现候选习惯，不能因为仓库中已经存在就自动成为规范；必须与用户确认的偏好一致。
- 每条规则必须说明适用条件和动作；出现例外时必须写明唯一判定条件。
- 不使用电脑相关的绝对路径。共享依赖的位置从目标项目依赖声明、项目文档或用户输入中解析。
- 不把某个业务项目的临时决定提升为共享规则。
- `references/` 新增、删除、拆分或重命名后，同步更新对应 `SKILL.md` 的分流表。
- 修改完成后，逐个运行 Agent Skills 校验，并检查链接、绝对路径和模糊措辞。

规则优先级为：用户在当前任务中的明确要求 > 目标项目的显式 `AGENTS.md`/项目规范 > 本仓库 skill > 目标项目中的历史写法。历史代码与 skill 不一致时，新增和本次修改的代码按 skill 执行；不顺带批量改造无关历史代码。
