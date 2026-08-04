#!/usr/bin/env python3
"""Windows installer transaction wrapper using the real lock initialization grace.

Repository-release tooling only; never installed or executed by AMS.
Windows directory timestamp backdating is not reliable across hosted filesystems,
so this wrapper preserves the exact product behavior and waits for the real grace.
"""
from __future__ import annotations

import time
from pathlib import Path

import verify_installers


def wait_for_initialization_grace(_path: Path) -> None:
    time.sleep(31)


verify_installers.make_directory_stale = wait_for_initialization_grace
raise SystemExit(verify_installers.main())
