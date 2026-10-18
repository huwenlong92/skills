# Git Collaboration V1 · PR #20 最终本地集成验收

日期：2026-10-18。结论：**本地集成、静态回归、真实 Git CLI 通过；真实 Codex Agent 16 项 BLOCKED，整体技术验收未通过。保持 Draft。**

## Git 基线与集成

- 权威仓库：huwenlong92/skills；origin Fetch/Push 均为该仓库 SSH URL；默认分支 main；当前账户 ADMIN，目标分支规则查询返回空列表。
- 起始本地 main `a79003e5a8ab5fc3ba7fa344de886bf8316b391a`；原工作区有未知 docs/ideas，保留不动。
- 实时 PR #20 Head `d406eedfaf52f72dd1652dc566518f74c95aaf31`；目标分支 feat/git-collaboration-v1-20261018；OPEN/Draft。
- 本轮 Fetch 的 main `226465e5f951cc1f1394a1c91e4c3f682f822b83`；共同祖先 `77e0664fcbb0943f9bd4aa8cad96ab0d14fa4c3a`；初始 main/PR 独有提交 5/11。
- 创建专属隔离 Worktree 和 integration/pr20-final-20261018 本地分支，基于已核验 PR Head。只向授权 PR 分支普通 Push。
- 执行 `git merge --no-ff --no-commit origin/main`，退出 1，唯一冲突为 AGENTS.md。逐项读取索引阶段 1/2/3 后移除冲突标记，保留 Git Collaboration 与 Project Skill Bootstrap 两个入口；没有无条件 ours/theirs。
- 其他 Worktree、未知修改、Stash 及操作状态已检查，未清理或改写。工作区清单仅在本地检查，不提交个人路径。
- [保全与协议审查](review.json)：授权范围外 449 个 main 文件原字节保留。AGENTS 相对 main 只有 Git Collaboration 入口增量；Bootstrap、全局迁移、已合入技术栈规则和历史证据保留。
- #21、#22 无本次目标文件重叠；交付前 #21 Head 已前进，重读文件集合后仍无重叠。新增 #24 Head e4bfdb945cf1d36c81a1a49eaaca853ef6f3ef59 与本 PR 在 Orchestration 为 L2，并声明依赖 #20/#21。已审查其 routing 与 collaboration diff：职责可兼容，但未合入 #24，未来联合集成必须再测试，不能把本报告当作 #24 已验收。
- 交付前 PR 旧 Head 的 CONFLICTING 是尚未 Push 本次解决结果时的远端状态。最终 Merge Commit、Head、Push 读回与 mergeable 由最终交付查询给出，不在提交内容中自引用 SHA。

## 实际修复

1. AGENTS 集成冲突：保留双方有效入口，未覆盖专题 A。
2. Foundry publishing、WikiOps repository：移动共享兼容与完成标准的顺序，使文件末尾保留可核验的完成标准；未改变原有授权与发布语义。
3. 原静态测试新增两个回归：双入口共存及 Reference 完成标准位置。
4. 增加隔离真实 CLI G01–G20、可复现全仓检查入口及脱敏验收证据；未创建 Git 自动执行器。

## Python、Manager 与链接

可复现入口：

```sh
python3 docs/testing/git-collaboration-v1/run_local.py --output <新的临时输出目录>
```

该脚本只启动当前源码中实际存在的测试文件；为子进程指定规范化的独立 TMPDIR，禁写 pyc。不调用模型、远端 Git 或 CI。每条原始命令、退出码和完整脱敏输出见 [最终本地结果](local-results.json)，CLI 工具调用见 [CLI 证据](cli-results.json)。

| 实际命令 | 通过 / 失败 | 退出码 |
|---|---:|---:|
| python3 scripts/test_git_collaboration.py -v | 9 / 0 | 0 |
| python3 scripts/test_git_collaboration_cli.py -v | 20 / 0 | 0 |
| python3 scripts/test_engineering_protocols.py -v | 17 / 0 | 0 |
| python3 scripts/test_markdown_links.py -v | 7 / 0 | 0 |
| python3 scripts/test_project_skill_global.py -v | 11 / 0 | 0 |
| python3 scripts/test_project_skill_safety.py -v | 28 / 0 | 0 |
| python3 scripts/test_ui_design.py -v | 9 / 0 | 0 |
| python3 skills/dockerops/scripts/test_binding.py -v | 9 / 0 | 0 |
| python3 skills/dockerops/scripts/test_catalog.py -v | 17 / 0 | 0 |
| python3 skills/dockerops/scripts/test_check_layout.py -v | 15 / 0 | 0 |
| python3 skills/foundry/tests/test_workspace.py -v | 18 / 0 | 0 |
| python3 skills/npmops/scripts/test_binding.py -v | 10 / 0 | 0 |
| python3 skills/npmops/scripts/test_packages.py -v | 10 / 0 | 0 |
| python3 skills/sdkit-skills/scripts/test_manager.py -v | 37 / 0 | 0 |
| python3 skills/sdkit-skills/scripts/test_migration.py -v | 7 / 0 | 0 |
| python3 skills/wikiops/scripts/test_extract_share.py -v | 13 / 0 | 0 |
| python3 skills/wikiops/tests/test_remote_safety.py -v | 8 / 0 | 0 |
| python3 skills/wikiops/tests/test_workspace.py -v | 18 / 0 | 0 |
| **unittest 合计** | **263 / 0** | **全部 0** |
| python3 skills/sdkit-skills/scripts/manager.py validate --all | 21 Skill | 0 |
| python3 scripts/check_markdown_links.py | 最终数量见下方文档复核 | 0 |

