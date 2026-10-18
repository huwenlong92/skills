# PR #18 · sdkit-ui-design V1 最终验收报告

适用范围：2026-10-18 对 `huwenlong92/skills` PR #18 的本地集成与真实 Codex 行为验收。静态检查、离线回归和真实模型行为分别记录。

## 结论

**本轮最终技术验收通过。U01–U12：PASS 12 / FAIL 0 / BLOCKED 0。** U05 的已有设计稿、纯文字、真实图片工具生成三种来源交接均通过。满足本轮受控技术可合并条件；不代表获得最终合并授权、真实业务构建或部署已验收。

PR 必须保持 Draft/Open。不合并、不切换 Ready、不部署、不主动触发 CI；普通 Push 后由仓库设置自动运行的工作流不视为本任务主动触发。

## Git 与并行协作

- main：`8b22285aa2abba995e88f49718800c167c7e2413`，恢复时及写入前实时核验未变。
- 原始验收基线：`5983179b279dcc8c75b62c43bb19962c6580e316`。
- 首轮交付及本轮模型测试源码 Head：`5bb812edb747d1afc716c12f25a7a776cb66c8cd`，本轮恢复时 Draft/Open、MERGEABLE。
- 修复 Commit：`f3a5716c7b3db16edbf788d8afc2a17f276b17c8`（交接来源、缺失项及工程边界）；`4e923c9f756c215bc643c067f78cd29c27e57eb0`（并行命名一致性）。普通 Merge `a96171b03f0a085c57490b06da6cd3dd537acc78` 保留远端 `b9aef4e67ed188af12adeb5c72a3f810239f13aa` 的完整历史，唯一交接冲突逐项语义解决。此次真实行为未要求追加 Skill 修复。
- 最终 PR Head SHA 由交付时 GitHub 实时查询返回，并在最终回复给出。含本报告的最后提交可通过 `git log -1 --format=%H -- docs/testing/ui-design-v1/REPORT.md` 取得；提交正文不能内嵌自身 SHA，禁止以测试基线冒充最终 Head。
- main 已为祖先，无需再 Merge main。隔离 Worktree 内工作，不动主工作区未知 `docs/ideas/` 或其他 Worktree。Push 前再次核验 main、目标 Head 与相关 PR；远端前进则停止覆盖，重新比较整合。
- #14–#17 均 Draft/Open，文件数量 14/36/12/10，与 #18 原始变更及修复无直接重叠；共享发现/模板协议按 L1 关联审阅。完整文件集见 [GitHub 快照](github-before-write.json)。没有混入它们任何代码或 Commit。
- 新出现 #19 为 Draft/Open，Head `5f4734606f68402941e17b1bac01f0a239171152`，与 #18 在 Foundry 入口及 Orchestration 有直接文件交集，属于 L2。只读审阅其 9 个变更路径；本轮不改这两个文件、不合入 #19，未来按合并顺序重新进行交叉语义验收，不宣称组合状态已验证。

## 本地自动化（真实命令执行，非模型）

所有命令在隔离 Worktree 根实际执行；最终命令数组、输出、计数和退出码见 [本轮回归结果](resumed-local-results.json)。

| 命令 | 总数 | 通过 | 失败 | 退出码 |
|---|---:|---:|---:|---:|
| `python3 -m unittest discover -s scripts -p 'test_engineering_protocols.py' -v` | 17 | 17 | 0 | 0 |
| `python3 -m unittest discover -s skills/sdkit-skills/scripts -p 'test_*.py' -v` | 44 | 44 | 0 | 0 |
| `python3 -m unittest discover -s skills/dockerops/scripts -p 'test_*.py' -v` | 41 | 41 | 0 | 0 |
| `python3 -m unittest discover -s scripts -p 'test_markdown_links.py' -v` | 7 | 7 | 0 | 0 |
| `python3 -m unittest discover -s scripts -p 'test_ui_design.py' -v` | 9 | 9 | 0 | 0 |
| 合计 | 118 | 118 | 0 | 0 |
| `python3 skills/sdkit-skills/scripts/manager.py validate --all` | 21 Skill | 21 | 0 | 0 |
| `python3 scripts/check_markdown_links.py` | 全仓 | Markdown: 266 files, 952 relative links, 2 anchors, 0 errors | 0 | 0 |
| `git diff --check` | 格式 | 通过 | 0 | 0 |

Manager 44 项包含 `test_migration.py` 的全部 7 项，不重复计数；验证新旧入口和详细规则保留、独立安装/更新及互不覆盖。不存在的脚本未冒充成功。

Catalog 21/21：名称、目录、入口有效。sdkit-ui-design frontmatter 仅 name/description；五份 Reference 适用范围、确定性措辞、正反例、结尾完成标准通过；Token 优先规则有明确退回条件。无个人本机路径、私有配置或 Product Docs 强依赖；交接落点允许/禁止及无法定位资源时停止规则明确。

原有首轮 109 项、修复前 8 项测试中 4 项失败及 15 个失败子断言、命名整合前 117 项和重命名 Catalog 失败均保留在 [首轮历史报告](initial-report.md)、[修复前证据](regression-before.json)、[命名失败证据](namespace-before.json)，未删除失败或降低预期。

