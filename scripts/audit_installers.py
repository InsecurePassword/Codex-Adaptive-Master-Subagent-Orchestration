#!/usr/bin/env python3
"""Run the complete offline audit for AMS installation, update, and uninstall tooling."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from process_utils import run_bounded

PACKAGE_PREFIX = "adaptive-master-subagent-orchestration-option-"
COMMAND_TIMEOUT = 180
TEXT_SUFFIXES = {".sh", ".py", ".ps1", ".md", ".toml", ".json", ".yaml", ".yml", ".sha256"}
TEXT_NAMES = {"VERSION", "PACKAGE-OPTION", ".gitattributes"}


def fail(message: str) -> None:
    raise RuntimeError(message)


def run(command: list[str], *, timeout: int = COMMAND_TIMEOUT) -> None:
    try:
        result = run_bounded(
            command,
            timeout=timeout,
            capture_output=False,
            check=False,
        )
    except subprocess.TimeoutExpired:
        fail(f"command timed out after {timeout}s: {command}")
    if result.returncode != 0:
        fail(f"command failed ({result.returncode}): {command}")


def line_ending_audit() -> None:
    print("[audit] reproducible LF line endings")
    attributes = ROOT / ".gitattributes"
    if not attributes.is_file() or "* text=auto eol=lf" not in attributes.read_text(encoding="utf-8"):
        fail(".gitattributes does not enforce LF for repository text files")
    bad: list[Path] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in TEXT_NAMES:
            continue
        if b"\r" in path.read_bytes():
            bad.append(path)
    if bad:
        fail("text files contain CR or CRLF bytes: " + ", ".join(str(path.relative_to(ROOT)) for path in bad))


def python_syntax_audit() -> None:
    print("[audit] Python syntax")
    for path in sorted(ROOT.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except (UnicodeDecodeError, SyntaxError) as exc:
            fail(f"Python syntax failure in {path}: {exc}")


def shell_syntax_audit() -> None:
    print("[audit] POSIX/Bash syntax")
    script = ROOT / "install.sh"
    for executable in ("sh", "dash", "bash"):
        resolved = shutil.which(executable)
        if resolved:
            run([resolved, "-n", str(script)], timeout=20)


def powershell_syntax_audit() -> None:
    print("[audit] PowerShell syntax")
    executable = shutil.which("pwsh") or shutil.which("powershell")
    if not executable:
        print("PowerShell runtime unavailable; repository root tests perform static delimiter and contract checks.")
        return
    scripts = sorted(ROOT.rglob("*.ps1"))
    quoted = ",".join("'" + str(path).replace("'", "''") + "'" for path in scripts)
    command = (
        "$failed=$false; foreach($p in @(" + quoted + ")) { "
        "$tokens=$null; $errors=$null; [System.Management.Automation.Language.Parser]::ParseFile($p,[ref]$tokens,[ref]$errors)|Out-Null; "
        "if($errors.Count){$failed=$true; Write-Error ($p + ': ' + (($errors|ForEach-Object Message)-join '; '))} }; "
        "if($failed){exit 1}"
    )
    run([executable, "-NoProfile", "-Command", command], timeout=60)


def no_generated_artifacts() -> None:
    print("[audit] generated-artifact hygiene")
    bad = [
        path
        for path in ROOT.rglob("*")
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}
    ]
    if bad:
        fail("generated Python artifacts are present: " + ", ".join(str(path) for path in bad))


def manifest_inventory_audit() -> None:
    print("[audit] canonical package manifests")
    run([sys.executable, "-B", "-E", "-s", "-S", str(ROOT / "scripts" / "refresh_manifests.py"), "--check"], timeout=60)


def markdown_audit() -> None:
    print("[audit] Markdown structure and links")
    run([sys.executable, "-B", "-E", "-s", "-S", str(ROOT / "scripts" / "audit_markdown.py")], timeout=60)


def root_integration_tests() -> None:
    script_name = "test_windows_installers.py" if os.name == "nt" else "test_installers.py"
    print(f"[audit] root installer integration ({script_name})")
    run(
        [sys.executable, "-B", "-E", "-s", "-S", str(ROOT / "tests" / script_name)],
        timeout=300 if os.name == "nt" else 180,
    )


def package_tests() -> None:
    print("[audit] package installer integration")
    packages = sorted(path for path in ROOT.iterdir() if path.is_dir() and path.name.startswith(PACKAGE_PREFIX))
    if len(packages) != 3:
        fail(f"expected three package options, found {len(packages)}")
    for package in packages:
        print(f"[audit] {package.name}")
        validator = package / "scripts" / "validate_package.py"
        run(
            [sys.executable, "-B", "-E", "-s", "-S", str(validator), "--scripts-only"],
            timeout=COMMAND_TIMEOUT,
        )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-root-tests", action="store_true", help="Skip repository-level Bash/PowerShell tests.")
    parser.add_argument("--skip-package-tests", action="store_true", help="Skip package-level integration tests.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    line_ending_audit()
    python_syntax_audit()
    shell_syntax_audit()
    powershell_syntax_audit()
    no_generated_artifacts()
    manifest_inventory_audit()
    markdown_audit()
    if not args.skip_root_tests:
        root_integration_tests()
    if not args.skip_package_tests:
        package_tests()
    no_generated_artifacts()
    print("INSTALLER AUDIT PASSED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print(f"INSTALLER AUDIT FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
