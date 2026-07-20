#!/usr/bin/env python3
"""Regenerate or verify all AMS package manifests from repository bytes."""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAMES = (
    "adaptive-master-subagent-orchestration-option-a-two-skill",
    "adaptive-master-subagent-orchestration-option-b-unified",
    "adaptive-master-subagent-orchestration-option-c-installer-required",
)
GENERATED_SUFFIXES = {".pyc", ".pyo"}


def package_manifest(package: Path) -> str:
    lines: list[str] = []
    paths = sorted(
        package.rglob("*"),
        key=lambda path: path.relative_to(package).as_posix(),
    )
    for path in paths:
        if path.is_symlink():
            raise RuntimeError(f"package contains a symbolic link: {path}")
        if not path.is_file() or path.name == "MANIFEST.sha256":
            continue
        if "__pycache__" in path.parts or path.suffix in GENERATED_SUFFIXES:
            raise RuntimeError(f"package contains a generated Python artifact: {path}")
        relative = path.relative_to(package).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {relative}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify manifests without changing files.")
    args = parser.parse_args(argv)

    failures: list[str] = []
    for name in PACKAGE_NAMES:
        package = ROOT / name
        if not package.is_dir() or package.is_symlink():
            failures.append(f"missing package directory: {package}")
            continue
        manifest_path = package / "MANIFEST.sha256"
        expected = package_manifest(package)
        if args.check:
            if not manifest_path.is_file() or manifest_path.is_symlink():
                failures.append(f"missing regular manifest: {manifest_path}")
            elif manifest_path.read_text(encoding="utf-8") != expected:
                failures.append(f"manifest is stale: {manifest_path}")
        else:
            manifest_path.write_text(expected, encoding="utf-8", newline="\n")
            print(f"refreshed: {manifest_path.relative_to(ROOT)}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    if args.check:
        print("PACKAGE MANIFESTS CURRENT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
