#!/usr/bin/env python3
"""Validate package structure, manifests, installers, and offline integration tests."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path, PurePosixPath

from process_utils import run_bounded

ROOT = Path(__file__).resolve().parents[1]
OPTION = __OPTION__
EXPECTED_PLUGIN = __PLUGIN_NAME__
EXPECTED_SKILLS = __EXPECTED_SKILLS__
VERSION = "3.1.0"
TEST_TIMEOUT = 120
REQUIRED_SCRIPTS = {
    "Install-Package.ps1",
    "scripts/Install-AgentProfiles.ps1",
    "scripts/Set-Intensity.ps1",
    "scripts/bootstrap_profiles.py",
    "scripts/install_package.py",
    "scripts/process_utils.py",
    "scripts/set_intensity.py",
    "scripts/test_bootstrap.py",
    "scripts/test_installation.py",
    "scripts/test_intensity.py",
    "scripts/validate_package.py",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scripts-only",
        action="store_true",
        help="Audit installation/update tooling without inspecting skill contents.",
    )
    return parser.parse_args(argv)


def fail(message: str) -> None:
    raise RuntimeError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def manifest_entries() -> dict[str, str]:
    path = ROOT / "MANIFEST.sha256"
    require(path.is_file() and not path.is_symlink(), f"manifest missing or not regular: {path}")
    entries: dict[str, str] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        parts = line.split("  ", 1)
        require(len(parts) == 2, f"malformed manifest line {number}: {line}")
        digest, relative = parts
        require(re.fullmatch(r"[0-9a-fA-F]{64}", digest) is not None, f"invalid digest on manifest line {number}")
        posix = PurePosixPath(relative)
        require(not posix.is_absolute() and all(part not in ("", ".", "..") for part in posix.parts), f"unsafe manifest path: {relative}")
        require(relative not in entries, f"duplicate manifest path: {relative}")
        entries[relative] = digest.lower()
    return entries


def actual_entries() -> dict[str, str]:
    entries: dict[str, str] = {}
    for path in ROOT.rglob("*"):
        if path.is_symlink():
            fail(f"package contains symbolic link: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative == "MANIFEST.sha256" or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        entries[relative] = sha256(path)
    return entries


def check_manifest() -> None:
    listed = manifest_entries()
    actual = actual_entries()
    if listed != actual:
        missing = sorted(set(actual) - set(listed))
        extra = sorted(set(listed) - set(actual))
        changed = sorted(key for key in set(actual) & set(listed) if actual[key] != listed[key])
        fail(f"manifest mismatch; unlisted={missing}, missing={extra}, changed={changed}")


def check_plugin_metadata() -> None:
    path = ROOT / ".codex-plugin" / "plugin.json"
    require(path.is_file() and not path.is_symlink(), f"plugin metadata missing: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail(f"invalid plugin metadata: {exc}")
    require(isinstance(data, dict), "plugin metadata root must be an object")
    require(data.get("name") == EXPECTED_PLUGIN, f"plugin name mismatch: {data.get('name')!r}")
    require(data.get("version") == VERSION, f"plugin version mismatch: {data.get('version')!r}")
    require(data.get("skills") == "./skills/", f"plugin skills path mismatch: {data.get('skills')!r}")


def check_profiles() -> None:
    directory = ROOT / "assets" / "agent-profiles"
    profiles = sorted(directory.glob("*.toml"))
    require(len(profiles) == 18, f"expected 18 profiles, found {len(profiles)}")
    for path in profiles:
        require(path.is_file() and not path.is_symlink(), f"profile is not a regular file: {path}")
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
            fail(f"invalid profile TOML {path}: {exc}")
        for key in ("name", "description", "model", "model_reasoning_effort", "developer_instructions"):
            require(isinstance(data.get(key), str) and str(data[key]).strip(), f"profile {path.name} missing {key}")
        require(data["name"] == path.stem, f"profile name mismatch: {path}")
        if path.stem.startswith("ams_spark_"):
            require(data["model_reasoning_effort"] in {"low", "medium", "high"}, f"invalid Spark effort: {path}")
            require(data.get("sandbox_mode") == "workspace-write", f"Spark profile missing workspace-write: {path}")
        else:
            require(data["model_reasoning_effort"] in {"low", "medium", "high", "xhigh", "max"}, f"invalid effort: {path}")


def check_scripts() -> None:
    for relative in sorted(REQUIRED_SCRIPTS):
        path = ROOT / relative
        require(path.is_file() and not path.is_symlink(), f"required script missing or not regular: {relative}")
        require(path.stat().st_size > 0, f"required script is empty: {relative}")
    for path in sorted((ROOT / "scripts").glob("*.py")):
        text = path.read_text(encoding="utf-8")
        try:
            compile(text, str(path), "exec")
        except SyntaxError as exc:
            fail(f"Python syntax error in {path}: {exc}")
    for path in [ROOT / "Install-Package.ps1", ROOT / "scripts" / "Install-AgentProfiles.ps1", ROOT / "scripts" / "Set-Intensity.ps1"]:
        text = path.read_text(encoding="utf-8")
        require("Set-StrictMode" in text, f"PowerShell strict mode missing: {path}")
        require("$ErrorActionPreference = \"Stop\"" in text, f"PowerShell stop-on-error missing: {path}")
        require("Resolve-Python311" in text, f"PowerShell Python resolution missing: {path}")


def check_skills_structure() -> None:
    skills_root = ROOT / "skills"
    actual = sorted(path.name for path in skills_root.iterdir() if path.is_dir())
    require(actual == sorted(EXPECTED_SKILLS), f"skill directory mismatch: actual={actual}, expected={EXPECTED_SKILLS}")
    for name in EXPECTED_SKILLS:
        skill = skills_root / name / "SKILL.md"
        agent = skills_root / name / "agents" / "openai.yaml"
        require(skill.is_file() and not skill.is_symlink(), f"skill file missing: {skill}")
        require(agent.is_file() and not agent.is_symlink(), f"skill agent metadata missing: {agent}")
        text = skill.read_text(encoding="utf-8")
        require(text.startswith("---\n") and "\n---\n" in text[4:], f"skill frontmatter malformed: {skill}")


def run_test(relative: str) -> None:
    command = [sys.executable, "-E", "-s", "-S", str(ROOT / relative)]
    try:
        result = run_bounded(
            command, text=True, capture_output=True, check=False, timeout=TEST_TIMEOUT
        )
    except subprocess.TimeoutExpired as exc:
        fail(f"test timed out after {TEST_TIMEOUT}s: {relative}")
    if result.returncode != 0:
        fail(
            f"test failed: {relative}\nstdout={result.stdout}\nstderr={result.stderr}"
        )
    output = result.stdout.strip()
    if output:
        print(output)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    check_manifest()
    check_plugin_metadata()
    check_profiles()
    check_scripts()
    if not args.scripts_only:
        check_skills_structure()
    run_test("scripts/test_bootstrap.py")
    run_test("scripts/test_intensity.py")
    run_test("scripts/test_installation.py")
    check_manifest()
    print(f"PACKAGE VALIDATION PASSED: option {OPTION}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print(f"PACKAGE VALIDATION FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
