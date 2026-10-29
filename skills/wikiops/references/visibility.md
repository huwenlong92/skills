# Wiki Source Visibility V1 维护

适用范围：新增或修改 Wiki 分类、目录、文章，或移动、删除、重分类内容、改变 visibility 时必须读取本文件。查询、检索和候选捕获不授权元数据写入。

## 先读取 Source 权威

- 必须先按 [Repository Resolver](resolver.md) 核验 Workspace、实际工作树和修改范围，再读取 Source 的 `AGENTS.md`、主题注册表、`standards/content-visibility-v1.md`、命中的 Schema 及原声明。禁止把 HEAD 同步当作工作树已同步，或覆盖未知未提交成果。
- 发布者默认规范为 [Wiki Content Visibility V1](https://github.com/huwenlong92/wiki/blob/main/standards/content-visibility-v1.md)。三值语义、Schema 和固定向量以 [Engine Content Visibility V1](https://github.com/huwenlong92/sdkit-content-engine/blob/main/docs/CONTENT-VISIBILITY-V1.md) 为准；必须使用 Source 已接入的 Engine 校验/解析，禁止在 Skill 或模板中维护第二套算法。
- 其他 Workspace 必须从实际规范发现声明位置；规范/Schema不可读取或 Source 尚未接入 V1 时，必须停止相关 visibility 写入并报告，禁止猜测分类或复制发布者路径。

## 分类、目录、文章

允许写入的位置仅为 Source 声明的分类注册表条目、目录 `.visibility.json` 和文章 Frontmatter；禁止手工更改门户生成内容、搜索产物或认证/私有发布配置来表达 Visibility。

- 必须只使用 public/private/inherit；缺省 inherit，未声明根默认 private。当前分类默认 public 已由注册表显式声明；未明确要求改变该声明时必须保留；禁止将该策略实现为另一套隐式 public 根默认。新增分类必须按当前 Owner 授权范围和 Source 规范显式决定，禁止从标签、主题名或当前公开门户猜测。
- 发布者 Source 的分类声明位于 `topics.json` 条目，目录为 `knowledge/<topic>/.../.visibility.json`，文章为原 Frontmatter.visibility。分类注册表已有声明时，禁止在同一根目录重复声明，即使值相同。
- Topic 注册分类是主归属根，文章 Frontmatter.topic 必须与所在物理分类一致，目录逐层构成唯一父链；必须保留原文章 ID。标签、专题引用、related topics、references 和交叉引用都不产生额外继承父级。禁止为了多专题展示复制正文或修改归属来绕过 private。
- 子目录、文章允许按授权显式 private；普通新文章未指定时必须继承唯一父级。显式 private 祖先阻断全部后代，子文章 public 或引用 public 专题都不能覆盖；引用 private 专题也不自动改变另一个公开分类文章的归属。
- status 的 draft/review/confirmed/archived 生命周期保持原规则，禁止自动改变 visibility。confirmed 不代表 public，draft 不代表 private，归档/迁移也不构成批量改写许可；旧文、CSS 候选及其他历史内容禁止擅自批量公开或改 private。
- 非法值、原始重复键、多处根声明、重复 ID、循环、多父级和不明确归属必须由 Source/Engine 拒绝；禁止合并掉原始重复声明、放宽 Schema 或任选一个父级规避验证。

## 变更与验证

1. 修改分类/目录可见性前，必须检查所有后代；重分类或移动时必须同时检查旧、新父链。必须列出修改前后继承结果、private 屏障、Normal 可见路径/数量差异与 Full 完整集合，并核对当前授权范围。未授权扩散必须停止并报告；授权已覆盖时不得重复索取确认。
2. 必须只增量修改授权声明；原文章状态、ID、正文与业务元数据继续按 [知识写入](writing.md) 和 [知识维护](maintenance.md) 执行。禁止为生成公开视图删除完整 Source、Catalog、Snapshot、Manifest 或 Release 中的 private 内容。
3. 分类、目录、文章新增、修改（包括只改正文）、移动或删除完成后，必须重新 prepare/check，并将新 graph 与 Source 一起验收。前置条件是 `SDCE_ENGINE_ROOT` 已明确指向通过 Source pin 校验的 Engine；禁止写入固定本机路径、自动安装依赖或为此访问 Store。

```sh
node content-source/visibility.mjs --prepare
node content-source/visibility.mjs --check
```

4. 必须用同一 Engine 可见集合核对 Catalog、导航、搜索；普通展示只保留有效 public，Full 展示完整内容且不绕过校验或既有认证/授权及 Store 权限。Visibility 不是身份认证或凭据；现有 Access 门禁保持不变，不因当前分类公开而关闭保护，也不因 private 元数据自动新设 Access。`/full/` Web 实现不属于内容维护。
5. prepare/check 不等于发布。真实发布必须另有当前授权，并执行 Source `publishVisibilitySource` 宿主门禁和 [门户与发布](publishing.md) 的原有验收；禁止绕过宿主直接运行旧 CLI 后宣称新门禁生效。

## 脱敏形态与反例

以下是已授权分类条目的增量片段，其他字段以实际 Schema 为准：

```json
{"id":"tools","title":"工具","visibility":"public"}
```

该分类中的内部目录 `.visibility.json`：

```json
{"visibility":"private"}
```

普通文章可以 `status: draft` 且继承分类 public；目录为 private 时，子文章即使 public 或引用其他 public 专题也仍 private。单篇文档可以保持 confirmed 并显式 private。反例：将旧文全部 confirmed 后自动公开；把专题 references 当第二个父级；修改 private 分类下文章为 public 来“修复导航”。

## 完成标准

必须交付声明路径、原/新值、分类/目录全部受影响后代、Normal/Full 差异、Source 校验及 Catalog/导航/搜索一致性结果；人工检查旧状态和 visibility 是否未经授权变化、专题引用是否被错作父级，以及 Full 是否被误作访问许可。Git、真实发布、部署与访问验收必须分别报告，未运行不得声称完成。
