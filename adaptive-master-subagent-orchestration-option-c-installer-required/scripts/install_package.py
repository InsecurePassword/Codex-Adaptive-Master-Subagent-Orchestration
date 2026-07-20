#!/usr/bin/env python3
"""Install this local Codex plugin, register it in the personal marketplace, profiles, and intensity defaults."""
from __future__ import annotations
import argparse, datetime as dt, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

PLUGIN_NAME = 'adaptive-master-subagent-orchestration-option-c-installer-required'
OPTION = 'C'
ALLOW_SKIP_PROFILES = False

def parse():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--home", type=Path, default=Path.home())
    p.add_argument("--skip-profiles", action="store_true")
    p.add_argument("--exclude-spark", action="store_true")
    p.add_argument("--spark-efforts", default="low,medium,high")
    p.add_argument("--upgrade-managed", action="store_true")
    p.add_argument("--intensity", choices=("auto","minimal","moderate","heavy","extreme"), default="auto")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()

def copy_transactional(src, dst, dry):
    if dry: return None
    dst.parent.mkdir(parents=True, exist_ok=True)
    stage=dst.with_name(dst.name+f".installing-{os.getpid()}")
    if stage.exists(): shutil.rmtree(stage)
    shutil.copytree(src, stage, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    backup=None
    if dst.exists():
        stamp=dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup=dst.with_name(dst.name+f".backup-{stamp}")
        i=2
        while backup.exists(): backup=dst.with_name(dst.name+f".backup-{stamp}-{i}"); i+=1
        dst.rename(backup)
    stage.rename(dst)
    return backup

def update_marketplace(path, plugin_rel, dry):
    if path.exists():
        try: data=json.loads(path.read_text(encoding="utf-8"))
        except Exception as e: raise SystemExit(f"Cannot parse existing marketplace {path}: {e}")
    else: data={"name":"adaptive-master-subagent-orchestration","interface":{"displayName":"Adaptive Master–Subagent Orchestration"},"plugins":[]}
    plugins=data.setdefault("plugins",[])
    entry={"name":PLUGIN_NAME,"source":{"source":"local","path":plugin_rel},"policy":{"installation":"AVAILABLE","authentication":"ON_INSTALL"},"category":"Productivity"}
    for i,item in enumerate(plugins):
        if isinstance(item,dict) and item.get("name")==PLUGIN_NAME: plugins[i]=entry; break
    else: plugins.append(entry)
    if dry: return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")

def main():
    a=parse()
    if a.skip_profiles and not ALLOW_SKIP_PROFILES:
        raise SystemExit("Option C requires profile installation; --skip-profiles is not allowed.")
    src=Path(__file__).resolve().parents[1]
    manifest=src/".codex-plugin"/"plugin.json"
    if not manifest.exists(): raise SystemExit(f"Plugin manifest not found: {manifest}")
    market_root=a.home/".agents"/"plugins"
    codex_home=Path(os.environ.get("CODEX_HOME", a.home/".codex"))
    dst=market_root/"plugins"/PLUGIN_NAME
    rel=f"./plugins/{PLUGIN_NAME}"
    if a.dry_run:
        print(f"would-install plugin {src} -> {dst}")
        print(f"would-register {PLUGIN_NAME} in {market_root/'marketplace.json'}")
    backup=copy_transactional(src,dst,a.dry_run)
    update_marketplace(market_root/"marketplace.json",rel,a.dry_run)
    exec_root=src if a.dry_run else dst
    if not a.skip_profiles:
        cmd=[sys.executable,str(exec_root/"scripts"/"bootstrap_profiles.py"),"--destination",str(codex_home/"agents"),"--spark-efforts",a.spark_efforts]
        if a.exclude_spark: cmd.append("--exclude-spark")
        if a.upgrade_managed: cmd.append("--upgrade-managed")
        if a.dry_run: cmd.append("--dry-run")
        subprocess.run(cmd,check=True)
    config=codex_home/"ams-orchestration.toml"
    if config.exists(): print(f"preserved intensity config: {config}")
    elif a.dry_run: print(f"would-create intensity config {config} with {a.intensity}")
    else:
        config.parent.mkdir(parents=True,exist_ok=True)
        config.write_text(f'schema_version = 1\\nintensity = "{a.intensity}"\\n',encoding="utf-8")
        print(f"created intensity config: {config}")
    print(f"plugin registered: {PLUGIN_NAME}")
    if backup: print(f"previous plugin backup: {backup}")
    print("Open the ChatGPT desktop app Plugins directory, install/enable the plugin from the personal marketplace, and restart if it is not detected.")
    return 0
if __name__ == "__main__": raise SystemExit(main())
