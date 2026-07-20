#!/usr/bin/env python3
"""Regression tests for set_intensity.py using only the Python standard library."""

from __future__ import annotations

import importlib.util
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path
from types import ModuleType

sys.dont_write_bytecode = True
from process_utils import run_bounded

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "set_intensity.py"
COMMAND_TIMEOUT = 15


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("set_intensity_under_test", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load intensity module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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

        lock.write_text("{malformed", encoding="utf-8")
        os.utime(lock, (old, old))
        run("heavy", env=env)
        require(not lock.exists(), "malformed stale intensity lock was not recovered")
        if hasattr(os, "symlink"):
            target = codex / "intensity-lock-target"
            target.write_text("target", encoding="utf-8")
            try:
                lock.symlink_to(target)
            except OSError:
                pass
            else:
                output = run("heavy", env=env, expect=1)
                require("not a regular file" in output, "intensity lock symlink error was unclear")
                lock.unlink()

        module = load_module()
        permission_config = base / "permission-intensity" / "ams-orchestration.toml"
        permission_lock = permission_config.parent / ".ams-orchestration-config.lock"
        original_open = module.os.open
        def denied_open(path, *args, **kwargs):
            if Path(path) == permission_lock:
                raise PermissionError("injected intensity lock creation denial")
            return original_open(path, *args, **kwargs)
        module.os.open = denied_open
        try:
            try:
                with module.config_lock(permission_config):
                    pass
            except SystemExit as exc:
                require("Unable to create intensity lock path" in str(exc), f"intensity lock creation denial was unclear: {exc}")
            else:
                raise AssertionError("intensity lock creation denial was not reported")
        finally:
            module.os.open = original_open

        permission_config.parent.mkdir(parents=True, exist_ok=True)
        permission_lock.write_text("{}\n", encoding="utf-8")
        original_lstat = module.Path.lstat
        def denied_lstat(self, *args, **kwargs):
            if self == permission_lock:
                raise PermissionError("injected intensity lock inspection denial")
            return original_lstat(self, *args, **kwargs)
        module.Path.lstat = denied_lstat
        try:
            try:
                with module.config_lock(permission_config):
                    pass
            except SystemExit as exc:
                require("Unable to inspect intensity lock path" in str(exc), f"intensity lock inspection denial was unclear: {exc}")
            else:
                raise AssertionError("intensity lock inspection denial was not reported")
        finally:
            module.Path.lstat = original_lstat
            permission_lock.unlink(missing_ok=True)

        cleanup_config = base / "cleanup-intensity" / "ams-orchestration.toml"
        cleanup_lock = cleanup_config.parent / ".ams-orchestration-config.lock"
        try:
            with module.config_lock(cleanup_config):
                require(cleanup_lock.exists(), "intensity lock was not created")
                raise RuntimeError("injected intensity operation failure")
        except RuntimeError:
            pass
        require(not cleanup_lock.exists(), "intensity lock was not cleaned after failure")

        output = run("--dry-run", env=env, expect=2)
        require("requires MODE" in output, "dry-run without mode error was unclear")
        output = run("heavy", "--show", env=env, expect=2)
        require("cannot be used together" in output, "mode/show conflict error was unclear")

    print("INTENSITY TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
