# 仓库与发布协作

适用范围：统一包父目录、新包创建与查找、定位当前 npm 源码包、Git 同步及关联 PR 检查。涉及包修改、版本发布或公开页写入前必须读取本文件。文件路径以对应源码仓库根目录为基准。

## 私有绑定与目标选择

- 长期绑定必须保存在 `~/.config/sdkit/skills/npmops/config.json`；脚本 `--config <path>` 必须读取显式路径。允许用户指定的私有配置位置，禁止把私人目录/远端 URL 写入 Skill 安装目录、源仓库或要求写死到项目 AGENTS.md；禁止创建空配置。
- 配置允许只包含 `packages_root`，表示新包和查找的统一父目录，不要求绑定一个全局源码仓库。只有确需长期绑定单个已有包时，才允许使用可选 `repository.local_path` 和 `repository.url` 保存该包目录与预期 SSH/HTTPS Git 远端。相对路径必须以配置文件所在目录解析；URL 禁止携带凭据、查询参数或片段。不存在配置时允许从当前用户要求与明确项目声明确定本次目标，禁止凭同名包、历史会话或 homepage 猜造绑定。
- 当前指令明确的目标必须覆盖长期绑定；目标不同仅影响当前任务，禁止自动改写配置。当前操作必需字段缺失、指定目录不可访问或声明与本地身份不一致时必须停止受影响写入，禁止静默切换其他仓库或修改 Remote。
- 包 `repository` 必须仍声明真实源码；用户配置不能把公开介绍页变为源码身份。包根目录、registry、scope、access 与版本仍必须从目标 package.json、Makefile 和命中说明解析，monorepo 必须确认具体包路径；它们不能替代 Git 或发布授权。
- 不建立 Workspace 或 Primary/Active 注册表。配置禁止存放 npm 登录态、Token 或 `.npmrc`；[认证](auth.md)仍是凭据的唯一权威定义。项目发布声明必须保留在本包 package.json、Makefile 与 `deploy/DEPLOY.md`，禁止复制到个人配置维护第二套。
- 迁移已有私有绑定时必须先校验内容、解析旧相对路径并确认目标不存在；目标存在时必须停止覆盖。新文件必须排他创建且权限为 `0600`，实际运行绑定检查并核对内容与权限后才算完成；旧文件必须保留，只有用户要求时才允许删除。

正向配置形态（必须替换为用户确认的实际目录）：

```json
{"packages_root": "../../repos/npm-packages"}
```

反例：在 AGENTS.md 写死个人目录，或将所有新包绑定到同一个旧包的 Remote。

## 新包默认目录与查找命令

- 创建新 npm 包时必须读取当前用户配置的 `packages_root`；当前指令未指定其他位置时，必须在该父目录下创建独立包子目录。用户明确指定例外位置时必须服从，但禁止因此改写长期配置。
- 统一父目录只是目录容器，不是一个公共 Git 仓库。禁止在父目录自动 `git init`、将现有包搬入或批量改 Remote；每个新包的 Git 仓库、源码 URL、包名与 registry 必须分别按当前用户授权和包声明确定，禁止从其他包或可选全局 `repository` 继承远端。
- 创建前必须检查父目录可访问、目录名为单一安全名称且不能为 node_modules，目标不存在且不是文件、目录或符号链接。重名或路径穿越必须停止，禁止覆盖、合并或自动追加数字改名。
- [目录命令](../scripts/packages.py)必须读取 `~/.config/sdkit/skills/npmops/config.json`，显式 `--config <path>` 时读取指定文件。`root`、`list`、`find` 只读；`create` 只允许创建指定空子目录，不初始化 package.json、Git、Remote，不安装依赖、提交或发布。

```bash
python3 <skill-dir>/scripts/packages.py root
python3 <skill-dir>/scripts/packages.py list
python3 <skill-dir>/scripts/packages.py find <keyword>
python3 <skill-dir>/scripts/packages.py create sample-tools
```

- `find` 必须按目录名和直接子目录的 package.json.name 匹配；scoped 包名与目录名必须分别处理，禁止将 `@scope/name` 直接当作单层目录名。查找只检查直接子目录，禁止递归遍历 node_modules、隐藏目录、其他目录或跟随符号链接；结果必须保留未初始化目录标记和解析异常，禁止把空结果称为全盘无匹配。
- 用户要求“创建 npm 包”时，建目录仅是第一步；必须继续按[包结构](package-json.md)与[Makefile](makefile.md)完成本次要求的初始化和验证。缺少包名、源码 URL 或发布声明时，必须只停止依赖这些信息的步骤，禁止把空目录声称为可发布包。
- 缺少 packages_root 或父目录不存在时，命令必须报错，禁止回退当前目录、创建空配置或擅自初始化父目录；只有用户明确指定该目录时，才允许 Agent 创建并配置它。已有包的维护必须保留现有位置，禁止强制搬迁。