Manager 同时验证 Catalog 分类/目录一一对应和 21 个 Skill 的仅 name/description frontmatter。命中 Reference 的九项人工门禁逐条见 review.json；未将 Manager 冒称为全部语义质量检查。

首轮历史见 [初次结果](initial-local-results.json)：Foundry 的 18 项中 1 项断言失败（suite 退出 1），macOS 临时目录 /var 与 /private/var 规范路径不一致。没有修改无关 Foundry 实现或测试；规范化 TMPDIR 后该套 18 项退出 0，最终全仓回归同样通过。原静态 Git 测试首轮 7 项，新增两项后为 9 项。失败历史保留，不覆盖为成功。

最终文档复核：`python3 scripts/check_markdown_links.py`：317 Markdown、1108 相对链接、2 锚点、0 错误，退出 0；`git diff --check` 退出 0。。

## 静态协议与质量审查

| 检查 | 结果与边界 |
|---|---|
| P0–P3 与 UNKNOWN | PASS：按风险取证，未知不写入；仅讨论不触发 Git 写入 |
| Bootstrap 与入口 | PASS：AGENTS 两入口并存，Bootstrap 和迁移内容保全 |
| Orchestration | PASS：业务 Primary 保留，Git 子任务职责清晰；不是独立安装 Skill |
| Development Execution | PASS：C0/P1、C2/P2/P3、C3 分项记录；未测模型阶段不标 verified |
| Collaboration Awareness | PASS：复用 L0–L3，Push/Merge 再核验；无第二状态数据库 |
| Foundry/WikiOps 独立安装 | PASS：现有双阶段同步、精确暂存、版本条件、授权与发布边界独立保留；共享协议缺失不能扩大授权 |
| GAP-B01/B02 条款 | 静态 PASS；真实 CLI 事实通过；真实模型行为 BLOCKED |
| Catalog/frontmatter/链接 | PASS：实际 Manager 与 Markdown 检查，不只检查关键词 |
| Reference 质量 | PASS（本次两个命中文件）：九项逐条人工检查，完成标准末尾回归通过 |
| 敏感信息与危险命令 | 见 scan.json 与最终文档复核；新增内容无凭据、Token 或私有绝对路径；危险操作文本均审查上下文 |

关键词契约测试只作为静态回归。上述协议一致性是条款、授权边界及实际 Git 证据的联合人工审查，不等于真实 Agent 已遵循协议。

## G01–G20 真实 Git CLI

所有仓库由脚本临时创建，虚构身份/Remote，不连接真实业务仓库。每场景保存 argv、cwd、退出码、stdout、stderr，路径脱敏为 <fixture>；测试结束仅清理自己创建的临时夹具。CLI 20 PASS / 0 FAIL，退出 0。

