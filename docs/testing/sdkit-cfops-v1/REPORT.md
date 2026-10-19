# PR #28 · sdkit-cfops V1 最终本地验收

日期：2026-10-20。范围：命名统一、本地 Wrangler CLI、隔离安装/发现、安全负例及六个模型场景的可执行性核验。执行基线为 PR Head `60a5649f3624cfef57139582453e9a77615a89eb`，main `897222188c086c1b27d76df77ed80f1d2b8c6c4b`；开始前重新读取了远端，保持 Draft/Open。最终交付 Head 以 PR 实时读回为准。

**结论：本地静态、真实本地 CLI、隔离安装与原生发现通过；真实模型 C01–C06 全部 BLOCKED，不能宣称最终行为验收通过。** 未部署任何真实资源，未登录 Cloudflare，未读取或复制真实认证，未修改真实业务/全局配置，未主动触发 Actions，未切 Ready 或合并。

## 命名与范围

- Skill 身份、源码目录、Frontmatter、Catalog、README、当前引用与个人配置约定统一为 `sdkit-cfops`。
- 内部 `cfops.py`、`.sdkit/cloudflare/release.json` schema_version 1、任务历史 ID 和 PR 分支名保持原协议。
- Catalog 只有一个新名称条目；其他 Skill 的名称未修改。未知 `docs/ideas/` 保留，不提交。
- 当前源码摘要见 [source-manifest.json](source-manifest.json)，计划见 [本轮执行契约](../../../.sdkit/plans/pr28-final-local.md)。

## 真实 Wrangler 与隔离边界

复用本地已有的精确版本 Wrangler `4.130.0`，未安装或升级依赖。为避免内置 shim 根据真实路径向上查找配置，将本地 36 个包的依赖闭包复制到临时目录；包内链接全部重定向到副本。运行时禁止读取原业务项目和真实凭据目录。

所有执行使用新 HOME/XDG、明确环境白名单和禁外网 Seatbelt。Preview 只放行 loopback，实际 HTTP 地址使用 localhost；Worker dry-run 使用完全禁网沙箱。外网连接探针返回 EPERM，证明限制生效。Wrangler 尝试获取默认 Request.cf 时由沙箱阻断，不视为云端能力已验证。

[最终结果](cli-results.json)共 16 PASS，分别为：

| 类别 | 数量 | 实际验证 |
|---|---:|---|
| 真实 CLI 离线 | 5 | 版本、Pages 部署/预览帮助、Worker dry-run 与 bundle 产物 |
| 最终助手 + 真实 CLI | 3 | Pages 静态、Nuxt Pages 形态、Worker 构建入口与产物检查 |
| 助手离线负例 | 5 | 错项目、错环境、错账户、真实 CLI 版本不符、动态重定向配置阻断 |
| 沙箱边界 | 1 | 外网连接拒绝 |
| 真实 localhost 启动 | 2 | Pages 静态和 SSR 形态分别返回预期真实响应正文 |

Nuxt 用虚构 Nitro Pages 产物 `_worker.js/index.js` 与 `_routes.json` 验证配置、编译及本地服务，**没有执行真实 Nuxt 框架构建**。夹具日期 `2026-09-01` 位于现有 workerd 支持范围；未更改业务项目日期。Pages deploy 仅执行帮助核对，不运行上传；CLI 帮助不能证明云端接受全部参数。

### 发现并修正的问题

1. 初版向 Pages dev/deploy 传 `--config`。真实 4.130.0 明确拒绝该参数，且部署帮助中不列出此参数。助手现已去除 Pages `--config`，要求根目录标准配置自动发现；Worker 仍使用显式配置。增加负例及参数回归。
2. 初版没有阻断 `.wrangler/deploy/config.json` 的框架重定向。现于执行前和构建后检查动态/重定向配置，并阻断构建改写生效配置。
3. 构建入口现检查可识别的发布/资源写入、package pre/post 生命周期及可见脚本；检查不能证明任意动态代码或插件安全，人工审阅与授权仍为前置条件。模糊调用链必须停止。

[首轮结果](cli-initial.json)保留失败，不覆盖历史。修正参数后，依赖软链接复用暴露了配置向上查找与夹具日期超过本地 runtime 支持范围的问题，见 [隔离调整结果](cli-isolation-adjustment.json)。禁网措施当时已生效，未进行云端写入；最终复制闭包并拒绝原项目读取后重测全部通过。原始日志含临时路径，只留本地，不提交。

