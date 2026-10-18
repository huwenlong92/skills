# DBOPS PR-B 执行契约

- Task: DBOPS-03/04
- Original main baseline: 8777b036311349fef7a99cdf094c36fd7011c15c
- Revision: r1
- Scope: sdkit-dbops Baseline/History/Snapshot/Drift 离线协议、JSON Schema、静态工具和测试
- Authorization: 独立 Draft PR、离线测试；禁止数据库连接、DDL/DML、合并、部署、主动触发 CI
- Dependencies: PR #21 已合并；PR #24 共享 Catalog 风险，本 PR 不修改 Catalog
- C0: main、PR 与目标路径已核验
- C1: 测试、Schema 和安全检查待验证
- C2: 提交前核验 Head
- C3: Draft PR 创建后回读状态
