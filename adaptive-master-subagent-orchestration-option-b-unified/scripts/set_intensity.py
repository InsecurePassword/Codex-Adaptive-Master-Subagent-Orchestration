#!/usr/bin/env python3
"""Read or set Adaptive Master–Subagent orchestration intensity."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import json
import os
import socket
import stat
import sys
import tempfile
import time
from pathlib import Path

sys.dont_write_bytecode = True

from process_utils import process_is_alive

try:
    import tomllib
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit("Python 3.11+ is required because this utility uses tomllib.") from exc

VALID = ("auto", "minimal", "moderate", "heavy", "extreme")
MANAGED_MARKER = "# managed-by: adaptive-master-subagent-orchestration"
LOCK_STALE_SECONDS = 2 * 60 * 60


def lock_owner_is_live(path: Path) -> bool:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    return (
        data.get("host") == socket.gethostname()
        and isinstance(data.get("pid"), int)
        and process_is_alive(int(data["pid"]))
    )


@contextlib.contextmanager
def config_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.parent / ".ams-orchestration-config.lock"
    payload = {
        "pid": os.getpid(),
        "host": socket.gethostname(),
        "created": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    while True:
        try:
            descriptor = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
                json.dump(payload, handle, sort_keys=True)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            break
        except FileExistsError:
            try:
                metadata = lock_path.lstat()
                age = time.time() - metadata.st_mtime
            except FileNotFoundError:
                continue
            if not stat.S_ISREG(metadata.st_mode):
                raise SystemExit(f"Intensity lock path is not a regular file: {lock_path}")
            if age > LOCK_STALE_SECONDS and not lock_owner_is_live(lock_path):
                try:
                    lock_path.unlink()
                except FileNotFoundError:
                    pass
                continue
            raise SystemExit(f"Another intensity update appears to be active: {lock_path}")
    try:
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", nargs="?", choices=VALID)
    parser.add_argument("--scope", choices=("user", "project"), default="user")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.show and args.mode:
        parser.error("MODE and --show cannot be used together")
    if args.dry_run and not args.mode:
        parser.error("--dry-run requires MODE")
    return args


def path_for(args: argparse.Namespace) -> Path:
    if args.scope == "project":
        return args.project_root.expanduser().resolve(strict=False) / ".codex" / "ams-orchestration.toml"
    codex_home_value = os.environ.get("CODEX_HOME", "").strip()
    codex_home = Path(codex_home_value).expanduser() if codex_home_value else Path.home() / ".codex"
    return codex_home.resolve(strict=False) / "ams-orchestration.toml"


def read_config(path: Path) -> tuple[str | None, str | None]:
    if not path.exists() and not path.is_symlink():
        return None, None
    if not path.is_file() or path.is_symlink():
        return None, f"configuration path is not a regular file: {path}"
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        return None, f"invalid TOML: {exc}"
    if data.get("schema_version") != 1:
        return None, f"unsupported or missing schema_version: {data.get('schema_version')!r}"
    mode = data.get("intensity")
    if mode not in VALID:
        return None, f"invalid or missing intensity: {mode!r}"
    return str(mode), None


def _fsync_directory(path: Path) -> None:
    if os.name == "nt":
        return
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    old_mode: int | None = None
    if path.exists() or path.is_symlink():
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"Configuration path is not a regular file: {path}")
        old_mode = stat.S_IMODE(path.stat().st_mode)
    descriptor, tmp_name = tempfile.mkstemp(prefix=".ams-intensity.", dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        if old_mode is not None:
            os.chmod(tmp_name, old_mode)
        os.replace(tmp_name, path)
        _fsync_directory(path.parent)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    path = path_for(args)
    if args.show or not args.mode:
        mode, error = read_config(path)
        if error:
            print(f"{path}: invalid ({error})")
            return 2
        print(f"{path}: {mode or 'unset (effective default: auto)'}")
        return 0

    text = f'{MANAGED_MARKER}\nschema_version = 1\nintensity = "{args.mode}"\n'
    if args.dry_run:
        print(f"would-write {path}\n{text}", end="")
    else:
        with config_lock(path):
            atomic_write(path, text)
        print(f"set {args.scope} intensity to {args.mode}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
