---
name: deepseek-usage-rules
description: 凭据来源、快照数据、消耗算法与边界条件
---

# 用量规则

## 凭据

- 依次读取 `DEEPSEEK_API_KEY`、`ANTHROPIC_AUTH_TOKEN`，命中即用，只在请求头中使用，禁止输出。
- `ANTHROPIC_AUTH_TOKEN` 可能是其他平台的密钥；接口返回 401/403 时报告凭据来源名称并提示改用 `DEEPSEEK_API_KEY`。
- 端点固定为 `https://api.deepseek.com/user/balance`，不接受自定义 Base URL，避免把密钥发往未核实主机。
- 解释器自带 CA 与接口证书链不匹配时（macOS 的 python.org 构建常见），仅在证书校验失败场景改用 `DEEPSEEK_CA_BUNDLE`（缺省 `/etc/ssl/cert.pem`）重试一次；不关闭校验、不改代理。

## 快照

- 数据文件：`$XDG_STATE_HOME/sdkit-skills/deepseek-usage/snapshots.jsonl`，未设置时为 `~/.local/state/...`；每行一个 JSON 对象。
- 字段：`ts`、`date`（本地日期）、`total`、`topped_up`、`granted`、`currency`。
- `report` 每次运行先追加一次快照，因此统计精度取决于调用频率；只跑过一次的日期标记为数据不足。

## 消耗算法

相邻快照区间：

```
消耗 = (topped_up 差值) + (granted 差值) - (total 差值)
```

- 充值或赠送会使 total 上升，上式仍能还原真实消耗；结果落在区间结束快照所在日期。
- 每日消耗为该日期内所有区间之和；跨日区间计入结束日。
- 浮点按两位小数输出，负值视为异常并提示人工核对。

## 边界

- 只提供余额与聚合消耗；无逐条请求、模型、Token 明细，不能替代官方账单页。
- 多币种时只统计首条 `balance_infos`，其余币种在输出中省略并提示。
- 接口超时 15 秒；失败不写快照，避免污染差值。