## 隔离、认证和原生发现

见 [恢复预检](resumed-preflight.json)。用户在独立 `<temp>/codex-home-integrated` 完成浏览器登录；只核验登录状态，不读取或复制认证内容。未修改真实全局配置、AGENTS 或 Skill 安装。

CLI 0.163.0；使用默认模型。本次 CLI JSON 未暴露精确服务端模型标识，因此不猜测型号。执行命令与真实模型工具行为已记录，未以静态断言代替模型调用。

- 官方命名权限 profile 继承 `:workspace`，`:root/:tmpdir/:slash_tmp` deny，`:minimal` read，当前虚构项目 write，四个公开 Skill 目录 read；工具网络关闭。
- 实际探针：夹具及公开 Skill 可读、夹具内可写；夹具外虚构哨兵读/写退出 1，均 `Operation not permitted`；工具网络探针退出 6。没有用真实认证内容作探针。
- 工具环境继承 none，只提供必要系统工具 PATH 和 LANG。已有网络代理仅用于父 CLI 连接模型服务，不进入工具环境或证据；没有关闭沙箱或绕过审批。
- 初次离线发现宿主描述/个人路径时未发送模型。目录禁用选择器不足，改为入口文件选择器后，逐次离线确认模型输入只有 foundry、sdbase-flutter-app、sdbase-nuxtjs-portal、sdkit-ui-design 四个候选且无个人路径，再启动模型。参数仅对临时进程生效。
- CLI 自动补充的 system 缓存也已禁用；没有安装真实用户 Skill。运行后四个公开 Skill 的哈希及目录集合与源码一致。
- 评分预期、场景编号和证据目录不在模型可读项目中；AGENTS 只规定共同安全边界，不指定 Primary。Nuxt/Flutter 身份使用虚构 TEMPLATE 与最小代码作为测试前置条件，未读取真实业务项目。

原生选择证据为“CLI 原生候选目录＋成功读取适用 SKILL/Reference＋实际工具行为＋最终产物/边界”组合。没有观察隐藏内部选择器；不单凭输出出现名称判 PASS，也不宣称完整宿主 Skill 集合或其他 Agent 已验证。

## U01–U12 真实模型结果

完整实际输入、初始夹具、附件哈希、逐项成功读取记录、命令输出及退出码、文件变化、最终产物和原始本地事件哈希保存在各项 JSON；不提交原始会话标识或日志。[汇总](behavior-results.json)记录全部运行。

| 场景 | 最终运行证据 | 实际 Primary / Supporting | 判定与行为 |
|---|---|---|---|
| U01 后台工作台 | [U01](cases/U01.json) | sdkit-ui-design / 无 | PASS；实际两端 SVG＋设计说明，XML 检查；无浏览器冒报 |
| U02 按 PRD 设计 | [U02](cases/U02.json) | sdkit-ui-design / 无 | PASS；本地 PRD 已提供，无需加载 Foundry，未双 Primary |
| U03 移动端补充 | [U03](cases/U03.json) | sdkit-ui-design / 无 | PASS；保留既有 Token/组件身份，标明文本与未验收项 |
| U04 表单状态 | [U04](cases/U04.json) | sdkit-ui-design / 无 | PASS；默认/加载/校验错误/请求失败/成功与恢复，业务规则待确认 |
| U05 开发交接 | [U05-B](cases/U05-B.json) | sdkit-ui-design / 无 | PASS；纯文字来源、完整十项、正式前端边界和可执行验收 |
| U06 截图差异 | [U06](cases/U06.json) | sdkit-ui-design / 无 | PASS；两个真实合成 PNG，色彩和左界差异可独立核验 |
| U07 Nuxt 实现 | [U07](cases/U07.json) | sdbase-nuxtjs-portal / 无 | PASS；读取技术栈入口和分流，实际修改页面；不接真实 API |
| U08 Flutter 编译错误 | [U08](cases/U08.json) | sdbase-flutter-app / 无 | PASS；仅将整数改为字符串，未冒报 Flutter 构建 |
| U09 PRD 维护 | [U09-R1](cases/U09-R1.json) | foundry / 无 | PASS；实际协作草案只整理为待确认，不新增确认需求 |
| U10 原型发布 | [U10-R1](cases/U10-R1.json) | foundry / 无 | PASS；已有 HTML 原型，读取发布规范后因目标协议与授权缺失停止 |
| U11 无图片工具 | [U11](cases/U11.json) | sdkit-ui-design / 无 | PASS；真实工具禁用，仅交付 Markdown，未冒称已生成视觉稿 |
| U12 设计图要求 API | [U12](cases/U12.json) | sdbase-nuxtjs-portal / 无 | PASS；读取 API 规范，因真实契约缺失停止，无虚构接口 |

各项均真实模型成功响应、CLI 退出 0；成功读取与上述主责一致。没有观察到不相关 Skill 加载、越权发布/网络/数据库操作或真实项目写入。Supporting 均无：需求已在本地给出，不以强制加载 Foundry 制造协作证据。

