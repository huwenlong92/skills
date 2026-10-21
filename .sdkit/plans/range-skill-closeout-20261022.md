# RANGE V1 模板 Skill 收尾

任务 `range-skill-closeout-20261022`，revision 1；初始 Skills 基线 `5752d368d0a7a82496c542abf74d8e76be7f17e2`，只读 Go 基线 `9567f312a20dc9c29beff450749c25c74c0d5de7`。用户授权两仓安全同步、必要 Skill 文档修改、Stage/Commit/普通 Push 及一个 Draft PR；不合并、发布、安装、部署、主动 CI 或执行数据库操作。

范围仅 `sdbase-go` Skill 模板使用 reference、主入口及交接。通用安全继续由已合并 `sdkit-dbops` 定义，禁止修改该 Skill、Go 源码/SQL、Core、Lite 或其他技术栈。Primary `sdkit-skills`，Supporting `sdbase-go` 事实核验与 `sdkit-dbops` 安全边界；遵循 Git Collaboration、Development Execution、Skill Orchestration、AGENTS、manager workflow/install 和命中模板 references。

阶段：C0 保护部署9项/64忽略文件、草稿、安装文件、引用和Worktree，核验远端及ff-only同步；C1 源码核对五表/三任务/入口，仅补充Skill；C2 离线校验、精确diff/敏感检查后独立提交推送及Draft；C3 回读PR与保护清单后停止。规范/归属或远端状态不明停止相应写入；扩大数据库/实现范围须另行授权。中断从首个未验证阶段恢复，不覆盖旧成果。

C0 verified：两仓main已ff-only同步到上述基线。Go原detached HEAD和索引不动；Skills原main仅有未知docs/ideas草稿，与main更新无路径冲突，原字节保留。独立分支 `codex/sdbase-go-range-skill-20261022`；旧Worktree登记保留，历史候选及验收数据不操作。远端Skills仅开放UI专题#22，与本次Skill无路径重叠。

C1 verified：新增模板事实/使用reference和主入口路由；区分虚构代码示例与已标记的模板事实清单，不改变业务设计示例要求。DBops和Catalog不改，不复制SQL或通用迁移算法。只读依据为Go模型base/五表DDL、三Template与注册、Admin查询路由、维护文档/脚本和测试入口。

C2 本地校验 verified，Git交付已获授权；C3 最终Draft身份和提交后保护复核以GitHub PR回读为准，不将本地完成等同合并或安装。

C2 离线验证（命令均退出0）：

- `PYTHONDONTWRITEBYTECODE=1 python3 skills/sdkit-skills/scripts/manager.py validate --all`：24 Skill、frontmatter、references与Catalog一致性PASS。未新增Skill，Catalog无需修改。
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_markdown_links.py`：374 Markdown、1242相对链接、2锚点，0错误。
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts -p test_engineering_protocols.py`：17 PASS，既有新旧入口/职责路由静态回归。
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts -p test_markdown_links.py`：7 PASS。
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/sdkit-skills/scripts -p test_manager.py`：37 PASS，仅隔离夹具，不安装实际Skill。
- `git diff --check`：修正文档末尾多余空行后PASS；模板事实与引用路径逐项人工核验PASS。

SKIP：Go/真实PostgreSQL/浏览器/原生Agent行为验收，本轮只改文档且明确禁止数据库操作；不以静态路由检查代替跨Agent发现证明。既有Go PR#5及Skills PR#30的真实验收仅作历史证据，未重跑。DBops整个目录、Catalog及已安装Skill必须保持字节不变；提交与PR最终身份以GitHub回读为准。

保护复核PASS：Go原HEAD/索引/9部署差异/64忽略文件不变；Skills原草稿11文件哈希不变；原8个Go和47个Skills Worktree登记全部保留，旧引用除授权main推进外不变，462个已安装Skill文件哈希不变，历史RANGE候选SHA不变。数据库未连接、未执行SQL，既有验收数据未操作。
