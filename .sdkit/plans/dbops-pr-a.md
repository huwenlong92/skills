# DBOPS PR-A 执行契约

- Task: DBOPS-01/02
- Original main baseline: 8c049239ef90a6b4215ba425cef439168cb43dd2
- Revision: r2
- Scope: 新增 skills/sdkit-dbops/、Catalog 登记和本计划；不修改 sdenv、sdbase-go 或数据库
- Authorization: 仅开发、静态测试、独立分支和 Draft PR；禁止合并、部署、主动触发高成本 CI 或数据库连接
- Dependencies: PR #14 Bootstrap、PR #20 Git Collaboration 规则按需核对，不覆盖其文件
- C0: main/PR/Catalog/目录占用已只读核验
- C1: 本地 Codex 已执行 86 项原有单测、Skill Manager 和链接检查；新增兄弟方言符号链接拒绝测试待重验
- C2: 提交前重新核验远端分支与 PR
- C3: Draft PR 创建后核验 Head、变更文件和测试证据
- Deferred: YAML 解析、真实 History、Snapshot、Provider、数据库连接与 Migration 执行均不在 PR-A