| ID | 场景与实际观察 | CLI 结果 |
|---|---|---|
| G01 | 单人 main 提交；干净且 AHEAD 1/0 | PASS |
| G02 | 第二 clone 推进远端；Fetch 确认祖先后 pull --ff-only 到目标 SHA | PASS |
| G03 | 本地 AHEAD，重新 Fetch，夹具已授权普通 Push 并 ls-remote 读回 | PASS |
| G04 | 分叉 1/1，ff-only 失败且 HEAD 保留 | PASS |
| G05 | 已修改同路径；pull 失败，原字节保留，无 Stash | PASS |
| G06 | 未跟踪同路径；pull 失败，sentinel 保留 | PASS |
| G07 | 无 upstream 可检测；不猜测或建立配置 | PASS |
| G08 | Worktree 文件隔离；已占用分支不能再次分配 | PASS |
| G09 | 两 clone 不同文件并行提交；普通 Merge 保留双方 | PASS |
| G10 | Merge 冲突，读取索引 1/2/3，合成内容并 continue | PASS |
| G11 | 仅未发布虚构 topic Rebase 中断，读取双方并 continue | PASS |
| G12 | Cherry-pick 中断，读取双方并 continue | PASS |
| G13 | 夹具 bare 服务端 update-ref 注入历史重写，旧远端 SHA 祖先检查失败，本地 HEAD 不变 | PASS |
| G14 | 普通 Push 被拒，先 ls-remote/Fetch，证实远端与分叉状态 | PASS |
| G15 | Git 对 localhost:1 真实连接失败，随后 ls-remote 正常 Remote 核验，HEAD/工作区不变 | PASS |
| G16 | 脏 Worktree remove 失败保全；本测试明确授权清理自己的 sentinel 后普通 remove | PASS |
| G17 | 检查已有 .git/顶层/HEAD，停止重复 init，配置原字节保留 | PASS |
| G18 | child 无 .git 仍解析到父仓库；检查 gitlink，不创建嵌套仓库，父索引不变 | PASS |
| G19 | 无配置授权仅检查 Remote 与来源，配置原字节不变 | PASS |
| G20 | 已授权添加及替换虚构 Remote；独立 Fetch/Push URL、refspec、upstream、配置来源读回 | PASS |

限制：G15 使用本机连接失败，不测试外部网络、超时后服务端写入成功或响应丢失。G03/G16/G17/G18/G19/G20 的授权选择由受控夹具明确限定，Git 本身不理解用户意图；**不声称它们证明 Agent 会主动拒绝无授权写入**。G13 的故障注入只在新建 bare 测试仓库，G11 只处理未发布虚构提交；真实 PR 历史没有 Rebase 或改写。

## 真实 Codex Agent

新建独立临时 home/CODEX_HOME，清除继承认证变量，仅执行 `codex login status`：退出 **1**，stderr **Not logged in**。CLI 参数从实际 `codex exec --help` 核验；未启动模型。没有读取、复制或提交认证内容，未修改真实 Codex 配置。

依用户第七节要求：需要额外登录即停止本部分；本轮不复用其他专题的隔离认证。边界测试、模型调用、工具行为审查均未执行。后续恢复必须先建立正常隔离认证，再验证文件/网络隔离与宿主 Skill/插件不加载；不能仅设置 CODEX_HOME 就声称已隔离。认证机制参考 [OpenAI 官方认证文档](https://learn.chatgpt.com/docs/auth)。

逐项输入与预期见 [真实 Agent 待验矩阵](agent-results.json)。当前 0 PASS / 0 FAIL / **16 BLOCKED**；不是失败模型结果，也不是静态模拟。

| ID | 场景 | 结果 |
|---|---|---|
| A01 | 继续开发按需 Preflight | BLOCKED |
| A02 | 同步代码保护未提交修改 | BLOCKED |
| A03 | 只暂存任务文件 | BLOCKED |
| A04 | 提交但不 Push | BLOCKED |
| A05 | 创建 PR 不自动 Merge | BLOCKED |
| A06 | Merge 前 Head/Review/CI/权限/授权 | BLOCKED |
| A07 | 冲突不无条件 ours/theirs | BLOCKED |
| A08 | 准备发布只核验 Git | BLOCKED |
| A09 | 纯讨论无 Git 写入 | BLOCKED |
| A10 | 其他 Agent 修改后再核验远端 | BLOCKED |
| A11 | 网络失败不盲目重试 | BLOCKED |
| A12 | 无授权危险操作拒绝 | BLOCKED |
| A13 | 无授权不自动 init | BLOCKED |
| A14 | 父仓库内不创建嵌套仓库 | BLOCKED |
| A15 | 无授权不添加/替换 Remote | BLOCKED |
| A16 | 明确授权 Remote 后读回 | BLOCKED |

## 交付判断与未执行项

- Git Collaboration V1 整体技术验收：**未达到**，缺真实 Agent 16 场景。
- GAP-B01/B02：条款与受控 Git 事实已覆盖，**真实 Agent 行为验证未完成**。
- 专题 A：全部有效规则与验收证据保留；原全局 git-initialization-rules 不修改。
- Ready/申请合并的完整技术条件：**尚不具备**；不得把本地通过当成模型门禁完成。
- 专题 A 的全局规则退出门禁：可以评阅本轮证据，**不能判为满足退出条件**；仍需真实行为、正式协议交付/可访问及授权语义等价验证。
- 未执行：真实模型、外部网络响应丢失、其他 Provider/Agent 行为、PR Merge/Ready、部署、主动 CI、全局规则迁移回归。前三类缺证据如上，其余为本次禁止或未授权操作。
- 保留独立 Worktree 与证据，普通 Push 后交还 ChatGPT Web 专题 B 最终远端核验；不自动继续合并或发布。
