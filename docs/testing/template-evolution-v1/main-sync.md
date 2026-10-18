# PR #24 最终安全同步与回归

适用范围：普通 Merge 最新 main 到 PR #24，验证本地协议与接口兼容；不执行业务 Apply。

## 基线与授权

原始 Head `7c78d7a9dd550a7e7ffb8cfc2b50f2a8917fa9b6`，main `8777b036311349fef7a99cdf094c36fd7011c15c`，均与用户给定基线一致。账号具备 push 权限；开始时 Draft/Open、mergeable UNKNOWN，最终状态必须重新查询。恢复入口：[计划](../../../.sdkit/plans/pr24-main-sync.md)。

本轮仅授权 #24 普通合入 main、必要修复、精确提交与普通 Push；保持 Draft，不合并 PR、不部署、不主动 CI。原本地分支被其他 Worktree 占用，采用新独立 detached Worktree 沿远端 #24 历史集成，再将其 Head 普通 Push 至同一目标分支；不移动其他 Worktree 的本地分支。

## 冲突和保全

执行 `git merge --no-ff --no-commit 8777b036311349fef7a99cdf094c36fd7011c15c`，退出 1，唯一冲突为 Catalog。读取三个索引阶段后按 Skill 名逐条核对：共同条目内容相同，main 全部 22 项与顺序保留，再追加 templateops；总计 23，dbops/templateops 各一次。[三方处理证据](main-sync-catalog.json)。没有使用 ours/theirs 整体覆盖。

本轮未修改 TE 协议或 Fixture；17 个原有协议/测试/Skill/报告文件逐字节保留。DBOPS 文件与 main 逐字节相同。既有 .sdkit 交接只追加本轮信息，不覆盖历史内容。

## 回归

所有最终命令退出码均为 0，精确数量见 [本地结果](main-sync-results.json)。

| 命令 | 结果 |
|---|---|
| `python3 -B scripts/test_template_evolution.py -v` | 47/47 |
| `python3 -B skills/sdkit-skills/scripts/manager.py validate --all` | 23 Skill；Catalog、Frontmatter 与目录一致 |
| `python3 -B scripts/check_markdown_links.py` | 全仓链接与锚点零错误，数量见 JSON |
| `python3 -B -m unittest discover -s skills/sdkit-skills/scripts -p 'test_*.py' -v` | 44/44 |
| `python3 -B -m unittest discover -s scripts -p 'test_*.py' -v` | 119/119（含 TE 47） |
| `python3 -B -m unittest discover -s skills/sdkit-dbops/tests -v` | 11/11 |
| `git diff --check` | 零错误 |
| `git diff --check origin/main...HEAD` | 零错误；Merge Commit 后再次执行 |
| `git diff --cached --check` | 零错误 |
| `python3 -B docs/testing/template-evolution-v1/check_main_sync.py` | Catalog、保全、敏感信息/绝对路径/凭据/冲突标记/无关文件，零错误 |

47 项 Fixture 保留模板身份、所有权/多模板冲突、Digest/Revision、授权拒绝、来源未知、Git/Provider 门禁、恢复和组完成状态断言。布尔授权不是身份认证，静态证据不替代实际 Agent 授权行为。

## 接口兼容

#20 Head `dbf71b252cefe799625cb7b81bde95b2beb783ab` 仍为独立 Draft；其 Git Collaboration 规范仅从已核验源码读取。`standards/skill-orchestration.md` 与同步前 #24 完全相同，不提前添加 #20 路由，也不纳入其 Commit。

在另一个临时快照中按共同祖先合成 #20 所需的 9 个协议/测试文件，Git 与模板路由共存且无文本冲突。执行以下命令，退出码均 0：[联合证据](main-sync-compatibility.json)。

- `python3 -B scripts/test_git_collaboration.py -v`：9/9。
- `python3 -B scripts/test_git_collaboration_cli.py -v`：20/20；仅本地虚构 Git 仓库，不是 Agent 行为测试。
- `python3 -B scripts/test_template_evolution.py -v`：47/47。
- `python3 -B -m unittest discover -s skills/sdkit-dbops/tests -v`：11/11。

#22 仅改 UI baseline Skill 与测试，无本轮目标文件交集；#25 仅改后续 DBOPS 能力，本轮不纳入。未写入 #20、#22、#25 或其他开发分支。

## 阶段与限制

C0 基线/权限/工作区检查完成；C1 唯一 Catalog 冲突解决；C2 全部本地回归和接口组合通过，后续普通提交/Push 需远端 SHA 再核验；C3 由最终 Git/Provider 查询完成，最终 Merge Commit 和 Head 以查询结果为准，不在文档内自引用提交 SHA。

本轮本地技术条件满足。BLOCKED（本次授权禁止执行）：真实业务/模板构建、Apply/恢复、真实 Agent 越权和跨 Provider 实例测试。未用 Fixture 冒充这些测试通过。远端 CI/Review 不是本轮本地回归证据，保持 Draft，后续最终合并仍需当前授权和实时门禁核验。

完成标准：两父普通 Merge Commit 包含锁定 main 与原始 #24，普通 Push 后 Head/Base/Draft/Open/mergeable 均由 Provider 确认；UNKNOWN 等计算后重新核验。其他 Worktree 的修改保留。
