# cfops V1 执行契约

- 任务 ID：cfops-v1；revision：1；日期：2026-10-20。
- 原始 Git 基线：19ca264157342e135351acbac17c1d432747c994；执行起点 main。交付分支 feat/cfops-v1-20261020。
- 已确认：用户同意提炼 Pages 静态、Nuxt Pages SSR、Worker 的发布流程；追加授权完成后提交、Push 并创建 PR，由 Skill 总控另行验收。
- 允许修改：skills/sdkit-cfops/**、catalog.json、README.md 中 cfops 的最小登记、本任务计划与 .sdkit 交接增量。
- 禁止：覆盖已有无关修改；业务项目写入、真实云部署、全局安装、数据库操作、CI 主动触发、合并 PR。
- Primary：sdkit-skills；Supporting：skill-creator（创建与脚本验证）、wrangler（命令事实核验）。命中 references：Manager workflow；cfops 自身五份 references。
- 恢复入口：本文件、任务表、实际 Git diff 与本任务测试。

## 阶段与验收

| 阶段 | 状态 | 修改范围与证据 |
|---|---|---|
| C0 目标及并发核验 | verified | 本地 main/HEAD、未知修改已读取；远端 main 等于基线；开放 PR #22 仅命中 UI Design 目录与其测试，无 cfops/Catalog/README 交集。离线代理初次失败后，受控只读联网查询成功，未触发 CI |
| C1 Skill 与脚本 | implemented | 自包含入口、五份分流 reference、示例计划与 Makefile、Python 助手、脱敏测试；新增目录与 Catalog 使用 Manager create，退出 0 |
| C1 本地验收 | verified | cfops 31 unittest、Manager/迁移 44 unittest、validate --all 24 Skill、Markdown 367 文件/1210 链接/2 锚点 0 错误、脱敏/措辞搜索与 diff 检查通过；命令均退出 0。quick_validate 因缺 PyYAML 未运行成功，使用本仓库更严格的 frontmatter/Catalog/链接校验作为等价检查；不安装额外依赖 |
| C2 交付 | verified | 3338056 提交并 Push 至 feat/cfops-v1-20261020；已创建 Draft PR #28，仅包含本任务 16 个文件。Push 前 main 与本地交付基线一致；docs/ideas 保留未提交。最终 Head 以 PR 实时读回为准 |
| C3 总控交接 | verified（交接；总控验收待执行） | Draft PR #28 描述包含本地结果、缺 PyYAML 的等价验证及真实云端/跨 Agent 未验收范围；未合并、部署或安装 |

## 变更与偏差

- D0：没有个人配置读取需求，不创建空 config；项目公共计划与本地忽略记录分开。
- D0：辅助脚本不猜测 CLI 输出里的部署 ID；Provider 实时读回由执行 Agent 完成。
- D0：框架动态配置、自定义 build hook、多配置歧义与特殊 bundle 在 V1 停止，必须先针对项目适配，禁止静默猜测。
- D2/D3：扩大到资源管理、数据库、业务配置修改、全局安装或真实发布前必须另行取得授权。

## 完成标准

仅本任务文件进入 PR；新增 Skill 静态与定向测试通过；未执行的真实 Wrangler、云端、自然语言跨 Agent 验收明确保留给总控。不混入此前工作区修改，不合并或发布。

- 并发事实：交付前其他会话已提交既有 Go 来源文档改动，main 前进到 897222188c086c1b27d76df77ed80f1d2b8c6c4b；本地 HEAD 与远端一致，原基线仍为祖先，未覆盖原有修改。该提交不含本任务文件。

交付：[Draft PR #28](https://github.com/huwenlong92/skills/pull/28)。后续交接记录提交不修改 Skill 或脚本，最终 Head 以 PR 实时结果核对。
