#!/usr/bin/env python3
"""Windows installer transaction wrapper using native Windows PowerShell state.

Repository-release tooling only; never installed or executed by AMS.
The GitHub job runs under PowerShell 7, so reset its PSModulePath before
launching Windows PowerShell 5.1. Directory timestamp backdating is also not
reliable across hosted Windows filesystems, so use the real initialization grace.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

# Let Windows PowerShell 5.1 construct its native module path instead of
# inheriting PowerShell 7's incompatible module search path from the runner.
os.environ.pop("PSModulePath", None)

import verify_installers


def wait_for_initialization_grace(_path: Path) -> None:
    time.sleep(31)


def diagnostic_patch_powershell(path: Path, url: str) -> None:
    text = (verify_installers.ROOT / "install.ps1").read_text(encoding="utf-8")
    text = text.replace(
        '$RawBaseUrl = "https://github.com/$RepositoryOwner/$RepositoryName/raw/refs/heads/main"',
        f'$RawBaseUrl = "{url}"',
    )
    text = text.replace(
        '$ManifestUrl = "$RawBaseUrl/install-manifest.txt"',
        f'$ManifestUrl = "{url}/install-manifest.txt"',
    )
    text = text.replace(
        'throw "AMS runtime path grants access outside the current user/system/administrators boundary: $Path"',
        'throw "AMS runtime path grants access outside the current user/system/administrators boundary: $Path; SID=$($Rule.IdentityReference.Value); rights=$($Rule.FileSystemRights); inherited=$($Rule.IsInherited)"',
    )
    path.write_text(text, encoding="utf-8", newline="\n")


verify_installers.make_directory_stale = wait_for_initialization_grace
verify_installers.patch_powershell = diagnostic_patch_powershell
raise SystemExit(verify_installers.main())
