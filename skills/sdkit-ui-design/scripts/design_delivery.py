#!/usr/bin/env python3
"""Offline static design asset packaging; Python standard library only."""
import argparse, hashlib, json, re, zipfile, struct, zlib
from pathlib import Path

PNG = bytes.fromhex("89504e470d0a1a0a")

def digest(data): return hashlib.sha256(data).hexdigest()

def valid_png(data):
    """Validate PNG chunk framing, CRC, core ordering, and compressed payload."""
    if not data.startswith(PNG): return False
    offset, chunks, compressed, dimensions = 8, [], bytearray(), None
    try:
        while offset + 12 <= len(data):
            length = struct.unpack_from(">I", data, offset)[0]
            if length > len(data) - offset - 12: return False
            tag = data[offset+4:offset+8]
            body = data[offset+8:offset+8+length]
            crc = struct.unpack_from(">I", data, offset+8+length)[0]
            if zlib.crc32(tag+body) != crc: return False
            if not all(65 <= c <= 90 or 97 <= c <= 122 for c in tag): return False
            if tag[0] < 97 and tag not in (b'IHDR', b'PLTE', b'IDAT', b'IEND'): return False
            if not chunks and (tag != b"IHDR" or length != 13): return False
            if tag == b"IHDR":
                if chunks or length != 13: return False
                width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", body)
                if not width or not height or width*height > 40000000: return False
                if (depth,color) not in ((1,0),(2,0),(4,0),(8,0),(16,0),(8,2),(16,2),(1,3),(2,3),(4,3),(8,3),(8,4),(16,4),(8,6),(16,6)): return False
                if compression or filtering or interlace not in (0,1): return False
                dimensions = (width,height)
            if tag == b'PLTE':
                if b'PLTE' in chunks or b'IDAT' in chunks or color in (0,4) or not length or length % 3 or length > 768: return False
                if color == 3 and length//3 > 2**depth: return False
            if tag == b"IDAT":
                if color == 3 and b'PLTE' not in chunks: return False
                if b'IDAT' in chunks and chunks[-1] != b'IDAT': return False
                compressed.extend(body)
            if tag == b"IEND":
                if length or offset+12 != len(data) or not compressed or dimensions is None: return False
                # PNG scanline lengths include one filter byte per row, also for Adam7 passes.
                passes = ((0,0,1,1),) if not interlace else ((0,0,8,8),(4,0,8,8),(0,4,4,8),(2,0,4,4),(0,2,2,4),(1,0,2,2),(0,1,1,2))
                channels = {0:1,2:3,3:1,4:2,6:4}[color]
                rows = []
                for x,y,dx,dy in passes:
                    w,h = max(0,(width-x+dx-1)//dx),max(0,(height-y+dy-1)//dy)
                    if w and h: rows.append((1+(w*depth*channels+7)//8,h))
                expected = sum(size*count for size,count in rows)
                decoder = zlib.decompressobj()
                raw = decoder.decompress(bytes(compressed),expected+1)
                if len(raw) != expected or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail: return False
                pos = 0
                for size,count in rows:
                    for _ in range(count):
                        if raw[pos] > 4: return False
                        pos += size
                return True
            chunks.append(tag)
            offset += 12 + length
    except (ValueError,struct.error,zlib.error,OverflowError):
        return False
    return False

def safe(path):
    if not isinstance(path,str) or not path or any(s in ("",".","..") for s in path.split("/")):
        raise ValueError("unsafe path")
    p = Path(path)
    if p.is_absolute() or ".." in p.parts or not p.parts or any(s in (".","..") or not re.fullmatch(r"[A-Za-z0-9_.-]+", s) for s in p.parts):
        raise ValueError("unsafe or non-ASCII path: " + str(path))
    return p.as_posix()

def unlinked(path):
    """Reject symlinks before resolve(), including existing ancestor components."""
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path,*path.parents)):
        raise ValueError('linked path: '+str(path))
    return path

def verify(root):
    root = unlinked(root)
    unlinked(root/'manifest.json')
    manifest = json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    if not isinstance(manifest,dict) or manifest.get('schema_version') != '1.0' or 'original_zip_path' in manifest or manifest.get("path_base") != "manifest_directory" or manifest.get("artifact_type") != "high_fidelity":
        raise ValueError("invalid manifest contract")
    if not isinstance(manifest.get("assets"),list): raise ValueError("invalid assets")
    paths, hashes = set(), {}
    for a in manifest["assets"]:
        if not isinstance(a,dict) or not {'path','module','page_id','page_name','kind','sha256','bytes','status'} <= a.keys():
            raise ValueError('missing asset fields')
        if not isinstance(a['page_id'],str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]*',a['page_id']) or any(not isinstance(a[k],str) or not a[k].strip() for k in ('page_name','status')):
            raise ValueError('invalid page metadata')
        if not isinstance(a['sha256'],str) or not re.fullmatch(r'[a-f0-9]{64}',a['sha256']) or type(a['bytes']) is not int or a['bytes'] <= 0:
            raise ValueError('invalid hash/size')
        if not isinstance(a.get("module"),str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*",a["module"]) or a.get("kind") not in ("selected","history"):
            raise ValueError("invalid module/kind")
        path = safe(a["path"])
        if path in paths or "original_zip_path" in a: raise ValueError("duplicate/legacy path")
        paths.add(path)
        f = unlinked(root/path)
        if not f.is_file():
            raise ValueError("missing/linked asset: "+path)
        data = f.read_bytes()
        if not valid_png(data) or digest(data) != a["sha256"] or len(data) != a["bytes"]:
            raise ValueError("asset mismatch: "+path)
        hashes.setdefault(a['sha256'],[]).append(path)
    if manifest.get('duplicate_sha256') != {h:p for h,p in hashes.items() if len(p)>1}:
        raise ValueError('duplicate hash metadata mismatch')
    modules = {a["module"] for a in manifest["assets"]}
    if {p.name for p in root.glob("*.zip")} != {m+".zip" for m in modules}:
        raise ValueError("ZIP set mismatch")
    for module in modules:
        expected = {a["path"] for a in manifest["assets"] if a["module"] == module}
        archive = unlinked(root/(module+".zip"))
        with zipfile.ZipFile(archive) as z:
            names = z.namelist()
            if len(names) != len(expected) or set(names) != expected or z.testzip() is not None:
                raise ValueError("ZIP mismatch: "+module)
            for name in expected:
                if digest(z.read(name)) != digest((root/name).read_bytes()):
                    raise ValueError("ZIP content mismatch: "+name)
    return len(paths)

def build(plan_path, source, output):
    source, output = unlinked(source).resolve(), unlinked(output)
    if output.exists() and any(output.iterdir()): raise ValueError("output must be empty")
    plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    output.mkdir(parents=True, exist_ok=True)
    assets, hashes, ids = [], {}, set()
    for page in plan["pages"]:
        pid, module = page["id"], page["module"]
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", pid) or pid in ids or not isinstance(module,str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*",module):
            raise ValueError("invalid page id/module")
        ids.add(pid)
        for kind, names in (("selected",[page["selected"]]),("history",page.get("history",[]))):
            for i, name in enumerate(names, 1):
                relative = Path(name)
                if relative.is_absolute() or ".." in relative.parts: raise ValueError("unsafe source")
                src = unlinked(source/relative).resolve()
                if not src.is_relative_to(source) or not src.is_file() or src.is_symlink():
                    raise ValueError("missing source")
                data = src.read_bytes()
                if not valid_png(data): raise ValueError("invalid PNG")
                path = safe(f"{kind}/{module}/{pid}" + (f"-{i:02d}" if kind=="history" else "") + ".png")
                dst = output/path
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(data)
                h = digest(data)
                hashes.setdefault(h, []).append(path)
                assets.append(dict(path=path,module=module,page_id=pid,page_name=page["name"],kind=kind,status=page.get("status","candidate"),sha256=h,bytes=len(data),source_filename=src.name))
    manifest = dict(schema_version="1.0",artifact_type="high_fidelity",path_base="manifest_directory",assets=assets,duplicate_sha256={h:p for h,p in hashes.items() if len(p)>1})
    (output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for module in {a["module"] for a in assets}:
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
