"""Pure helpers for on-demand GitHub PR collaboration awareness."""
from __future__ import annotations

import re
from pathlib import PurePosixPath


def dependencies(body: str) -> set[int]:
    """Read explicit PR dependencies, not instructions."""
    result = set()
    for line in (body or "").splitlines():
        match = re.fullmatch(r"Collaboration-Depends-On:\\s*(#[0-9]+(?:\\s*,\\s*#[0-9]+)*)\\s*", line.strip(), re.I)
        if match:
            result.update(int(item.strip()[1:]) for item in match.group(1).split(","))
    return result


def classify(own_files, other_files, *, related=False, complete=True, remote_verified=True):
    """Return L0/L1/L2/L3; incomplete evidence fails closed."""
    if not complete or not remote_verified:
        return "L3"
    own = set(own_files)
    other = set(other_files)
    if own & other:
        return "L2"
    if related:
        return "L1"
    return "L0"
