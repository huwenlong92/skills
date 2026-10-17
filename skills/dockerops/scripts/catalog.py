#!/usr/bin/env python3
"""Read a configured mirror catalogue without executing configs or contacting registries."""

import argparse
import json
import os
from pathlib import Path
import re
import sys


PLATFORMS = {"linux/amd64", "linux/arm64"}
DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")
ASSIGNMENT = re.compile(
    r"([A-Za-z_][A-Za-z0-9_]*)=(?:'([A-Za-z0-9_./:@,+-]*)'|"
    r'"([A-Za-z0-9_./:@,+-]*)"|([A-Za-z0-9_./:@,+-]*))\Z'
)


def inside(root, path):
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"path escapes mirror repository: {path.relative_to(root)}")
    return resolved


def fields(root, path):
    values = {}
    for number, line in enumerate(inside(root, path).read_text().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = ASSIGNMENT.fullmatch(line)
        if not match:
            raise ValueError(f"{path.relative_to(root)}:{number}: unsupported literal assignment")
        key = match[1]
        if key in values:
            raise ValueError(f"{path.relative_to(root)}:{number}: duplicate key {key}")
        values[key] = next(value for value in match.groups()[1:] if value is not None)
    return values


def check_platforms(value, issues, label):
    parts = value.split(",") if value else []
    if len(parts) != 2 or set(parts) != PLATFORMS:
        issues.append(f"{label}: expected exactly linux/amd64 and linux/arm64")


def check_digests(data, keys, issues):
    for key in keys:
        if not DIGEST.fullmatch(data.get(key, "")):
            issues.append(f"missing or invalid {key}")


def official(root, directory):
    relative = Path(directory)
    if relative.is_absolute() or len(relative.parts) != 2 or ".." in relative.parts:
        raise ValueError(f"invalid image directory: {directory}")
    base = root / relative
    issues = []
    config = fields(root, base / "image.conf")
    if set(config) != {"SOURCE_IMAGE", "TARGET_IMAGE", "PLATFORM"}:
        issues.append("image.conf must contain only SOURCE_IMAGE, TARGET_IMAGE and PLATFORM")
    for key in ("SOURCE_IMAGE", "TARGET_IMAGE"):
        if not config.get(key):
            issues.append(f"missing {key}")
    check_platforms(config.get("PLATFORM", ""), issues, "configuration")
    lock_path = inside(root, base / "digest.lock")
    lock = fields(root, lock_path) if lock_path.exists() else {}
    if lock:
        for key, config_key in (("source_image", "SOURCE_IMAGE"), ("target_image", "TARGET_IMAGE"), ("platform", "PLATFORM")):
            if lock.get(key) != config.get(config_key):
                issues.append(f"lock/config mismatch: {key}")
        digest_keys = ["source_digest", "target_digest"]
        for architecture in ("amd64", "arm64"):
            source_key = f"source_linux_{architecture}_digest"
            target_key = f"target_linux_{architecture}_digest"
            digest_keys.extend((source_key, target_key))
            if lock.get(source_key) != lock.get(target_key):
                issues.append(f"source/target child mismatch: {architecture}")
        check_digests(lock, digest_keys, issues)
        expected_pin = f"{config.get('TARGET_IMAGE', '')}-sha-{lock.get('target_digest', '').removeprefix('sha256:')[:12]}"
        if lock.get("target_pinned_image") != expected_pin:
            issues.append("rollback reference does not match target index digest")
        if not lock.get("synced_at"):
            issues.append("missing synced_at")
    elif lock_path.exists():
        issues.append("empty digest.lock")
    return {
        "kind": "official", "directory": directory,
        "source_image": config.get("SOURCE_IMAGE"), "target_image": config.get("TARGET_IMAGE"),
        "platform": config.get("PLATFORM"), "lock": lock,
        "status": "inconsistent" if issues else ("recorded" if lock else "unrecorded"),
        "issues": issues, "remote_verified": False,
    }


def builder(root, base, lock_paths):
    issues = []
    lock = {}
    if len(lock_paths) > 1:
        issues.append("multiple builder locks: inspect recipe and publication entry")
    elif lock_paths:
        lock = fields(root, lock_paths[0])
        check_platforms(lock.get("platform", ""), issues, "builder lock")
        check_digests(lock, ("digest", "amd64_digest", "arm64_digest"), issues)
        for key in ("image", "alias_image", "published_at", "source_image"):
            if not lock.get(key):
                issues.append(f"missing {key}")
        if "@" not in lock.get("source_image", "") or not DIGEST.fullmatch(lock.get("source_image", "").rsplit("@", 1)[-1]):
            issues.append("builder base is not pinned by digest")
    return {
        "kind": "builder", "directory": str(base.relative_to(root)),
        "target_image": lock.get("alias_image") or lock.get("image"),
        "platform": lock.get("platform"), "lock": lock,
        "status": "inconsistent" if issues else ("recorded" if lock else "unrecorded"),
        "issues": issues, "remote_verified": False,
    }


def repository(argument, config_argument=None):
    selected = argument if argument is not None else os.environ.get("DOCKEROPS_MIRROR_REPO")
    if selected is not None:
        if not selected.strip():
            raise ValueError("mirror repository path must not be empty")
        return Path(selected).expanduser().resolve()
    config_value = config_argument if config_argument is not None else os.environ.get("DOCKEROPS_CONFIG")
    if config_value is not None and not str(config_value).strip():
        raise ValueError("configuration path must not be empty")
    config = (Path(config_value).expanduser() if config_value is not None else
              Path.home() / ".config" / "sdkit" / "skills" / "dockerops" / "config.json")
    if not config.is_file():
        raise ValueError("mirror repository not bound; use --repo, DOCKEROPS_MIRROR_REPO or machine config")
    data = json.loads(config.read_text())
    if not isinstance(data, dict):
        raise ValueError("machine config must be a JSON object")
    if "repository" in data:
        repo = data["repository"]
        if not isinstance(repo, dict) or not isinstance(repo.get("url"), str) or not repo["url"].strip():
            raise ValueError("machine config requires repository.url")
        selected_path = repo.get("local_path")
    else:
        # Explicitly supplied old configurations remain readable during migration.
        if config_value is None:
            raise ValueError("Default config requires repository.url and repository.local_path; migrate legacy mirror_repo explicitly")
        selected_path = data.get("mirror_repo")
    if not isinstance(selected_path, str) or not selected_path.strip():
        raise ValueError("machine config requires a nonempty local repository path")
    value = Path(selected_path).expanduser()
    return (value if value.is_absolute() else config.parent / value).resolve()


def catalogue(root):
    records, issues, seen = [], [], set()
    lines = inside(root, root / "images.txt").read_text().splitlines()
    for directory in lines:
        directory = directory.strip()
        if not directory or directory.startswith("#"):
            continue
        if directory in seen:
            issues.append(f"duplicate images.txt entry: {directory}")
            continue
        seen.add(directory)
        try:
            records.append(official(root, directory))
        except (OSError, ValueError) as error:
            issues.append(f"{directory}: {error}")
    # Versioned recipes and published builder locks are independent of images.txt.
    bases = {path.parent for path in root.glob("*/*/Dockerfile")}
    bases.update(path.parent for path in root.glob("*/*/*builder*.lock"))
    for base in sorted(bases):
        if str(base.relative_to(root)) in seen:
            continue
        try:
            inside(root, base)
            records.append(builder(root, base, sorted(base.glob("*builder*.lock"))))
        except (OSError, ValueError) as error:
            issues.append(f"{base.relative_to(root)}: {error}")
    targets = set()
    for record in records:
        issues.extend(f"{record['directory']}: {issue}" for issue in record["issues"])
        target = record.get("target_image")
        if target and target in targets:
            issues.append(f"duplicate target_image: {target}")
        if target:
            targets.add(target)
    return records, issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="mirror repository root (relative to cwd)")
    parser.add_argument("--config", help="private JSON configuration (overrides DOCKEROPS_CONFIG)")
    parser.add_argument("--search", default="", help="case-insensitive substring filter")
    args = parser.parse_args()
    try:
        root = repository(args.repo, args.config)
        records, issues = catalogue(root)
        if args.search:
            query = args.search.casefold()
            records = [record for record in records if query in json.dumps(record, ensure_ascii=False).casefold()]
        print(json.dumps({"repository": str(root), "remote_verified": False, "images": records, "issues": issues}, ensure_ascii=False, indent=2))
        return 2 if issues else 0
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error), "remote_verified": False}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
