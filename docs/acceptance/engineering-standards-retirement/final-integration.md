# PR #15 专题 A 最终集成验收

适用范围：本 PR 的最新 main 集成、定向修复及最终本地验收。初始 Head `744d022ad5680c6702c9e39354aa88184e9f606f`，main `77e0664fcbb0943f9bd4aa8cad96ab0d14fa4c3a`。普通 Merge 在独立 Worktree 完成，无文本冲突，未使用 ours/theirs、Reset Hard、Rebase 或 Force Push。

## 结果与范围

- 已从 `744d022ad5680c6702c9e39354aa88184e9f606f` 开始，包含 R027–R044 源码对账修订。原始 69 文档、409 组、覆盖统计 42 冲突/311 已覆盖/30 部分/26 缺失、35 废弃决定均保留；audit.json SHA-256 为 `314f6bed66360cc67291a28fb8f33c3cd9f5a9e7b7cdf86c2117df270b344ad6`，与原审计和本次初始 Head 逐字节一致。
- Nuxt 模板 main 已前进至 `6a23a981cc248a742a8521a04da9f466ad0cc25e`。只读归档检查 Nuxt 4.5.2、core runtimeConfig、templates/themes、Pinia 两处 storesDirs、request 上下文、i18n/SEO/realtime 与 routeRules；未把新 main 当作业务项目已升级。五组模板测试在归档中实际执行 **36/36、退出 0**，见 [本轮模板测试](final-template-tests.json)；依赖复用既有临时缓存（Nuxt 4.5.2 / TypeScript 5.9.3 / Pinia 4.0.3），未安装或更改业务依赖。没有执行生产 build/typecheck/浏览器或真实 R2 测试。
- D1 修复两处冲突：config/env 的本地 API 配置统一为实际 runtimeConfig.public.apiBase 对应的 NUXT_PUBLIC_API_BASE，旧 APP_API_BASE 仅在明确旧版构建输入时允许；core layer 表格不再把可切换配色全部归入 core assets，链接到独立 themes layer 权威规则。两套入口同步；主入口描述与路由语义不变。
- 平台 Binding/R2 只是接入门禁，不声称本模板已经接入。SSR 数据/Cookie、用户身份与 payload 隔离保留；page meta 的菜单生成只按实际消费者启用，不把保留类型当作已实现。
- 18 组 UI/原型规则中，R027–R035、R037–R040 共 13 组仅“规范归属可关闭”，不等于跨系统端到端通过；R036 数据职责逐栈对账待补；R041 模块级 Latest 消费待验证；R042 版本化页面导航 Schema 仍阻塞；R043 消息安全仍部分通过；R044 发布/浏览器端到端仍部分通过。原增量结论全文保留，未因静态测试将其升级。
- 纯设计由 sdkit-ui-design，产品/原型交付由 Foundry，正式 Nuxt 实现由技术栈 Skill；未复制 18 组规则或修改 Content Engine、Prototype Runtime、UI 仓库。旧规范库尚不具备删除条件。没有无法安全解决的合并冲突。


本轮核心回归共 **118 个 unittest**，全部通过；21 Skill 校验和 Markdown 相对链接/锚点零错误。命令输出与数量见 [最终检查](final-integration-checks.json)。

| 命令 | 数量 | 退出码 |
|---|---:|---:|
| `python3 -m unittest discover -s scripts -p test_engineering_protocols.py -v` | 17 | 0 |
| `python3 -m unittest discover -s skills/sdkit-skills/scripts -p test_*.py -v` | 44 | 0 |
| `python3 -m unittest discover -s skills/dockerops/scripts -p test_*.py -v` | 41 | 0 |
| `python3 -m unittest discover -s scripts -p test_markdown_links.py -v` | 7 | 0 |
| `python3 -m unittest discover -s scripts -p test_ui_design.py -v` | 9 | 0 |
| `python3 skills/sdkit-skills/scripts/manager.py validate --all` | 静态检查 | 0 |
| `python3 scripts/check_markdown_links.py` | 静态检查 | 0 |
| `git diff --check` | 静态检查 | 0 |

[兼容性记录](final-integration-compatibility.json)：历史验收资料 5 文件逐字节保留。详细 Reference 除新旧身份说明 repository.md 外一致；main 中知识/UI/编排/开发执行入口不变。路由语义无实质变化，复用 main 已有 T01–T10、U01–U12 与知识 16 场景的适用证据；旧迁移探针 BLOCKED 历史仍保留，本轮模型调用 0，不将静态与原生发现冒充模型重测。

## Git 与权限

- 开始核验：main 未保护，适用规则集为空，当前账号具有 Push 权限；四个目标 PR 为 Draft/Open、MERGEABLE/CLEAN，其他三个相关分支未混入本 PR。GitHub 分支/Head/权限状态均为按需快照，不能代替最终实时核验。
- Push 前必须核验 main、目标 Head 与相关开放 PR；未预期前进时停止覆盖。普通 Commit/Push 后保持 Draft/Open；最终 Head、Merge Commit 和 mergeable 以交付时 GitHub 查询及最终回复为准。
- 未合并 PR、Ready、部署或主动 CI；未修改真实全局 AGENTS、已安装 Skill、业务仓库或旧规范库。原工作区未知文件和其他 Worktree 保留。

## 完成标准与未完成边界

本地指定门禁、兼容性、历史证据保留和源码一致性核验通过。当前源码具备本 PR 范围的技术合并准备条件；不代表真实业务构建/浏览器/数据库验收、跨 Agent 全量路由或旧规范库删除已通过。后续真实配置整理、安装更新、合并及删除均须单独授权。

交付核验：普通集成提交 `d99cc23a0903b5ae5ff94ad9580978deb050635f` 已 Push，GitHub Draft/Open、MERGEABLE/CLEAN，main 未前进。详见同目录 final-delivery.json；随后仅补记交接，最终 Head 以最后查询为准。
