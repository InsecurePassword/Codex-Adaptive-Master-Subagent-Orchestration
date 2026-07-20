#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

PAYLOAD = Path(__file__).resolve().parent
REPO = PAYLOAD.parent
ROOT = PAYLOAD / "root"
SHARED = PAYLOAD / "shared"
ASSEMBLED = PAYLOAD / ".assembled"

OPTIONS = {
    "adaptive-master-subagent-orchestration-option-a-two-skill": {
        "option": "A",
        "plugin": "adaptive-master-subagent-orchestration-option-a-two-skill",
        "allow_skip": "True",
        "skills": ["ams-installer", "ams-orchestration"],
    },
    "adaptive-master-subagent-orchestration-option-b-unified": {
        "option": "B",
        "plugin": "adaptive-master-subagent-orchestration-option-b-unified",
        "allow_skip": "True",
        "skills": ["adaptive-master-subagent-orchestration"],
    },
    "adaptive-master-subagent-orchestration-option-c-installer-required": {
        "option": "C",
        "plugin": "adaptive-master-subagent-orchestration-option-c-installer-required",
        "allow_skip": "False",
        "skills": ["ams-orchestration"],
    },
}

SHARED_FILES = (
    "bootstrap_profiles.py",
    "set_intensity.py",
    "test_bootstrap.py",
    "test_installation.py",
    "test_intensity.py",
    "process_utils.py",
)


def shared_source(name: str) -> Path:
    final_parts = sorted(SHARED.glob(name + ".final-*"))
    if final_parts:
        parts = final_parts
    else:
        direct = SHARED / name
        if direct.is_file():
            return direct
        parts = sorted(SHARED.glob(name + ".part-*"))
    if not parts:
        raise FileNotFoundError(f"No staged source found for {name}")
    target = ASSEMBLED / name
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as output:
        for part in parts:
            output.write(part.read_text(encoding="utf-8"))
    return target


def copy_file(src: Path, dst: Path) -> None:
    if not src.is_file():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def render(src: Path, dst: Path, values: dict[str, object]) -> None:
    text = src.read_text(encoding="utf-8")
    replacements = {
        "__PLUGIN_NAME__": repr(values["plugin"]),
        "__OPTION__": repr(values["option"]),
        "__ALLOW_SKIP_PROFILES__": str(values["allow_skip"]),
        "__EXPECTED_SKILLS__": repr(values["skills"]),
    }
    for placeholder, replacement in replacements.items():
        text = text.replace(placeholder, replacement)
    unresolved = sorted(token for token in replacements if token in text)
    if unresolved:
        raise RuntimeError(f"Unresolved template placeholders in {src}: {unresolved}")
    compile(text, str(dst), "exec")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8", newline="\n")


def regenerate_manifest(package: Path) -> None:
    generated = [
        path
        for path in package.rglob("*")
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}
    ]
    if generated:
        raise RuntimeError(f"Generated Python artifacts found before manifest generation: {generated}")
    lines: list[str] = []
    files = sorted(path for path in package.rglob("*") if path.is_file() and path.name != "MANIFEST.sha256")
    for path in files:
        relative = path.relative_to(package).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {relative}")
    (package / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    staged_python = [shared_source(name) for name in SHARED_FILES]
    staged_python += [shared_source("install_package_template.py"), shared_source("validate_package_template.py")]
    for path in staged_python:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")

    for src in sorted(ROOT.rglob("*")):
        if src.is_file():
            copy_file(src, REPO / src.relative_to(ROOT))

    for name, values in OPTIONS.items():
        package = REPO / name
        scripts = package / "scripts"
        copy_file(SHARED / "Install-Package.ps1", package / "Install-Package.ps1")
        copy_file(SHARED / "Install-AgentProfiles.ps1", scripts / "Install-AgentProfiles.ps1")
        copy_file(SHARED / "Set-Intensity.ps1", scripts / "Set-Intensity.ps1")
        for filename in SHARED_FILES:
            copy_file(shared_source(filename), scripts / filename)
        render(shared_source("install_package_template.py"), scripts / "install_package.py", values)
        render(shared_source("validate_package_template.py"), scripts / "validate_package.py", values)
        regenerate_manifest(package)

    (REPO / "install.sh").chmod(0o755)
    for path in (REPO / "scripts" / "audit_installers.py", REPO / "tests" / "test_installers.py"):
        path.chmod(0o755)
    print("Installer audit payload applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
