"""Deterministic read-only Template Evolution V1 protocol validators."""
import hashlib
import json
from fnmatch import fnmatchcase

class ProtocolError(ValueError):
    def __init__(self, code, detail):
        self.code = code
        super().__init__(f"{code}: {detail}")

def require(ok, code, detail):
    if not ok:
        raise ProtocolError(code, detail)

def path(value):
    require(isinstance(value, str) and bool(value) and "\\" not in value and "\x00" not in value and not value.startswith(("/", "~")), "TE-1004", "invalid path")
    require(all(p not in ("", "..") for p in value.split("/")), "TE-1004", "path traversal")
    return "/".join(p for p in value.split("/") if p != ".") or "."

def sha(value):
    return isinstance(value, str) and len(value) == 40 and all(c in "0123456789abcdefABCDEF" for c in value)

def identity(doc):
    require(isinstance(doc, dict) and doc.get("schema_version") == 1 and isinstance(doc.get("project"), dict) and bool(doc["project"].get("repository")), "TE-1001", "identity invalid")
    mounts = doc.get("templates")
    require(isinstance(mounts, list) and bool(mounts), "TE-1001", "mounts missing")
    ids = set()
    for m in mounts:
        require(isinstance(m, dict), "TE-1001", "invalid mount")
        mid = m.get("mount_id")
        require(isinstance(mid, str) and bool(mid) and mid not in ids, "TE-1004", "duplicate mount")
        ids.add(mid)
        for key in ("template_id", "repository", "variant"):
            require(isinstance(m.get(key), str) and bool(m[key]), "TE-1001", key + " missing")
        path(m.get("project_path"))
        origin = m.get("origin")
        require(isinstance(origin, dict) and origin.get("status") in ("verified", "declared", "inferred", "unknown"), "TE-1001", "invalid origin")
        if origin["status"] == "verified":
            require(sha(origin.get("commit")) and bool(origin.get("evidence_refs")), "TE-1001", "source evidence missing")
        require(m.get("tracking") in ("active", "paused", "detached"), "TE-1001", "invalid tracking")
        own = m.get("ownership")
        require(isinstance(own, dict) and isinstance(own.get("include"), list) and isinstance(own.get("exclude"), list), "TE-1004", "ownership missing")
        for pattern in own["include"] + own["exclude"]:
            path(pattern)
    return doc

def owns(mount, filepath):
    p = path(filepath)
    base = path(mount["project_path"])
    if base != ".":
        if not p.startswith(base + "/"):
            return False
        p = p[len(base)+1:]
    own = mount["ownership"]
    return not any(fnmatchcase(p, pattern) for pattern in own["exclude"]) and any(fnmatchcase(p, pattern) for pattern in own["include"])

def unique_owner(doc, filepath):
    claims = [m["mount_id"] for m in doc["templates"] if owns(m, filepath)]
    require(len(claims) == 1, "TE-1004", "unknown or overlapping ownership")
    return claims[0]

CONTRACT_KEYS = ("task_id", "revision", "group", "members", "scope", "diff", "verification", "recovery_strategy")

def digest(plan):
    canonical = json.dumps({k: plan[k] for k in CONTRACT_KEYS}, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()

def plan_valid(plan):
    require(isinstance(plan, dict) and plan.get("schema_version") == 1 and type(plan.get("revision")) is int and plan["revision"] > 0, "TE-4004", "plan invalid")
    members = plan.get("members")
    require(isinstance(members, list) and bool(members), "TE-4004", "members missing")
    group = plan.get("group")
    require(isinstance(group, dict) and isinstance(group.get("required_mounts"), list) and set(group["required_mounts"]) <= {m.get("mount_id") for m in members}, "TE-4004", "group invalid")
    scope = plan.get("scope")
    require(isinstance(scope, dict) and isinstance(scope.get("allowed_paths"), list) and isinstance(scope.get("forbidden_paths"), list), "TE-4004", "scope invalid")
    for p in scope["allowed_paths"] + scope["forbidden_paths"]:
        path(p)
    require(plan.get("plan_digest") == digest(plan), "TE-4004", "digest mismatch")
    return plan

PHASES = ("discovered", "baselined", "diffed", "planned", "applying", "verifying", "completed")

def transition(state, target):
    require(state.get("phase") in PHASES and target in PHASES, "TE-4004", "phase invalid")
    require(state.get("health") == "ready" and state.get("recovery") in ("not_required", "recovered"), "TE-5003", "blocked")
    index = PHASES.index(state["phase"])
    require(index + 1 < len(PHASES) and PHASES[index+1] == target, "TE-4004", "transition invalid")
    if target == "completed":
        require(state.get("verification_passed") is True, "TE-5002", "verification missing")
    return {**state, "phase": target}

def apply_gate(plan, doc, *, user_authorized=False, approved_digest=None, git_fresh=False, provider_ready=False, conflicts=False):
    plan_valid(plan)
    identity(doc)
    require(user_authorized and approved_digest == plan["plan_digest"], "TE-4001", "authorization missing")
    require(git_fresh, "TE-4002", "git baseline stale")
    require(provider_ready, "TE-4005", "provider unavailable")
    require(not conflicts, "TE-4003", "conflict")
    mounts = {m["mount_id"]: m for m in doc["templates"]}
    for member in plan["members"]:
        mount = mounts.get(member["mount_id"])
        require(mount is not None and mount["origin"]["status"] == "verified" and mount["tracking"] == "active", "TE-1001", "source unknown")
        for field in ("source_template_commit", "target_template_commit", "project_commit"):
            require(sha(member.get(field)), "TE-1002", "baseline missing")
    for p in plan["scope"]["allowed_paths"]:
        if "*" not in p:
            unique_owner(doc, p)
    return True

def exact_toolchain(required, actual):
    """Compare already-discovered exact runtime versions without invoking managers."""
    require(isinstance(required, str) and bool(required) and isinstance(actual, str) and bool(actual), "TE-2001", "version evidence missing")
    require(required == actual, "TE-2001", "runtime mismatch")
    return True

def lock_consistent(declared_digest, resolved_digest):
    """Compare previously computed declaration/lock dependency fingerprints."""
    require(isinstance(declared_digest, str) and bool(declared_digest) and isinstance(resolved_digest, str) and bool(resolved_digest), "TE-2002", "lock evidence missing")
    require(declared_digest == resolved_digest, "TE-2002", "lock drift")
    return True

def classify_change(base, target, project):
    """Conservative content-level three-way classification for a single file."""
    if target == base:
        return "unchanged"
    if target is None and project != base:
        return "blocked"
    if project != base and target != project:
        return "review"
    return "safe_candidate"
