# Engineering Standards → Agent Skills 迁移记录

> 状态：整理中。本文用于在新会话中继续迁移；完成全部验收后再决定保留、归档或删除。

## 目标

把原共享规范库中的工程约定迁移为可通过 Git 安装和升级的独立 Agent Skills。重点不是复制文档或编写框架 API 手册，而是提炼用户认可的 opinionated 代码习惯，让 Codex、Claude Code、Kimi Code CLI 和 DeepSeek Harness（DSH）能够理解、模仿并验证同一套写法。

目标仓库：当前仓库（`.`）

素材来源：同级旧规范仓库（`../engineering-standards`）

## 已确定的仓库模型

- 不发布 npm 包；仓库本身遵循通用 Agent Skills 结构。
- 使用 `pnpx skills add huwenlong92/skills ...` 从 GitHub 安装和更新。
- 按技术栈拆成独立 skill，不建立包含所有语言规范的单一巨型 skill。
- `SKILL.md` 只负责触发、分流、执行顺序和共同门禁。
- 具体代码习惯全部写在 `references/`，并按修改场景渐进加载。
- 涉及代码形态的 reference 同时包含决策条件、脱敏正向示例、必要反例和完成检查；只写边界或禁止项不算完成。
- 历史项目代码只作为候选习惯的证据；与用户已确认偏好冲突的历史写法不得进入规范。
- 不加个人名字或个人署名；仓库定位为 opinionated SDKit 工程约定。

当前 skill 划分：

1. `sdkit`
2. `sdkitgo`
3. `vab-admin`
4. `nuxtjs`
5. `rust-sdcore`
6. `npm-package`
7. `software-installation-docs`

## Reference 写作标准

每个 reference 都必须是 agent 可以直接执行的规范：

1. 明确适用范围；说明哪些修改必须读取。
2. 固定代码习惯使用“必须”“禁止”。
3. 仅在确实存在两个合法方案时使用条件分支，并给出唯一、可观察的判定条件。
4. “优先”必须同时写出何时允许使用次选方案。
5. 同时写明允许的文件落点和禁止的落点。
6. 不出现工作站绝对路径；共享依赖从项目依赖声明、workspace、仓库说明或用户输入解析。
7. 不把具体业务项目清单、临时决定、真实凭据或机器状态写成共享规范。
8. 每项可执行修改给出验收命令或人工核对对象。
9. 同一 skill 中只能有一处权威规则；其他 reference 链接它，不能复制出不同版本。
10. 存量代码与 skill 不一致时，新代码和本次修改按 skill 执行，但不顺带重构无关历史代码。

规则优先级：当前用户明确要求 > 目标项目显式规则 > 本仓库 skill > 目标项目历史写法。

## 当前完成度

已完成：

