# PR #28 最终本地验收

适用范围：本轮命名迁移、真实本地 CLI、隔离安装及行为验收；不改变初版历史证据。

- ID：pr28-final-local；revision：1；原始 Head：60a5649f3624cfef57139582453e9a77615a89eb。
- 重新查询 main：897222188c086c1b27d76df77ed80f1d2b8c6c4b；PR #28 Draft/Open、MERGEABLE；开放 #22 无本任务文件交集。
- 分支：feat/cfops-v1-20261020；未知 docs/ideas/ 保留。
- 授权范围：skills/sdkit-cfops/**、旧源码目录迁移、Catalog/README/本任务引用、docs/testing/sdkit-cfops-v1/** 和 .sdkit/ 最小交接；普通 Commit/Push、更新 PR 标题说明。
- 禁止：其他 Skill 改名、真实业务/全局配置写入、真实 Cloudflare 登录或 Token、部署/资源/数据/DNS/Access/CI 写入、Ready/Merge、强推、清理未知文件。
- Primary：sdkit-skills；Supporting：skill-creator、wrangler（仅本地 CLI）、openai-docs（Codex 隔离与发现）；所有命中的本 Skill references 已读取。

| 阶段 | 状态 | 验收条件 |
|---|---|---|
| 预检 | verified | 实时远端 SHA 与工作区符合上述记录 |
| 命名 | verified | 唯一新目录/frontmatter/Catalog；cfops.py 与项目 release.json 协议不变；无旧源码路径失效引用 |
| CLI 与负例 | verified | 已有锁定依赖，隔离 HOME/环境，无真实凭据；真实 dry-run/本地预览与帮助参数证据分别记录；假 CLI 安全负例通过 |
| 独立安装/模型 | 安装/原生发现 verified；模型 BLOCKED | 隔离安装更新；六场景独立证据；缺认证或服务记 BLOCKED，不复制全局认证 |
| 回归交付 | 本地 verified；普通提交交付按 PR 读回 | 定向测试、Manager、validate、链接/锚点、diff 与脱敏；普通 Commit/Push，读回 Draft/Head/mergeable |

偏差仅允许本 PR 内 D0/D1 修复。真实模型阻塞不影响本地检查与范围内修复的普通提交；不得据此宣称最终行为验收全部通过。恢复先核对本文件、报告及实际 Git/远端。

完成标准：提交脱敏结果及明确分层报告；任何 BLOCKED 保留；保持 Draft 并停止，等待总控。

证据：[最终本地报告](../../docs/testing/sdkit-cfops-v1/REPORT.md)。真实 CLI/助手与边界 16 PASS；专项 41 PASS；独立安装更新及 Codex 原生发现通过。隔离认证预检 exit 1 / Not logged in，C01–C06 全部 BLOCKED，未调用模型，不宣称行为验收通过。已修正 Pages --config 不兼容、动态配置和构建隐式写入门禁；初轮失败保留。
