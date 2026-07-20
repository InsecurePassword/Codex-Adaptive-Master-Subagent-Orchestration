#!/usr/bin/env python3
"""Regression tests for bootstrap_profiles.py using only the Python standard library."""

from __future__ import annotations

import importlib.util
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from types import ModuleType

sys.dont_write_bytecode = True

from process_utils import run_bounded

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "scripts" / "bootstrap_profiles.py"
MANAGED = "# managed-by: adaptive-master-subagent-orchestration"
COMMAND_TIMEOUT = 20


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run(destination: Path, *args: str, expect: int = 0) -> dict[str, object] | str:
    command = [
        sys.executable,
        "-B",
        "-E",
        "-s",
        "-S",
        str(BOOTSTRAP),
        "--destination",
        str(destination),
        "--json",
        *args,
    ]
    try:
        result = run_bounded(
            command,
            text=True,
            capture_output=True,
            check=False,
            timeout=COMMAND_TIMEOUT,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired as exc:
        raise AssertionError(f"bootstrap command timed out after {COMMAND_TIMEOUT}s: {command}") from exc
    if result.returncode != expect:
        raise AssertionError(
            f"command returned {result.returncode}, expected {expect}: {command}\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
    if expect != 0:
        return (result.stderr or "") + (result.stdout or "")
    return json.loads(result.stdout or "{}")


def backup_files(path: Path) -> list[Path]:
    return sorted(path.parent.glob(path.name + ".bak-*"))


def load_bootstrap_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ams_bootstrap_under_test", BOOTSTRAP)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load bootstrap module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_transaction_rollback(base: Path) -> None:
    module = load_bootstrap_module()
    destination = base / "rollback"
    args = module.parse_args(["--destination", str(destination), "--exclude-spark"])
    original = module.atomic_write
    calls = 0

    def failing_write(path: Path, text: str, mode: int | None = None) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected write failure")
        original(path, text, mode)

    module.atomic_write = failing_write
    try:
        try:
            module.run(args)
        except OSError as exc:
            require("injected write failure" in str(exc), f"unexpected rollback exception: {exc}")
        else:
            raise AssertionError("rollback test did not fail as expected")
    finally:
        module.atomic_write = original
    require(not destination.exists(), "failed transaction left a destination directory")
    lock = destination.parent / f".{destination.name}.ams-profile-install.lock"
    require(not lock.exists(), "failed transaction left the profile lock")


def test_rollback_preserves_concurrent_change(base: Path) -> None:
    module = load_bootstrap_module()
    destination = base / "rollback-concurrent"
    args = module.parse_args(["--destination", str(destination), "--exclude-spark"])
    original = module.atomic_write
    first_path: Path | None = None
    calls = 0

    def failing_write(path: Path, text: str, mode: int | None = None) -> None:
        nonlocal calls, first_path
        calls += 1
        if calls == 1:
            original(path, text, mode)
            first_path = path
            return
        if first_path is not None:
            first_path.write_text("concurrent user content\n", encoding="utf-8")
        raise OSError("injected write failure after concurrent edit")

    module.atomic_write = failing_write
    try:
        try:
            module.run(args)
        except SystemExit as exc:
            require("rollback refused" in str(exc), f"concurrent rollback conflict was not reported: {exc}")
        else:
            raise AssertionError("concurrent rollback test did not fail as expected")
    finally:
        module.atomic_write = original
    require(first_path is not None and first_path.exists(), "concurrent file disappeared")
    require(first_path.read_text(encoding="utf-8") == "concurrent user content\n", "rollback overwrote concurrent content")


def test_lock_handling(base: Path) -> None:
    destination = base / "lock-test" / "agents"
    destination.parent.mkdir(parents=True)
    lock = destination.parent / f".{destination.name}.ams-profile-install.lock"
    live = {"pid": os.getpid(), "host": socket.gethostname(), "created": "old"}
    lock.write_text(json.dumps(live) + "\n", encoding="utf-8")
    old = time.time() - (3 * 60 * 60)
    os.utime(lock, (old, old))
    output = run(destination, "--exclude-spark", expect=1)
    require("appears to be active" in output, "live stale-looking lock was not preserved")
    require(lock.exists(), "live lock was removed")

    lock.write_text(json.dumps({"pid": 99999999, "host": socket.gethostname()}) + "\n", encoding="utf-8")
    os.utime(lock, (old, old))
    run(destination, "--exclude-spark")
    require(not lock.exists(), "dead stale lock was not cleared")

    lock.mkdir()
    output = run(destination, "--exclude-spark", expect=1)
    require("not a regular file" in output, "non-file lock error was unclear")
    lock.rmdir()

    lock.write_text("{malformed", encoding="utf-8")
    os.utime(lock, (old, old))
    run(destination, "--exclude-spark")
    require(not lock.exists(), "malformed stale profile lock was not recovered")

    if hasattr(os, "symlink"):
        target = destination.parent / "profile-lock-target"
        target.write_text("target", encoding="utf-8")
        try:
            lock.symlink_to(target)
        except OSError:
            pass
        else:
            output = run(destination, "--exclude-spark", expect=1)
            require("not a regular file" in output, "profile lock symlink error was unclear")
            lock.unlink()

    module = load_bootstrap_module()
    permission_destination = base / "permission-profile-lock" / "agents"
    permission_lock = permission_destination.parent / f".{permission_destination.name}.ams-profile-install.lock"
    original_open = module.os.open
    def denied_open(path, *args, **kwargs):
        if Path(path) == permission_lock:
            raise PermissionError("injected profile lock creation denial")
        return original_open(path, *args, **kwargs)
    module.os.open = denied_open
    try:
        try:
            with module.exclusive_lock(permission_destination):
                pass
        except SystemExit as exc:
            require("Unable to create profile lock path" in str(exc), f"profile lock creation denial was unclear: {exc}")
        else:
            raise AssertionError("profile lock creation denial was not reported")
    finally:
        module.os.open = original_open

    permission_destination.parent.mkdir(parents=True, exist_ok=True)
    permission_lock.write_text("{}\n", encoding="utf-8")
    original_lstat = module.Path.lstat
    def denied_lstat(self, *args, **kwargs):
        if self == permission_lock:
            raise PermissionError("injected profile lock inspection denial")
        return original_lstat(self, *args, **kwargs)
    module.Path.lstat = denied_lstat
    try:
        try:
            with module.exclusive_lock(permission_destination):
                pass
        except SystemExit as exc:
            require("Unable to inspect profile lock path" in str(exc), f"profile lock inspection denial was unclear: {exc}")
        else:
            raise AssertionError("profile lock inspection denial was not reported")
    finally:
        module.Path.lstat = original_lstat
        permission_lock.unlink(missing_ok=True)

    cleanup_destination = base / "cleanup-profile-lock" / "agents"
    cleanup_lock = cleanup_destination.parent / f".{cleanup_destination.name}.ams-profile-install.lock"
    try:
        with module.exclusive_lock(cleanup_destination):
            require(cleanup_lock.exists(), "profile lock was not created")
            raise RuntimeError("injected profile operation failure")
    except RuntimeError:
        pass
    require(not cleanup_lock.exists(), "profile lock was not cleaned after failure")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="ams-bootstrap-tests-") as tmp:
        base = Path(tmp)

        dry = base / "dry"
        report = run(dry, "--dry-run", "--transaction-id", "txn_test_123")
        require(not dry.exists(), "dry-run created destination")
        require(len(report["profiles"]) == 18, "dry-run did not plan all profiles")
        require(
            all(isinstance(item.get("expected_sha256"), str) and not item.get("expected_absent") for item in report["profiles"]),
            "dry-run mutation expectations were incomplete",
        )

        full = base / "full"
        report = run(full)
        require(len(list(full.glob("*.toml"))) == 18, "full install did not create 18 profiles")
        require(len(report["profiles"]) == 18, "full report did not include 18 profiles")
        second = run(full)
        require(
            all(item["action"] == "preserved-identical" for item in second["profiles"]),
            f"second run was not idempotent: {second}",
        )

        no_spark = base / "no-spark"
        run(no_spark, "--exclude-spark", "--spark-model", 'bad"ignored')
        require(len(list(no_spark.glob("*.toml"))) == 15, "exclude-spark profile count mismatch")

        selected = base / "selected"
        run(selected)
        high = selected / "ams_spark_high.toml"
        require(high.exists(), "full install did not create Spark High")
        report = run(selected, "--spark-efforts", "low,medium", "--transaction-id", "spark-retire")
        require(not high.exists(), "unselected managed Spark High was not retired")
        retired = next(item for item in report["profiles"] if item["requested_name"] == "ams_spark_high")
        require(retired.get("expected_absent") is True and retired.get("expected_sha256") is None, "delete expectation was incorrect")
        require(any(".bak-spark-retire" in str(path) for path in backup_files(high)), "transaction backup name was not used")
        require(backup_files(high), "retired managed Spark High was not backed up")
        require(
            any(item["action"] == "retired-unselected-managed" for item in report["profiles"]),
            "Spark retirement was not reported",
        )

        user_spark = base / "user-spark"
        run(user_spark)
        user_high = user_spark / "ams_spark_high.toml"
        user_high.write_text('name = "user_spark"\nmodel = "user"\n', encoding="utf-8")
        run(user_spark, "--spark-efforts", "low,medium")
        require(user_high.exists(), "unselected user-owned Spark profile was removed")

        empty_spark = base / "empty-spark"
        report = run(empty_spark, "--spark-efforts", "")
        require(report["spark_efforts"] == [], "empty Spark selection was not preserved")
        require(len(list(empty_spark.glob("*.toml"))) == 15, "empty Spark selection profile count mismatch")

        collision = base / "collision"
        collision.mkdir()
        original = 'name = "foreign"\ndescription = "foreign"\n'
        canonical = collision / "ams_sol_low.toml"
        canonical.write_text(original, encoding="utf-8")
        report = run(collision, "--exclude-spark")
        require(canonical.read_text(encoding="utf-8") == original, "user file changed")
        alternate = collision / "ams_sol_low_adaptive.toml"
        require(alternate.exists(), "nonconflicting profile was not created")
        require(
            any(item["action"] == "created-nonconflicting" for item in report["profiles"]),
            "collision action was not reported",
        )
        modified = alternate.read_text(encoding="utf-8").replace('model = "gpt-5.6"', 'model = "gpt-5.6-custom"')
        alternate.write_text(modified, encoding="utf-8")
        preserved = run(collision, "--exclude-spark")
        item = next(item for item in preserved["profiles"] if item["requested_name"] == "ams_sol_low" and not str(item["action"]).startswith("retired"))
        require(item["installed_name"] == "ams_sol_low_adaptive", f"alternate mapping drifted: {item}")
        require(item["action"] == "preserved-managed-different", f"alternate was not preserved: {item}")
        upgraded = run(collision, "--exclude-spark", "--upgrade-managed")
        item = next(item for item in upgraded["profiles"] if item["requested_name"] == "ams_sol_low" and not str(item["action"]).startswith("retired"))
        require(item["action"] == "upgraded-managed", f"managed alternate was not upgraded: {item}")
        require(backup_files(alternate), "managed alternate upgrade did not create backup")

        marker_collision = base / "marker-collision"
        marker_collision.mkdir()
        marker_canonical = marker_collision / "ams_sol_low.toml"
        marker_user_text = (
            'name = "user_sol_low"\n'
            'description = "# managed-by: adaptive-master-subagent-orchestration"\n'
            'model = "user-model"\n'
            'reasoning_effort = "low"\n'
        )
        marker_canonical.write_text(marker_user_text, encoding="utf-8")
        marker_report = run(marker_collision, "--exclude-spark", "--upgrade-managed")
        require(marker_canonical.read_text(encoding="utf-8") == marker_user_text, "marker text inside a profile value was misclassified as package ownership")
        require((marker_collision / "ams_sol_low_adaptive.toml").exists(), "user-owned marker collision did not receive a nonconflicting managed profile")
        marker_item = next(item for item in marker_report["profiles"] if item["requested_name"] == "ams_sol_low")
        require(marker_item["action"] == "created-nonconflicting", f"marker collision action was incorrect: {marker_item}")

        indented_marker = base / "indented-marker-profile"
        indented_marker.mkdir()
        indented_canonical = indented_marker / "ams_sol_low.toml"
        indented_user_text = (
            "  # managed-by: adaptive-master-subagent-orchestration\n"
            'name = "user_sol_low"\n'
            'description = "user-owned profile"\n'
            'model = "user-model"\n'
            'reasoning_effort = "low"\n'
        )
        indented_canonical.write_text(indented_user_text, encoding="utf-8")
        indented_report = run(indented_marker, "--exclude-spark", "--upgrade-managed")
        require(indented_canonical.read_text(encoding="utf-8") == indented_user_text, "noncanonical marker comment was misclassified as profile ownership")
        require((indented_marker / "ams_sol_low_adaptive.toml").exists(), "noncanonical marker collision did not receive a nonconflicting managed profile")
        indented_item = next(item for item in indented_report["profiles"] if item["requested_name"] == "ams_sol_low")
        require(indented_item["action"] == "created-nonconflicting", f"indented marker action was incorrect: {indented_item}")

        canonical.unlink()
        migrated = run(collision, "--exclude-spark")
        require(canonical.exists(), "canonical profile was not restored after collision disappeared")
        require(not alternate.exists(), "obsolete managed alternate was not retired")
        require(
            any(item["action"] == "retired-duplicate-managed" for item in migrated["profiles"]),
            "managed alternate retirement was not reported",
        )

        malformed = base / "malformed"
        run(malformed, "--exclude-spark")
        malformed_path = malformed / "ams_terra_medium.toml"
        malformed_path.write_text(MANAGED + "\nnot valid toml\n", encoding="utf-8")
        report = run(malformed, "--exclude-spark")
        item = next(item for item in report["profiles"] if item["requested_name"] == "ams_terra_medium")
        require(item["action"] == "repaired-managed-malformed", "malformed managed profile was not repaired")
        require(backup_files(malformed_path), "malformed managed profile was not backed up")

        legacy = base / "legacy"
        legacy.mkdir()
        legacy_path = legacy / "ams_spark_runner.toml"
        legacy_path.write_text(MANAGED + '\nname = "ams_spark_runner"\n', encoding="utf-8")
        run(legacy, "--exclude-spark")
        require(legacy_path.exists(), "legacy managed profile changed without upgrade")
        report = run(legacy, "--exclude-spark", "--upgrade-managed")
        require(not legacy_path.exists(), "legacy managed profile was not retired")
        require(backup_files(legacy_path), "legacy retirement did not create backup")
        require(any(item["action"] == "retired-legacy-managed" for item in report["profiles"]), "legacy retirement not reported")

        invalid = run(base / "invalid", "--exclude-spark", "--sol-model", "bad model", expect=1)
        require("Invalid Sol model identifier" in invalid, "invalid model error was unclear")

        if hasattr(os, "symlink"):
            symlink_dir = base / "symlink"
            symlink_dir.mkdir()
            target = symlink_dir / "target.toml"
            target.write_text("user\n", encoding="utf-8")
            link = symlink_dir / "ams_luna_low.toml"
            try:
                link.symlink_to(target)
            except OSError:
                pass
            else:
                run(symlink_dir, "--exclude-spark")
                require(link.is_symlink(), "profile collision symlink was replaced")
                require((symlink_dir / "ams_luna_low_adaptive.toml").exists(), "symlink collision did not use alternate")

        test_transaction_rollback(base)
        test_rollback_preserves_concurrent_change(base)
        test_lock_handling(base)

    print("BOOTSTRAP TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
