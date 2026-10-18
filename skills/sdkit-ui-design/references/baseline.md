# 设计基线归档 V1.1

适用范围：Codex 或其他开发 Agent 已实际收到设计图片，并被授权基于该图进行设计迭代、交互原型或正式开发。仅讨论、评审、只读任务禁止归档写入。

## 归档前门禁

1. 必须先通过 Foundry Workspace / Repository Resolver 核验唯一项目身份、立项状态、权威仓库、工作区和写入授权；已立项必须使用项目仓库，未立项才允许使用已核验的临时产品文档仓库。身份不明、多个候选、远端冲突、文件不可访问或权限不足时标记 BLOCKED 并停止写入。
2. 必须读取目标仓库 AGENTS.md、已有 DESIGN.md 和设计目录约定；有约定时必须沿用。仅当没有约定时允许最小创建 docs/design/DESIGN.md、assets/、必要的 revisions/；禁止批量迁移既有文件或生成空文档。
3. 必须读取原始图片实际字节，检查文件格式与扩展名一致、文件完整且非空，计算 SHA-256。Web 会话中的图片链接或文字描述不等于 Codex 可访问的字节；无法读取时 BLOCKED，不得以重绘、截图或占位图冒充原图。
4. 写入前必须检查目标工作区 dirty 状态、并行 Worktree、目标路径所有权及相关 PR；同路径并发冲突必须停止，不允许覆盖其他作者的内容。

## 保存事务

1. 以 Project/Module、稳定 Design ID 和 Revision 识别设计；记录 Source Type、可核验 Source Reference、Asset Path、SHA-256、Created At、Design Status、Implementation Mode、Related Pages 和 Acceptance Notes。未知字段标记待确认，禁止编造。
2. 先检查现有资源和索引：相同 Design ID 与相同 SHA-256 直接复用已有资源，不创建重复修订；同名但哈希不同必须采用新的修订文件名，禁止覆盖。不得仅凭文件名判断相同。
3. 以目标仓库既有命名规范保存原始图片字节，再增量更新 DESIGN.md，保留已有有效内容和历史；必要时才创建 revisions/<revision>.md。文件写入失败时不得把归档状态标为成功，必须保留可恢复证据并报告不一致。
4. 更新索引前重新核对图片 SHA-256、路径及设计 ID；写入后读回验证。并发修改导致索引版本变化时停止覆盖，重新读取和整合，禁止 last-writer-wins。
5. 设计 Revision、交接文档版本、原型版本、业务 Commit、Content Engine Release 是独立标识，不得互相代替。项目暂停或终止不得自动删除历史资料。
6. 探索项目立项后，迁移由 Foundry 管理：先验证目标仓库及完整资源，再保留 product-docs 来源/去向声明，旧资料历史只读；不得形成两个可编辑权威源。

## 交接与授权

- implementationMode 只能为 production、prototype、undecided。production 由技术栈 Skill 负责真实业务实现，不得虚构 API、权限或数据；prototype 由 Foundry/目标仓库规范负责原型源码及模拟数据；undecided 只允许归档和说明，不自动写业务或原型代码。
- 在当前项目写入授权覆盖设计资料时，开发前必须先完成基线保存及读回核验；归档成功不授权 Git Commit、Push、PR、Merge、Deploy、R2 发布或变更全局配置。各操作必须分别核验授权及 Git 协作规则。
- DESIGN.md 最小包含设计目标、模块、页面关系、图片路径及哈希、视觉与交互状态、响应式、已确认/待确认、模式和验收项。小修改仅增量更新，不生成无意义文件。
- 设计稿中出现凭据、Token、私有路径或敏感数据时不得原样公开提交；先报告并获得安全处理方案，不擅自改写原始证据。

正向形态：核验项目仓库与图片字节 → 计算 SHA-256 → 幂等检查 → 保存不可覆盖的修订 → 更新 DESIGN.md → 读回校验 → 进入选定开发模式。

反例：仅凭聊天截图猜测文件路径，覆盖 home.png，然后声称图片已保存并已发布。

## 完成标准

必须报告仓库与路径、Design ID/Revision、真实 SHA-256、归档及读回状态、模式、冲突检查和未完成授权动作。静态规则测试、真实文件系统测试、真实 Codex 行为测试和浏览器视觉验收必须分别记录；未执行不得宣称通过。
