# Foundry · 安装与 Workspace 配置

Foundry 用于产品规划、PRD、技术方案、设计、原型和 Product Docs 协作。本文件面向安装者；Agent 的执行约束以 [SKILL.md](SKILL.md)、[Workspace](references/workspace.md)、[Repository Resolver](references/resolver.md) 和 [提交与验收](references/publishing.md) 为准。

## 安装

在本地安装前确认 Codex 的实际 Skill 搜索路径。全局安装示例：

```bash
pnpx skills add huwenlong92/skills --skill foundry -a codex -g
```

若使用已克隆的本仓库作为来源，可从该本地目录安装（将路径替换为实际位置）；安装后必须检查 `SKILL.md`、`references/`、`config/` 和 `scripts/` 是否完整。安装副本不一定随源码仓库 `git pull` 自动更新。详细安装方式见仓库根目录 [README](../../README.md)。

## 配置位置与优先级

本地个人配置默认保存在：

```text
~/.config/sdkit/skills/foundry/config.json
```

禁止将个人配置放进 Skill 安装目录、源码仓库或业务仓库，也不要提交个人本机路径。使用 `--config <path>` 可以显式指定其他配置文件。

- 存在用户 `config.json` 时，完整使用用户配置；即使 `workspaces` 为空，也不会回退发布者默认仓库。
- 用户配置不存在时，解析器只读加载 Skill 内的 `config/defaults.yaml`，默认 Primary 为 `personal`，指向 `huwenlong92/product-docs`。公开地址不代表拥有写入权限。
- `init` 创建空用户配置且不覆盖已有文件。**已配置用户不要重新初始化或删除配置。**

## config.json 完整示例

下方是个人产品中心的示例；`local_path` 必须替换成自己电脑上真实的 Git 仓库绝对路径。

```json
{
  "version": 1,
  "primary_workspace": "personal",
  "workspaces": {
    "personal": {
      "repository": {
        "provider": "github",
        "url": "git@github.com:huwenlong92/product-docs.git",
        "local_path": "/path/to/product-docs"
      }
    }
  }
}
```

| 字段 | 作用 |
| --- | --- |
| `version` | 配置协议版本，目前为 `1` |
| `primary_workspace` | 未明确指定目标时默认选择的 Workspace ID |
| `workspaces` | 多个独立的个人或团队产品中心 |
| `repository.provider` | `github`、`gitlab`、`gitee` 或 `git` |
| `repository.url` | 完整 SSH/HTTPS Git URL，用于验证仓库身份 |
| `repository.local_path` | 可选本机目录；`null` 表示未指定固定路径 |

不配置 `branch`：本地尊重当前检出分支（通常 `main`），远端 PR/MR 目标分支依据目标仓库规范发现。不持久化 `active_workspace`：它只用于当前任务，不修改 Primary。Web PR/MR 和本地 Git 交付规则也不写入每个 Workspace。

## 首次初始化与登记本地仓库

以下命令均从 **skills 仓库根目录** 执行；也可直接使用已安装 Foundry 内的 `scripts/workspace.py` 路径。

```bash
python3 skills/foundry/scripts/workspace.py init

python3 skills/foundry/scripts/workspace.py add personal \
  git@github.com:huwenlong92/product-docs.git \
  --provider github \
  --path /path/to/product-docs \
  --primary

python3 skills/foundry/scripts/workspace.py list
python3 skills/foundry/scripts/workspace.py resolve personal
```

若已有 `personal`，`add` 会拒绝覆盖。只需要修改本地路径时执行：

```bash
python3 skills/foundry/scripts/workspace.py set-path personal /path/to/product-docs
```

正常本地解析应返回 `"mode": "local"`、已验证仓库身份、路径和当前分支。路径名称不必等于远端仓库名，但 Git `origin` 必须与配置中的 URL 指向同一仓库。

## 多 Workspace、Primary 与 Active

可同时绑定个人与团队 Workspace。以下团队仓库仅为示例：

```bash
python3 skills/foundry/scripts/workspace.py add team \
  git@gitlab.example.com:team/product-docs.git \
  --provider gitlab \
  --path /path/to/team-product-docs

python3 skills/foundry/scripts/workspace.py set-primary personal
python3 skills/foundry/scripts/workspace.py resolve --active team
```

`set-primary` 持久化修改默认空间；`resolve --active team` 只影响当次解析。删除绑定可使用 `remove team`，但不会删除本地 Git 仓库。跨 Workspace 同名项目必须明确目标，不能自动迁移或覆盖。

## Local-first 与同步检查

在具有本地文件访问能力的 Codex 环境，Resolver 先检查当前工作区，再检查配置的 `local_path`；只有找不到匹配的本地仓库时才返回 `mode: remote`。如果已配置的本地仓库存在但身份不匹配，必须报错，不得静默切换远端。

```bash
# 只读解析，不访问远端
python3 skills/foundry/scripts/workspace.py resolve personal

# 只看本地缓存的上游状态
python3 skills/foundry/scripts/workspace.py sync-check personal

# 执行 git fetch origin，再检查最新跟踪状态
python3 skills/foundry/scripts/workspace.py sync-check personal --fetch
```

`sync-check` 可能返回 `up-to-date`、`push-candidate`、`fast-forward-required`、`blocked-dirty`、`blocked-diverged` 或 `blocked-no-upstream`。不带 `--fetch` 的 ahead/behind 仅为缓存；不应据此允许 Push。带 `--fetch` 也只是同步预检，不会执行 Pull、Commit、Rebase 或 Push；`can_push` 不是权限证明，也不能替代分支保护检查。

## Web 与本地 Git 工作流

**ChatGPT Web**：无本地文件访问能力时，通过已授权的 Git Provider 使用独立任务分支，默认创建 PR/MR；核验目标分支、Head SHA、冲突与适用 CI 后，才在授权范围内合并。合并不等于部署。

**本地 Codex**：尊重当前分支，通常直接在 `main` 修改和提交，不强制新建 PR。必须执行双阶段同步：

1. 修改前检查工作区、上游和目标仓库身份；`git fetch` 后，只有工作区干净且可以快进时才执行 `git pull --ff-only`。
2. 修改、测试、仅暂存任务文件并提交到当前分支。
3. Push 前再次 Fetch 并检查上游状态。远端有新提交时必须安全整合并重新验证；出现分叉、未提交修改、缺失上游或冲突时停止危险操作，禁止强推、Reset 或自动 Stash。
4. 遵守目标仓库分支保护与用户授权；不因本地使用 `main` 就绕过 PR/MR 强制规则。

## 升级与排障

更新 `skills/main` 不一定自动更新 Codex 的已安装 Skill；先确认实际安装来源，再按安装方式同步。用户配置在独立目录，升级 Skill 时不得覆盖。

从旧配置路径迁移时，先验证原 JSON、确认新路径不存在，复制后检查内容及 `0600` 文件权限，并运行 `resolve`；验证完成前保留旧文件。不要在迁移前直接运行 `init`，避免生成互不一致的配置。

可在仓库根目录运行：

```bash
python3 -m unittest discover -s skills/foundry/tests -v
```

## 验收标准

安装后必须确认 Skill 完整可见、`list` 读取正确的 Primary、`resolve` 选择预期的本地仓库、`sync-check --fetch` 报告真实同步状态。无法访问本地仓库、远端 Provider 或受保护分支时，必须明确报告，不得宣称已经同步、提交、合并或部署。