正向形态：读取用户配置 → 查重 → 创建独立子目录 → 按本次需求初始化包 → 确认该包自己的 Remote。反例：统一父目录后，把所有包推向同一个默认源码仓库。

## 当前包与 Git 身份

- 必须核对当前包及其 Git 根目录，读取最新 `AGENTS.md`、package.json、Makefile 与命中规范。必须保留实际分支和包目录，禁止自动新建任务分支、切换分支或遍历主目录寻找同名包。
- 不建立 Workspace、Primary/Active、Repository Resolver 或 Provider 切换机制。路径不可访问、仓库归属冲突时必须停止依赖该路径的任务，禁止静默改用另一个仓库。
- 本地路径存在但有脏工作树或分叉时，必须保护现有内容并停止受影响自动同步。用户明确要求修改已有未提交内容时，必须先核对归属和文件范围，禁止清理其他任务内容。
- Git 写入前必须将当前用户指令或用户配置中的预期 URL（未配置时使用项目明确声明的源码 URL） 与 `origin` 全部 Fetch/Push URL 比较。必须保留主机、非默认端口和路径身份，只允许已核实的 SSH/HTTPS 等价形式；包处于子目录时必须同时核对 `repository.directory`。存在冲突 URL 或缺少 origin 时必须停止，禁止自动修改 Remote。
- Git 读取、提交、推送、PR/MR、registry 发布与公开页写入能力必须分别核验；只读访问不能推导为可发布，离线 Git 信息不能证明远端版本或包权限。没有 Git 仓库的本地包允许只读结构检查；涉及 Git 写入的步骤必须停止并报告未满足条件。

## 只读绑定检查

[绑定检查脚本](../scripts/binding.py)只读取当前 Skill 的私有绑定。

用户已保存单包绑定时，在实际 Skill 目录运行；只有 packages_root 配置时，必须为本次具体包显式提供目录与预期 URL：

```bash
python3 <skill-dir>/scripts/binding.py
python3 <skill-dir>/scripts/binding.py --config <private-config.json>
python3 <skill-dir>/scripts/binding.py --path <package-dir> --url <expected-repository-url>
```

脚本只读校验本地目录及 origin 的全部 Fetch/Push URL，并输出分支、dirty、上游与缓存 ahead/behind；禁止写配置、改 Remote、切分支、联网或 Fetch。缺配置必须报错，不执行初始化；`identity_verified` 不能替代实时远端、权限或发布授权核验。新建绑定后必须运行该检查并核对 `0600` 权限；未绑定时禁止声称已验证长期目标。

## 双阶段同步与跨会话

1. 修改前必须检查分支、dirty、上游、任务文件及版本声明，并按需 Fetch；仅工作区干净且可以快进时允许 `git pull --ff-only`。Detached HEAD、无上游或分叉时必须停止自动同步，禁止用 Reset、Stash、Rebase、Clean 或强推绕过。
2. 包写入前必须从远端发现默认分支并检查开放 PR 摘要，禁止固定为 main；只对同包、同文件、共享锁文件/发布入口或显式依赖 PR 读取 diff。只读包结构评审不要求全量 PR 扫描；感知过程禁止触发 CI、bump、npm 发布或部署。
3. 同包版本、exports、依赖、Makefile、锁文件或公开页并行修改必须比较双方意图和发布先后。冲突未解决或必要实时证据不可用时必须停止受影响写入，保留草稿和未合并工作；禁止只凭标题认定独立。
4. Push 前必须再次 Fetch 并核对远端 HEAD、全部 Fetch/Push URL、上游、分支保护和授权，远端前进时先整合再验证。只允许暂存本次包任务文件，禁止全量暂存、强推或自动推送默认分支；仓库要求 PR/MR 时必须遵守。
5. Git 同步不授权版本变化或 npm 发布；真实发布前仍必须执行[发布流程](workflow.md)的干净工作区、认证、registry 精确版本与 dist-tag 检查。公开介绍页必须独立验证目标，按[公开页规则](public-page.md)在临时 Clone 中操作，禁止清空本地源码或已有目标 Checkout。

正向形态：确认具体包及源码 URL → 核对本地和关联 PR → 整合版本与锁文件 → 验证 tarball → 按各自授权提交或发布。反例：把公开 homepage 当作源码仓库，或从 GitHub 只读访问推导 npm 发布权限。

## 完成标准

创建/查找任务必须报告实际 packages_root、目标目录、查重与初始化阶段，并核对未改动现有包。源码维护或发布任务必须报告源码仓库、包根目录、registry、实际分支/dirty/上游、关联 PR 与授权边界；未 Fetch 状态必须标记为缓存。人工检查 URL 等价性、monorepo 包归属与并行版本冲突；测试、Git 同步、registry 发布和公开页更新必须分别给出真实结果，禁止把其中一步成功称为全部完成。
