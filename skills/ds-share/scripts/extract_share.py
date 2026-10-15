#!/usr/bin/env python3
"""Validate a local DeepSeek share response and extract content without network access."""

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import urlsplit


def canonical_url(value):
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        raise ValueError("invalid share URL") from None
    match = re.fullmatch(r"/share/([A-Za-z0-9_-]+)/?", parsed.path)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "chat.deepseek.com"
        or parsed.username is not None
        or parsed.password is not None
        or port not in (None, 443)
        or not match
    ):
        raise ValueError("expected an HTTPS chat.deepseek.com/share/<share_id> URL")
    return f"https://chat.deepseek.com/share/{match[1]}"


def validate_response(data):
    if not isinstance(data, dict):
        raise ValueError("response must be an object")
    business = data.get("data")
    if not isinstance(business, dict):
        raise ValueError("missing response data object")
    for code in (data.get("code"), business.get("biz_code")):
        if type(code) is not int or code != 0:
            raise ValueError("response code and biz_code must both be integer zero")
    body = business.get("biz_data")
    messages = body.get("messages") if isinstance(body, dict) else None
    if not isinstance(messages, list) or not messages:
        raise ValueError("missing or empty messages array")
    for index, message in enumerate(messages, 1):
        if not isinstance(message, dict):
            raise ValueError(f"message {index} must be an object")
        if not isinstance(message.get("role"), str) or not message["role"].strip():
            raise ValueError(f"message {index} requires a nonempty role")
        if not isinstance(message.get("content"), str):
            raise ValueError(f"message {index} requires string content")
        message_id = message.get("message_id")
        if message_id is not None and type(message_id) not in (str, int):
            raise ValueError(f"message {index} has an unsupported message_id type")
    if not any(message["content"].strip() for message in messages):
        raise ValueError("messages contain no nonblank content")
    return messages


def review_signals(messages):
    reviews = []
    for index, message in enumerate(messages, 1):
        reasons = []
        if not message["content"].strip():
            reasons.append("empty_content")
        if message.get("status") != "FINISHED":
            reasons.append("missing_or_unrecognized_status")
        incomplete = message.get("incomplete_message")
        if incomplete is not None and incomplete is not False:
            reasons.append("incomplete_message")
        files = message.get("files")
        if files is not None and not isinstance(files, list):
            reasons.append("unrecognized_files_structure")
        elif files:
            reasons.append("attachments_not_extracted")
        if message["role"] not in ("USER", "ASSISTANT"):
            reasons.append("unrecognized_role")
        if message.get("message_id") is None:
            reasons.append("missing_message_id")
        if reasons:
            reviews.append({"position": index, "message_id": message.get("message_id"), "reasons": reasons})
    return reviews


def label(value):
    # Keep metadata on one heading line, including unusual strings.
    return json.dumps(value, ensure_ascii=False)


def render(source, messages):
    parts = [f"Source: {source}", "Scope: messages returned by this share; attachments and reasoning fields excluded."]
    for index, message in enumerate(messages, 1):
        identifier = "not provided" if message.get("message_id") is None else label(message["message_id"])
        parts.extend([f"## {index}. {label(message['role'])} (message_id: {identifier})", message["content"]])
    return "\n\n".join(parts) + "\n"


def extract(input_path, source, output_parent=None):
    source = canonical_url(source)
    messages = validate_response(json.loads(Path(input_path).read_text(encoding="utf-8")))
    if output_parent is not None:
        parent = Path(output_parent).expanduser().resolve()
        skill_root = Path(__file__).resolve().parent.parent
        if parent == skill_root or skill_root in parent.parents:
            raise ValueError("outputs must not be written inside this skill")
        if not parent.is_dir():
            raise ValueError("output parent must be an existing controlled directory")
    else:
        parent = None
    output = Path(tempfile.mkdtemp(prefix="ds-share-", dir=parent))
    summary = {
        "source": source,
        "message_count": len(messages),
        "roles": list(dict.fromkeys(message["role"] for message in messages)),
        "scope": "returned_messages_only",
        "http_verified": False,
        "review_messages": review_signals(messages),
    }
    (output / "conversation.md").write_text(render(source, messages), encoding="utf-8")
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"output_directory": str(output), **summary}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="local JSON response file")
    parser.add_argument("--source", required=True, help="original DeepSeek share URL")
    parser.add_argument("--check-url", action="store_true", help="only validate and print canonical URL")
    parser.add_argument("--output-parent", help="existing controlled directory; default: system temporary directory")
    args = parser.parse_args()
    try:
        if args.check_url:
            print(canonical_url(args.source))
            return 0
        if not args.input:
            parser.error("--input is required unless --check-url is used")
        summary = extract(args.input, args.source, args.output_parent)
    except (OSError, ValueError) as error:
        # JSONDecodeError details can contain response text, so do not echo it.
        detail = "invalid JSON response" if isinstance(error, json.JSONDecodeError) else str(error)
        print(json.dumps({"error": detail}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
