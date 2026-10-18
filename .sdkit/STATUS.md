# 已核验状态

最后核验：2026-10-18，PR #18 最终集成本地验收通过。main `f1df67a6ff070fd4991a16e6135bf3902ee3e0da`，集成前 Head `ad8914562ebf2b9228c43b35b4f8383414609234`。#19 已合并；以下历史快照中的未合入、未来冲突和旧 main 仅指当时状态。

恢复入口：[集成计划](plans/pr18-final-integration.md)。[集成报告](../docs/testing/ui-design-v1/final-integration.md)：5 个文本冲突已逐项解决，Orchestration 联合审查通过；195 unittest、21 Skill 与全仓相对链接/锚点检查通过。双方证据逐字节保留，路由语义不变，复用 U01–U12/#19 既有模型证据，本轮模型调用 0。普通 Merge Commit `566d727e4a94c099b64efbdddf091028a308c91e` 已 Push；GitHub 核验 main 未变、#18 Draft/Open、MERGEABLE/CLEAN。后续交接记录提交不改路由或测试源码，最终 Head 由最终远端核验返回。保持 Draft，不合并、不部署、不主动 CI。

## PR #18 集成前历史快照

最后核验：2026-10-18，PR #18 sdkit-ui-design V1 最终真实模型验收。

- [报告](../docs/testing/ui-design-v1/REPORT.md)及[行为汇总](../docs/testing/ui-design-v1/behavior-results.json)：U01–U12 最终 12 PASS / 0 FAIL / 0 BLOCKED，U05 已有图片/纯文字/外层真实图片工具三类交接通过。
- 本轮 18 次独立 Codex 运行全部模型完成、CLI 退出 0，另有真实 image_gen 1 次。首次无认证阻塞、离线隔离问题、传输回退、夹具歧义/缺失与修正重测全部保留；不以静态测试代替原生加载行为。
- 21 Skill、118 个本地 unittest、全仓 Markdown 相对链接/锚点的最终数量与退出码见报告及 resumed-local-results.json。
- main 8b22285aa2abba995e88f49718800c167c7e2413；本轮测试 Skill 源码 Head 5bb812edb747d1afc716c12f25a7a776cb66c8cd。原始验收基线仍为 5983179b279dcc8c75b62c43bb19962c6580e316。main 已为祖先。
- 历史修复 f3a5716c7b3db16edbf788d8afc2a17f276b17c8 与 4e923c9f756c215bc643c067f78cd29c27e57eb0；普通 Merge 保留并行 sdkit-ui-design 命名；本轮未追加 Skill 代码修改。
- #14–#17 未混入；新 #19 在 Foundry/Orchestration 为 L2，未合入或覆盖。本轮不宣称未来联合合并状态已验证。
- 达到本轮受控技术验收条件；最终 Head、Push、Draft/Open、mergeable 以实时 GitHub 为准。无合并、Ready、部署、主动 CI 或真实配置/Skill/业务改动。
- 本轮完成后停止，等待最终合并授权；真实业务构建/API/部署、完整宿主 Skill 和跨 Agent 不在已验证范围。历史 #13 与首轮 #18 证据保留。

## main 中既有验收历史快照

最后核验：2026-10-18，PR #13 最终集成验收。

- PR #12 已合并到 main 444b7da7b786ff78864f22a3210a8ddcc0bf0597。从 #13 Head 032197e89fa8b0bc1752ab70bd5db6dd07906c7a 普通 Merge main，生成 a3ea32f501ecedaf82739bb7c192c4ee09da928a，无冲突；main 已为祖先，保留历史。
- [最终集成报告](../docs/testing/engineering-v1/2026-10-18-integration-report.md)：Catalog/frontmatter/目录 20/20；临时独立安装/更新 20/20；Codex 本地发现主入口/其他 15 和旧兼容 5；无模型调用、无全局安装修改。
- 协议 17、Manager/迁移 44（37+7）、DockerOps 41、Markdown 工具 7，共 109 个 unittest 通过；validate 20，所有命令退出 0。全仓相对链接与两个本地锚点通过。
- AGENTS、两份核心协议、既有真实行为报告/逐项证据整合前后逐字节未变；复用 [T01–T10 证据](../docs/testing/engineering-v1/2026-10-18-report.md)，不重复模型测试。静态选路无实质变化或未解决协议冲突。
- 限制：Foundry 附属 README 保留既有源仓库根 README 导航，独立安装后该导航不可用；不是新的执行依赖，未改动已合并 Skill。本地发现不等同于自然语言自动选择已重新实测。
- 本轮技术验收通过；保持 Draft/Open，最终交付 Head/mergeable 以实时 PR 核验为准。没有合并、Ready 切换、部署或主动触发 Actions；完成后等待最终合并授权。

## PR #19 本地验收（2026-10-18）

16 项真实行为最终通过；首轮 15/16 的正文重复读取缺陷修复后，7/13/16 功能重测通过，C13 另以逐轮核验的可写沙箱补测通过。20 Skill、44+24 单元测试和全仓 Markdown 最终复核以 [本次报告](../docs/testing/knowledge-v1/REPORT.md) 与 [结果](../docs/testing/knowledge-v1/results.json) 为准。仅测试虚构资料，无真实产品/Wiki 写入。本地验收 verified；提交前远端 Head/main 未变化，#19 Draft/Open、MERGEABLE/CLEAN。Commit/Push 最终结果以远端和本轮最终回复为准。
