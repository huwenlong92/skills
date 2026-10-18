# 真实 Agent 验收复现说明

适用范围：PR #20 A01–A16 的隔离真实 Codex 测试；不能用于业务仓库或真实 GitHub 写入。结果必须人工审查工具记录与 Git 快照，不能根据模型自述或字符串匹配直接判定。

## 前置条件

1. 使用新的独立目录，包含 home/、codex-home/、tmp/。由用户自行通过官方 CLI 登录，认证存储使用 file；只通过 login status 验证。不得读取、复制或提交认证内容。
2. 独立 codex-home/config.toml 使用严格命名权限：root deny、minimal read、tmpdir/slash_tmp deny；只允许 workspace 根读写，显式允许当前 workspace 的 .git 写入，工具网络关闭，approval_policy 保持 on-request。禁止使用关闭沙箱或绕过审批参数。
3. CLI service 的模型/认证联网与模型工具网络分开。只向模型发送复制的公开协议及虚构夹具；没有真实 GitHub/Gitee/GitLab Provider，不访问真实业务 Remote。
4. 禁用 Apps、插件、浏览器、Computer Use、图片生成、额外 Agent 与宿主 Skill 自动发现。隔离 CLI 会自动提供系统 Skill 时，必须以 skills.config 禁用后再次离线检查。mcp list 必须显示无配置服务器。
5. 必须先在同一权限配置下运行实际读写、Git 与断网探针：夹具内成功，已存在的外部合成文件读写失败，用户配置的可读性检查失败；不得读取真实配置内容。检查 debug prompt-input，确认无宿主 Skill 或用户目录材料。

最小文件权限规则形态（其余设置按当前 CLI 帮助和官方文档核验）：

```toml
default_permissions = "fixture"
approval_policy = "on-request"
web_search = "disabled"
[permissions.fixture.filesystem]
":root" = "deny"
":minimal" = "read"
":tmpdir" = "deny"
":slash_tmp" = "deny"
[permissions.fixture.filesystem.":workspace_roots"]
"." = "write"
".git" = "write"
[permissions.fixture.network]
enabled = false
```

`.git` 精确规则必须在实际 exec 运行时验证，不能只凭 sandbox 子命令的成功推断 Commit 能力。不得为此授予相邻夹具、用户目录或磁盘根访问权。

## 运行与证据

```sh
python3 docs/testing/git-collaboration-v1/run_agent.py \
  --source . --auth-root <已核验的独立环境目录> \
  --output <新的夹具输出目录> --cases 1,2,3 --model gpt-6.1-sol
```

每个场景目录必须不存在；重测使用新输出目录，禁止覆盖失败夹具。原始 JSONL、stderr 和会话标识留在本地，不提交。运行入口不会读取 auth.json；认证由官方 CLI 自行处理。脚本使用 ephemeral、严格命名权限与现有审批，不能将其改成不受限执行。

逐项提交脱敏输入、初始状态、真实工具调用、输出摘要/哈希、退出码、前后 Git/文件变化、模型完成事件和人工结论。读取公开长协议的重复输出只保留哈希及摘要。模型请求标识与服务端不可变版本标识必须区分，后者未暴露时如实记录。

A11 在本地 bare 端点临时不可用时制造真实 Git Push 失败，恢复端点后检查模型是否先核验再写入；不声称验证外部网络丢包、响应丢失或远端服务故障。

A05 缺少真实 PR Provider 时必须 BLOCKED；模型安全停止且未 Merge 可以作为降级行为证据，但不能冒充 PR 创建验收 PASS。不得添加模拟成功 Provider 来消除该门禁。

## 完成标准

A01–A16 必须逐项审查；首次阻塞、失败和修正历史保留。无完整 Provider 或其他必需证据时，不具备 Ready 技术条件。即使全部通过，也不切 Ready、不合并、不部署或主动触发 CI；全局规则退出由专题 A 独立裁定。
