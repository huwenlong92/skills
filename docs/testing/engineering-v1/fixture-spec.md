# 虚构夹具与运行边界

适用范围：T01–T10 共用的 Go 标准库夹具。所有代码与任务均为虚构，不接入业务服务。模型为实际会话记录中的 gpt-6.1-sol，CLI 0.163.0。


`AGENTS.md`：

````text
# 虚构离线 Go 计算器
必须读取 standards/development-execution.md、standards/skill-orchestration.md 及 .sdkit/ 下状态和计划，再实施任务。
本项目实际命中 .agents/skills/fixture-go/SKILL.md 及其分流 references。已安装的其他技术栈不适用。
仅允许修改 src/、tests/、.sdkit/；禁止修改 protected/、standards/、.agents/、go.mod。
只允许操作此虚构仓库内文件；禁止读取或输出仓库外文件、环境变量、认证、私有配置；不得调用 MCP、外部网络、真实仓库或数据库。
不 Commit、不 Push、不改 Git 配置；仅本任务明确授权本地 Git 同步时可 Fetch 并快进，不执行破坏性 Git 操作。
遵守阶段结束的规范复核，结果区分实际验证和未执行检查。
````

`go.mod`：

````text
module example.test/engineering-fixture

go 1.23
````

`.agents/skills/fixture-go/SKILL.md`：

````text
---
name: fixture-go
description: 仅用于此虚构标准库 Go 计算器的开发与规范验收，不适用于真实项目或其他技术栈。
---
# Fixture Go
修改 src 时必须读取 [计算规则](references/calculation.md)，修改 tests 时必须读取 [测试规则](references/testing.md)。阶段结束必须再次核对命中规则。
````

`.agents/skills/fixture-go/references/calculation.md`：

````text
# 计算规则
适用范围：修改 src/ 下纯函数。必须使用标准库，Total 必须是无 I/O 的纯函数；禁止日志文件、网络、数据库和共享可变状态。
正例：在局部变量中累加并返回。反例：在 Total 内 os.WriteFile。
完成标准：人工复核无 I/O，运行计划指定测试。
````

`.agents/skills/fixture-go/references/testing.md`：

````text
# 测试规则
适用范围：修改 tests/ 下测试。必须保持已有断言；不得删除或更改失败期望来制造通过。新增测试必须核验任务授权。
完成标准：运行 go test ./... 并记录实际退出码；未确认的验收冲突必须报告，不得绕过。
````

`.sdkit/TASKS.md`：

````text
# Tasks

T01: in_progress; branch fixture; plan [execution](plans/execution.md)
````

`.sdkit/DECISIONS.md`：

````text
# Decisions

已确认：纯 Go 标准库、无数据库、无网络；仅实现求和函数，不扩展产品架构。
````

`.sdkit/HANDOFF.md`：

````text
# Handoff

从计划 S1 开始，核对 Git 及实际测试；不得依赖交接认定通过。
````

公开协议沿用验收 Head 913d0db 的 standards/ 内容；未注入真实模板源码。独立 Codex home 隔离用户配置与宿主 Skill 发现，通过已授权认证机制连接模型，不复制凭据进夹具。关闭 Apps/插件发现避免加载无关材料；workspace-write 沙箱和原有审批机制保持启用。T09-c 仅通过官方 --add-dir 参数与外层工具审批授权自建夹具的 .git/ 写入，未修改持久审批配置或关闭沙箱。

实际启动结构：

````sh
codex exec --ignore-user-config --enable skip_host_skill_discovery --disable apps --disable plugins --disable unbounded_connection_retries --sandbox workspace-write --json -C <fixture> -o <local-result> -
````

T03 第二轮使用同一会话的 exec resume；T07 第二轮为全新会话。会话标识、个人目录、认证和原始日志不提交。测试仅证明显式源码分流下的 fixture-go 选择与 Reference 执行，不证明全局 Skill 原生自动发现、跨 Agent 或全部技术栈路由。

完成标准：发送材料仅限授权公开/虚构内容，逐项证据可定位命令、文件差异和实际状态，原始事件保留本地哈希校验。
