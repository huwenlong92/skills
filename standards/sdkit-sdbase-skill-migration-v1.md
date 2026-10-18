# SDKit / SDBase 开发 Skill 迁移 V1

> 状态：Draft PR 已完成主入口迁移，保留旧名称兼容；本文件描述当前仓库状态，不代表用户已安装或业务项目已升级。

## 分类与目标

| 旧 Skill | 目标 Skill | 分类 | 目标源码 |
| --- | --- | --- | --- |
| sdkit | sdkit-go-core | framework | huwenlong92/sdkit |
| rust-sdcore | sdkit-rust-core | framework | 实际 sdcore 依赖/checkout |
| sdkitgo | sdbase-go | template | huwenlong92/sdbase-go |
| vab-admin | sdbase-vab-admin | template | huwenlong92/sdbase-vab-admin |
| nuxtjs | sdbase-nuxtjs-portal | template | huwenlong92/sdbase-nuxtjs-portal |
| （新增） | sdbase-lite | template | huwenlong92/sdbase-lite |
| （新增） | sdbase-admin-lite | template | huwenlong92/sdbase-admin-lite |
| （新增） | sdbase-flutter-app | template | huwenlong92/sdbase-flutter-app |

## 迁移门禁

1. 每个目标 Skill 先读取实际模板的 README、TEMPLATE、AGENTS、依赖与目录，再迁移；不能根据名字推定兼容。
2. 新旧目录共存期间，新名称是正常开发主入口；旧名称仅用于明确指定的历史安装、兼容检查或迁移。禁止在同一 Agent 安装范围同时安装同职责的新旧 Skill；不得用删除旧源码目录完成切换。
3. 迁移前搜索仓库 README、Catalog、所有 references、安装命令和其他 Skill 对旧名称的引用；本地 Codex 安装属于用户环境，不能通过仓库修改冒充完成。
4. 目标 Skill 的 frontmatter name 与目录一致，references 链接完整，独立安装可用；项目根 AGENTS 的明确规则优先。
5. sdbase-lite 不继承完整版 PostgreSQL、多服务空壳；sdbase-admin-lite 不继承 Vab 动态菜单、RBAC 和目录结构。
6. 本阶段不修改六个模板仓库，不改其 AGENTS，不自动创建 .sdkit/；跨会话状态感知另按统一协议评估。
7. 切换阶段必须单独核对旧 Skill 安装来源和项目引用；在用户批准删除旧入口前不得移除旧目录。
8. 每阶段检查 Catalog/目录一致、全部 Skill frontmatter、相对链接和必要本地测试；不自动提交、合并、部署或主动触发高成本 CI。

## 分阶段执行

- A：审计五个旧 Skill 与六个模板的真实兼容性、触发边界、旧名称引用。
- B：新增三个独立 Lite/Flutter Skill，完善 references 与验证。
- C：迁移五个既有 Skill 到新命名，保留旧入口与清晰的过渡触发策略。
- D：使用临时隔离目录验证安装、更新和 Codex 发现；不得修改用户现有全局安装。自动选择行为必须另行实测；无法运行时报告未验证。旧目录和 Catalog 条目保留，清理另行授权。

## 验收

- 八个目标 Skill 的职责明确，所有源码和引用可追溯。
- 普通 Go、Rust、Vue 项目不会仅因语言命中 SDBase 模板 Skill。
- Lite 与完整版不混用数据库、目录、路由和认证规则。
- 新旧过渡期不覆盖用户本地 Skill，无法确认的自动选择冲突必须停止切换。
