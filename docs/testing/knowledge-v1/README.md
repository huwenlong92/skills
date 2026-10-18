# Knowledge Retrieval & Capture V1 本地行为验收

适用范围：PR #19 的真实 Codex 自然语言选路、来源检索、知识分类、候选去重和授权边界验收。静态检查与真实行为必须分别报告。

## 材料与边界

- `run_behavior.py` 必须从完整 skills 源仓库读取 Foundry、WikiOps 和两份公开协议，仅在调用者明确指定的临时输出目录创建虚构材料。
- 虚构产品为 LumaNote（别名星笺），虚构远端统一使用 `example.invalid`；产品和知识资料均由脚本生成，不来自真实私有仓库。
- Skill 必须逐字复制当前源文件；显式 Active Workspace 将资料读取限定在夹具内，不改写 Skill 默认配置，不读取个人配置。
- 必须使用隔离的 Codex home 与正常授权的认证机制；不得复制凭据进夹具、证据或仓库。脚本不配置认证，不读取认证内容。
- 运行环境必须保持 Codex 沙箱与审批机制启用；禁止使用绕过沙箱、绕过 hook trust 或忽略审批规则的参数。必须隔离宿主 Skill、Apps 与插件，禁止连接真实产品或知识库。
- 项目 AGENTS.md 提供协议入口和虚构 Workspace，不在用户场景中点名 Foundry/WikiOps，也不预置正确回答。实际 Skill 加载以工具命令中的 SKILL.md/reference 读取为证据，不能仅凭模型自述判定。
- 每个场景必须使用新会话；第 13 项必须用同一会话真实续接十轮；`--sandbox` 必须同时传给首轮与 `exec resume` 的父命令，逐轮核对会话元数据，不得假定续接自动继承。普通闲聊与通用概念问答不得注入历史资料正文。

## 运行方式

由调用者在仓库外准备隔离 Codex home，并通过进程环境提供 `CODEX_HOME`。运行入口：

```sh
python3 docs/testing/knowledge-v1/run_behavior.py \
  --source . --output <独立临时目录> --model gpt-6.1-sol
```

可用 `--cases 1,2,3` 选择尚未执行的场景，使用 `--sandbox workspace-write` 在仍启用沙箱的虚构目录中补测具备本地写入能力时的授权边界；输出目录内已有同名场景时必须停止，禁止覆盖已有夹具。脚本使用真实 `codex exec`/`exec resume`，超时或模型失败不能算通过。

## 证据审查

- 原始 JSONL、stderr、会话 ID 与运行目录必须留在临时目录；只能提交审查后的 `Cxx-evidence.json`，其中记录输入、响应、工具命令、退出码、完成事件、命令输出与原始日志 SHA-256、文件未改动检查。重复的完整命令输出留在本地原始日志，不提交第二份 Skill 正文。
- 提交前必须搜索个人路径、会话标识和敏感内容，核对命令中没有真实仓库访问、外部网络或写入尝试；模型返回的来源必须与实际读过的文件相符。
- 模型版本必须记录 CLI 请求值与隔离会话 `turn_context.model`；无法取得服务端不可变版本标识时必须说明。
- 夹具证据只证明指定项目协议、Skill 安装与虚构 Active Workspace 下的行为，不能宣称未配置全局环境或其他 Agent 已验证，也不能代替真实仓库实时身份、权限与同步验收。

## 完成标准

必须按 [16 项场景基线](../../../standards/knowledge-retrieval-capture-acceptance.md) 逐项人工核对通过、失败或未执行；记录实际 Skill 与来源。授权边界须同时检查文件快照未改动和工具记录无写入尝试，不能仅凭沙箱阻止写入判定模型正确。
