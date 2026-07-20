#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import hashlib, shutil

PAYLOAD = Path(__file__).resolve().parent
REPO = PAYLOAD.parent
ROOT = PAYLOAD / 'root'
SHARED = PAYLOAD / 'shared'
OPTIONS = {
    'adaptive-master-subagent-orchestration-option-a-two-skill': {
        'option': 'A', 'plugin': 'adaptive-master-subagent-orchestration-option-a-two-skill', 'allow_skip': 'True'
    },
    'adaptive-master-subagent-orchestration-option-b-unified': {
        'option': 'B', 'plugin': 'adaptive-master-subagent-orchestration-option-b-unified', 'allow_skip': 'True'
    },
    'adaptive-master-subagent-orchestration-option-c-installer-required': {
        'option': 'C', 'plugin': 'adaptive-master-subagent-orchestration-option-c-installer-required', 'allow_skip': 'False'
    },
}

def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)

def render(src: Path, dst: Path, values: dict[str, str]) -> None:
    text = src.read_text(encoding='utf-8')
    text = text.replace('__PLUGIN_NAME__', repr(values['plugin']))
    text = text.replace('__OPTION__', repr(values['option']))
    text = text.replace('__ALLOW_SKIP_PROFILES__', values['allow_skip'])
    dst.write_text(text, encoding='utf-8')

def regenerate_manifest(package: Path) -> None:
    lines=[]
    for path in sorted(p for p in package.rglob('*') if p.is_file() and p.name != 'MANIFEST.sha256' and '__pycache__' not in p.parts and p.suffix not in {'.pyc','.pyo'}):
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(package).as_posix()}")
    (package/'MANIFEST.sha256').write_text('\n'.join(lines)+'\n', encoding='utf-8')

for src in ROOT.rglob('*'):
    if src.is_file():
        copy_file(src, REPO / src.relative_to(ROOT))

for name, values in OPTIONS.items():
    package = REPO / name
    scripts = package / 'scripts'
    copy_file(SHARED/'Install-Package.ps1', package/'Install-Package.ps1')
    copy_file(SHARED/'Install-AgentProfiles.ps1', scripts/'Install-AgentProfiles.ps1')
    copy_file(SHARED/'Set-Intensity.ps1', scripts/'Set-Intensity.ps1')
    for filename in ['bootstrap_profiles.py','set_intensity.py','test_bootstrap.py','test_installation.py','test_intensity.py','process_utils.py']:
        copy_file(SHARED/filename, scripts/filename)
    render(SHARED/'install_package_template.py', scripts/'install_package.py', values)
    render(SHARED/'validate_package_template.py', scripts/'validate_package.py', values)
    regenerate_manifest(package)

(REPO/'install.sh').chmod(0o755)
for path in [REPO/'scripts/audit_installers.py', REPO/'tests/test_installers.py']:
    path.chmod(0o755)
print('Installer audit payload applied.')