- 建立根 `README.md` 和仓库维护规则 `AGENTS.md`。
- 为七个技术栈建立独立 `SKILL.md` 和分流表。
- `sdkit` 与 `sdkitgo` 已分离：前者只约束 Go sdkit 框架自身的 `core/`、`pkg/`、facade、driver 和 runtime；后者只约束使用 sdkitgo 的业务项目。
- Skill 已统一命名为 `sdkit`、`sdkitgo`、`vab-admin`、`nuxtjs`、`rust-sdcore`、`npm-package`、`software-installation-docs`，目录名与 frontmatter `name` 一致。
- 七个 `SKILL.md` 使用中文说明；代码标识符、路径、命令和协议名保留英文。
- 将旧规范复制为迁移素材，保留原来的主题拆分。
- 删除 `npm-package/references/README.md`；其分流职责已由 `SKILL.md` 接管。
- 第一轮消除工作站绝对路径。
- 明确 core/Vab/shared package 的源码位置必须从目标项目解析，不能写死目录。
- `sdkitgo` 已完成第一轮精度审计：补齐每份 reference 的适用范围和完成标准，收敛 handler/projection、model/migration、config/provider 的重复权威规则，并消除无条件模糊措辞。
- 已确认 reference 不只负责边界门禁，还必须让 agent 学会实际代码习惯；`service/handler.md` 已补充“直接查表、禁止单调用方小方法”的决策表、虚构正反示例和候选扫描命令。
- `sdkitgo/references` 已按实际修改区域建立目录，例如 `service/handler.md`、`service/router.md`、`models/base.md`、`models/struct.md`、`worker/handler.md`、`crontab/handler.md` 和 `realtime/events.md`。
- `sdkit` 已建立 `architecture/core-vs-pkg.md`、`core/framework.md` 和 `pkg/library.md` 草稿，用于继续讨论框架能力、独立 library 与业务项目代码的归属。
- `sdkit` 与 `sdkitgo` 的每份 reference 都具有独立 `name` 和 `description` frontmatter，正文继续负责适用范围、确定性规则、虚构示例和验收。
- 新增 `http/foundation.md`，固定 `app/http/form`、`app/http/response`、`app/http/validator` 的职责以及与 handler、middleware、infra、core 的边界。
- 新增 `http/validator.md`，固定统一 binding 入口、自定义 tag 准入条件、纯函数边界、翻译和正向写法。
- 新增 `service/creation.md`，列明新增 `app/{service}` 时必须同步创建或修改的 app、cmd、service config、instances 和 `cmd/serve` 入口。
- `service/handler.md` 已加入一级业务模块目录、同资源 CRUD 同文件、直接 GORM list/options/常量接口的正向形态。
- `database/query.md` 与 `database/projection.md` 已统一关联展示规则：默认使用 `{author:{id,name}, category:{id,name}, ...resourceFields}` 形式的嵌套 JSON object/array；只有既有公开兼容契约或用户明确指定的特殊场景才允许保留扁平字段。
- `database/projection.md` 已补齐 PostgreSQL 直接构造 JSON 的写法：单对象使用 `datatypes.JSONMap + jsonb_build_object`，对象数组使用 `datatypes.JSON + jsonb_agg`，完整树允许由 CTE 直接输出 JSON；detail 中多个独立一对多集合分别查询，禁止硬 Join 成笛卡尔积，也禁止查询后用 Go `for range` 补关联或组装 JSON。
- `service/router.md` 已按逐层 `Group`、相对 path、中间件继承和集中可见路由树重写。
- `service/write-handler.md` 已固定 create/update/delete 直接使用 GORM、transaction 边界和 commit 后 realtime 通知。
- `service/handler.md` 已补齐 `GetXxxDetail` 的完整形态：匿名 query request、局部 projection、权限范围进入查询、`Select + Take`、独立处理 `gorm.ErrRecordNotFound`，关联展示继续由 PostgreSQL 直接构造。
- 新增 `service/action-handler.md`，固定 enable、disable、approve、reject、reset、assign 和 batch 等非 CRUD 动作直接写 handler，并明确并发状态条件、集合式写入、transaction 和 commit 后副作用。
- 新增 `http/form.md`，固定 `PageRequest`、`ListRequest`、`SortRequest` 和 allowlist 排序；客户端字段不得直接拼接 SQL。
- `models/struct.md` 已明确 model 文件禁止访问全局 DB、定义普通查询/CRUD/业务方法；model 只保留表声明、常量、`TableName`、`BeforeCreate` 和受限的分区 helper。
- `models/base.md` 与 `models/struct.md` 已拆分；struct 规则固定字段 comment、简化表名与字段名、禁止数据库外键和 GORM association。
- `models/base.md` 已确认新业务持久化表默认使用 `BaseFullModel`；只有 view、外部表、任务范围外的既有 schema 或固定基础设施契约形成明确冲突时才向用户确认，AI 不得自行改用 `BaseModel`。
- `models/hooks.md` 已按实际代码习惯收口为只推荐 `BeforeCreate`，用于创建时标识、默认值、当前 row 归一化和行内校验；`BeforeSave`、`AfterSave` 等其他 lifecycle hook 不列入常规写法，未经用户当前任务明确指定不得新增。
- `worker/handler.md` 已确认简单任务逻辑直接写在 handler；只有存在独立失败处理、资源生命周期、transaction、重试或测试边界的复杂阶段才允许拆 private helper，禁止一对一转发 wrapper。
- `crontab/handler.md` 已固定领域目录、template/run handler 同文件、两层显式注册、直接任务逻辑和禁止单任务小方法。
- `realtime/events.md` 已固定事件分散归属、gateway 集中聚合，以及 `Push`、`Broadcast`、`Notify` 的错误语义。
- `realtime/events.md` 已根据实际 service 组织补齐文件落点：service 私有 definition 与 publisher 放 `app/{service}/infra/realtime`，跨 service contract 与 subject helper 放 `app/infra/realtime`，gateway 只在 `app/realtime/events.go` 集中聚合；正向示例已使用虚构 service 和资源脱敏重写。
- 新增 `service/auth.md` 和 `service/middleware.md`：auth 只负责 service 身份契约、Session 映射和 identity helper；middleware 负责可复用请求门禁、统一 abort 和 context 输出，接口专属业务检查仍留在 handler。
- 新增 `service/server.md`，固定 `NewServerWithContext`、Start、Shutdown、构造失败清理和资源所有权；Server 只能关闭自身创建的资源，不能关闭 runtime 注入 capability。
- 新增 `infra/capability.md`，区分 core facade 薄 adapter 与项目业务 capability，固定 `UseConfigFile`、container bind、`FromServiceContext` 和 dependency/ownership，并禁止包级 `defaultService`。
- 测试位置已确认统一使用根目录 `tests/`；生产代码目录禁止出现 `_test.go`，新增测试使用外部 test package 并优先进入已有对应测试目录。
- 新增 `service/excel.md`，先固定 Excel 导入导出的 handler 落点、同步上限、临时文件清理、批量写入和 worker 分流；具体 workbook 模板与字段等待实际实现成熟后再补充。
- 第二轮 `sdkitgo` 审计同时参考了原始手写项目、框架模板和较新业务项目；素材只用于交叉验证，`BeforeSave`、GORM association、model 全局 DB helper、客户端排序直拼 SQL、包级 capability default 和手动散落 transaction 等早期写法明确不进入新规范。
- `sdkitgo` 的框架判断已收口到 `framework/boundary.md`：业务项目只负责判断留在 handler/infra 还是上提 sdkit；上提后继续区分 `core/` 与 `pkg/` 候选。
- `framework/boundary.md` 已补齐 wrapper、业务 adapter、runtime capability、driver 和 runtime adapter 的可观察行为与唯一落点；`runtime.Adapter` 不再与普通业务 adapter 混用。
- 新增 `code/imports.md`，固定 Go import 默认不使用显式别名；只有真实同名冲突、package 声明名差异或当前 package 名冲突时才允许最短语义别名，dot import 与隐式注册也已收口。
- `infra/placement.md` 已明确 `app/infra` 不是默认业务层或工具箱，只允许跨运行入口的稳定业务不变量、项目接口实现、runtime capability wiring 和集中注册契约；代码较长、多个 handler 调用或目录命名不能证明归属。
- 根据真实项目中的格式校验、值转换、通用机制、runtime 状态和 model 创建逻辑案例，已提炼为通用边界：HTTP custom tag 只返回校验结果，canonical value 由 handler 显式取得；可独立机制归 `pkg/`，配置与生命周期归 capability/core，业务常量与 model 创建契约留在项目所属位置。
- `models/hooks.md` 已明确单 model 的创建时标识、前缀和默认值直接写在对应 model 的 `BeforeCreate`；只为共享少量生成代码不得建立项目级 infra 注册表。具体标识格式必须沿用目标项目契约，不把参考项目的格式固化进 skill。
- 本轮真实代码只作为归纳依据；已明确禁止把现存目录逐项整理成 bug list，或把某个项目的 package、注册表与标识格式原样迁入 skill。
- 所有新增示例均改用虚构 catalog/resource 领域；真实项目的表名、schema、事件、权限、route 和业务文案不得进入共享 reference。
- 已在 `.agents/skills/` 创建指向 `skills/sdkit` 与 `skills/sdkitgo` 的项目级符号链接，用于当前仓库测试；未安装到全局 agent 目录。
- `sdkitgo` 已通过 frontmatter、全仓 Markdown 相对链接、代码围栏、绝对路径、模糊措辞和 reference 完成标准的等价校验。
- `vab-admin` 已完成 reference 精度审计：新增 `structure/directories.md`，统一 `src/views`、`src/api`、`src/components`、`src/plugins/App*`、store、composable、utils、styles、router 与 `library` 的职责，禁止为单次需求新增同义分层。
- `vab-admin` 已统一页面与组件模型：路由页面使用短 kebab-case 目录加 `index.vue`，页面入口保留查询、主数据和刷新编排；独立表单、抽屉、详情、上传和状态动作按状态边界拆分，禁止用完整 `XxxPage` 或 `XxxView` 隐藏复杂页面。
- `vab-admin` 的组件调用范围、目录、短命名、`reload` 事件和提升门禁以 `components/placement.md` 为唯一权威；`code/page.md`、`code/base.md` 和 `workflow.md` 已改为引用该规则，旧的重复表述已删除。
- Vab Admin 与 Nuxt.js 的 options 规则已拆成三处唯一权威：`components/business-options.md` 只判定固定枚举、远端注册表和关联展示模型；`components/enum-components.md` 约束固定枚举组件；`components/remote-options.md` 约束远端注册表组件与 store。
- 固定枚举组件已按同一协议收口：单一 `options.ts` 导出 `Value`、`Option`、`options` 和 `label()`；展示入口复用 `useStatusRender` 并支持 tag/link/text；select/radio/checkbox 共用同一 options 和 `v-model:value`，特殊 icon mode 只能留在当前枚举组件。
- 远端注册表组件已按同一协议收口：版本化 API → 短业务域 Pinia store → 语义展示/输入组件 → 页面。Store 必须使用独立 loaded/loading、模块级 pending、cache-first fetch、显式 refresh 和参数 key；有效空列表不能重复请求，维护成功后必须刷新缓存。
- Nuxt.js 已确认存在 Pinia 聚合 options、pending 去重、hydrate/ensure/refresh/clear 等同类实现；新规范在共同协议上补充 SSR hydrate 边界，普通交互 options 不得自动提升为 SSR bootstrap。
- `nuxtjs` 已完成 reference 精度审计并新增 `structure/directories.md`，固定 `layers/core`、`src/pages`、`src/modules`、`src/components`、API、store、composable、config、layout、plugin、assets、public 和 server 的职责与禁止内容。
- Nuxt 页面所有权冲突已解决：`src/pages` 默认直接拥有 route meta、主数据、页面级状态和业务区块组合；只有至少两个真实路由复用完全相同流程，并且只在 meta、访问角色或明确 context 上不同，才允许使用薄路由壳。
- Nuxt 页面私有区块放 `src/modules/<domain>/<page>/<name>/index.vue`；同业务域两个以上页面复用后才提升为 domain module，跨业务域稳定后才进入 `src/components`，满足 framework 四项门禁后才进入 `layers/core`。
- Vab Admin 与 Nuxt.js 使用一致的组件拆分原则：不以行数为阈值，而以独立业务语义、请求、表单、校验、提交、loading、empty、error 和复用范围为判定条件；简单字段和无独立状态的小片段禁止过度组件化。
- `vab-admin` 与 `nuxtjs` 的全部 references 已补齐 `name`、`description`、适用范围和 `## 验收`；当前 32 个 skill/reference 文件已通过 YAML、名称唯一性、Markdown 相对链接、代码围栏、绝对路径、真实项目词和模糊措辞的等价校验。
- 已在 `.agents/skills/` 增加指向 `skills/vab-admin` 与 `skills/nuxtjs` 的项目级符号链接；它们只用于当前仓库测试，未安装到全局 agent 目录。
- 第一轮迁移时原有六个 skill 均通过 `quick_validate.py`；新增 `sdkit` 以及本轮修改后的 `sdkitgo` 校验状态见“校验环境说明”。

