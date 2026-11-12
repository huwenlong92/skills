#!/usr/bin/env python3
"""DeepSeek balance snapshots and spend reporting (stdlib only)."""

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

BALANCE_URL = "https://api.deepseek.com/user/balance"
TIMEOUT = 15


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def state_file():
    base = os.environ.get("XDG_STATE_HOME") or os.path.expanduser("~/.local/state")
    return Path(base) / "sdkit-skills" / "deepseek-usage" / "snapshots.jsonl"


def resolve_key():
    for name in ("DEEPSEEK_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
        value = os.environ.get(name)
        if value:
            return value, name
    fail("未找到 DEEPSEEK_API_KEY 或 ANTHROPIC_AUTH_TOKEN")


def open_balance(request):
    """Retry with the system CA bundle when the interpreter's CA store is incomplete."""
    try:
        return urllib.request.urlopen(request, timeout=TIMEOUT)
    except urllib.error.URLError as exc:
        reason = exc.reason
        if not (
            isinstance(reason, ssl.SSLCertVerificationError)
            or "CERTIFICATE_VERIFY_FAILED" in str(reason)
        ):
            raise
        bundle = os.environ.get("DEEPSEEK_CA_BUNDLE", "/etc/ssl/cert.pem")
        if not os.path.exists(bundle):
            raise
        context = ssl.create_default_context(cafile=bundle)
        return urllib.request.urlopen(request, timeout=TIMEOUT, context=context)


def fetch_balance():
    key, source = resolve_key()
    request = urllib.request.Request(
        BALANCE_URL,
        headers={"Authorization": f"Bearer {key}", "Accept": "application/json"},
    )
    try:
        with open_balance(request) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        fail(f"接口返回 HTTP {exc.code}（凭据来源 {source}）")
    except urllib.error.URLError as exc:
        fail(f"无法连接余额接口：{exc.reason}")

    infos = payload.get("balance_infos") or []
    if not infos:
        fail("响应缺少 balance_infos")
    info = infos[0]
    return {
        "available": bool(payload.get("is_available")),
        "total": float(info.get("total_balance") or 0),
        "topped_up": float(info.get("topped_up_balance") or 0),
        "granted": float(info.get("granted_balance") or 0),
        "currency": info.get("currency") or "CNY",
        "extra_currencies": [i.get("currency") for i in infos[1:]],
    }


def append_snapshot(balance):
    now = datetime.now().astimezone()
    row = {
        "ts": now.isoformat(timespec="seconds"),
        "date": now.date().isoformat(),
        "total": balance["total"],
        "topped_up": balance["topped_up"],
        "granted": balance["granted"],
        "currency": balance["currency"],
    }
    path = state_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def read_snapshots():
    path = state_file()
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    rows.sort(key=lambda row: row["ts"])
    return rows


def interval_spend(previous, current):
    return (
        current["topped_up"]
        - previous["topped_up"]
        + current["granted"]
        - previous["granted"]
        - (current["total"] - previous["total"])
    )


def build_report(days):
    today = date.today()
    start = today - timedelta(days=days - 1)
    rows = read_snapshots()

    daily = {}
    counts = {}
    for previous, current in zip(rows, rows[1:]):
        day = current["date"]
        daily[day] = daily.get(day, 0.0) + interval_spend(previous, current)
        counts[day] = counts.get(day, 0) + 1

    daily = {d: v for d, v in daily.items() if start.isoformat() <= d <= today.isoformat()}
    first_ts = rows[0]["ts"] if rows else None
    return {
        "currency": rows[-1]["currency"] if rows else "CNY",
        "start": start.isoformat(),
        "end": today.isoformat(),
        "snapshots": len(rows),
        "daily": {d: round(v, 2) for d, v in sorted(daily.items())},
        "intervals": counts,
        "first_snapshot": first_ts,
        "partial": start.isoformat() <= (first_ts or "")[:10] <= today.isoformat(),
    }


def print_balance(balance):
    print(f"余额：{balance['total']:.2f} {balance['currency']}")
    print(f"可用：{'是' if balance['available'] else '否'}")
    print(
        f"充值余额：{balance['topped_up']:.2f}　赠送余额：{balance['granted']:.2f}"
    )
    if balance["extra_currencies"]:
        print(f"其他币种未统计：{', '.join(balance['extra_currencies'])}")


def print_report(report, days):
    print(f"币种：{report['currency']}　统计区间：{report['start']} ~ {report['end']}")
    print(f"快照总数：{report['snapshots']}")
    if not report["daily"]:
        print("暂无可用区间数据：至少需要两天的快照才能计算消耗。")
        print("提示：定期运行 report 或 balance 会累积快照。")
        return
    print("")
    print(f"{'日期':<12}{'消耗':>10}{'区间数':>8}")
    total = 0.0
    for day, value in report["daily"].items():
        total += value
        print(f"{day:<12}{value:>10.2f}{report['intervals'].get(day, 0):>8}")
    print(f"{'合计':<12}{round(total, 2):>10.2f}")
    if report["partial"]:
        print("")
        print(f"注意：最早快照为 {report['first_snapshot']}，该日消耗不完整。")
    if days > 1:
        missing = [
            (report["start"] and date.fromisoformat(report["start"]) + timedelta(days=offset)).isoformat()
            for offset in range(days)
        ]
        gaps = [d for d in missing if d not in report["daily"]]
        if gaps:
            print(f"无数据日期：{', '.join(gaps)}")


def main():
    parser = argparse.ArgumentParser(description="DeepSeek 余额与消耗统计")
    parser.add_argument("command", choices=["balance", "report", "snapshot"])
    parser.add_argument("--days", type=int, default=7, help="统计天数，默认 7")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    if args.command == "balance":
        balance = fetch_balance()
        if args.json:
            print(json.dumps(balance, ensure_ascii=False, indent=2))
        else:
            print_balance(balance)
        return

    if args.command == "snapshot":
        balance = fetch_balance()
        row = append_snapshot(balance)
        if args.json:
            print(json.dumps(row, ensure_ascii=False))
        else:
            print(f"已记录快照：{row['ts']} 余额 {row['total']:.2f} {row['currency']}")
        return

    if args.days < 1:
        fail("--days 必须大于 0")
    balance = fetch_balance()
    append_snapshot(balance)
    report = build_report(args.days)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report, args.days)


if __name__ == "__main__":
    main()
