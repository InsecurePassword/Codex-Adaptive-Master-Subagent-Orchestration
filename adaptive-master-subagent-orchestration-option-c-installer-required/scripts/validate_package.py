#!/usr/bin/env python3
"""Validate an AMS package and run its installer regression suite."""
from __future__ import annotations
import argparse, json, shutil, subprocess, sys, tomllib
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from process_utils import run_bounded
PLUGIN_NAME='adaptive-master-subagent-orchestration-option-c-installer-required'
OPTION='C'
EXPECTED_SKILLS=['ams-orchestration']
PACKAGE_LABELS={
    'A':'Option A — Two-skill automated setup',
    'B':'Option B — Unified conditional bootstrap',
    'C':'Option C — Installer-required lean runtime',
}
TIMEOUT=180

def require(c:bool,m:str)->None:
    if not c: raise RuntimeError(m)

def run(path:Path)->None:
    command=[sys.executable,'-B','-E','-s','-S',str(path)]
    try: result=run_bounded(command,timeout=TIMEOUT,check=False,stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired as exc: raise RuntimeError(f'test timed out: {path.name}') from exc
    require(result.returncode==0,f'test failed ({result.returncode}): {path.name}')

def manifest_check()->None:
    import install_package
    install_package.validate_manifest(ROOT)

def structure_check(*, scripts_only: bool)->None:
    require((ROOT/'VERSION').read_text(encoding='utf-8').strip()=='3.1.0','VERSION mismatch')
    require((ROOT/'PACKAGE-OPTION').read_text(encoding='utf-8').strip()==PACKAGE_LABELS[OPTION],'PACKAGE-OPTION mismatch')
    data=json.loads((ROOT/'.codex-plugin/plugin.json').read_text(encoding='utf-8'))
    require(data.get('name')==PLUGIN_NAME,'plugin name mismatch'); require(data.get('version')=='3.1.0','plugin version mismatch'); require(data.get('skills')=='./skills/','skills path mismatch')
    skills=sorted(p.name for p in (ROOT/'skills').iterdir() if p.is_dir())
    require(skills==sorted(EXPECTED_SKILLS),f'skill set mismatch: {skills}')
    if not scripts_only:
        for skill in EXPECTED_SKILLS:
            text=(ROOT/'skills'/skill/'SKILL.md').read_text(encoding='utf-8'); require(text.startswith('---\n'),'skill frontmatter missing'); require(f'name: {skill}' in text,'skill name mismatch')
            require((ROOT/'skills'/skill/'agents/openai.yaml').is_file(),'agent metadata missing')
    profiles=sorted((ROOT/'assets/agent-profiles').glob('*.toml')); require(len(profiles)==18,'profile count mismatch')
    for path in profiles:
        data=tomllib.loads(path.read_text(encoding='utf-8')); require(data.get('name')==path.stem,f'profile name mismatch: {path.name}')
    required=['Install-Package.ps1','scripts/Install-AgentProfiles.ps1','scripts/Set-Intensity.ps1','scripts/bootstrap_profiles.py','scripts/install_package.py','scripts/process_utils.py','scripts/set_intensity.py','scripts/test_bootstrap.py','scripts/test_installation.py','scripts/test_intensity.py','scripts/validate_package.py']
    for rel in required: require((ROOT/rel).is_file(),f'missing {rel}')
    bad=[p for p in ROOT.rglob('*') if '__pycache__' in p.parts or p.suffix in {'.pyc','.pyo'}]; require(not bad,f'generated artifacts present: {bad}')

def syntax_check()->None:
    for p in ROOT.rglob('*.py'): compile(p.read_text(encoding='utf-8'),str(p),'exec')
    for exe in ('sh','dash','bash'):
        resolved=shutil.which(exe)
        if resolved and (ROOT/'../install.sh').is_file(): pass

def main(argv:list[str]|None=None)->int:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--scripts-only',action='store_true'); args=parser.parse_args(argv)
    structure_check(scripts_only=args.scripts_only); syntax_check(); manifest_check()
    for name in ('test_bootstrap.py','test_intensity.py','test_installation.py'): run(ROOT/'scripts'/name)
    manifest_check()
    print(f'PACKAGE VALIDATION PASSED: option {OPTION}')
    return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except SystemExit: raise
    except Exception as exc: print(f'PACKAGE VALIDATION FAILED: {exc}',file=sys.stderr); raise SystemExit(1) from exc