尚未完成：

- `sdkit` 的 `core/` 与 `pkg/` 规则仍是讨论草稿，需要结合框架仓库的真实设计继续确认，不得视为最终稳定规范。
- 对 `rust-sdcore`、`npm-package`、`software-installation-docs` 的每一份 reference 做最终精度审计，消除无条件的“优先、建议、可以、按需、尽量、视情况、默认”等措辞。
- 给上述三个 skill 中缺少验收条件的 references 补齐完成检查。
- 合并上述三个 skill 中的重复规则，确保每条规则只有一个权威位置。
- 检查 npm 发布规范中的外部时效信息，把稳定代码习惯和需要实时核验的 npm 平台规则分开。
- 校验模板占位符和 shell 语法；frontmatter 与 Markdown 相对链接已通过检查。

## 已解决的冲突

### Nuxt `src/pages` 所有权

旧规范曾同时存在两种互斥说法：

- `src/pages` 只做 `definePageMeta` 和主体组件挂载；业务请求和主体放 `src/modules`。
- `src/pages` 直接承载当前路由的主体、请求、状态和操作；不得退化成只引入完整 `*View` 的转发层。

现已选择“页面直接拥有路由级主流程、按独立区块拆分”为权威模型，并同步重写：

- `skills/nuxtjs/references/code/page.md`
- `skills/nuxtjs/references/modules/placement.md`
- `skills/nuxtjs/references/components/placement.md`
- `skills/nuxtjs/references/ui/style.md`

