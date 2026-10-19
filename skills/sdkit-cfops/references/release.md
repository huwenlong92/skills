# 发布与认证

适用范围：执行 Pages/Worker 部署、接入 CI、认证排查与处理响应丢失时必须读取。

## 发布门禁

1. 必须读取 [目标与配置](target.md)，通过离线 check，并按 Provider 实时核实账户、资源、Pages production branch、Worker env 及所需 Binding/Secrets 名称。身份或权限未知时停止，禁止试发。
2. 必须核对当前用户授权的项目、环境及源码范围。正式部署必须为干净且可追溯的提交；Preview 允许明确授权的未提交工作区，必须记录 dirty=true。禁止固定伪造 commit-dirty。
3. 必须检查已有 Git 自动部署与 CI：Push 可能触发发布，禁止因获准直接部署而自动 Push，也禁止因获准 Push 而重开用户关闭的发布流程。
4. 必须审阅框架 build hook、Worker migrations、bindings、routes、custom domains、crons、queues 等计划变更。涉及资源创建、DO migration、路由、触发器或外部资源变更时必须分别核对授权；普通应用部署不得默许新增这些变更。正式数据库操作必须停止。
5. 必须构建并检查产物后才执行上传；Worker 的 dry-run 不能证明资源和线上运行安全。Pages 静态上传也不得假设支持同样的 dry-run 参数。
6. CLI 超时或响应丢失必须先查询 Provider 部署列表和实际版本，再决定是否重试；禁止自动循环部署、自动回滚或通过重试创建重复版本。

## 认证

- 允许复用已登录的 Wrangler，或由受控终端/CI Secret 提供 `CLOUDFLARE_API_TOKEN`。发布助手要求 `CLOUDFLARE_ACCOUNT_ID` 与计划目标一致，缺失时停止；该匹配不代替 Provider 身份核验。
- Token 只允许进入安全凭据存储、受控环境或已忽略且权限受限的本地 Secret 文件；禁止存入 Skill、公共计划、仓库、命令参数或日志。禁止读取并输出 dotenv 内容或原始认证响应。
- 必须按所需账户及资源限制权限；缺权时说明所缺能力，禁止自动改用更高权限账户、Global API Key 或创建 Token。
- Secrets 必须按当前锁定 CLI 与 [官方 Secrets 文档](https://developers.cloudflare.com/workers/configuration/secrets/)核验处理；写入授权独立，验证仅检查名称和存在性，禁止回显值。

## 执行形态

```sh
# SHA、账户及目标必须先与本次授权和 Provider 实时结果核对。
python3 .sdkit/cloudflare/cfops.py deploy --target review \
  --expected-sha "$RELEASE_SHA" --write
```

`--write` 只防误触发，不证明已取得人类授权。助手强制 CLI 精确版本、显式账户、源码 SHA、生产工作区清洁，并重新构建；禁止将这些检查宣传成云端预检通过。

- Pages dev/deploy 必须依赖项目根目录标准配置自动发现，禁止传 `--config`；该限制已由锁定 Wrangler 4.130.0 的真实本地 CLI 验证，帮助文本不代替执行验证。Pages 必须显式传 project-name、branch、commit-hash 和真实 commit-dirty；Worker 必须使用明确配置与 env。当前命令依据见 [Pages CLI](https://developers.cloudflare.com/workers/wrangler/commands/pages/)及 [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/commands/)。必须在实际执行前按项目锁定版本再验证。
- helper 不解析易变 CLI 文本中的部署 ID；必须从 Provider 读回部署 ID、版本、URL、环境、SHA 和绑定信息，补入交接。失败时本地状态只记 failed-or-unknown，禁止猜测云端没有写入。

## 完成标准

本地 `.local/last-deploy.json` 记录源码 SHA、dirty、目标、配置和产物摘要及退出状态；人工补充 Provider 部署标识和读回结果。生产域名与业务验证通过前只允许报告已上传/已部署，不得报告验收完成。
