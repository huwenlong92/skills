# PR #13 最终集成验收

适用范围：PR #12 合并后，PR #13 的 main 整合、20 个 Skill 与工程协议兼容、本地回归及行为证据复用。报告不代替 GitHub 当前 Head/Draft 的实时核验。

## Git 基线与整合

- 实时 main：444b7da7b786ff78864f22a3210a8ddcc0bf0597；PR #12 已于 2026-10-18 合并，merge commit 即此 SHA。
- PR #13 整合前 Head：032197e89fa8b0bc1752ab70bd5db6dd07906c7a，Draft/Open。
- 新建独立 Worktree，执行普通 `git merge --no-ff origin/main`，生成 a3ea32f501ecedaf82739bb7c192c4ee09da928a；无冲突、无 ours/theirs 覆盖、无历史重写。
- `git merge-base --is-ancestor origin/main HEAD` 实际退出 0。最终交付 SHA 以包含此报告的 PR #13 最新提交为准。
- 其他 Worktree 和主工作区未跟踪 docs 保留。未修改 main、其他仓库或全局 Skill。

## 20 Skill 与选路兼容

Catalog、目录及 frontmatter 全部一致；八个新入口和五个旧兼容入口均存在。实际安装和更新在独立临时父目录逐个执行，20/20 文件 manifest 与来源一致。八个迁移目标的独立安装、五组互不覆盖、旧详细 references 保留与 README 安装入口另由现有迁移测试覆盖。

Codex CLI 0.163.0 的本地 App Server 使用 `initialize` 与 `skills/list` 实际发现项目级入口，未启动模型会话。测试使用临时 Codex home、没有复制认证或修改全局安装；主入口和旧兼容入口分两个项目范围安装。只记录 project scope 的结果，不提交宿主其他 Skill 信息或原始响应。

| 安装范围 | 预期 | 实际发现 | 发现错误 |
|---|---|---|---|
| 主入口与其他能力 | 15 | 15，含八个新入口 | 0 |
| 历史兼容入口 | 5 | 5 | 0 |

实际脱敏发现结果：

```json
{
  "independent_install_update": 20,
  "native_discovery": [
    {
      "scope": "primary",
      "expected_count": 15,
      "found": [
        "dockerops",
        "foundry",
        "npmops",
        "sdbase-admin-lite",
        "sdbase-flutter-app",
        "sdbase-go",
        "sdbase-lite",
        "sdbase-nuxtjs-portal",
        "sdbase-vab-admin",
        "sdenv",
        "sdkit-go-core",
        "sdkit-rust-core",
        "sdkit-skills",
        "swops",
        "wikiops"
      ],
      "errors": []
    },
    {
      "scope": "legacy",
      "expected_count": 5,
      "found": [
        "nuxtjs",
        "rust-sdcore",
        "sdkit",
        "sdkitgo",
        "vab-admin"
      ],
      "errors": []
    }
  ],
  "model_calls": 0
}
```

| 任务/身份 | Primary 与兼容判定 |
|---|---|
| 已核实 SDBase Go 完整模板 | sdbase-go；SQLite 单 Web 则选 sdbase-lite，禁止误用 PostgreSQL/多服务规则 |
| 已核实 Nuxt 门户模板 | sdbase-nuxtjs-portal；普通 Nuxt、Vab 排除 |
| 已核实完整 Vab 后台 | sdbase-vab-admin；Admin Lite、Nuxt 排除 |
| 修改共享 Go 框架本身 | sdkit-go-core；业务 CRUD 排除 |
| 维护/消费实际 Cargo sdcore | sdkit-rust-core；先解析 Cargo 实际来源，不编造仓库地址，普通 Rust 排除 |
| Admin Lite / Flutter 模板 | sdbase-admin-lite / sdbase-flutter-app；核验模板身份，禁止把 Lite 当 Vab 或把未接 SDK 当已实现 |
| 五组旧名称 | sdkit、rust-sdcore、sdkitgo、vab-admin、nuxtjs 仅显式历史兼容/迁移；不得与对应新入口重复成为同一子任务 Primary |
| 普通非 SDKit Go/Rust/Vue/Nuxt/Flutter | 无模板来源证据时不选择专用模板/core Skill；不得只凭扩展名推断 |
| 运维、产品、知识与管理任务 | dockerops/npmops/sdenv/swops/foundry/wikiops/sdkit-skills 各按自身职责；不因技术栈项目自动启动发布、数据库或 PRD 操作 |

