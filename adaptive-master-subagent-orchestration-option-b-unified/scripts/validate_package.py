#!/usr/bin/env python3
"""Validate the Adaptive Master–Subagent package and its deterministic installers."""
from __future__ import annotations
import hashlib, json, re, subprocess, sys, tempfile, tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OPTION='B'
EXPECTED_SKILLS=['unified']
VALID_INTENSITY={"auto","minimal","moderate","heavy","extreme"}

def fail(msg): raise AssertionError(msg)
def frontmatter(text):
    if not text.startswith("---\n"): fail("SKILL.md missing frontmatter")
    end=text.find("\n---\n",4)
    if end<0: fail("SKILL.md unterminated frontmatter")
    fm=text[4:end]
    for k in ("name:","description:"):
        if k not in fm: fail(f"SKILL.md missing {k}")
    return fm

def check_manifest():
    data=json.loads((ROOT/".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    assert data["version"]=="3.1.0" and data["skills"]=="./skills/"
    assert data["name"]=="adaptive-master-subagent-orchestration-option-b-unified"

def check_hashes():
    listed={}
    for line in (ROOT/"MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        h,rel=line.split("  ",1); listed[rel]=h
    actual={}
    for p in ROOT.rglob("*"):
        if p.is_file() and p.name!="MANIFEST.sha256" and "__pycache__" not in p.parts:
            actual[p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    assert listed==actual, "manifest membership or digest mismatch"

def check_profiles():
    profiles=sorted((ROOT/"assets/agent-profiles").glob("*.toml")); assert len(profiles)==18
    for p in profiles:
        d=tomllib.loads(p.read_text(encoding="utf-8"))
        for k in ("name","description","model","model_reasoning_effort","developer_instructions"): assert d.get(k)
        assert d["name"]==p.stem
        assert f"profile-version: 3.1.0" in p.read_text(encoding="utf-8")
        if p.stem.startswith("ams_spark_"):
            assert d["model_reasoning_effort"] in {"low","medium","high"}
            assert d.get("sandbox_mode")=="workspace-write"
        else: assert d["model_reasoning_effort"] in {"low","medium","high","xhigh","max"}

def check_skills():
    dirs=sorted(p.name for p in (ROOT/"skills").iterdir() if p.is_dir())
    mapping={"profile-manager":"ams-profile-manager","runtime":"ams-orchestration","resume":"ams-resume","unified":"adaptive-master-subagent-orchestration"}
    expected=sorted(mapping[x] for x in EXPECTED_SKILLS)
    actual=[]
    texts={}
    for d in (ROOT/"skills").iterdir():
        if not d.is_dir(): continue
        p=d/"SKILL.md"; assert p.exists() and (d/"agents/openai.yaml").exists()
        t=p.read_text(encoding="utf-8"); fm=frontmatter(t)
        m=re.search(r'(?m)^name:\s*(.+)$',fm); assert m
        actual.append(m.group(1).strip()); texts[m.group(1).strip()]=t
        assert f"Module version: 3.1.0" in t
    assert sorted(actual)==expected, (actual,expected)
    for name,t in texts.items():
        if name in {"ams-orchestration","adaptive-master-subagent-orchestration"}:
            for mode in VALID_INTENSITY: assert f'`{mode}`' in t
            assert "`auto`" in t and "previous skill behavior" in t
            assert "never an agent quota" in t
            spark=t.index("### Supplemental Spark routing")
            effort=t.index("### Sol/Terra/Luna effort routing")
            assert effort < spark, "general effort routing nested after Spark"
            for phrase in ["Sol Max", "direct, non-delegating children", "WORK ORDER", "RESULT", "Execution-deviation decision gate", "Continue autonomously", "Terminal state", "Prohibited behavior"]: assert phrase in t, phrase
        if name=="ams-resume":
            for phrase in ["Interrupted-project recovery","Do not wait for inaccessible","Recovery anti-stall","original objective","final-diff"]: assert phrase in t
    if OPTION in {"A","C"}:
        rt=texts["ams-orchestration"]
        assert "bootstrap_profiles.py" not in rt and "Profile bootstrap must be idempotent" not in rt
    if OPTION=="A": assert "ams-profile-manager" in texts and "bootstrap_profiles.py" in texts["ams-profile-manager"]
    if OPTION=="B":
        u=texts["adaptive-master-subagent-orchestration"]
        assert "bootstrap_profiles.py" in u and "When all required selected profiles are valid" in u and "Recovery overlay" in u
    if OPTION=="C": assert "ams-profile-manager" not in texts

def run_tests():
    subprocess.run([sys.executable,str(ROOT/"scripts/test_bootstrap.py")],check=True)
    with tempfile.TemporaryDirectory(prefix="ams-v300-") as tmp:
        home=Path(tmp)/"home"
        cmd=[sys.executable,str(ROOT/"scripts/install_package.py"),"--home",str(home),"--dry-run"]
        subprocess.run(cmd,check=True)
        assert not home.exists(), "package dry-run mutated home"
        cmd=[sys.executable,str(ROOT/"scripts/install_package.py"),"--home",str(home),"--exclude-spark"]
        subprocess.run(cmd,check=True)
        assert (home/".agents/plugins/marketplace.json").exists()
        assert len(list((home/".codex/agents").glob("*.toml")))==15
        config=(home/".codex/ams-orchestration.toml").read_text(encoding="utf-8")
        assert 'intensity = "auto"' in config
        subprocess.run([sys.executable,str(ROOT/"scripts/set_intensity.py"),"heavy","--scope","user"],check=True,env={**dict(__import__('os').environ),"CODEX_HOME":str(home/".codex")})
        assert 'intensity = "heavy"' in (home/".codex/ams-orchestration.toml").read_text(encoding="utf-8")
        if OPTION=="C":
            r=subprocess.run([sys.executable,str(ROOT/"scripts/install_package.py"),"--home",str(Path(tmp)/"bad"),"--skip-profiles"],text=True,capture_output=True)
            assert r.returncode!=0 and "requires profile installation" in (r.stdout+r.stderr)

def main():
    check_manifest(); check_profiles(); check_skills(); run_tests(); check_hashes(); print(f"PACKAGE VALIDATION PASSED: option {OPTION}")
if __name__=="__main__":
    try: main()
    except Exception as e:
        print(f"PACKAGE VALIDATION FAILED: {e}",file=sys.stderr); raise