保留一个受限例外：至少两个真实路由复用完全相同的流程，并且只在 meta、访问角色或明确 context 参数上不同，才允许由薄路由壳挂载共享完整流程。

## 继续工作的建议顺序

### 本轮交叉复查

本轮复查范围为 `sdkit`、`sdkitgo`、`vab-admin`、`nuxtjs`，没有扩展到其余三个 skill 的内容审计，也没有安装全局 skill 或修改业务项目。

- 统一 handler/helper 门槛：普通查询与 CRUD 内联；共享不变量或具有明确独立阶段的复杂流程允许 private helper，复杂度不自动导向 infra/capability。
- 修正框架归属判定顺序：先分机制与业务语义，再看调用范围；单调用方不能掩盖已有 core 契约缺口。普通业务 adapter 与 runtime capability 不再混用名称。
- 统一前后端 options 数组契约；修正维护后刷新复用旧 pending 的问题；pending 按 store 实例隔离，补充 SSR、清缓存和上下文切换时旧响应不得回写的检查。
- 消除简单字段与语义枚举组件、全局组件与远端 options、Nuxt 薄壳例外之间的冲突；统一 kebab-case 示例和明确的 Vue 文件导入。
- `label()` 只在真实非组件调用需要时增加；补充数字零值、空值、布尔字符串的转换边界，禁止为协议完整性创建无调用方 helper。
- 两份 remote options 示例通过 Node 执行验证：空列表缓存、并发去重、旧请求在途时维护后刷新、失败清理与重试、多个 store 实例隔离。此项不是完整 Nuxt SSR 集成测试，也不代替实际项目 typecheck。
- 72 份 Markdown 通过 frontmatter、命名、围栏、相对链接、分流覆盖、验收段落与工作站路径检查；官方 Python 校验仍因缺少 PyYAML 无法启动，未安装全局依赖。

