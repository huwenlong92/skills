# 分享对话读取方法

适用范围：读取、总结 `https://chat.deepseek.com/share/...`，排查网页只有摘要，以及在用户要求时把对话整理成笔记。执行或修改上述流程前必须读取本文件。

## 读取入口

必须从用户提供的 URL 解析主机、路径与分享 ID；主机必须为 `chat.deepseek.com`，路径必须为 `/share/<share_id>`（允许末尾斜杠）。查询参数与 fragment 不属于 ID。ID 必须为非空字母、数字、下划线或连字符序列；遇到其他形态必须先核对页面，禁止把任意输入直接拼入 shell 命令。

必须优先请求以下接口；仅当网络不可用、HTTP 或业务状态失败、响应结构变化或正文不完整时，才进入“失败与降级”。不必先抓取分享页 HTML。

```text
GET https://chat.deepseek.com/api/v0/share/content?share_id=<share_id>
```

请求必须使用 `GET`。禁止因抓取失败直接改为 `POST`。必须保留浏览器式 `User-Agent`、JSON `Accept` 和对应分享页 `Referer`，并设置连接及总超时。

这是网页内部接口，不是有稳定兼容承诺的开放 API。2026-09-08 维护时已用历史分享样本实测：顶层 `code` 与 `data.biz_code` 均为 `0`，`data.biz_data.messages` 返回 26 条消息，包含 `USER` 与 `ASSISTANT`。该记录只证明当日样本，不证明其他分享仍然有效。

## 请求与结构验证

以下示例依赖 `curl` 和 `jq`；必须先确认工具可用。缺少 `jq` 时，允许使用已有 Python JSON 解析工具实现相同检查，不必为此全局安装依赖。运行前必须把 `example_share_id` 替换为从实际链接中解析并验证的 ID。

以下命令必须在同一个 shell 会话中执行。原始 JSON 与中间 Markdown 只允许保存在系统临时目录或用户指定的受控输出目录；禁止默认写入技能源目录、业务仓库或知识库。相对输出路径以目标项目根目录为基准。

```bash
set -eu
command -v curl >/dev/null
command -v jq >/dev/null
share_id='example_share_id'
case "$share_id" in
  ''|*[!A-Za-z0-9_-]*) echo 'Invalid share ID' >&2; exit 1 ;;
esac
share_url="https://chat.deepseek.com/share/${share_id}"
# mktemp 使用系统临时目录；保留输出路径供后续读取。
share_workdir="$(mktemp -d)"
share_json="${share_workdir}/content.json"

curl --fail --silent --show-error \
  --connect-timeout 10 --max-time 45 \
  -A 'Mozilla/5.0' \
  -H 'Accept: application/json, text/plain, */*' \
  -H "Referer: ${share_url}" \
  --get --data-urlencode "share_id=${share_id}" \
  'https://chat.deepseek.com/api/v0/share/content' \
  -o "$share_json"

jq -e '
  .code == 0 and .data.biz_code == 0 and
  (.data.biz_data.messages | type == "array" and length > 0) and
  all(.data.biz_data.messages[];
    (.role | type == "string" and length > 0) and
    (.content | type == "string")) and
  any(.data.biz_data.messages[]; .content | length > 0)
' "$share_json" >/dev/null

printf 'Source: %s\nJSON: %s\n' "$share_url" "$share_json"
```

结构检查失败必须停止正常提取，进入“失败与降级”；禁止用空数组、空字符串或页面标题伪装成功。HTTP 200 本身不代表读取成功。

## 提取与完整性检查

必须在上述校验成功后执行。提取必须保持数组原顺序，保留角色与消息 ID，禁止将 `USER` 和 `ASSISTANT` 合并成无来源的结论。消息 ID 不要求连续，禁止仅因 ID 有间隔就判断丢失。

```bash
jq -r '.data.biz_data.messages[] |
  "## " + .role + " #" + (.message_id | tostring) +
  "\n\n" + .content + "\n"' \
  "$share_json" > "${share_workdir}/conversation.md"

# 只看用户问题脉络；不能用这一结果替代完整对话阅读。
jq -r '.data.biz_data.messages[] | select(.role == "USER") |
  "- #" + (.message_id | tostring) + " " + (.content | gsub("\n"; " "))' \
  "$share_json"

# 输出完整性信号，不输出附件内容或额外推理字段。
jq '{
  message_count: (.data.biz_data.messages | length),
  roles: ([.data.biz_data.messages[].role] | unique),
  review_messages: [.data.biz_data.messages[] | select(
    (.incomplete_message != null and .incomplete_message != false) or
    (.status != null and .status != "FINISHED") or
    (.content | length == 0) or
    ((.files // []) | length > 0)
  ) | {message_id, role, status, incomplete_message,
       attachment_count: ((.files // []) | length)}]
}' "$share_json"
```

