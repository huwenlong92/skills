# 验收交接

最后核验：2026-10-18。当前任务为 PR #18 ui-design V1 最终本地验收。

- [计划](plans/pr18-final-acceptance.md)、[报告](../docs/testing/ui-design-v1/REPORT.md)和[测试结果](../docs/testing/ui-design-v1/local-results.json)为恢复入口；先核验实际 Git/远端与证据。
- 本地 117 项 unittest、21 Skill 与 Markdown 链接/锚点检查通过；范围内修复已单独提交，验收证据另行提交并普通 Push。
- 整体 BLOCKED：独立 Codex Home 无认证。模型调用 0，U01–U12 均未执行；不得将准备输入或离线契约测试认作模型行为通过。
- 恢复需不复制真实认证文件的已授权认证机制，以及实际只读文件边界、宿主 Skill/插件隔离预检；随后执行全部真实场景、三类交接并保存实际 Skill 加载证据。
- 保持 Draft/Open；不合并、不切换 Ready、不部署、不主动触发 CI。最终完整 SHA、Push 和 mergeable 以实时核验为准。
- 不动其他 Worktree、未知文件、真实业务与全局配置；#14–#17 未混入，未来合并前重新核验冲突与语义兼容。

历史 #13 的计划、报告与证据保留，不覆盖其原始基线。