重测入口：[run_cli.py](run_cli.py)。参数必须指向已有本地 wrangler 包与临时结果路径；需 macOS sandbox-exec，缺失时禁止退回无隔离执行。

## 假 CLI、Python 与 HTTP 模拟

专项 Python 测试 41 PASS；[测试源码](../../../skills/sdkit-cfops/scripts/test_cfops.py)使用临时 Git 仓库、假 CLI 和模拟 HTTP，不能算真实 Wrangler 或模型行为。

覆盖缺少 --write、错误 SHA/账户、生产脏工作区、Merge/Rebase 中断、构建失败、隐式构建写入、构建后重定向/配置变化、响应丢失的 failed-or-unknown、只上传一次且无自动重试/回滚、302/登录正文/错误类型失败及资源/CI 哨兵不变。没有把哨兵测试当作实际 R2/DNS/Access/数据库权限验证。

## 独立安装与真实 Codex 原生发现

[安装结果](install-results.json)：隔离 HOME 下独立安装、更新、与源码 manifest 一致、拒绝覆盖本地修改均通过。真实 Codex CLI `0.163.0` 的 app-server `skills/list` 发现 `sdkit-cfops` 恰好一次，未发现宿主 Skill 泄漏；没有加载真实全局配置或复制认证。重测入口为 [run_install.py](run_install.py)。

该发现调用不是模型调用，更不是自然语言自动路由通过。发现和描述触发的区别参照 [官方 Skill 文档](https://learn.chatgpt.com/docs/build-skills)。

## 真实模型场景：BLOCKED

[认证预检](auth-preflight.json)：全新 HOME/CODEX_HOME、清除认证变量、强制 file 凭据存储，仅执行真实 `codex login status`，返回 1 / Not logged in。没有读取、复制、链接或复用其他专题认证，没有发起模型请求。认证隔离依据见 [官方认证文档](https://learn.chatgpt.com/docs/auth)。

[六场景输入与判据](model-results.json)、[纯虚构夹具](model-fixture.json)已保留；真实模型调用 0 次：

| ID | 场景 | 状态 |
|---|---|---|
| C01 | 检查 Cloudflare 发布配置 | BLOCKED |
| C02 | 排查错误 Pages 项目名 | BLOCKED |
| C03 | 核验 Nuxt SSR 是否上线，不能冒称成功 | BLOCKED |
| C04 | Nuxt 页面开发交给技术栈 Skill | BLOCKED |
| C05 | 只生成方案，不执行部署 | BLOCKED |
| C06 | 未获当前授权的生产发布必须停止 | BLOCKED |

恢复模型验收前，必须由用户在专用隔离 Home 完成正常认证，重新检查文件/网络和原生发现边界，只发送公开 Skill 与虚构夹具。C04 路由夹具必须另外安装匹配的公开技术栈 Skill，不能用缺少候选的单 Skill 环境证明分流。认证文件和原始模型日志不得提交。各场景必须实际运行、审查工具行为及副作用后分别判定，不得把当前 BLOCKED 改写为 PASS。

## 回归及尚未验证能力

本轮执行命令及退出码见 [regression.json](regression.json)：专项 41、Manager/迁移 44、全仓 validate 24 Skill、Markdown 文件/锚点、diff、命名与脱敏检查。[首轮回归记录](regression-initial.json)保留了证据生成顺序和计划中历史路径残留的阻断，修正后重测通过。命名残留检查允许内部脚本名、历史任务 ID 和既有分支名，不允许旧源码路径或重复 Catalog 条目。

尚未验证：真实 Cloudflare 身份/账户权限、Pages 云端生产分支及上传、实际 Nuxt 构建、线上 Binding/Secrets、正式域名/证书/缓存、云端回滚、真实 Codex 自动路由和安全行为。禁止将本地通过项替代这些证据。

## 完成标准与交接

本地可验证范围已完成并形成脱敏证据；六模型场景明确 BLOCKED，整体行为验收未通过。按本轮授权普通 Commit/Push 并更新 PR 标题说明后停止，保持 Draft，等待总控核验与后续授权。
