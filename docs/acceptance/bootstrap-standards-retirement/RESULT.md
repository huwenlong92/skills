# Bootstrap 本地验收

本轮不写真实全局配置、不改业务项目、不卸载 Skill。真实全局文件只读用于生成脱敏完整草案与内容指纹；旧规范库 73 个非 Git 文件及 Git 状态保持不变。

修复：共用配置事务、授权与 SHA 无差异门禁、符号/硬链接拒绝、倒置标记、未托管原文精确保留、持久备份/权限、中断 pending 阻断和显式恢复；修正旧名词边界误报及项目托管块内旧名无法更新的问题。修正协议中的字面反斜杠换行，独立 Skill 不再被假定携带根 standards/。

完整推荐全局草案在 standards/codex-global-AGENTS.recommended.md；它提议退出旧库日常入口，但不会被工具自动套用。自动工具只维护自己的有界区块，原七个用户区块不删不排不改。根 AGENTS 的协议链接通过全仓检查。

隔离集成回归：Bootstrap 35、工程协议 17、Manager/迁移 44、DockerOps 41、链接单测 7，全通过，退出码均为 0；validate 20 Skill。完整命令与结果在同目录 local-regression.json。原生 skills/list 实际发现主入口 15/15、兼容入口 5/5，20 个独立安装/更新通过；不等于模型已遵守全局协议。可从仓库运行 `python3 scripts/check_project_skill_discovery.py --output <temporary-summary.json>` 复验。

模型路由探针 BLOCKED：只使用公开 Skill、虚构需求和隔离 Home，只读 sandbox；45 秒未完成，未绕过审批或复制真实认证，未虚报隐式选择成功。

已知边界：flock 仅约束合作写入者，外部编辑器可能在最终检查与 replace 之间竞争，维护期间必须停止其他写入；本工具不承诺对恶意并发写入的原子 CAS。中断 journal 必须先人工检查，不自动回滚。旧 UI/原型协议缺口属于独立迁移审计，不纳入 #14。

保持 Draft；没有合并、部署、手动触发 CI 或改真实 Codex 配置。完整迁移与真实隐式行为尚有阻塞，不能把本地静态通过等同于最终迁移完成。
