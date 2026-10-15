---
name: ds-share-read
description: 分享 URL 校验、GET 请求、本地响应提取、完整性信号与失败降级。
---

# 分享读取与完整性

适用范围：读取、导出或总结 DeepSeek 分享链接，以及排查只有摘要、接口失败和正文不完整。笔记写入必须另外读取[笔记与知识库](notes.md)。

## URL 与请求入口

- 必须校验用户提供的 HTTPS URL，主机为 chat.deepseek.com，路径为 /share/<share_id>，允许末尾斜杠、查询参数和 fragment，但查询参数和 fragment 不属于 ID。ID 必须是非空 ASCII 字母、数字、下划线或连字符；禁止用户信息、非 443 端口、其他主机与路径。
- 必须先使用下面的 GET 内部接口；仅当网络/HTTP/业务失败、结构变化或正文不完整时进入降级。不要求先抓分享页 HTML，禁止因失败直接改为 POST 或猜造端点。
- 该接口没有稳定兼容承诺，必须以本次 HTTP、业务码和响应结构为准；历史成功样本不能证明当前分享有效。本次维护的离线夹具只验证提取逻辑，不证明在线接口可用。

```text
GET https://chat.deepseek.com/api/v0/share/content?share_id=<share_id>
```

以下形态依赖已有 curl 与 Python 3.9+。share_tool 必须替换为实际技能目录中的脚本路径，share_url 必须来自当前用户提供的链接。禁止安装全局依赖来替代可用的标准库解析。

```bash
set -eu
command -v curl >/dev/null
command -v python3 >/dev/null
share_tool='<skill-dir>/scripts/extract_share.py'
share_url='https://chat.deepseek.com/share/example_share_id'
share_url="$(python3 "$share_tool" --source "$share_url" --check-url)"
share_id="${share_url##*/}"
share_workdir="$(mktemp -d)"
share_json="${share_workdir}/content.json"
share_http="$(curl --fail --silent --show-error \
  --connect-timeout 10 --max-time 45 \
  -A 'Mozilla/5.0' \
  -H 'Accept: application/json, text/plain, */*' \
  -H "Referer: ${share_url}" \
  --get --data-urlencode "share_id=${share_id}" \
  'https://chat.deepseek.com/api/v0/share/content' \
  --write-out '%{http_code}' -o "$share_json")"
test "$share_http" = 200
python3 "$share_tool" --source "$share_url" --input "$share_json"
```

- 请求必须保留浏览器式 User-Agent、JSON Accept、对应分享页 Referer，以及连接/总超时。禁止索取登录凭据；HTTP 不是 200 时必须进入降级。
- 原始 JSON 与中间 Markdown 只允许保存到系统临时目录或用户指定的受控输出目录，相对路径以目标项目根目录为基准；禁止默认写入 skill、业务仓库或知识库。
- 本地[提取工具](../scripts/extract_share.py)不联网，校验后写入独立临时子目录，返回路径与检查摘要；--output-parent 仅允许指向已存在、由用户确认的受控目录。禁止因工具返回零就声称 HTTP 已验证或全文已取得。

## 结构与提取

- 必须核对顶层 code 和 data.biz_code 均为整数 0，data.biz_data.messages 是非空数组，每项有非空白字符串 role 与字符串 content，且至少一项正文非空白。message_id 存在时只接受字符串或整数，其他形态按结构变化处理。不满足时必须停止正常提取，禁止用空数组、页面标题或默认空字符串伪装成功。
- 必须保持数组原顺序、原角色和可取得的 message_id；ID 有间隔不构成消息丢失证据，缺少 ID 时必须标记未提供，禁止生成一个 ID 冒充原始值。导出中的 position 只表示返回数组顺序。
- 默认只提取 content；禁止将 thinking_content 或附件引用混入正文。用户明确要求其他公开可见字段时必须单独处理并标注来源，不能自动扩大读取范围。
- conversation.md 是供阅读的完整返回正文，summary.json 仅含来源、数量、角色和复核信号；两者禁止取代彼此。原始 JSON 必须保留到必要复核完成，禁止将全部 JSON 直接当成笔记。

## 完整性复核

- 必须读取全部提取正文；工具输出被截断时必须分段读取，禁止根据标题、用户问题列表或截断输出声称已读完。
- review_messages 非空时必须逐条核对原始字段或浏览器页面。空正文、未完成标志、缺失/未知 status、未知角色、缺少 ID 与附件结构异常是复核信号，不能直接当成接口失败或已经完成。
- files 只表示附件引用，工具不读取附件。正文依赖附件、图片或其他未提取字段时必须说明缺失；只有当前工具能够且用户已授权访问对应材料时才允许补读，否则请求用户提供材料。
- 即使没有复核信号，也只能声称读完“该分享返回的消息”，禁止推断原始会话全部轮次已经取得。人工复核后的影响必须写入交付，禁止仅输出消息数量就宣称完整。

正向形态：HTTP 与业务校验成功后读取全部正文，保留角色与顺序，并说明“已读该分享返回的消息；其中附件尚未读取”。反例：接口返回 200 或网页 meta 有摘要，就声称已经读完原会话。

## 失败与降级

| 结果 | 必须执行的动作 |
|---|---|
| DNS、代理、沙箱或连接错误 | 区分本机网络故障与接口错误；有已授权联网入口时允许再试一次，禁止把环境故障写成链接失效 |
| 超时或 5xx | 只允许再试一次；仍失败停止同一路径并使用可用浏览器 |
| 401/403/429、验证码或登录要求 | 停止自动重试，禁止索取凭据或绕过限制；浏览器正常显示已获准正文时允许读取，否则请用户提供正文/导出 |
| 分享删除/过期/不存在或非零业务码 | 报告实际状态，禁止猜测正文；请用户提供有效分享或导出 |
| 3xx、405、HTML、非 JSON、结构变化或无可读消息 | 核对真实请求和页面正文；工具明确支持网络观测时，允许从页面实际请求确认入口，禁止猜造新端点 |
| 只有 meta/OpenGraph、标题或部分正文 | 明确“仅摘要/部分正文，全文未取得”，请求用户复制、导出或提供截图 |

- 同一路径的自动重试总计最多一次，禁止在环境切换与超时分支之间累计重试；仅有新的用户输入或明确修复后才允许重新开始。
- 浏览器必须按当前工具文档使用，不依赖某个 Agent 专有工具名；无浏览器时直接报告失败阶段与所需材料。

## 完成标准

- 成功：HTTP、业务和结构验证通过，已读全部可取得正文，交付包含来源、分享范围及复核结果；附件未读取与字段缺失均准确说明。
- 降级：报告失败阶段、已读范围和缺失内容，没有把 meta 当正文或无限重试。
- 维护必须运行 skill 校验、链接检查和 `python3 <skill-dir>/scripts/test_extract_share.py`；离线夹具必须覆盖成功、业务失败、空消息、结构变化、顺序/ID与附件信号。
- 人工检查真实界面与接口差异、输出截断及附件依赖；没有真实分享时只能报告离线验证通过，禁止声称在线接口已验证。
