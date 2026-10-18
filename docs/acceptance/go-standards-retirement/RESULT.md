# go 独立规范迁移验收

范围：Go 本地 replace 联调/发布退出、已确认基础设施管理面保护、按需地理注册表独立语义。主 Skill 与旧兼容入口的详细规则同步，旧 description 仍只服务显式兼容任务，不改 Catalog 的 15 主入口/5 旧入口划分。没有写入旧规范库、业务模板、真实 Codex 配置或用户安装目录。

本分支基于 main，未合入 PR #14；Bootstrap 本体测试在含 #14 的隔离集成副本运行，不能把 main 上不存在的测试记作已执行。集成回归命令及实际退出码在 local-regression.json：35/17/44/41/7 全通过、validate 20、Markdown 链接/锚点零错误、diff --check 通过。各分支单独的 Manager、validate、链接与 diff 另行交付前运行。

隔离 Codex 原生发现：15 主入口与 5 兼容入口分别发现，20 独立安装/更新通过。隐式模型路由探针 45 秒超时，标 BLOCKED；静态映射与原生发现不能代替模型实际选择。

Nuxt 规则额外对照公开模板已提交源码的隔离归档，i18n/realtime/seo/template/request-context 35 项测试全部通过。Vab 仅核验源码与规范，不冒称本轮重现性能收益。Go 未执行数据库或消费方构建。Rust 未编造远端身份。

所有 PR 保持 Draft，未合并、发布或主动触发 CI。旧 UI/原型导航归属冲突、真实全局旧库入口和已安装旧 bootstrap 依赖尚未消除；不具备清理旧规范库的条件。
