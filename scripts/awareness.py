"""Pure, fail-closed helpers for on-demand PR collaboration awareness."""
from __future__ import annotations

import re
from typing import Mapping


def _metadata(body: str, key: str) -> list[str]:
    prefix = re.compile(rf"{re.escape(key)}:\s*(.+)", re.I)
    values = []
    for line in (body or "").splitlines():
        match = prefix.fullmatch(line.strip())
        if match:
            values.extend(x.strip().lower() for x in match.group(1).split(",") if x.strip())
    return values


def dependencies(body: str) -> set[int]:
    """Parse declared PR references; never execute body content."""
    return {int(x[1:]) for x in _metadata(body, "Collaboration-Depends-On")
            if re.fullmatch(r"#[1-9][0-9]*", x)}


def protocols(body: str) -> set[str]:
    return set(_metadata(body, "Collaboration-Protocol"))


def affects(body: str) -> set[str]:
    return set(_metadata(body, "Collaboration-Affects"))


def changed_paths(files) -> set[str]:
    """Include rename sources; reject malformed or truncated file records."""
    result = set()
    for item in files:
        if isinstance(item, str):
            if not item:
                raise ValueError("empty filename")
            result.add(item)
            continue
        if not isinstance(item, Mapping) or not item.get("filename"):
            raise ValueError("invalid changed-file record")
        result.add(item["filename"])
        if item.get("status") == "renamed":
            if not item.get("previous_filename"):
                raise ValueError("rename source missing")
            result.add(item["previous_filename"])
    return result


def classify(own_files, other_files, *, related=False, complete=True,
             remote_verified=True, head_unchanged=True):
    """L0 independent, L1 related, L2 overlap, L3 unsafe/unknown."""
    if not complete or not remote_verified or not head_unchanged:
        return "L3"
    try:
        own = changed_paths(own_files)
        other = changed_paths(other_files)
    except (TypeError, ValueError):
        return "L3"
    if own & other:
        return "L2"
    return "L1" if related else "L0"


def related_pr(own_number: int, own_body: str, other_number: int, other_body: str) -> bool:
    return (other_number in dependencies(own_body)
            or own_number in dependencies(other_body)
            or bool(protocols(own_body) & protocols(other_body))
            or bool(affects(own_body) & affects(other_body)))


def complete_page_count(pages, expected_count: int | None = None, *, page_size: int = 100) -> bool:
    """Require an explicit terminal short page; empty final page is valid."""
    if not pages or page_size <= 0:
        return False
    if any(not isinstance(page, list) or len(page) > page_size for page in pages):
        return False
    if len(pages[-1]) >= page_size:
        return False
    return expected_count is None or sum(map(len, pages)) == expected_count
