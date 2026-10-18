# Template Evolution V1 本地最终技术验收

适用范围：PR #24 的只读协议、Python Fixture、安全拒绝与 #20/#21 联合兼容；不执行业务升级。

原始 Head `078d2222c9d7aa80375d62ced328670d4e9a577e`；实时 main `226465e5f951cc1f1394a1c91e4c3f682f822b83` 已为祖先。#24、#20、#21 均 Open/Draft。#20 Head `dbf71b252cefe799625cb7b81bde95b2beb783ab`；#21 Head `162c53596b0a5e006adc8cc493368a37d018f7bf`。

## 复现与修复

原有 `python3 scripts/test_template_evolution.py -v`：退出 0，28/28。新增回归首次 `python3 -B scripts/test_template_evolution.py -v`：退出 1，40 项中 9 失败；修复后 40/40，再扩充到 47/47。

9 个已复现缺口：规范化路径绕过 forbidden；路径所有者不在计划成员；源基线 SHA 未匹配；可选工具链字段未纳入 Digest；重复成员；空 required mounts；字符串授权真值；未完成组可标 verified；大小写冲突范围。修复限于协议验证，不增加执行器。

新增 19 项覆盖多模板分离所有权、规范化禁止路径、源基线/last_synced、工具链摘要、重复成员、组验收、严格布尔授权、文件伪造授权、旧 Digest 审批失效、失败恢复与 stale Git、blocked 组与 interrupted 成员 Apply 拒绝。原有状态转换、未知来源、Revision 修改导致旧 Digest 失效、冲突、Provider、删除保护全部保留。

## 命令与证据

以下每个命令最终退出码均为 0，完整命令与摘要见 [本地结果](checks.json)。

| 命令 | 通过数量 |
|---|---|
| `python3 -B scripts/test_template_evolution.py -v` | 47 |
| `python3 -B skills/sdkit-skills/scripts/manager.py validate --all` | 22 Skill，含 Catalog/Frontmatter/目录一一对应 |
| `python3 -B scripts/check_markdown_links.py` | 全仓文件/链接/锚点，无错误；数量见 JSON |
| `python3 -B -m unittest discover -s skills/sdkit-skills/scripts -p test_*.py -v` | 44 |
| `python3 -B -m unittest discover -s scripts -p test_*.py -v` | 119（含前述 47，不重复计数） |
| `git diff --check 226465e...HEAD` | 0 错误 |
| `git diff --check` | 0 错误 |
| `python3 <临时证据目录>/sensitive_check.py` | 0 命中 |

敏感检查脚本仅在本地临时目录执行；仓库内不得保留工作站绝对路径。检查本 PR 全部变更与本轮交接文件中的个人目录、真实凭据、私钥及模糊措辞；结果为零命中。该扫描不构成全仓秘密审计。

## #20/#21 联合兼容

L2：#20 与 #24 共同修改 `standards/skill-orchestration.md`；按共同祖先三方组合无冲突，模板只读规划与 Git Guardrail 两组路由保留。#21 与 #24 共同在 Catalog 末尾新增条目，存在同位置文本冲突，临时组合按唯一名称取并集并断言既有条目完全相同，保留 dbops 与 templateops。未把任何其他 PR 提交合入 #24，也未修改其分支。

仅在新临时目录组合真实 Head 的文件差异，执行结果见 [联合结果](compatibility.json)：Manager 23 Skill、全仓链接、Template Evolution 47、Git 协议 9、隔离 Git CLI 20、DBOps 11 全通过，命令退出均 0。此结果证明所述显式组合兼容，不代表 GitHub 自动合并无冲突。

## 边界和完成标准

授权记录、PR 和计划字段不能自行授予权限；授权参数必须来自可信调用方。布尔参数不是密码学认证，不能证明不受信任调用方无法伪造当前用户意图。单份计划只能检查摘要与 Revision 值，历史递增必须比对上一份可信计划。真实 Git/blob、符号链接和来源验证由调用方完成。

BLOCKED（本次禁止执行）：真实业务/模板构建与 Apply/恢复、真实 Agent 越权行为和跨 Provider 实例测试。Fixture 不代表这些能力已通过。

本地技术验收条件满足；不宣称真实升级可执行。最终 Head、普通 Push 与 Draft/Open 由最终 Provider 查询核验。原工作区与其他 Worktree 的未知修改保留；无合并、部署、Ready 切换、主动 CI 或全局工具链安装。
