"""Executable, offline FC2 fixtures. No Git or application writes."""
import copy
import unittest
from template_evolution_protocol import ProtocolError, identity, owns, unique_owner, digest, plan_valid, transition, apply_gate, path, exact_toolchain, lock_consistent, classify_change

S, T, P = "a"*40, "b"*40, "c"*40

def fixture_identity():
    return {"schema_version":1,"project":{"repository":"example/app"},"templates":[{"mount_id":"web","template_id":"nuxt","repository":"example/nuxt","project_path":"apps/web","variant":"default","origin":{"status":"verified","commit":S,"evidence_refs":["commit:source"]},"tracking":"active","ownership":{"include":["src/**","package.json"],"exclude":["src/business/**"]}}]}

def fixture_plan():
    x={"schema_version":1,"task_id":"upgrade-01","revision":1,"group":{"required_mounts":["web"],"status":"pending"},"members":[{"mount_id":"web","source_template_commit":S,"target_template_commit":T,"project_commit":P,"phase":"planned","health":"ready","recovery":"not_required"}],"scope":{"allowed_paths":["apps/web/package.json"],"forbidden_paths":["apps/web/src/business/**"],"deletions_allowed":False},"diff":{"safe":[],"review":[],"blocked":[]},"verification":{"static":"pending","build":"pending"},"recovery_strategy":"isolated-worktree"}
    x["plan_digest"]=digest(x)
    return x

