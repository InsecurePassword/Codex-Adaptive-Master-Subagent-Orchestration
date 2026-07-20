#!/usr/bin/env python3
"""Read or set Adaptive Master–Subagent orchestration intensity."""
from __future__ import annotations
import argparse, os, re, tempfile
from pathlib import Path

VALID = ("auto", "minimal", "moderate", "heavy", "extreme")

def args():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", nargs="?", choices=VALID)
    p.add_argument("--scope", choices=("user","project"), default="user")
    p.add_argument("--project-root", type=Path, default=Path.cwd())
    p.add_argument("--show", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()

def path_for(a):
    if a.scope == "project": return a.project_root.resolve()/".codex"/"ams-orchestration.toml"
    return Path(os.environ.get("CODEX_HOME", Path.home()/".codex"))/"ams-orchestration.toml"

def read_mode(path):
    if not path.exists(): return None
    m=re.search(r'(?m)^\s*intensity\s*=\s*"([^"]+)"\s*$', path.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m and m.group(1) in VALID else None

def write_atomic(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=".ams-intensity.", dir=str(path.parent), text=True)
    try:
        with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as f: f.write(text)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def main():
    a=args(); path=path_for(a)
    if a.show or not a.mode:
        print(f"{path}: {read_mode(path) or 'unset (effective default: auto)'}")
        return 0
    text=f'schema_version = 1\nintensity = "{a.mode}"\n'
    if a.dry_run:
        print(f"would-write {path}\n{text}", end="")
    else:
        write_atomic(path,text); print(f"set {a.scope} intensity to {a.mode}: {path}")
    return 0
if __name__ == "__main__": raise SystemExit(main())
