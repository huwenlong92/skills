# PM Source Visibility V1 维护

适用范围：新增或修改 PM 项目 Profile、目录、文档，或移动、删除内容、改变 visibility 时必须读取本文件。仅检索和回答不授权元数据写入。

## 先读取 Source 权威

- 必须先按 [Repository Resolver](resolver.md) 核验 Workspace、实际工作树和修改范围，再读取目标 Source 的 `AGENTS.md`、`standards/content-visibility-v1.md`、命中的 Schema 及现有声明。禁止把 HEAD 对齐当作工作文件已同步，或覆盖未知未提交成果。
- 发布者默认 Source 规范为 [PM Content Visibility V1](https://github.com/huwenlong92/product-docs/blob/main/standards/content-visibility-v1.md)。通用语义、Schema 和固定向量以 [Engine Content Visibility V1](https://github.com/huwenlong92/sdkit-content-engine/blob/main/docs/CONTENT-VISIBILITY-V1.md) 为准；必须调用 Source 已接入的 Engine 校验/解析，禁止在 Skill、模板或脚本中另写继承算法。
- 其他 Workspace 必须从其实际规范发现等效声明位置；未取得规范、Schema 或 Source 尚未接入 V1 时，必须停止相关 visibility 写入并报告缺口，禁止猜测字段或套用发布者的业务路径。

## 作者声明与默认值

允许写入的位置仅为 Source 声明的项目 `profile.json`、目录 `.visibility.json` 和文章 Markdown Frontmatter；禁止把展示元数据写入生成页面、搜索产物、认证配置或私有发布目标。

- 必须只使用 `public`、`private`、`inherit`。缺省为 inherit，未声明根默认 private；项目默认 public 是作者显式声明策略，不得修改 Engine 根默认值。
- 新建且已获授权的项目，未另有 Owner 明确选择时必须在 Profile 显式写 `visibility: public`；修改既有项目时，未明确要求改变 visibility 必须保留原声明；禁止以“默认 public”为由覆盖 private 或批量补 public。项目根已有 Profile 声明时，禁止再添加同根目录声明，即使值相同。
- `docs` 默认继承 public 项目，不添加 private 默认，也不为越过屏障写 public。新建 `tech`、`deployment`、`internal`、`private`、`ops`、`operations` 目录必须按 Source 规则声明 private；既有目录/文档的显式 private 必须保留。
- 普通新文档未指定时必须继承唯一父级；部署文档必须保持 private，包括 `deployment.md`、`deployment.markdown`、任意层 `deployment/` 内文章及 Source 判定的字节相同副本。禁止通过 public 覆盖部署限制，禁止仅按标题关键词推断部署分类。
- 目录/文章只有实际物理父级参与继承；Profile 身份和 Frontmatter.project 必须与物理项目一致。标签、关联文档和交叉引用不是继承父级；显式 private 节点及其所有后代不能被 public 绕过。
- status、draft、confirmed、implementation 等生命周期与开发状态字段不得自动改变 visibility。禁止因确认、发布、移动到 docs 或修补 Frontmatter 而批量公开历史内容。
- 非法值、原始重复键、多处根声明、循环、多父级或不明确归属必须交由 Source/Engine 拒绝；禁止先合并声明、放宽 Schema 或选一个父级消除报错。

## 变更与验证

1. 修改项目或目录可见性前，必须检查其全部后代；移动内容时同时检查旧、新父链。必须列出修改前后继承结果、private 屏障、Normal 可见路径及数量差异和 Full 完整集合，并与当前授权范围核对。发现未授权扩散时必须停止该变化并报告；授权已覆盖时不得重复索取确认。
2. 必须仅修改授权的声明；文章状态、ID、路径与业务字段继续按原规范维护。禁止为统一格式批量添加 visibility、重写旧内容或按可见性裁掉完整 Source、Catalog、Snapshot、Manifest、Release。
3. 项目/目录/文档新增、修改（包括只改正文）、移动或删除完成后，必须按 Source 规范重新 prepare/check，交付同步的 graph 和业务 Source。前置条件是 `SDCE_ENGINE_ROOT` 已明确指向经 Source pin 校验的 Engine；禁止硬编码工作站路径、自动安装依赖或为此连接 Store。

```sh
node content-source/visibility.mjs --prepare
node content-source/visibility.mjs --check
```

4. 必须使用 Engine 的同一可见集合核对 Catalog、导航、搜索；普通展示只保留有效 public，Full 展示完整内容但不绕过校验或既有认证/授权及 Store 权限。Visibility 不是身份认证；现有 Access、`development=1` 和 Web 路由保持不变，禁止为隐藏内容新设或关闭 Access、自动实现 `/full/`。
5. prepare/check 不是内容发布。真实发布必须另有当前授权并遵守 [提交与发布验收](publishing.md) 及 Source 宿主 `publishVisibilitySource` 门禁；禁止把旧 CLI 直接发布冒充已接入该门禁。

## 脱敏形态与反例

已授权新建 `demo` 项目时，增量合入现有必需字段的 Profile 片段：

```json
{"visibility":"public"}
```

`docs` 不设置覆盖声明；`tech/.visibility.json` 使用：

```json
{"visibility":"private"}
```

普通 docs 文档可以保持 `status: draft` 并继承 public；tech 下即使文章声明 public，结果仍是 private。反例：把 confirmed 文档自动设 public；给 private 目录下的文章加 public“修复搜索”；因新建 docs 而覆盖其已有 private 子目录。

## 完成标准

必须交付实际声明路径、原/新值、受影响后代范围和 Normal/Full 差异、Source 校验与三种投影结果；人工检查默认公开是否仅用于授权的新建对象，部署分类/已有 private 是否保留，以及是否把生命周期、Full 或发布成功误当公开/访问许可。未执行的发布或访问验证必须如实标记。
