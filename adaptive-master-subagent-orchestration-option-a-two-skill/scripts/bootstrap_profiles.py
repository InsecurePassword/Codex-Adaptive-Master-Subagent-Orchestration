#!/usr/bin/env python3
"""Install Adaptive Master–Subagent custom-agent profiles safely and idempotently."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import socket
import stat
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

sys.dont_write_bytecode = True

from process_utils import process_is_alive

try:
    import tomllib
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit("Python 3.11+ is required because this installer uses tomllib.") from exc

MANAGED_MARKER = "# managed-by: adaptive-master-subagent-orchestration"
LEGACY_SPARK = "ams_spark_runner"
VALID_SPARK_EFFORTS = ("low", "medium", "high")
VALID_STANDARD_EFFORTS = ("low", "medium", "high", "xhigh", "max")
MODEL_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
NAME_RE = re.compile(r'(?m)^name\s*=\s*"([^"]+)"\s*$')
MODEL_RE = re.compile(r'(?m)^model\s*=\s*"([^"]+)"\s*$')
STANDARD_NAME_RE = re.compile(
    r"^ams_(?:sol|terra|luna)_(low|medium|high|xhigh|max)(?:_adaptive(?:_\d+)?)?$"
)
SPARK_NAME_RE = re.compile(r"^ams_spark_(low|medium|high)(?:_adaptive(?:_\d+)?)?$")
EXPECTED_PROFILE_NAMES = {
    *(f"ams_{family}_{effort}" for family in ("sol", "terra", "luna") for effort in VALID_STANDARD_EFFORTS),
    *(f"ams_spark_{effort}" for effort in VALID_SPARK_EFFORTS),
}
LOCK_STALE_SECONDS = 2 * 60 * 60
MAX_PROFILE_ALIASES = 1000
TRANSACTION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


@dataclass(frozen=True)
class FileSnapshot:
    existed: bool
    data: bytes = b""
    mode: int | None = None


@dataclass
class ProfilePlan:
    requested_name: str
    installed_name: str
    path: Path
    action: str
    text: str | None = None
    delete: bool = False
    needs_backup: bool = False
    backup_path: Path | None = None


@dataclass(frozen=True)
class AppliedChange:
    path: Path
    expected_data: bytes | None  # None means the installer left the path absent.


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
    codex_home_value = os.environ.get("CODEX_HOME", "").strip()
    default_home = Path(codex_home_value).expanduser() if codex_home_value else Path.home() / ".codex"
    parser.add_argument("--destination", type=Path, default=default_home / "agents")
    parser.add_argument("--exclude-spark", action="store_true", help="Do not install Spark profiles.")
    parser.add_argument(
        "--spark-efforts",
        type=parse_spark_efforts,
        default=VALID_SPARK_EFFORTS,
        help="Comma-separated Spark efforts to install: low,medium,high.",
    )
    parser.add_argument("--sol-model", default="gpt-5.6")
    parser.add_argument("--terra-model", default="gpt-5.6-terra")
    parser.add_argument("--luna-model", default="gpt-5.6-luna")
    parser.add_argument("--spark-model", default="gpt-5.3-codex-spark")
    parser.add_argument(
        "--upgrade-managed",
        action="store_true",
        help="Back up and replace differing managed profiles; retire the legacy managed Spark runner.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--transaction-id", default="", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.transaction_id and not TRANSACTION_ID_RE.fullmatch(args.transaction_id):
        parser.error("--transaction-id contains unsupported characters or is too long")
    return args


def validate_model_id(value: str, label: str) -> None:
    if not MODEL_ID_RE.fullmatch(value):
        raise SystemExit(f"Invalid {label} model identifier: {value!r}")


def parse_profile(text: str) -> dict[str, object] | None:
    try:
        data = tomllib.loads(text)
    except (tomllib.TOMLDecodeError, ValueError):
        return None
    required = ("name", "description", "model", "model_reasoning_effort", "developer_instructions")
    if not all(isinstance(data.get(key), str) and str(data[key]).strip() for key in required):
        return None
    if "sandbox_mode" in data and not isinstance(data["sandbox_mode"], str):
        return None
    return data


def expected_effort_for_name(name: str) -> str | None:
    standard = STANDARD_NAME_RE.fullmatch(name)
    if standard:
        return standard.group(1)
    spark = SPARK_NAME_RE.fullmatch(name)
    if spark:
        return spark.group(1)
    return None


def valid_profile(text: str, expected_name: str | None = None) -> bool:
    data = parse_profile(text)
    if data is None:
        return False
    if expected_name is not None and data["name"] != expected_name:
        return False
    name = str(data["name"])
    expected_effort = expected_effort_for_name(name)
    if expected_effort is None or data["model_reasoning_effort"] != expected_effort:
        return False
    if SPARK_NAME_RE.fullmatch(name) and data.get("sandbox_mode") != "workspace-write":
        return False
    return bool(MODEL_ID_RE.fullmatch(str(data["model"])))


def replace_exact(pattern: re.Pattern[str], text: str, value: str, label: str) -> str:
    updated, count = pattern.subn(lambda _: f'{label} = "{value}"', text, count=1)
    if count != 1:
        raise SystemExit(f"Bundled profile is missing {label}")
    return updated


def replace_model(text: str, model: str) -> str:
    return replace_exact(MODEL_RE, text, model, "model")


def replace_name(text: str, name: str) -> str:
    return replace_exact(NAME_RE, text, name, "name")


def snapshot(path: Path) -> FileSnapshot:
    if not path.exists() and not path.is_symlink():
        return FileSnapshot(False)
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"Expected a regular profile file, found another file type: {path}")
    info = path.stat()
    return FileSnapshot(True, path.read_bytes(), stat.S_IMODE(info.st_mode))


def atomic_write(path: Path, text: str, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        if mode is not None:
            os.chmod(tmp_name, mode)
        os.replace(tmp_name, path)
        _fsync_directory(path.parent)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def _current_regular_bytes(path: Path) -> bytes | None:
    if not path.exists() and not path.is_symlink():
        return None
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"rollback path changed to a non-regular file: {path}")
    return path.read_bytes()


def restore_if_unchanged(path: Path, state: FileSnapshot, applied: AppliedChange) -> None:
    """Rollback only when the path still has the exact state written by this installer."""
    current = _current_regular_bytes(path)
    if applied.expected_data is None:
        if current is not None:
            raise RuntimeError(f"rollback refused to overwrite a concurrently created file: {path}")
    elif current != applied.expected_data:
        raise RuntimeError(f"rollback refused to overwrite a concurrently modified file: {path}")

    if state.existed:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.restore.", dir=str(path.parent))
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(state.data)
                handle.flush()
                os.fsync(handle.fileno())
            if state.mode is not None:
                os.chmod(tmp_name, state.mode)
            os.replace(tmp_name, path)
            _fsync_directory(path.parent)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
    elif path.exists() or path.is_symlink():
        # The equality check above proves this is still the regular file we created.
        path.unlink()
        _fsync_directory(path.parent)


def next_backup_path(path: Path, transaction_id: str = "") -> Path:
    stamp = transaction_id or dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    candidate = path.with_name(f"{path.name}.bak-{stamp}")
    index = 2
    while candidate.exists() or candidate.is_symlink():
        candidate = path.with_name(f"{path.name}.bak-{stamp}-{index}")
        index += 1
    return candidate


def read_regular_text(path: Path) -> str | None:
    if not path.exists() and not path.is_symlink():
        return None
    if not path.is_file() or path.is_symlink():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def plan_existing_managed(
    *, requested: str, installed_name: str, path: Path, expected_text: str, current: str, upgrade_managed: bool
) -> ProfilePlan:
    if current == expected_text:
        return ProfilePlan(requested, installed_name, path, "preserved-identical")
    if not valid_profile(current, installed_name):
        return ProfilePlan(
            requested,
            installed_name,
            path,
            "repaired-managed-malformed",
            text=expected_text,
            needs_backup=True,
        )
    if upgrade_managed:
        return ProfilePlan(
            requested,
            installed_name,
            path,
            "upgraded-managed",
            text=expected_text,
            needs_backup=True,
        )
    return ProfilePlan(requested, installed_name, path, "preserved-managed-different")


def plan_profile(*, src: Path, destination: Path, model: str, upgrade_managed: bool) -> ProfilePlan:
    requested = src.stem
    source_text = replace_model(src.read_text(encoding="utf-8"), model)
    if not valid_profile(source_text, requested):
        raise SystemExit(f"Bundled profile is invalid: {src}")

    canonical = destination / src.name
    current = read_regular_text(canonical)
    if current is None and not canonical.exists() and not canonical.is_symlink():
        return ProfilePlan(requested, requested, canonical, "created", text=source_text)
    if current is not None:
        if current == source_text:
            return ProfilePlan(requested, requested, canonical, "preserved-identical")
        if MANAGED_MARKER in current:
            return plan_existing_managed(
                requested=requested,
                installed_name=requested,
                path=canonical,
                expected_text=source_text,
                current=current,
                upgrade_managed=upgrade_managed,
            )

    index = 1
    while index <= MAX_PROFILE_ALIASES:
        suffix = "_adaptive" if index == 1 else f"_adaptive_{index}"
        installed_name = requested + suffix
        candidate = destination / f"{installed_name}.toml"
        candidate_text = replace_name(source_text, installed_name)
        candidate_current = read_regular_text(candidate)
        if candidate_current is None and not candidate.exists() and not candidate.is_symlink():
            return ProfilePlan(requested, installed_name, candidate, "created-nonconflicting", text=candidate_text)
        if candidate_current is not None:
            if candidate_current == candidate_text:
                return ProfilePlan(requested, installed_name, candidate, "preserved-nonconflicting")
            if MANAGED_MARKER in candidate_current:
                planned = plan_existing_managed(
                    requested=requested,
                    installed_name=installed_name,
                    path=candidate,
                    expected_text=candidate_text,
                    current=candidate_current,
                    upgrade_managed=upgrade_managed,
                )
                if planned.action == "preserved-identical":
                    planned.action = "preserved-nonconflicting"
                return planned
        index += 1
    raise SystemExit(
        f"Unable to allocate a nonconflicting profile name for {requested}; "
        f"checked {MAX_PROFILE_ALIASES} managed aliases in {destination}"
    )


def plan_legacy(destination: Path, upgrade_managed: bool) -> ProfilePlan | None:
    legacy = destination / f"{LEGACY_SPARK}.toml"
    current = read_regular_text(legacy)
    if current is None:
        if legacy.exists() or legacy.is_symlink():
            return ProfilePlan(LEGACY_SPARK, LEGACY_SPARK, legacy, "preserved-legacy-nonfile")
        return None
    if MANAGED_MARKER not in current:
        return ProfilePlan(LEGACY_SPARK, LEGACY_SPARK, legacy, "preserved-legacy-user-authored")
    if not upgrade_managed:
        return ProfilePlan(LEGACY_SPARK, LEGACY_SPARK, legacy, "preserved-legacy-managed")
    return ProfilePlan(
        LEGACY_SPARK,
        LEGACY_SPARK,
        legacy,
        "retired-legacy-managed",
        delete=True,
        needs_backup=True,
    )


def requested_name_for_installed(name: str) -> str | None:
    if name in EXPECTED_PROFILE_NAMES:
        return name
    match = re.fullmatch(r"(.+)_adaptive(?:_\d+)?", name)
    if match and match.group(1) in EXPECTED_PROFILE_NAMES:
        return match.group(1)
    return None


def plan_managed_cleanup(destination: Path, selected_plans: list[ProfilePlan]) -> list[ProfilePlan]:
    if not destination.is_dir():
        return []
    selected_paths = {plan.path for plan in selected_plans}
    selected_names = {plan.requested_name for plan in selected_plans}
    cleanup: list[ProfilePlan] = []
    for path in sorted(destination.glob("ams_*.toml")):
        if path in selected_paths:
            continue
        current = read_regular_text(path)
        if current is None or MANAGED_MARKER not in current:
            continue
        requested = requested_name_for_installed(path.stem)
        if requested is None:
            continue
        action = (
            "retired-unselected-managed"
            if requested.startswith("ams_spark_") and requested not in selected_names
            else "retired-duplicate-managed"
        )
        cleanup.append(
            ProfilePlan(
                requested,
                path.stem,
                path,
                action,
                delete=True,
                needs_backup=True,
            )
        )
    return cleanup


def dry_run_action(action: str) -> str:
    replacements = {
        "created": "would-create",
        "created-nonconflicting": "would-create-nonconflicting",
        "repaired-managed-malformed": "would-repair-managed-malformed",
        "upgraded-managed": "would-upgrade-managed",
        "retired-legacy-managed": "would-retire-legacy-managed",
        "retired-unselected-managed": "would-retire-unselected-managed",
        "retired-duplicate-managed": "would-retire-duplicate-managed",
    }
    return replacements.get(action, action)


@contextlib.contextmanager
def exclusive_lock(destination: Path) -> Iterator[None]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    lock_path = destination.parent / f".{destination.name}.ams-profile-install.lock"
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
        except (FileExistsError, IsADirectoryError, PermissionError):
            try:
                metadata = lock_path.lstat()
                age = time.time() - metadata.st_mtime
            except FileNotFoundError:
                continue
            except OSError as exc:
                raise SystemExit(f"Unable to inspect profile lock path {lock_path}: {exc}") from exc
            if not stat.S_ISREG(metadata.st_mode):
                raise SystemExit(f"Profile lock path is not a regular file: {lock_path}")
            if age > LOCK_STALE_SECONDS and not lock_owner_is_live(lock_path):
                try:
                    lock_path.unlink()
                except FileNotFoundError:
                    pass
                continue
            raise SystemExit(f"Another profile installation appears to be active: {lock_path}")
    try:
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def validate_source_profiles(source_dir: Path) -> list[Path]:
    sources = sorted(source_dir.glob("*.toml"))
    names = {source.stem for source in sources}
    if names != EXPECTED_PROFILE_NAMES:
        missing = sorted(EXPECTED_PROFILE_NAMES - names)
        extra = sorted(names - EXPECTED_PROFILE_NAMES)
        raise SystemExit(f"Profile asset set mismatch; missing={missing}, extra={extra}")
    for source in sources:
        if not source.is_file() or source.is_symlink():
            raise SystemExit(f"Profile asset is not a regular file: {source}")
    return sources


def build_plan(args: argparse.Namespace) -> tuple[list[ProfilePlan], set[str]]:
    selected_spark = set() if args.exclude_spark else set(args.spark_efforts)
    for label, value in (("Sol", args.sol_model), ("Terra", args.terra_model), ("Luna", args.luna_model)):
        validate_model_id(value, label)
    if selected_spark:
        validate_model_id(args.spark_model, "Spark")

    root = Path(__file__).resolve().parents[1]
    source_dir = root / "assets" / "agent-profiles"
    if not source_dir.is_dir():
        raise SystemExit(f"Profile assets not found: {source_dir}")
    sources = validate_source_profiles(source_dir)

    plans: list[ProfilePlan] = []
    for source in sources:
        if source.stem.startswith("ams_spark_"):
            effort = source.stem.removeprefix("ams_spark_")
            if effort not in selected_spark:
                continue
            model = args.spark_model
        elif source.stem.startswith("ams_sol_"):
            model = args.sol_model
        elif source.stem.startswith("ams_terra_"):
            model = args.terra_model
        elif source.stem.startswith("ams_luna_"):
            model = args.luna_model
        else:
            raise SystemExit(f"Unexpected bundled profile: {source.name}")
        plans.append(
            plan_profile(src=source, destination=args.destination, model=model, upgrade_managed=args.upgrade_managed)
        )
    plans.extend(plan_managed_cleanup(args.destination, plans))
    legacy = plan_legacy(args.destination, args.upgrade_managed)
    if legacy is not None:
        plans.append(legacy)
    return plans, selected_spark


def apply_plan(destination: Path, plans: list[ProfilePlan], transaction_id: str = "") -> None:
    destination_existed = destination.exists()
    snapshots: dict[Path, FileSnapshot] = {}
    created_backups: list[Path] = []
    applied: list[AppliedChange] = []
    destination.mkdir(parents=True, exist_ok=True)
    try:
        for plan in plans:
            if plan.text is None and not plan.delete:
                continue
            state = snapshots.setdefault(plan.path, snapshot(plan.path))
            if plan.needs_backup and state.existed:
                backup_path = next_backup_path(plan.path, transaction_id)
                shutil.copy2(plan.path, backup_path)
                created_backups.append(backup_path)
                plan.backup_path = backup_path
            if plan.delete:
                plan.path.unlink()
                _fsync_directory(plan.path.parent)
                applied.append(AppliedChange(plan.path, None))
            elif plan.text is not None:
                atomic_write(plan.path, plan.text, state.mode)
                applied.append(AppliedChange(plan.path, plan.text.encode("utf-8")))
    except BaseException as exc:
        rollback_errors: list[str] = []
        for change in reversed(applied):
            try:
                restore_if_unchanged(change.path, snapshots[change.path], change)
            except Exception as restore_exc:
                rollback_errors.append(f"restore {change.path}: {restore_exc}")
        for backup_path in created_backups:
            try:
                backup_path.unlink()
            except FileNotFoundError:
                pass
            except OSError as remove_exc:
                rollback_errors.append(f"remove backup {backup_path}: {remove_exc}")
        if not destination_existed:
            try:
                destination.rmdir()
            except OSError:
                pass
        if rollback_errors:
            raise SystemExit(
                f"Profile installation failed: {exc}; rollback also reported: {'; '.join(rollback_errors)}"
            ) from exc
        raise


def summary_for(args: argparse.Namespace, plans: list[ProfilePlan], selected_spark: set[str]) -> dict[str, object]:
    profiles: list[dict[str, object]] = []
    for plan in plans:
        action = dry_run_action(plan.action) if args.dry_run else plan.action
        expected_data = plan.text.encode("utf-8") if plan.text is not None else None
        profiles.append(
            {
                "requested_name": plan.requested_name,
                "installed_name": plan.installed_name,
                "path": str(plan.path),
                "action": action,
                "backup": str(plan.backup_path) if plan.backup_path else "",
                "expected_sha256": (
                    hashlib.sha256(expected_data).hexdigest() if expected_data is not None else None
                ),
                "expected_absent": bool(plan.delete),
            }
        )
    return {
        "destination": str(args.destination),
        "dry_run": args.dry_run,
        "spark_included": not args.exclude_spark,
        "spark_efforts": sorted(selected_spark, key=VALID_SPARK_EFFORTS.index),
        "profiles": profiles,
    }


def run(args: argparse.Namespace) -> dict[str, object]:
    args.destination = args.destination.expanduser().resolve(strict=False)
    plans, selected_spark = build_plan(args)
    if not args.dry_run:
        with exclusive_lock(args.destination):
            # Rebuild after acquiring the lock so decisions reflect the current destination.
            plans, selected_spark = build_plan(args)
            apply_plan(args.destination, plans, args.transaction_id)
    return summary_for(args, plans, selected_spark)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    summary = run(args)
    if args.as_json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"Destination: {summary['destination']}")
        for item in summary["profiles"]:
            suffix = f"; backup={item['backup']}" if item["backup"] else ""
            mapping = "" if item["requested_name"] == item["installed_name"] else f" -> {item['installed_name']}"
            print(f"{item['action']}: {item['requested_name']}{mapping} ({item['path']}){suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
