# Codex 全局 AGENTS.md 推荐整理草案

适用范围：已有 Codex 全局 AGENTS.md 的非破坏性整理建议。此文件仅为审阅草案，禁止直接作为安装脚本替换整个用户文件。现有个人路径仅在用户本机原始配置中保留，不写入通用模板。

## 推荐顺序

1. Superpowers 使用偏好：原区块原样保留。
2. SDKit 全局 Bootstrap：由 `project_skill_global.py` 维护独立标记区块；只记录 Skill 路由与共享协议入口。
3. Git 初始化安全：原区块保留；与 GitOps 协作规则有不同授权范围时以更严格的用户明确限制为准。
4. 数据库环境：原区块保留 Docker context、`sd help db`、`pg18` 与基础设施 Schema 保护。
5. 本地 Web：保留 `localhost` 规则。
6. Wiki 知识库：保留用户的知识沉淀触发和发布授权，详细仓库操作交给 wikiops。
7. 工程规范：保留现有 engineering-standards 入口，不推断其已迁移。只在核验真实本地文件后判断与 skills 的规则重复或冲突。
8. GitNexus：保留 `--index-only` 默认行为。

## 自动化范围

- 当前 PR 仅自动追加/更新 SDKit 独立托管区块，不移动、删除、重排其他七个用户区块。
- 对旧 Skill 名称及 engineering-standards 只输出检查报告，不机械替换或宣称已弃用。
- 全局配置本身不存放本机绝对路径模板；现有个人配置由用户保管，不复制到仓库。
- 已有自定义规则必须逐字节保留。全局入口与项目 AGENTS.md 冲突时停止受影响操作。
- 只有获得单独授权且已核验 dry-run Diff 后才允许修改真实 Codex 全局配置。

## 待本地核验

- 读取实际 engineering-standards 目录及 README，按技术栈对照新版 Skill references，确认是否存在尚未迁移的独有规则。
- 检查当前 `CODEX_HOME` 与 `AGENTS.md`，不假定默认路径。
- 以脱敏的七个区块夹具测试标记完整性、原文保护、旧名称提示、幂等、备份、权限、并发与恢复。
- 隔离 Codex Home 真实启动后验证全局入口能否加载，模型自动选择另行授权测试。

## 完成标准

全局原有区块零删除、零重排、零内容改写；仅托管 SDKit 区块有明确 Diff；遗留规范来源报告准确；没有访问或修改真实用户配置与业务仓库。