迁移 references 中保留的 sdkitgo、nuxtjs、vab-admin、rust-sdcore 文档 frontmatter 或历史规范名称不是额外 Skill 入口；不机械改写这些已保留的详细规则。

上述选路为实际描述、SKILL 与 repository 规则的静态语义核对，不伪称新增自然语言模型选路测试。Primary 唯一、Supporting 按命中范围、Guardrail 不提供额外授权，与八个新入口无冲突。Development Execution 的基线、C0–C3、D0–D3、测试和停止门禁不改变技术栈目录、版本或数据库边界；模板 main 仍不表示业务项目已升级。

包内链接审计共 861 个相对链接。20 个 Skill 的执行入口和 references 不存在未声明的跨包依赖。严格审计整个包时，Foundry 的附属 README 中有一条 `../../README.md`，属于现有源仓库安装导航：源仓库内有效，但独立安装副本中不可用。该 README 与 main 逐字节一致，没有被本轮引入或改变，不是必需的运行能力依赖；本轮不修改已合并 Skill。这是已记录的非阻断文档限制，不能宣称全部附属 README 链接都在包内。

## 真实行为证据复用

与 032197e 整合前逐字节比较，AGENTS.md、Skill Orchestration、Development Execution 及既有 T01–T10 报告/逐项证据均未改变。未发现路由语义或开发阶段门禁的实质变化，按用户要求复用 [T01–T10 真实行为报告](2026-10-18-report.md)：PASS 10 / FAIL 0 / BLOCKED 0，保留当时 14 次真实模型调用及受限重测记录。

本轮模型调用为 0；本地 skills/list 是发现验证，不是模型自动选择。既有证据只证明受控试点，不能推导所有安装范围或技术栈都不会误触发。

## 实际本地命令与结果

| 命令 | 数量/结果 | 退出码 |
|---|---|---|
| `python3 -m unittest discover -s scripts -p 'test_engineering_protocols.py' -v` | 17 通过 | 0 |
| `python3 -m unittest discover -s skills/sdkit-skills/scripts -p 'test_*.py' -v` | 44 通过：Manager 37 + Migration 7 | 0 |
| `python3 -m unittest discover -s skills/dockerops/scripts -p 'test_*.py' -v` | 41 通过 | 0 |
| `python3 skills/sdkit-skills/scripts/manager.py validate --all` | validated 20 skills | 0 |
| `python3 -m unittest discover -s scripts -p 'test_markdown_links.py' -v` | 7 个正反例通过 | 0 |
| `python3 scripts/check_markdown_links.py` | 255 份 Markdown、905 个相对链接、2 个本地锚点，零错误 | 0 |
| `git diff --check` | 无空白错误 | 0 |
| `git merge-base --is-ancestor origin/main HEAD` | main 已在当前历史中 | 0 |

合计 109 个 unittest 通过；DockerOps 测试全部使用离线夹具，未执行真实镜像、数据库、Webhook 或部署操作。新增 Markdown 工具补齐原有检查未覆盖的锚点，并用缺失文件、缺失锚点、重复标题、中文/编码路径、显式锚点、代码示例及越界反例验证，不弱化原有测试。外部 URL 不访问、不宣称可用。

## 交付结论与完成标准

没有未解决的集成协议冲突；本轮 main 同步、20 Skill 兼容、109 项测试与全仓链接/锚点检查通过，达到 PR #13 本轮可合并技术条件。Foundry 附属 README 的既有导航限制单独记录，不作为新协议已破坏独立执行的证据，也不擅自扩展本轮修改范围。

保持 Draft/Open，不切换 Ready、不合并、不部署、不主动触发 Actions。Push 前必须再次核验 main 与 PR #13 Head；最终 mergeable 由 GitHub 实时返回。全部完成后停止，等待用户最终合并授权。
