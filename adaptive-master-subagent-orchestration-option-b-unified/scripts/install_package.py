#!/usr/bin/env python3
"""Install, update, switch, or uninstall Adaptive Master–Subagent Orchestration."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
import shutil
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterator

sys.dont_write_bytecode = True

from process_utils import process_is_alive, run_bounded

try:
    import tomllib
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit("Python 3.11+ is required because this installer uses tomllib.") from exc

PLUGIN_NAME = 'adaptive-master-subagent-orchestration-option-b-unified'
OPTION = 'B'
ALLOW_SKIP_PROFILES = True
EXPECTED_SKILLS = ['adaptive-master-subagent-orchestration']
VERSION = "3.1.0"
MANAGED_MARKER = "# managed-by: adaptive-master-subagent-orchestration"
VALID_INTENSITIES = ("auto", "minimal", "moderate", "heavy", "extreme")
VALID_SPARK_EFFORTS = ("low", "medium", "high")
ALL_PLUGIN_NAMES = (
    "adaptive-master-subagent-orchestration-option-a-two-skill",
    "adaptive-master-subagent-orchestration-option-b-unified",
    "adaptive-master-subagent-orchestration-option-c-installer-required",
    "adaptive-master-subagent-orchestration-option-a-modular",
    "adaptive-master-subagent-orchestration-option-c-lean",
    "adaptive-master-subagent-orchestration",
)
LEGACY_SKILL_NAMES = ("adaptive-master-subagent-orchestration", "ams-orchestration", "ams-installer")
LOCK_STALE_SECONDS = 2 * 60 * 60
DEFAULT_PROFILE_TIMEOUT_SECONDS = 120


@dataclass(frozen=True)
class FileSnapshot:
    existed: bool
    data: bytes = b""
    mode: int | None = None


@dataclass(frozen=True)
class ConfigPlan:
    action: str
    text: str | None = None


@dataclass(frozen=True)
class ProfileExpectation:
    path: Path
    expected_sha256: str | None
    expected_absent: bool
    before: FileSnapshot


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


def positive_environment_integer(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise SystemExit(f"{name} must be a positive integer; received: {raw}") from exc
    if value <= 0:
        raise SystemExit(f"{name} must be a positive integer; received: {raw}")
    return value


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


def parse_spark_efforts(value: str) -> tuple[str, ...]:
    values = tuple(dict.fromkeys(part.strip().lower() for part in value.split(",") if part.strip()))
    invalid = sorted(set(values) - set(VALID_SPARK_EFFORTS))
    if invalid:
        raise argparse.ArgumentTypeError(
            f"unsupported Spark effort(s): {', '.join(invalid)}; allowed: {', '.join(VALID_SPARK_EFFORTS)}"
        )
    return values


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--skip-profiles", action="store_true")
    parser.add_argument("--exclude-spark", action="store_true")
    parser.add_argument("--spark-efforts", type=parse_spark_efforts, default=VALID_SPARK_EFFORTS)
    parser.add_argument("--upgrade-managed", action="store_true")
    parser.add_argument("--intensity", choices=VALID_INTENSITIES, default="auto")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--yes", action="store_true", help="Confirm non-interactive uninstall.")
    return parser.parse_args(argv)


def normalize_paths(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    home = args.home.expanduser().resolve(strict=False)
    codex_home_value = os.environ.get("CODEX_HOME", "").strip()
    codex_home = (
        Path(codex_home_value).expanduser().resolve(strict=False)
        if codex_home_value
        else home / ".codex"
    )
    market_root = home / ".agents" / "plugins"
    return home, codex_home, market_root


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_manifest(root: Path) -> None:
    manifest_path = root / "MANIFEST.sha256"
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise SystemExit(f"Package manifest was not found or is not a regular file: {manifest_path}")
    listed: dict[str, str] = {}
    try:
        lines = manifest_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise SystemExit(f"Package manifest could not be read: {manifest_path}: {exc}") from exc
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            expected, relative = line.split("  ", 1)
        except ValueError as exc:
            raise SystemExit(f"Malformed package manifest line {number}: {line}") from exc
        if len(expected) != 64 or any(char not in "0123456789abcdefABCDEF" for char in expected):
            raise SystemExit(f"Malformed package manifest digest on line {number}")
        posix = PurePosixPath(relative)
        if posix.is_absolute() or any(part in ("", ".", "..") for part in posix.parts):
            raise SystemExit(f"Unsafe package manifest path on line {number}: {relative}")
        normalized = posix.as_posix()
        if normalized in listed:
            raise SystemExit(f"Duplicate package manifest entry: {normalized}")
        listed[normalized] = expected.lower()

    actual: dict[str, str] = {}
    for path in root.rglob("*"):
        if path.is_symlink():
            raise SystemExit(f"Package contains an unsupported symbolic link: {path}")
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            raise SystemExit(f"Package contains a generated Python artifact: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative == "MANIFEST.sha256":
            continue
        actual[relative] = sha256(path)
    if listed != actual:
        unlisted = sorted(set(actual) - set(listed))
        missing = sorted(set(listed) - set(actual))
        changed = sorted(key for key in set(actual) & set(listed) if actual[key] != listed[key])
        raise SystemExit(
            "Package manifest verification failed; "
            f"unlisted={unlisted}, missing={missing}, changed={changed}"
        )


def package_file_map(root: Path) -> dict[str, str] | None:
    if not root.is_dir() or root.is_symlink():
        return None
    result: dict[str, str] = {}
    try:
        for path in root.rglob("*"):
            if path.is_symlink():
                return None
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                continue
            result[relative] = sha256(path)
    except OSError:
        return None
    return result


def packages_identical(left: Path, right: Path) -> bool:
    left_map = package_file_map(left)
    return left_map is not None and left_map == package_file_map(right)


def validate_plugin_metadata(root: Path) -> None:
    path = root / ".codex-plugin" / "plugin.json"
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"Plugin metadata was not found or is not a regular file: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Plugin metadata is invalid: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"Plugin metadata root must be an object: {path}")
    expected = {"name": PLUGIN_NAME, "version": VERSION, "skills": "./skills/"}
    for key, value in expected.items():
        if data.get(key) != value:
            raise SystemExit(f"Plugin metadata mismatch for {key}: expected {value!r}, found {data.get(key)!r}")
    skills_root = root / "skills"
    actual_skills = sorted(path.name for path in skills_root.iterdir() if path.is_dir() and not path.is_symlink()) if skills_root.is_dir() else []
    if actual_skills != sorted(EXPECTED_SKILLS):
        raise SystemExit(f"Skill set mismatch; expected={sorted(EXPECTED_SKILLS)}, found={actual_skills}")


def snapshot_file(path: Path) -> FileSnapshot:
    if not path.exists() and not path.is_symlink():
        return FileSnapshot(False)
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"Expected a regular file, found another file type: {path}")
    info = path.stat()
    return FileSnapshot(True, path.read_bytes(), stat.S_IMODE(info.st_mode))


def atomic_write_bytes(path: Path, data: bytes, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if mode is not None:
            os.chmod(tmp_name, mode)
        os.replace(tmp_name, path)
        _fsync_directory(path.parent)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def atomic_write_text(path: Path, text: str, mode: int | None = None) -> None:
    atomic_write_bytes(path, text.encode("utf-8"), mode)


def current_regular_bytes(path: Path) -> bytes | None:
    if not path.exists() and not path.is_symlink():
        return None
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"path changed to a non-regular file: {path}")
    return path.read_bytes()


def restore_file_if_unchanged(path: Path, state: FileSnapshot, expected_after: bytes | None) -> None:
    current = current_regular_bytes(path)
    if current != expected_after:
        raise RuntimeError(f"rollback refused to overwrite a concurrent change: {path}")
    if state.existed:
        atomic_write_bytes(path, state.data, state.mode)
    elif path.exists() or path.is_symlink():
        path.unlink()
        _fsync_directory(path.parent)


def load_marketplace(path: Path) -> dict[str, object]:
    if not path.exists() and not path.is_symlink():
        return {
            "name": "adaptive-master-subagent-orchestration",
            "interface": {"displayName": "Adaptive Master–Subagent Orchestration"},
            "plugins": [],
        }
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"Marketplace path is not a regular file: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot parse existing marketplace {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"Marketplace root must be a JSON object: {path}")
    plugins = data.get("plugins")
    if plugins is None:
        data["plugins"] = []
    elif not isinstance(plugins, list):
        raise SystemExit(f"Marketplace 'plugins' value must be a list: {path}")
    return data


def marketplace_for_install(data: dict[str, object]) -> dict[str, object]:
    updated = json.loads(json.dumps(data))
    plugins = updated.setdefault("plugins", [])
    if not isinstance(plugins, list):
        raise SystemExit("Marketplace plugins must be a list")
    filtered = [
        item
        for item in plugins
        if not (isinstance(item, dict) and item.get("name") in ALL_PLUGIN_NAMES)
    ]
    filtered.append(
        {
            "name": PLUGIN_NAME,
            "source": {"source": "local", "path": f"./plugins/{PLUGIN_NAME}"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        }
    )
    updated["plugins"] = filtered
    return updated


def marketplace_for_uninstall(data: dict[str, object]) -> dict[str, object]:
    updated = json.loads(json.dumps(data))
    plugins = updated.setdefault("plugins", [])
    if not isinstance(plugins, list):
        raise SystemExit("Marketplace plugins must be a list")
    updated["plugins"] = [
        item
        for item in plugins
        if not (isinstance(item, dict) and item.get("name") in ALL_PLUGIN_NAMES)
    ]
    return updated


def marketplace_text(data: dict[str, object]) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def validate_config_text(text: str, path: Path) -> None:
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise SystemExit(f"Invalid orchestration configuration {path}: {exc}") from exc
    if data.get("schema_version") != 1:
        raise SystemExit(f"Unsupported or missing schema_version in {path}; expected 1")
    intensity = data.get("intensity")
    if intensity not in VALID_INTENSITIES:
        raise SystemExit(f"Invalid or missing intensity in {path}: {intensity!r}")


def inspect_config(path: Path, initial_intensity: str) -> ConfigPlan:
    if not path.exists() and not path.is_symlink():
        return ConfigPlan("create", f'{MANAGED_MARKER}\nschema_version = 1\nintensity = "{initial_intensity}"\n')
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"Configuration path is not a regular file: {path}")
    raw = path.read_text(encoding="utf-8", errors="strict")
    if "\\n" in raw and "\n" not in raw:
        normalized = raw.replace("\\n", "\n")
        if MANAGED_MARKER not in normalized:
            normalized = f"{MANAGED_MARKER}\n{normalized}"
        validate_config_text(normalized, path)
        return ConfigPlan("repair-legacy-newlines", normalized)
    validate_config_text(raw, path)
    return ConfigPlan("preserve")


def copy_package(src: Path, dst: Path) -> None:
    shutil.copytree(
        src,
        dst,
        symlinks=False,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".pytest_cache"),
    )


def next_backup_path(backup_root: Path, name: str) -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    candidate = backup_root / f"{name}.backup-{stamp}"
    index = 2
    while candidate.exists() or candidate.is_symlink():
        candidate = backup_root / f"{name}.backup-{stamp}-{index}"
        index += 1
    return candidate


@contextlib.contextmanager
def install_lock(market_root: Path) -> Iterator[None]:
    market_root.mkdir(parents=True, exist_ok=True)
    lock_path = market_root / ".ams-install.lock"
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
                raise SystemExit(f"Install lock path is not a regular file: {lock_path}")
            if age > LOCK_STALE_SECONDS and not lock_owner_is_live(lock_path):
                try:
                    lock_path.unlink()
                except FileNotFoundError:
                    pass
                continue
            raise SystemExit(f"Another AMS installation or removal appears to be active: {lock_path}")
    try:
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def bootstrap_command(
    root: Path,
    codex_home: Path,
    args: argparse.Namespace,
    *,
    dry_run: bool,
    transaction_id: str,
    json_output: bool,
) -> list[str]:
    command = [
        sys.executable,
        "-B",
        "-E",
        "-s",
        "-S",
        str(root / "scripts" / "bootstrap_profiles.py"),
        "--destination",
        str(codex_home / "agents"),
        "--spark-efforts",
        ",".join(args.spark_efforts),
        "--transaction-id",
        transaction_id,
    ]
    if args.exclude_spark:
        command.append("--exclude-spark")
    if args.upgrade_managed:
        command.append("--upgrade-managed")
    if dry_run:
        command.append("--dry-run")
    if json_output:
        command.append("--json")
    return command


def run_bootstrap(
    root: Path,
    codex_home: Path,
    args: argparse.Namespace,
    *,
    dry_run: bool,
    transaction_id: str,
    json_output: bool = False,
) -> dict[str, object] | None:
    timeout = positive_environment_integer("AMS_PROFILE_TIMEOUT_SECONDS", DEFAULT_PROFILE_TIMEOUT_SECONDS)
    command = bootstrap_command(
        root,
        codex_home,
        args,
        dry_run=dry_run,
        transaction_id=transaction_id,
        json_output=json_output,
    )
    try:
        result = run_bounded(
            command,
            check=False,
            timeout=timeout,
            text=True,
            capture_output=json_output,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired as exc:
        lock_path = codex_home / ".agents.ams-profile-install.lock"
        try:
            if lock_path.exists() and not lock_owner_is_live(lock_path):
                lock_path.unlink()
        except OSError:
            pass
        raise SystemExit(
            f"Profile installation exceeded {timeout} seconds and was stopped: {' '.join(command)}"
        ) from exc
    if result.returncode:
        output = ((result.stderr or "") + (result.stdout or "")).strip()
        raise SystemExit(f"Profile installation failed with exit code {result.returncode}: {output}")
    if not json_output:
        return None
    try:
        parsed = json.loads(result.stdout or "")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Profile installer returned invalid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise SystemExit("Profile installer JSON root must be an object")
    return parsed


def profile_expectations(summary: dict[str, object]) -> list[ProfileExpectation]:
    profiles = summary.get("profiles")
    if not isinstance(profiles, list):
        raise SystemExit("Profile dry-run summary is missing profiles")
    expectations: list[ProfileExpectation] = []
    for item in profiles:
        if not isinstance(item, dict):
            raise SystemExit("Profile dry-run summary contains a non-object entry")
        action = item.get("action")
        path_value = item.get("path")
        if not isinstance(action, str) or not isinstance(path_value, str):
            raise SystemExit("Profile dry-run summary entry is incomplete")
        expected_hash = item.get("expected_sha256")
        expected_absent = bool(item.get("expected_absent", False))
        mutating = action.startswith("would-")
        if not mutating:
            continue
        path = Path(path_value)
        if expected_hash is not None and not isinstance(expected_hash, str):
            raise SystemExit("Profile dry-run expected_sha256 is invalid")
        expectations.append(
            ProfileExpectation(
                path=path,
                expected_sha256=expected_hash,
                expected_absent=expected_absent,
                before=snapshot_file(path),
            )
        )
    return expectations


def restore_profile_expectations(expectations: list[ProfileExpectation]) -> list[str]:
    errors: list[str] = []
    for expectation in reversed(expectations):
        path = expectation.path
        try:
            if expectation.expected_absent:
                current_matches = not path.exists() and not path.is_symlink()
            else:
                current_matches = (
                    path.is_file()
                    and not path.is_symlink()
                    and expectation.expected_sha256 is not None
                    and sha256(path) == expectation.expected_sha256
                )
            if not current_matches:
                # A nonmatching path may be untouched (bootstrap failed before it) or concurrently changed.
                current = snapshot_file(path)
                if current == expectation.before:
                    continue
                raise RuntimeError(f"rollback refused to overwrite a concurrent profile change: {path}")
            if expectation.before.existed:
                atomic_write_bytes(path, expectation.before.data, expectation.before.mode)
            elif path.exists() or path.is_symlink():
                path.unlink()
                _fsync_directory(path.parent)
        except Exception as exc:
            errors.append(str(exc))
    return errors


def cleanup_profile_transaction_backups(codex_home: Path, transaction_id: str) -> list[str]:
    errors: list[str] = []
    agents = codex_home / "agents"
    if not agents.is_dir():
        return errors
    for path in agents.glob(f"*.bak-{transaction_id}*"):
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        except OSError as exc:
            errors.append(f"remove profile backup {path}: {exc}")
    return errors


def clean_stale_transactions(market_root: Path) -> None:
    for path in market_root.glob(".ams-transaction-*"):
        if not path.is_dir() or path.is_symlink():
            continue
        try:
            shutil.rmtree(path)
        except OSError as exc:
            print(f"warning: could not remove stale transaction directory {path}: {exc}", file=sys.stderr)


def rollback_plugin_moves(
    *,
    src: Path,
    new_plugin: Path,
    old_locations: list[tuple[Path, Path]],
    remove_new_plugin: bool,
) -> list[str]:
    errors: list[str] = []
    if remove_new_plugin and (new_plugin.exists() or new_plugin.is_symlink()):
        try:
            if not packages_identical(src, new_plugin):
                raise RuntimeError(f"rollback refused to remove a concurrently modified plugin: {new_plugin}")
            shutil.rmtree(new_plugin)
        except Exception as exc:
            errors.append(str(exc))
    for original, staged in reversed(old_locations):
        try:
            if not (staged.exists() or staged.is_symlink()):
                continue
            if original.exists() or original.is_symlink():
                raise RuntimeError(f"rollback refused to overwrite a concurrently created plugin: {original}")
            original.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staged, original)
        except Exception as exc:
            errors.append(f"restore {original}: {exc}")
    return errors


def install(args: argparse.Namespace) -> int:
    if args.skip_profiles and not ALLOW_SKIP_PROFILES:
        raise SystemExit("Option C requires profile installation; --skip-profiles is not allowed.")

    src = Path(__file__).resolve().parents[1]
    validate_manifest(src)
    validate_plugin_metadata(src)
    home, codex_home, market_root = normalize_paths(args)
    plugin_root = market_root / "plugins"
    marketplace_path = market_root / "marketplace.json"
    config_path = codex_home / "ams-orchestration.toml"

    marketplace = load_marketplace(marketplace_path)
    config_plan = inspect_config(config_path, args.intensity)
    profile_transaction = uuid.uuid4().hex
    profile_summary: dict[str, object] | None = None
    if not args.skip_profiles:
        profile_summary = run_bootstrap(
            src,
            codex_home,
            args,
            dry_run=True,
            transaction_id=profile_transaction,
            json_output=True,
        )

    new_plugin = plugin_root / PLUGIN_NAME
    selected_identical = packages_identical(src, new_plugin)
    active = [
        plugin_root / name
        for name in ALL_PLUGIN_NAMES
        if (plugin_root / name).exists() or (plugin_root / name).is_symlink()
    ]
    if args.dry_run:
        if selected_identical:
            print(f"would-preserve identical plugin: {new_plugin}")
        else:
            print(f"would-install plugin {src} -> {new_plugin}")
        for path in active:
            if path != new_plugin or not selected_identical:
                print(f"would-deactivate existing AMS plugin: {path}")
        print(f"would-register only {PLUGIN_NAME} in {marketplace_path}")
        if config_plan.action == "create":
            print(f"would-create intensity config {config_path} with {args.intensity}")
        elif config_plan.action == "repair-legacy-newlines":
            print(f"would-repair legacy newline encoding in {config_path}")
        else:
            print(f"would-preserve intensity config: {config_path}")
        return 0

    with install_lock(market_root):
        clean_stale_transactions(market_root)
        validate_manifest(src)
        validate_plugin_metadata(src)
        marketplace = load_marketplace(marketplace_path)
        config_plan = inspect_config(config_path, args.intensity)
        if not args.skip_profiles:
            profile_summary = run_bootstrap(
                src,
                codex_home,
                args,
                dry_run=True,
                transaction_id=profile_transaction,
                json_output=True,
            )
        expectations = profile_expectations(profile_summary) if profile_summary is not None else []

        plugin_root.mkdir(parents=True, exist_ok=True)
        backup_root = market_root / "backups"
        transaction_root = market_root / f".ams-transaction-{uuid.uuid4().hex}"
        staged_plugin = transaction_root / "new-plugin"
        old_root = transaction_root / "old-plugins"
        transaction_root.mkdir(parents=True)
        new_plugin = plugin_root / PLUGIN_NAME
        selected_identical = packages_identical(src, new_plugin)
        if not selected_identical:
            copy_package(src, staged_plugin)

        marketplace_state = snapshot_file(marketplace_path)
        config_state = snapshot_file(config_path)
        desired_marketplace = marketplace_text(marketplace_for_install(marketplace)).encode("utf-8")
        expected_marketplace_after = marketplace_state.data
        expected_config_after = config_state.data
        old_locations: list[tuple[Path, Path]] = []
        committed_backups: list[Path] = []
        new_plugin_created = False
        try:
            for name in ALL_PLUGIN_NAMES:
                original = plugin_root / name
                if selected_identical and original == new_plugin:
                    continue
                if not original.exists() and not original.is_symlink():
                    continue
                if not original.is_dir() or original.is_symlink():
                    raise SystemExit(f"Active plugin path is not a regular directory: {original}")
                staged_old = old_root / name
                staged_old.parent.mkdir(parents=True, exist_ok=True)
                os.replace(original, staged_old)
                old_locations.append((original, staged_old))

            if not selected_identical:
                os.replace(staged_plugin, new_plugin)
                new_plugin_created = True
            if not marketplace_state.existed or marketplace_state.data != desired_marketplace:
                atomic_write_bytes(marketplace_path, desired_marketplace, marketplace_state.mode)
                expected_marketplace_after = desired_marketplace
            if config_plan.text is not None:
                expected_config_after = config_plan.text.encode("utf-8")
                atomic_write_bytes(config_path, expected_config_after, config_state.mode)

            backup_root.mkdir(parents=True, exist_ok=True)
            for original, staged_old in old_locations:
                backup_path = next_backup_path(backup_root, original.name)
                os.replace(staged_old, backup_path)
                committed_backups.append(backup_path)

            if not args.skip_profiles:
                run_bootstrap(
                    new_plugin,
                    codex_home,
                    args,
                    dry_run=False,
                    transaction_id=profile_transaction,
                    json_output=False,
                )
        except BaseException as exc:
            # Move committed plugin backups back into the transaction staging area first.
            rollback_errors: list[str] = []
            for index, backup_path in enumerate(committed_backups):
                try:
                    staged_old = old_locations[index][1]
                    if backup_path.exists() or backup_path.is_symlink():
                        staged_old.parent.mkdir(parents=True, exist_ok=True)
                        os.replace(backup_path, staged_old)
                except Exception as move_exc:
                    rollback_errors.append(f"restage plugin backup {backup_path}: {move_exc}")
            rollback_errors.extend(rollback_plugin_moves(
                src=src,
                new_plugin=new_plugin,
                old_locations=old_locations,
                remove_new_plugin=new_plugin_created,
            ))
            if expected_marketplace_after != marketplace_state.data:
                try:
                    restore_file_if_unchanged(marketplace_path, marketplace_state, expected_marketplace_after)
                except Exception as restore_exc:
                    rollback_errors.append(f"restore {marketplace_path}: {restore_exc}")
            if expected_config_after != config_state.data:
                try:
                    restore_file_if_unchanged(config_path, config_state, expected_config_after)
                except Exception as restore_exc:
                    rollback_errors.append(f"restore {config_path}: {restore_exc}")
            rollback_errors.extend(restore_profile_expectations(expectations))
            rollback_errors.extend(cleanup_profile_transaction_backups(codex_home, profile_transaction))
            if rollback_errors:
                raise SystemExit(
                    f"Installation failed: {exc}; rollback also reported: {'; '.join(rollback_errors)}"
                ) from exc
            raise
        finally:
            try:
                shutil.rmtree(transaction_root)
            except FileNotFoundError:
                pass
            except OSError as cleanup_error:
                print(f"warning: could not remove transaction directory {transaction_root}: {cleanup_error}", file=sys.stderr)

    print(f"plugin registered: {PLUGIN_NAME}")
    for backup_path in committed_backups:
        print(f"previous plugin backup: {backup_path}")
    if config_plan.action == "create":
        print(f"created intensity config: {config_path}")
    elif config_plan.action == "repair-legacy-newlines":
        print(f"repaired legacy intensity config: {config_path}")
    else:
        print(f"preserved intensity config: {config_path}")
    print("Restart Codex if the plugin or profiles are not detected immediately.")
    return 0


def path_has_managed_marker(path: Path) -> bool:
    if not path.is_file() or path.is_symlink():
        return False
    try:
        return MANAGED_MARKER in path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def uninstall_targets(home: Path, codex_home: Path, market_root: Path) -> list[Path]:
    targets: list[Path] = []
    plugin_root = market_root / "plugins"
    backup_root = market_root / "backups"
    if plugin_root.is_dir():
        for path in plugin_root.iterdir():
            if any(
                path.name == name
                or path.name.startswith(f"{name}.backup-")
                or path.name.startswith(f"{name}.installing-")
                or path.name.startswith(f".{name}.ams-uninstalling-")
                for name in ALL_PLUGIN_NAMES
            ):
                targets.append(path)
    if backup_root.is_dir():
        for path in backup_root.iterdir():
            if any(
                path.name.startswith(f"{name}.backup-")
                or (path.name.startswith(f".{name}.backup-") and ".ams-uninstalling-" in path.name)
                for name in ALL_PLUGIN_NAMES
            ):
                targets.append(path)
    if market_root.is_dir():
        targets.extend(path for path in market_root.glob(".ams-transaction-*") if path.is_dir() and not path.is_symlink())

    agents = codex_home / "agents"
    if agents.is_dir():
        targets.extend(
            path
            for path in agents.iterdir()
            if path_has_managed_marker(path)
            or (path.name.startswith(".ams_") and ".ams-uninstalling-" in path.name)
        )
    config = codex_home / "ams-orchestration.toml"
    if path_has_managed_marker(config):
        targets.append(config)
    if codex_home.is_dir():
        targets.extend(
            path
            for path in codex_home.glob(".ams-orchestration.toml.ams-uninstalling-*")
            if path_has_managed_marker(path)
        )
    legacy_root = home / ".agents" / "skills"
    for name in LEGACY_SKILL_NAMES:
        path = legacy_root / name
        if path.exists() or path.is_symlink():
            targets.append(path)
        if legacy_root.is_dir():
            targets.extend(legacy_root.glob(f".{name}.ams-uninstalling-*"))
    return list(dict.fromkeys(targets))


def make_writable(path: Path) -> None:
    try:
        if path.is_dir() and not path.is_symlink():
            for child in path.rglob("*"):
                try:
                    os.chmod(child, stat.S_IRUSR | stat.S_IWUSR | (stat.S_IXUSR if child.is_dir() else 0))
                except OSError:
                    pass
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | (stat.S_IXUSR if path.is_dir() else 0))
    except OSError:
        pass


def remove_staged(path: Path) -> None:
    last_error: OSError | None = None
    for attempt in range(5):
        try:
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            else:
                path.unlink()
            return
        except FileNotFoundError:
            return
        except OSError as exc:
            last_error = exc
            make_writable(path)
            time.sleep(0.1 * (attempt + 1))
    if last_error is not None:
        raise last_error


def uninstall(args: argparse.Namespace) -> int:
    if not args.yes and not args.dry_run:
        raise SystemExit("Uninstall requires --yes. Use --dry-run to preview removal.")
    home, codex_home, market_root = normalize_paths(args)
    marketplace_path = market_root / "marketplace.json"
    marketplace = load_marketplace(marketplace_path)
    targets = uninstall_targets(home, codex_home, market_root)
    if args.dry_run:
        for target in targets:
            print(f"would-remove: {target}")
        if marketplace_path.exists() or marketplace_path.is_symlink():
            print(f"would-remove AMS marketplace registrations from: {marketplace_path}")
        return 0
    if not targets and not marketplace_path.exists() and not marketplace_path.is_symlink():
        print("No package-managed AMS installation was found.")
        return 0

    with install_lock(market_root):
        clean_stale_transactions(market_root)
        marketplace = load_marketplace(marketplace_path)
        targets = uninstall_targets(home, codex_home, market_root)
        marketplace_state = snapshot_file(marketplace_path)
        desired_marketplace = marketplace_text(marketplace_for_uninstall(marketplace)).encode("utf-8")
        token = uuid.uuid4().hex
        staged: list[tuple[Path, Path]] = []
        marketplace_written = False
        try:
            for target in targets:
                staged_path = target.with_name(f".{target.name}.ams-uninstalling-{token}")
                if staged_path.exists() or staged_path.is_symlink():
                    raise SystemExit(f"Uninstall staging path already exists: {staged_path}")
                os.replace(target, staged_path)
                staged.append((target, staged_path))
            if marketplace_state.existed and marketplace_state.data != desired_marketplace:
                atomic_write_bytes(marketplace_path, desired_marketplace, marketplace_state.mode)
                marketplace_written = True
        except BaseException as exc:
            errors: list[str] = []
            for original, staged_path in reversed(staged):
                try:
                    if staged_path.exists() or staged_path.is_symlink():
                        if original.exists() or original.is_symlink():
                            raise RuntimeError(f"rollback refused to overwrite concurrent path: {original}")
                        os.replace(staged_path, original)
                except Exception as restore_exc:
                    errors.append(f"restore {original}: {restore_exc}")
            if marketplace_written:
                try:
                    restore_file_if_unchanged(marketplace_path, marketplace_state, desired_marketplace)
                except Exception as restore_exc:
                    errors.append(f"restore {marketplace_path}: {restore_exc}")
            if errors:
                raise SystemExit(f"Uninstall failed: {exc}; rollback also reported: {'; '.join(errors)}") from exc
            raise

        cleanup_errors: list[str] = []
        for _, staged_path in staged:
            try:
                remove_staged(staged_path)
            except Exception as exc:
                cleanup_errors.append(f"{staged_path}: {exc}")
        if cleanup_errors:
            print(
                "warning: uninstall completed, but some staged files could not be deleted and will be retried on a later removal: "
                + "; ".join(cleanup_errors),
                file=sys.stderr,
            )

    print("Uninstall complete. Restart Codex to refresh discovered plugins and agents.")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.uninstall:
        return uninstall(args)
    return install(args)


if __name__ == "__main__":
    raise SystemExit(main())