class ProtocolFixtures(unittest.TestCase):
    def denied(self, code, func):
        with self.assertRaises(ProtocolError) as ctx:
            func()
        self.assertEqual(ctx.exception.code, code)
    def apply(self, p=None, i=None, **kwargs):
        p=p or fixture_plan()
        return apply_gate(p, i or fixture_identity(), approved_digest=p["plan_digest"], user_authorized=True, git_fresh=True, provider_ready=True, **kwargs)
    def test_01_known_origin(self):
        self.assertEqual(identity(fixture_identity())["templates"][0]["origin"]["status"],"verified")
    def test_02_unknown_origin(self):
        i=fixture_identity();i["templates"][0]["origin"]={"status":"unknown","commit":None}
        self.denied("TE-1001",lambda:self.apply(i=i))
    def test_03_node_version_source(self):
        self.denied("TE-2001",lambda:exact_toolchain("24.20.0","22.0.0"))
    def test_04_go_toolchain_source(self):
        self.denied("TE-2001",lambda:exact_toolchain("go1.25.10","go1.24.0"))
    def test_05_rust_toolchain_source(self):
        self.denied("TE-2001",lambda:exact_toolchain("1.96.0","1.95.0"))
    def test_06_python_lock_source(self):
        self.denied("TE-2002",lambda:lock_consistent("sha256:old","sha256:new"))
    def test_07_template_added(self):
        self.assertEqual(classify_change(None,"new",None),"safe_candidate")
    def test_08_business_file_excluded(self):
        self.assertEqual(classify_change("old",None,"custom"),"blocked")
    def test_09_both_modified_review_record(self):
        self.assertEqual(classify_change("base","target","business"),"review")
    def test_10_dependency_scope_changes_digest(self):
        p=fixture_plan();p["scope"]["allowed_paths"].append("apps/web/pnpm-lock.yaml")
        self.denied("TE-4004",lambda:plan_valid(p))
    def test_11_adopted_origin_not_verified(self):
        i=fixture_identity();i["templates"][0]["origin"]={"status":"declared","commit":S};i["templates"][0]["adopted_baseline"]={"template_commit":S}
        self.denied("TE-1001",lambda:self.apply(i=i))
    def test_12_parallel_conflict(self):
        self.denied("TE-4003",lambda:apply_gate(fixture_plan(),fixture_identity(),approved_digest=fixture_plan()["plan_digest"],user_authorized=True,git_fresh=True,provider_ready=True,conflicts=True))
    def test_13_interrupted(self):
        self.denied("TE-5003",lambda:transition({"phase":"applying","health":"interrupted","recovery":"required"},"verifying"))
    def test_14_recovery_cannot_skip(self):
        self.denied("TE-4004",lambda:transition({"phase":"applying","health":"ready","recovery":"recovered"},"completed"))
    def test_15_business_protection(self):
        self.denied("TE-1004",lambda:unique_owner(fixture_identity(),"apps/web/src/business/page.vue"))
    def test_16_digest_canonical(self):
        p=fixture_plan();q=copy.deepcopy(p);q["authorization"]={"approval_ref":"untrusted"}
        self.assertEqual(digest(p),digest(q))
    def test_17_ci_failure_blocks_complete(self):
        self.denied("TE-5002",lambda:transition({"phase":"verifying","health":"ready","recovery":"not_required","verification_passed":False},"completed"))
    def test_18_unauthorized_agent(self):
        p=fixture_plan()
        self.denied("TE-4001",lambda:apply_gate(p,fixture_identity(),approved_digest=p["plan_digest"],git_fresh=True,provider_ready=True))
    def test_19_provider_degraded(self):
        p=fixture_plan()
        self.denied("TE-4005",lambda:apply_gate(p,fixture_identity(),approved_digest=p["plan_digest"],user_authorized=True,git_fresh=True))
    def test_20_cross_stack_overlap(self):
        i=fixture_identity();m=copy.deepcopy(i["templates"][0]);m["mount_id"]="admin";i["templates"].append(m)
        identity(i)
        self.denied("TE-1004",lambda:unique_owner(i,"apps/web/src/core.ts"))
    def test_21_revision_invalidates_digest(self):
        p=fixture_plan();p["revision"]=2
        self.denied("TE-4004",lambda:plan_valid(p))
    def test_22_path_escape(self):
        self.denied("TE-1004",lambda:path("../secrets"))
    def test_23_verified_requires_evidence(self):
        i=fixture_identity();i["templates"][0]["origin"]["evidence_refs"]=[]
        self.denied("TE-1001",lambda:identity(i))
    def test_24_valid_plan(self):
        self.assertEqual(plan_valid(fixture_plan())["revision"],1)
    def test_25_valid_gate_only_not_apply(self):
        self.assertTrue(self.apply())

    def test_26_wildcard_scope_fail_closed(self):
        p=fixture_plan();p["scope"]["allowed_paths"]=["apps/web/src/**"];p["plan_digest"]=digest(p)
        self.denied("TE-1004",lambda:self.apply(p=p))
    def test_27_forbidden_scope_rejected(self):
        p=fixture_plan();p["scope"]["forbidden_paths"]=["apps/web/package.json"];p["plan_digest"]=digest(p)
        self.denied("TE-3002",lambda:self.apply(p=p))
    def test_28_deletion_requires_separate_approval(self):
        p=fixture_plan();p["scope"]["deletions_allowed"]=True;p["plan_digest"]=digest(p)
        self.denied("TE-3002",lambda:self.apply(p=p))

    def test_29_normalized_forbidden_path(self):
        p=fixture_plan();p["scope"]["allowed_paths"]=["apps/web/./package.json"];p["scope"]["forbidden_paths"]=["apps/web/package.json"];p["plan_digest"]=digest(p)
        self.denied("TE-3002",lambda:self.apply(p=p))
    def test_30_owner_must_be_member(self):
        i=fixture_identity();m=copy.deepcopy(i["templates"][0]);m["mount_id"]="api";m["project_path"]="apps/api";m["origin"]={"status":"unknown"};i["templates"].append(m)
        p=fixture_plan();p["scope"]["allowed_paths"]=["apps/api/package.json"];p["plan_digest"]=digest(p)
        self.denied("TE-1004",lambda:self.apply(p=p,i=i))
    def test_31_source_commit_must_match(self):
        p=fixture_plan();p["members"][0]["source_template_commit"]=T;p["plan_digest"]=digest(p)
        self.denied("TE-1002",lambda:self.apply(p=p))
    def test_32_toolchain_changes_digest(self):
        p=fixture_plan();before=digest(p);p["toolchain"]={"node":"24.0.0"}
        self.assertNotEqual(before,digest(p))
    def test_33_duplicate_members_rejected(self):
        p=fixture_plan();p["members"].append(copy.deepcopy(p["members"][0]));p["plan_digest"]=digest(p)
        self.denied("TE-4004",lambda:plan_valid(p))
    def test_34_empty_required_mounts_rejected(self):
        p=fixture_plan();p["group"]["required_mounts"]=[];p["plan_digest"]=digest(p)
        self.denied("TE-4004",lambda:plan_valid(p))
    def test_35_truthy_authorization_rejected(self):
        p=fixture_plan()
        self.denied("TE-4001",lambda:apply_gate(p,fixture_identity(),approved_digest=p["plan_digest"],user_authorized="false",git_fresh=True,provider_ready=True))
    def test_36_file_authorization_cannot_grant(self):
        p=fixture_plan();p["authorization"]={"granted":True,"approved_digest":p["plan_digest"]}
        self.denied("TE-4001",lambda:apply_gate(p,fixture_identity(),git_fresh=True,provider_ready=True))
    def test_37_incomplete_group_not_verified(self):
        p=fixture_plan();p["group"]["status"]="verified";p["plan_digest"]=digest(p)
        self.denied("TE-4004",lambda:plan_valid(p))
    def test_38_failed_recovery_blocks(self):
        self.denied("TE-5003",lambda:transition({"phase":"applying","health":"failed","recovery":"partially_restored"},"verifying"))
    def test_39_recovered_continues_one_phase(self):
        self.assertEqual(transition({"phase":"applying","health":"ready","recovery":"recovered"},"verifying")["phase"],"verifying")
    def test_40_case_collision_rejected(self):
        p=fixture_plan();p["scope"]["allowed_paths"].append("apps/web/Package.json");p["plan_digest"]=digest(p)
        self.denied("TE-1004",lambda:plan_valid(p))

    def test_41_multi_template_disjoint_members(self):
        i=fixture_identity();m=copy.deepcopy(i["templates"][0]);m["mount_id"]="api";m["project_path"]="apps/api";i["templates"].append(m)
        p=fixture_plan();member=copy.deepcopy(p["members"][0]);member["mount_id"]="api";p["members"].append(member);p["group"]["required_mounts"].append("api");p["scope"]["allowed_paths"].append("apps/api/package.json");p["plan_digest"]=digest(p)
        self.assertTrue(self.apply(p=p,i=i))
    def test_42_old_approval_rejected_after_revision(self):
        p=fixture_plan();old=p["plan_digest"];p["revision"]=2;p["plan_digest"]=digest(p)
        self.denied("TE-4001",lambda:apply_gate(p,fixture_identity(),approved_digest=old,user_authorized=True,git_fresh=True,provider_ready=True))
    def test_43_verified_group_requires_all_members(self):
        p=fixture_plan();p["group"]["status"]="verified";p["members"][0].update(phase="completed",health="ready",recovery="recovered",verification_passed=True);p["verification"]["cross_template_passed"]=True;p["plan_digest"]=digest(p)
        self.assertEqual(plan_valid(p)["group"]["status"],"verified")
    def test_44_last_synced_baseline(self):
        p=fixture_plan();i=fixture_identity();i["templates"][0]["last_synced"]={"template_commit":T};p["members"][0]["source_template_commit"]=T;p["plan_digest"]=digest(p)
        self.assertTrue(self.apply(p=p,i=i))
    def test_45_stale_git_rejected(self):
        p=fixture_plan()
        self.denied("TE-4002",lambda:apply_gate(p,fixture_identity(),approved_digest=p["plan_digest"],user_authorized=True,provider_ready=True))

    def test_46_blocked_group_cannot_apply(self):
        p=fixture_plan();p["group"]["status"]="blocked";p["plan_digest"]=digest(p)
        self.denied("TE-5003",lambda:self.apply(p=p))
    def test_47_interrupted_member_cannot_apply(self):
        p=fixture_plan();p["members"][0].update(health="interrupted",recovery="required");p["plan_digest"]=digest(p)
        self.denied("TE-5003",lambda:self.apply(p=p))

if __name__=="__main__":
    unittest.main()
