# 专题 A 授权最终 Squash Merge 契约

适用范围：PR #16 → #15 → #14 严格依次 Ready、Squash Merge 与合并后验证。任务 ID topic-a-authorized-squash，revision 1；原始 main 基线 8c049239ef90a6b4215ba425cef439168cb43dd2。

- 用户本轮已明确授权安全核验、必要同步修复/普通 Commit/Push、Ready、锁定 Head 的 Squash Merge 及合并后验证；此前“本地禁止合并”只适用于历史轮次，不限制本轮当前明确授权。
- 只处理三个目标 PR；禁止其他 PR 合并、Force Push/Rebase/Reset Hard、保护规则修改、主动 CI、部署、真实全局配置/Skill 安装/业务或旧规范库写入。
- 命中根 AGENTS、sdkit-skills/workflow、Project Collaboration、Collaboration Awareness、Orchestration、Development Execution 及各 PR 既有命中 Reference。范围为必要状态冲突、定向修复和本轮验收资料；不扩展架构。发生无法解决的语义冲突或测试失败立即停止后续合并，D2/D3 不越权扩围。
- 每阶段检查 Open/目标 main/Head/祖先关系、权限/保护/Rulesets、审查/必需检查/mergeable；普通 Merge 后逐项保留双方验收历史，重跑受影响检查。Ready 后再次核验 Head/门禁，再以 sha 与 merge_method=squash 请求合并。
- 只在当前 PR merged=true、Squash Commit 位于最新 main 且文件/证据完整后进入下一个；main 再次前进时重新核验和整合。

| 阶段 | 依赖与验收 | 状态 |
|---|---|---|
| S16 | 无前置；Ready/锁定 Head Squash/验证 | verified；a874524db55edae7bd7d9613b74a1d03ac6ff8b4，merged=true、main 单父与验收树一致 |
| S15 | S16 验证成功；同步最新 main/测试/Ready/Squash/验证 | verified；3c425efde5b913070dc41348630806070882c5c6，merged=true、main 单父与验收树一致 |
| S14 | S15 验证成功；同步最新 main/测试/Ready/Squash/验证 | 待完成 |
| Final | 四 PR Merged、21 Skill/16主5旧、证据与未完成审计保留 | 待完成 |

命令/退出码保存在本轮检查 JSON 与最终交付记录；GitHub 交付事实以实时查询为准。完成标准为全部目标 PR 按序 Squash Merge、最终 main 校验通过且无未授权副作用，结束后停止等待只读复核。恢复时核对真实 PR 与 Git，从首个未验收阶段继续。