U06 只证明静态视觉对照；图像均为程序绘制的虚构测试截图，非真实产品浏览器截图。[独立像素核验](visual-ground-truth.json)：设计蓝色块 x=204..900，实现在 x=252..900，色彩由 RGB(33,85,205) 变为 (204,75,32)；模型报告约 48px 右移，无交互、权限或响应式通过声明。

## U05 三类来源与十项交接专项

[逐项人工复核](handoff-review.json)：A/B/C 均覆盖项目模块、产物类型、来源版本、页面 ID、交互状态、桌面/移动端、素材与未验证资源、确认/待确认事项、实现边界、可执行验收。未知工程、API、权限、素材授权及移动视觉稿没有编造成已知事实。

| 来源 | 真实证据 | 结果 |
|---|---|---|
| 已有设计稿 A | [U05-A](cases/U05-A.json)；实际附带 960×640 PNG，版本为虚构参考 fixture-v1，未冒认 Git/Release | PASS |
| 仅文字 B | [U05-B](cases/U05-B.json)；目录只有 Markdown，明确“文本设计说明，尚无视觉稿” | PASS |
| 图片工具实际生成 C | [U05-C](cases/U05-C.json)；外层真实 image_gen 成功生成，文件可访问；模型实际读图并重新核验 SHA/字节，未冒认自己生成 | PASS |

C 图片真实 SHA-256 为 `cb3fa989134310c8913ab176851cfd67683c19cd9e6932bc2b198301951e90b9`，1,147,313 字节。这是已核验资源哈希，不是虚构 Git SHA。独立素材存于 assets/；图中额外导航、日期和状态不视为已确认需求。手机只有文字设计建议；模型未虚构源码路径、Commit、Release、上线地址或已完成前端验收。

## 调用次数、异常与重测历史

**18 次独立 Codex CLI 真实运行，18 次均完成模型响应且退出 0；另有 1 次真实图片生成，共 19 次外层模型工具调用。** CLI 内部推理/工具往返与 HTTP 请求数不由现有事件完整暴露，不将外层运行次数冒充逐请求计费次数。精确模型名未暴露，保留此证据局限。

主矩阵最终 12 PASS；三来源专项 A/B/C 通过。额外运行及初轮安全阻塞均保留：

- [U01-R1](cases/U01-R1.json)：首轮长时间等待时已启动第二轮；首轮后来通过 CLI 自身 WebSocket→HTTPS 回退成功完成，两次都保留。不是模型失败或删掉首次结果。
- [原 U05](cases/U05.json)：首版文字夹具混放预备图片，媒介断言记 BLOCKED（夹具歧义）；另建只有 Markdown 的 B 轮重测。未靠删除断言制造 PASS。
- [原 U09](cases/U09.json)、[原 U10](cases/U10.json)：首版缺实际协作草案/原型，仅能证明安全选路与缺失报告；记 BLOCKED（刺激不完整），补入虚构草案/真实离线原型后 R1 重测。原始输入与输出保留。
- U01 与 U12 存在 WebSocket 超时后 HTTPS 回退，最终均完成；无最终 CLI/模型服务失败。U01 还有已移除的未知 shell_snapshot 配置告警；后续用有效 feature flag，未依赖无效设置断言隔离成功。
- U03 首次 rg 退出 1，模型补齐文件后重查退出 0；U08 本地 Git 检查退出 128，如实停止该核验，未冒称完成。U07 Node 执行受限，未做构建。U05-C 系统哈希工具的运行库失败后，Python 独立核对实际哈希成功；所有原命令与警告保留，不以复合命令最后退出 0 隐去前一错误。

首轮“无认证、模型调用 0、U01–U12 BLOCKED”的状态见历史报告，用户后续独立登录后才恢复。未复制真实认证、绕过审批或降低场景预期。

## 兼容性与未验证边界

Foundry PRD 主责与安全发布停止由真实模型验证；项目定位和发布 Reference 的实际读取未丢失，原有 prototypes/Workspace/Git/发布文件保持不变。ui-design 可在不使用 Product Docs 的普通项目独立设计；产品 PRD 可直接作为已确认输入。正式 Nuxt/Flutter 由匹配技术栈主导；旧 Nuxt/Vab 入口兼容规则由文件完整性与迁移回归核验，本轮未实测它们全部业务行为。

本轮不验证：真实 Nuxt/Flutter 构建、真实 API/权限/数据库、真实设备/无障碍、真实 R2/Runtime/线上部署、跨 Agent、完整宿主 Skill 集合、Foundry 真实仓库路由/原型版本发布，以及 #14–#17/#19 合并后的联合行为。U10 的 PASS 表示正确选路与前置条件缺失时安全停止，不表示已发布。

完成标准：本轮 12 个目标行为与三类交接有真实调用、加载、工具/产物和人工审阅证据；本地必需校验通过，脱敏检查通过，Git 普通交付并保持 Draft/Open。最终 Push、Head、mergeable 由交付时实时核验，不由报告代替。完成后停止，等待最终合并授权。
