# 任务

- range-skill-closeout-20261022 | safe main sync verified; template RANGE usage reference and 61 offline tests verified; Draft delivery authorized, final state per GitHub | codex/sdbase-go-range-skill-20261022 | [计划](plans/range-skill-closeout-20261022.md)

| ID | 状态 | 负责分支 | 计划 |
|---|---|---|---|
| pr13-final-acceptance | verified | feat/engineering-orchestration-execution-v1-20261018 / PR #13 | [验收计划](plans/pr13-final-acceptance.md) |
| pr13-codex-behavior | verified | feat/engineering-orchestration-execution-v1-20261018 / PR #13 | [真实行为验收](plans/pr13-codex-behavior.md) |
| pr13-final-integration | verified | feat/engineering-orchestration-execution-v1-20261018 / PR #13 | [最终集成验收](plans/pr13-final-integration.md) |
| pr18-final-acceptance | verified（本地与真实模型验收通过） | feat/ui-design-v1 / PR #18 | [最终本地验收](plans/pr18-final-acceptance.md) |
| pr19-local-acceptance | verified | feat/knowledge-retrieval-capture-v1 / PR #19 | [验收计划](plans/pr19-local-acceptance.md) |
| pr18-final-integration | verified | feat/ui-design-v1 / PR #18 | [最终集成](plans/pr18-final-integration.md) |
| pr14-topic-a-final | verified | feat/project-skill-bootstrap-v1 / PR #14 | [最终集成](plans/pr14-topic-a-final.md) |
| pr15-topic-a-final | verified | audit/engineering-standards-retirement-20261018 / PR #15 | [最终集成](plans/pr15-topic-a-final.md) |
| pr16-topic-a-final | verified | docs/vab-standards-retirement-20261018 / PR #16 | [最终集成](plans/pr16-topic-a-final.md) |
| pr17-topic-a-final | verified | docs/go-standards-retirement-20261018 / PR #17 | [最终集成](plans/pr17-topic-a-final.md) |
| topic-a-authorized-squash | in_progress（#16/#15已合并，#14最终门禁） | feat/project-skill-bootstrap-v1 / PR #14 | [执行契约](plans/topic-a-authorized-squash.md) |

| pr20-final-integration | verified（真实 Agent 16 PASS；保持 Draft） | feat/git-collaboration-v1-20261018 / PR #20 | [计划](plans/pr20-final-integration.md) |

| pr24-final-local | verified（本地协议） | feat/template-evolution-v1 / PR #24 | [计划](plans/pr24-final-local.md) |

| pr24-main-sync | verified（本地回归） | feat/template-evolution-v1 / PR #24 | [同步计划](plans/pr24-main-sync.md) |

| cfops-v1 | verified（本地与 PR 交付；待总控验收） | feat/cfops-v1-20261020 / PR #28 | [计划](plans/cfops-v1.md) |

| pr28-final-local | implemented（本地通过；6 模型 BLOCKED；交付按 PR 读回） | feat/cfops-v1-20261020 / PR #28 | [验收计划](plans/pr28-final-local.md) |

- range-maintenance-v1-20261021 | local sdkit-dbops reference/links/tests verified; paired Go PostgreSQL acceptance complete; Git delivery explicitly authorized on 2026-10-22; final state per GitHub | codex/range-maintenance-v1-20261021 | [计划](plans/range-maintenance-v1-20261021.md)

## RANGE Retention V1.1（2026-10-22）

独立分支codex/range-retention-v11-20261022，预建daily/清理monthly、12/6/12个月delete/keep、单一共享SQL及首次启用门禁。只在本轮新建数据库验证，不清理原验收数据、不安装Skill。进度与验收见[计划](plans/range-retention-v11-20261022.md)，最终Git交付以实时结果为准。