- 必须读取全部提取出的正文；工具输出被截断时，必须分段读取文件，禁止依据截断输出声称已读完。
- `review_messages` 非空时，必须逐条核对原始 JSON 或浏览器页面，报告空消息、未完成状态和附件的实际影响。必须把这些字段视为检查信号，禁止把未知状态擅自解释为已完成。
- 只允许声称读取了“该分享返回的消息”；禁止推断分享包含原会话的所有轮次。
- `files` 仅说明存在附件引用，不说明已经读到附件。正文依赖附件、图片或其他未提取字段时，必须说明缺失，并按当前工具能力补读或请求用户提供材料。
- 默认提取 `content`，禁止自动把 `thinking_content` 混进助手最终回答。用户明确要求其他公开字段时，必须单独标注并按实际可见内容处理。

## 失败与降级

必须区分环境故障、链接失效和正文缺失；禁止因一次工具失败就断言链接不可读。

| 观察结果 | 必须执行的动作 |
|---|---|
| DNS、代理、网络沙箱或连接错误 | 检查当前环境提供的网络执行方式；存在已授权的联网入口时允许再试一次。禁止把环境故障记成 DeepSeek 接口失效 |
| 超时或服务端 5xx | 允许再试一次；仍失败时停止同一路径，报告错误并使用可用浏览器读取 |
| 401、403、429、验证码或登录要求 | 停止自动重试；禁止索取凭据或绕过限制。浏览器已能正常显示用户获准访问的正文时允许读取，否则请用户提供正文或导出文件 |
| 分享不存在、删除、过期或非零业务状态 | 报告实际状态；禁止猜测正文。请用户提供有效分享或导出内容 |
| 405、HTML、非 JSON、JSON 结构变化或空消息 | 核对实际请求方法；使用可用浏览器检查页面正文。当前工具明确支持网络观测时，允许从该页面实际请求确认新入口；禁止猜造新端点 |
| 只有标题、OpenGraph/meta 摘要或部分正文 | 明确标注“仅摘要／部分正文，全文未取得”；请用户复制正文、导出 Markdown 或提供截图 |

使用浏览器时必须按当前浏览器工具文档读取页面，不得依赖某个 Agent 专有工具名。没有可用浏览器时，必须直接报告受阻原因与所需补充材料。

## 后续处理边界

- 只要求阅读或总结时，必须直接交付阅读结果；禁止自动创建知识库草稿。
- 用户要求同步或整理成笔记时，必须读取目标知识库规则并搜索已有主题，再决定更新或新建。允许写入该规则确定的正文与附件目录；禁止写入工具配置目录或未经指定的新知识库。
- 笔记必须保留分享 URL，并区分用户原始意图、DeepSeek 建议和当前 Agent 的分析。必须提炼长期可用内容，禁止把全部原始 JSON 当作成品笔记。
- 当前产品、API、政策和技术事实必须用官方文档或一手资料核验；无法核验时必须标注“待确认”。禁止把 DeepSeek 回答当作事实依据。
- 敏感数据必须脱敏；禁止把账号凭据、Token、私钥、密码和非公开连接串写入长期笔记或共享 skill。
- 仅摘要或部分正文入库时，必须明确缺失范围，使用目标知识库的草稿状态；没有状态约定时使用 `status: draft`。禁止标记为完整或已验证。

## 完成标准

- 成功：已验证 HTTP／业务状态与消息结构，已读全部可取得正文；最终结果包含来源，并准确说明分享范围、附件或未完成消息等限制。
- 降级：已说明失败阶段、已读范围及缺失内容，没有把 meta 当正文，没有无界重试。
- 入库：仅在用户要求时写入，已遵循目标知识库规则、搜索已有主题、脱敏并保留来源。
- 维护验证：必须运行 skill 校验，检查相对链接；实际请求样本或本地响应夹具必须覆盖成功、业务失败、空消息和结构变化。人工检查角色顺序、输出截断与附件缺失说明。