### 后续顺序

1. 继续确认 `sdkit` 的 core/pkg 边界草稿。
2. 按 `rust-sdcore` → `npm-package` → `software-installation-docs` 的顺序继续审计 references。
3. 每完成一个 skill，运行：

   ```bash
   python3 <skill-creator-path>/scripts/quick_validate.py skills/<skill-name>
   ```

4. 全仓执行绝对路径和模糊词扫描，逐条人工判定；不能为了让扫描归零而机械替换句子。
5. 验证 `SKILL.md` 中每个相对链接都存在，模板没有真实仓库 URL 或凭据。
6. 检查 `git diff`，确认没有纳入 `.idea/` 或其他用户文件。

## 校验环境说明

本轮修改后调用 `skill-creator/scripts/quick_validate.py` 校验 `sdkit`、`sdkitgo`、`vab-admin` 和 `nuxtjs` 时，当前 Python 解释器缺少 `PyYAML`，脚本停止在 `ModuleNotFoundError: No module named 'yaml'`。未修改全局 Python 环境；已使用 Ruby YAML 按相同 frontmatter 条件完成等价校验，并额外通过 Markdown 相对链接、代码围栏、绝对路径、模糊措辞和 reference 验收检查。

项目级行为测试已通过：临时 Codex 实例可以从 `.agents/skills` 发现 `sdkit` 与 `sdkitgo`。`sdkit` 能把“可独立构造且无需 runtime 的 queue driver”分流到 `pkg/queue/{driver}`，并读取 workflow、core/pkg 判定、pkg 和 testing reference；`sdkitgo` 能把分页列表 handler 分流到 workflow、handler、request、response、query、projection 和 testing reference。两次测试均为只读，没有修改业务项目或安装全局 skill。

## 源库保护

源规范库当前包含用户尚未提交的修改。迁移只读取和复制，不得清理、回滚、覆盖或提交源库内容。开始迁移时观察到的状态包括：

```text
 M go/sdkitgo/README.md
 M go/sdkitgo/database/migration.md
 M go/sdkitgo/database/model.md
 M go/sdkitgo/database/projection.md
 M go/sdkitgo/database/query.md
 M go/sdkitgo/http/handler.md
 M go/sdkitgo/http/router.md
 M go/sdkitgo/infra.md
 M go/sdkitgo/service/crontab.md
 M go/sdkitgo/testing.md
 M go/sdkitgo/workflow.md
 M nuxtjs/portal/README.md
 M vue/admin/code/page.md
 M vue/admin/ui/style.md
?? go/sdkitgo/database/batch-write.md
?? go/sdkitgo/database/seed.md
?? nuxtjs/portal/components/business-options.md
```

目标仓库原先已有未跟踪的 `.idea/`，它属于用户文件；不得删除、覆盖或加入提交。

## Git 边界

- 不执行 `git add`、`git commit` 或 `git push`，除非用户明确要求。
- 不修改现有 remote。
- 不把 `.idea/` 纳入迁移内容。
