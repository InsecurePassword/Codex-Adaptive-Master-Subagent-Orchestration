#!/usr/bin/env python3
"""Regression tests for set_intensity.py using only the Python standard library."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path

sys.dont_write_bytecode = True
from process_utils import run_bounded

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "set_intensity.py"
COMMAND_TIMEOUT = 15


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run(*args: str, env: dict[str, str] | None = None, expect: int = 0) -> str:
    command = [sys.executable, "-B", "-E", "-s", "-S", str(SCRIPT), *args]
    try:
        result = run_bounded(
            command,
            text=True,
            capture_output=True,
            check=False,
            env=env,
            timeout=COMMAND_TIMEOUT,
        )
    except subprocess.TimeoutExpired as exc:
        raise AssertionError(f"intensity command timed out: {command}") from exc
    if result.returncode != expect:
        raise AssertionError(
            f"command returned {result.returncode}, expected {expect}: {command}\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
    return (result.stdout or "") + (result.stderr or "")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="ams-intensity-tests-") as tmp:
        base = Path(tmp)
        codex = base / "codex"
        env = dict(os.environ)
        env["CODEX_HOME"] = str(codex)

        output = run("--show", env=env)
        require("unset (effective default: auto)" in output, "unset user intensity was reported incorrectly")
        require(not codex.exists(), "show created CODEX_HOME")

        run("heavy", env=env)
        config = codex / "ams-orchestration.toml"
        require(tomllib.loads(config.read_text(encoding="utf-8"))["intensity"] == "heavy", "user intensity was not written")
        before = config.read_bytes()
        output = run("extreme", "--dry-run", env=env)
        require("would-write" in output, "dry-run output was unclear")
        require(config.read_bytes() == before, "dry-run changed the config")

        project = base / "project"
        run("moderate", "--scope", "project", "--project-root", str(project), env=env)
        project_config = project / ".codex" / "ams-orchestration.toml"
        require(tomllib.loads(project_config.read_text(encoding="utf-8"))["intensity"] == "moderate", "project intensity was not written")
        require(tomllib.loads(config.read_text(encoding="utf-8"))["intensity"] == "heavy", "project update changed user config")

        config.write_text("invalid", encoding="utf-8")
        output = run("--show", env=env, expect=2)
        require("invalid TOML" in output, "invalid config was not reported")
        run("minimal", env=env)
        require(tomllib.loads(config.read_text(encoding="utf-8"))["intensity"] == "minimal", "explicit set did not repair invalid config")

        lock = codex / ".ams-orchestration-config.lock"
        lock.write_text(json.dumps({"pid": os.getpid(), "host": socket.gethostname()}) + "\n", encoding="utf-8")
        old = time.time() - (3 * 60 * 60)
        os.utime(lock, (old, old))
        output = run("auto", env=env, expect=1)
        require("appears to be active" in output, "live config lock was not enforced")
        require(lock.exists(), "live config lock was removed")

        lock.write_text(json.dumps({"pid": 99999999, "host": socket.gethostname()}) + "\n", encoding="utf-8")
        os.utime(lock, (old, old))
        run("auto", env=env)
        require(not lock.exists(), "dead stale config lock was not cleared")
        require(tomllib.loads(config.read_text(encoding="utf-8"))["intensity"] == "auto", "stale-lock recovery did not update config")

        lock.mkdir()
        output = run("heavy", env=env, expect=1)
        require("not a regular file" in output, "non-file intensity lock error was unclear")
        lock.rmdir()

        output = run("--dry-run", env=env, expect=2)
        require("requires MODE" in output, "dry-run without mode error was unclear")
        output = run("heavy", "--show", env=env, expect=2)
        require("cannot be used together" in output, "mode/show conflict error was unclear")

    print("INTENSITY TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
