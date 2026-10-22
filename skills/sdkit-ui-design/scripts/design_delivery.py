#!/usr/bin/env python3
"""Offline static design asset packaging; Python standard library only."""
import argparse, hashlib, json, re, zipfile
from pathlib import Path

MODULES = ("discover","circles","publish","messages","profile","management","common")
PNG = bytes.fromhex("89504e470d0a1a0a")

def digest(data): return hashlib.sha256(data).hexdigest()

def safe(path):
    p = Path(path)
    if p.is_absolute() or ".." in p.parts or not p.parts or any(not re.fullmatch(r"[A-Za-z0-9_.-]+", s) for s in p.parts):
        raise ValueError("unsafe or non-ASCII path: " + str(path))
    return p.as_posix()

def verify(root):
    root = Path(root)
    manifest = json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    if manifest.get("path_base") != "manifest_directory" or manifest.get("artifact_type") != "high_fidelity":
        raise ValueError("invalid manifest contract")
    paths = set()
    for a in manifest["assets"]:
        path = safe(a["path"])
        if path in paths or "original_zip_path" in a: raise ValueError("duplicate/legacy path")
        paths.add(path)
        f = root/path
        if not f.is_file() or f.is_symlink(): raise ValueError("missing asset: "+path)
        data = f.read_bytes()
        if not data.startswith(PNG) or digest(data) != a["sha256"] or len(data) != a["bytes"]:
            raise ValueError("asset mismatch: "+path)
    for module in MODULES:
        expected = {a["path"] for a in manifest["assets"] if a["module"] == module}
        archive = root/(module+".zip")
        if not expected:
            if archive.exists(): raise ValueError("unexpected ZIP")
            continue
        with zipfile.ZipFile(archive) as z:
            if set(z.namelist()) != expected or z.testzip() is not None:
                raise ValueError("ZIP mismatch: "+module)
            for name in expected:
                if digest(z.read(name)) != digest((root/name).read_bytes()):
                    raise ValueError("ZIP content mismatch: "+name)
    return len(paths)

def build(plan_path, source, output):
    source, output = Path(source).resolve(), Path(output)
    if output.exists() and any(output.iterdir()): raise ValueError("output must be empty")
    plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    output.mkdir(parents=True, exist_ok=True)
    assets, hashes, ids = [], {}, set()
    for page in plan["pages"]:
        pid, module = page["id"], page["module"]
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", pid) or pid in ids or module not in MODULES:
            raise ValueError("invalid page id/module")
        ids.add(pid)
        for kind, names in (("selected",[page["selected"]]),("history",page.get("history",[]))):
            for i, name in enumerate(names, 1):
                relative = Path(name)
                if relative.is_absolute() or ".." in relative.parts: raise ValueError("unsafe source")
                src = (source/relative).resolve()
                if not src.is_relative_to(source) or not src.is_file() or src.is_symlink():
                    raise ValueError("missing source")
                data = src.read_bytes()
                if not data.startswith(PNG): raise ValueError("invalid PNG")
                path = safe(f"{kind}/{module}/{pid}" + (f"-{i:02d}" if kind=="history" else "") + ".png")
                dst = output/path
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(data)
                h = digest(data)
                hashes.setdefault(h, []).append(path)
                assets.append(dict(path=path,module=module,page_id=pid,page_name=page["name"],kind=kind,status=page.get("status","candidate"),sha256=h,bytes=len(data),source_filename=src.name))
    manifest = dict(schema_version="1.0",artifact_type="high_fidelity",path_base="manifest_directory",assets=assets,duplicate_sha256={h:p for h,p in hashes.items() if len(p)>1})
    (output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for module in MODULES:
        paths = [a["path"] for a in assets if a["module"]==module]
        if paths:
            with zipfile.ZipFile(output/(module+".zip"),"w",zipfile.ZIP_DEFLATED) as z:
                for path in paths: z.write(output/path,path)
    return verify(output)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd",required=True)
    b = sub.add_parser("build")
    for flag in ("plan","source","output"): b.add_argument("--"+flag,required=True)
    v = sub.add_parser("verify"); v.add_argument("--output",required=True)
    a = p.parse_args()
    try:
        print("PASS",build(a.plan,a.source,a.output) if a.cmd=="build" else verify(a.output))
    except (OSError,ValueError,KeyError,zipfile.BadZipFile) as e:
        p.exit(1,"FAIL: "+str(e)+"\n")
