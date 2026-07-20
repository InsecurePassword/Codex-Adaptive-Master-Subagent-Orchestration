#!/usr/bin/env python3
"""Install Adaptive Master–Subagent custom-agent profiles idempotently."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import tempfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError as exc:  # Python <3.11
    raise SystemExit("Python 3.11+ is required because this installer uses tomllib.") from exc

MANAGED_MARKER = "# managed-by: adaptive-master-subagent-orchestration"
LEGACY_SPARK = "ams_spark_runner"
VALID_SPARK_EFFORTS = ("low", "medium", "high")
MODEL_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
NAME_RE = re.compile(r'(?m)^name\s*=\s*"([^"]+)"\s*$')
MODEL_RE = re.compile(r'(?m)^model\s*=\s*"([^"]+)"\s*$')


def parse_spark_efforts(value: str) -> tuple[str, ...]:
    values = tuple(dict.fromkeys(part.strip().lower() for part in value.split(",") if part.strip()))
    invalid = sorted(set(values) - set(VALID_SPARK_EFFORTS))
    if invalid:
        raise argparse.ArgumentTypeError(
            f"unsupported Spark effort(s): {', '.join(invalid)}; allowed: {', '.join(VALID_SPARK_EFFORTS)}"
        )
    return values


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    default_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
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
    return parser.parse_args()


def validate_model_id(value: str, label: str) -> None:
    if not MODEL_ID_RE.fullmatch(value):
        raise SystemExit(f"Invalid {label} model identifier: {value!r}")


def parse_profile(text: str) -> dict[str, object] | None:
    try:
        data = tomllib.loads(text)
    except Exception:
        return None
    required = ("name", "description", "model", "model_reasoning_effort", "developer_instructions")
    if not all(isinstance(data.get(key), str) and str(data[key]).strip() for key in required):
        return None
    if "sandbox_mode" in data and not isinstance(data["sandbox_mode"], str):
        return None
    return data


def expected_effort_for_name(name: str) -> str | None:
    if name.startswith(("ams_sol_", "ams_terra_", "ams_luna_", "ams_spark_")):
        return name.rsplit("_", 1)[1]
    return None


def valid_profile(text: str, expected_name: str | None = None) -> bool:
    data = parse_profile(text)
    if data is None:
        return False
    if expected_name is not None and data["name"] != expected_name:
        return False
    name = str(data["name"])
    expected_effort = expected_effort_for_name(name)
    if expected_effort is not None and data["model_reasoning_effort"] != expected_effort:
        return False
    if name.startswith("ams_spark_") and data.get("sandbox_mode") != "workspace-write":
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


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent), text=True)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def backup(path: Path) -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    candidate = path.with_name(f"{path.name}.bak-{stamp}")
    index = 1
    while candidate.exists():
        candidate = path.with_name(f"{path.name}.bak-{stamp}-{index}")
        index += 1
    shutil.copy2(path, candidate)
    return candidate


def profile_action(
    *, src: Path, destination: Path, model: str, dry_run: bool, upgrade_managed: bool
) -> dict[str, str]:
    requested = src.stem
    text = replace_model(src.read_text(encoding="utf-8"), model)
    if not valid_profile(text, requested):
        raise SystemExit(f"Bundled profile is invalid: {src}")

    dest = destination / src.name
    installed_name = requested
    backup_path = ""

    if not dest.exists():
        action = "would-create" if dry_run else "created"
        if not dry_run:
            atomic_write(dest, text)
    else:
        current = dest.read_text(encoding="utf-8", errors="replace")
        if current == text:
            action = "preserved-identical"
        elif MANAGED_MARKER in current:
            if not valid_profile(current, requested):
                action = "would-repair-managed-malformed" if dry_run else "repaired-managed-malformed"
                if not dry_run:
                    backup_path = str(backup(dest))
                    atomic_write(dest, text)
            elif upgrade_managed:
                action = "would-upgrade-managed" if dry_run else "upgraded-managed"
                if not dry_run:
                    backup_path = str(backup(dest))
                    atomic_write(dest, text)
            else:
                action = "preserved-managed-different"
        else:
            suffix = "_adaptive"
            installed_name = requested + suffix
            alt = destination / f"{installed_name}.toml"
            counter = 2
            while alt.exists():
                alt_text = replace_name(text, installed_name)
                alt_current = alt.read_text(encoding="utf-8", errors="replace")
                if alt_current == alt_text:
                    break
                installed_name = f"{requested}{suffix}_{counter}"
                alt = destination / f"{installed_name}.toml"
                counter += 1
            dest = alt
            text = replace_name(text, installed_name)
            if dest.exists() and dest.read_text(encoding="utf-8", errors="replace") == text:
                action = "preserved-nonconflicting"
            else:
                action = "would-create-nonconflicting" if dry_run else "created-nonconflicting"
                if not dry_run:
                    atomic_write(dest, text)

    return {
        "requested_name": requested,
        "installed_name": installed_name,
        "path": str(dest),
        "action": action,
        "backup": backup_path,
    }


def legacy_action(destination: Path, dry_run: bool, upgrade_managed: bool) -> dict[str, str] | None:
    legacy = destination / f"{LEGACY_SPARK}.toml"
    if not legacy.exists():
        return None
    current = legacy.read_text(encoding="utf-8", errors="replace")
    if MANAGED_MARKER not in current:
        action = "preserved-legacy-user-authored"
        backup_path = ""
    elif not upgrade_managed:
        action = "preserved-legacy-managed; use --upgrade-managed to retire"
        backup_path = ""
    else:
        action = "would-retire-legacy-managed" if dry_run else "retired-legacy-managed"
        backup_path = ""
        if not dry_run:
            backup_path = str(backup(legacy))
            legacy.unlink()
    return {
        "requested_name": LEGACY_SPARK,
        "installed_name": LEGACY_SPARK,
        "path": str(legacy),
        "action": action,
        "backup": backup_path,
    }


def main() -> int:
    args = parse_args()
    for label, value in (
        ("Sol", args.sol_model),
        ("Terra", args.terra_model),
        ("Luna", args.luna_model),
        ("Spark", args.spark_model),
    ):
        validate_model_id(value, label)

    root = Path(__file__).resolve().parents[1]
    source_dir = root / "assets" / "agent-profiles"
    if not source_dir.is_dir():
        raise SystemExit(f"Profile assets not found: {source_dir}")

    sources = sorted(source_dir.glob("*.toml"))
    selected_spark = set() if args.exclude_spark else set(args.spark_efforts)
    selected: list[Path] = []
    for source in sources:
        if source.stem.startswith("ams_spark_"):
            effort = source.stem.removeprefix("ams_spark_")
            if effort not in selected_spark:
                continue
        selected.append(source)

    if not args.dry_run:
        args.destination.mkdir(parents=True, exist_ok=True)

    actions: list[dict[str, str]] = []
    for source in selected:
        if source.stem.startswith("ams_sol_"):
            model = args.sol_model
        elif source.stem.startswith("ams_terra_"):
            model = args.terra_model
        elif source.stem.startswith("ams_luna_"):
            model = args.luna_model
        elif source.stem.startswith("ams_spark_"):
            model = args.spark_model
        else:
            raise SystemExit(f"Unexpected bundled profile: {source.name}")
        actions.append(
            profile_action(
                src=source,
                destination=args.destination,
                model=model,
                dry_run=args.dry_run,
                upgrade_managed=args.upgrade_managed,
            )
        )

    legacy = legacy_action(args.destination, args.dry_run, args.upgrade_managed)
    if legacy is not None:
        actions.append(legacy)

    summary = {
        "destination": str(args.destination),
        "dry_run": args.dry_run,
        "spark_included": not args.exclude_spark,
        "spark_efforts": sorted(selected_spark, key=VALID_SPARK_EFFORTS.index),
        "profiles": actions,
    }
    if args.as_json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"Destination: {args.destination}")
        for item in actions:
            suffix = f"; backup={item['backup']}" if item["backup"] else ""
            mapping = "" if item["requested_name"] == item["installed_name"] else f" -> {item['installed_name']}"
            print(f"{item['action']}: {item['requested_name']}{mapping} ({item['path']}){suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
