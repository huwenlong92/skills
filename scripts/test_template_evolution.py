"""Executable, offline FC2 fixtures. No Git or application writes."""
import copy
import unittest
from template_evolution_protocol import ProtocolError, identity, owns, unique_owner, digest, plan_valid, transition, apply_gate, path, exact_toolchain, lock_consistent, classify_change

S, T, P = "a"*40, "b"*40, "c"*40

def fixture_identity():
    return {"schema_version":1,"project":{"repository":"example/app"},"templates":[{"mount_id":"web","template_id":"nuxt","repository":"example/nuxt","project_path":"apps/web","variant":"default","origin":{"status":"verified","commit":S,"evidence_refs":["commit:source"]},"tracking":"active","ownership":{"include":["src/**","package.json"],"exclude":["src/business/**"]}}]}

def fixture_plan():
    x={"schema_version":1,"task_id":"upgrade-01","revision":1,"group":{"required_mounts":["web"],"status":"pending"},"members":[{"mount_id":"web","source_template_commit":S,"target_template_commit":T,"project_commit":P}],"scope":{"allowed_paths":["apps/web/package.json"],"forbidden_paths":["apps/web/src/business/**"],"deletions_allowed":False},"diff":{"safe":[],"review":[],"blocked":[]},"verification":{"static":"pending","build":"pending"},"recovery_strategy":"isolated-worktree"}
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

if __name__=="__main__":
    unittest.main()
