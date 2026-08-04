#!/usr/bin/env python3
"""Windows installer transaction wrapper using native Windows PowerShell state.

Repository-release tooling only; never installed or executed by AMS.
The GitHub job runs under PowerShell 7, so reset its PSModulePath before
launching Windows PowerShell 5.1. Directory timestamp backdating is also not
reliable across hosted Windows filesystems, so use the real initialization grace.
"""
from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path

# Let Windows PowerShell 5.1 construct its native module path instead of
# inheriting PowerShell 7's incompatible module search path from the runner.
os.environ.pop("PSModulePath", None)

import verify_installers


def wait_for_initialization_grace(_path: Path) -> None:
    time.sleep(31)


verify_installers.make_directory_stale = wait_for_initialization_grace

# Add fixture-only diagnostics for an unexpected Windows ACL entry. The copied
# script is disposable and does not change the product installer.
with tempfile.TemporaryDirectory() as diagnostic_dir:
    diagnostic_path = Path(diagnostic_dir) / "install-diagnostic.ps1"
    text = verify_installers.INSTALL_PS1.read_text(encoding="utf-8")
    text = text.replace(
        'throw "AMS runtime path grants access outside the current user/system/administrators boundary: $Path"',
        'throw "AMS runtime path grants access outside the current user/system/administrators boundary: $Path; SID=$($Rule.IdentityReference.Value); rights=$($Rule.FileSystemRights); inherited=$($Rule.IsInherited)"',
    )
    diagnostic_path.write_text(text, encoding="utf-8", newline="\n")
    verify_installers.INSTALL_PS1 = diagnostic_path
    raise SystemExit(verify_installers.main())
