#!/usr/bin/env python3
"""Regression tests for bootstrap_profiles.py using only the standard library."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "scripts" / "bootstrap_profiles.py"
MANAGED = "# managed-by: adaptive-master-subagent-orchestration"


def run(destination: Path, *args: str, expect: int = 0) -> dict[str, object] | str:
    command = [sys.executable, str(BOOTSTRAP), "--destination", str(destination), "--json", *args]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != expect:
        raise AssertionError(
            f"command returned {result.returncode}, expected {expect}: {command}\nstdout={result.stdout}\nstderr={result.stderr}"
        )
    if expect != 0:
        return result.stderr + result.stdout
    return json.loads(result.stdout)


def backup_files(path: Path) -> list[Path]:
    return sorted(path.parent.glob(path.name + ".bak-*"))


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="ams-bootstrap-tests-") as tmp:
        base = Path(tmp)

        dry = base / "dry"
        report = run(dry, "--dry-run")
        assert not dry.exists(), "dry-run created destination"
        assert all(str(item["action"]).startswith("would-") for item in report["profiles"]), report

        full = base / "full"
        report = run(full)
        assert len(list(full.glob("*.toml"))) == 18
        assert len(report["profiles"]) == 18
        second = run(full)
        assert all(item["action"] == "preserved-identical" for item in second["profiles"]), second

        no_spark = base / "no-spark"
        run(no_spark, "--exclude-spark")
        assert len(list(no_spark.glob("*.toml"))) == 15
        assert not list(no_spark.glob("ams_spark_*.toml"))

        selected = base / "selected"
        report = run(selected, "--spark-efforts", "low,medium")
        assert report["spark_efforts"] == ["low", "medium"]
        assert len(list(selected.glob("*.toml"))) == 17
        assert not (selected / "ams_spark_high.toml").exists()

        collision = base / "collision"
        collision.mkdir()
        original = 'name = "foreign"\ndescription = "foreign"\n'
        (collision / "ams_sol_low.toml").write_text(original, encoding="utf-8")
        report = run(collision, "--exclude-spark")
        assert (collision / "ams_sol_low.toml").read_text(encoding="utf-8") == original
        assert (collision / "ams_sol_low_adaptive.toml").exists()
        assert any(item["action"] == "created-nonconflicting" for item in report["profiles"])

        malformed = base / "malformed"
        malformed.mkdir()
        bad = malformed / "ams_terra_medium.toml"
        bad.write_text(MANAGED + "\nname = \"ams_terra_medium\"\n", encoding="utf-8")
        report = run(malformed, "--exclude-spark")
        item = next(item for item in report["profiles"] if item["requested_name"] == "ams_terra_medium")
        assert item["action"] == "repaired-managed-malformed", item
        assert backup_files(bad), "malformed repair did not create backup"

        upgrade = base / "upgrade"
        run(upgrade, "--exclude-spark")
        target = upgrade / "ams_luna_low.toml"
        modified = target.read_text(encoding="utf-8").replace("Extraction, classification", "Changed but valid")
        target.write_text(modified, encoding="utf-8")
        preserved = run(upgrade, "--exclude-spark")
        item = next(item for item in preserved["profiles"] if item["requested_name"] == "ams_luna_low")
        assert item["action"] == "preserved-managed-different", item
        upgraded = run(upgrade, "--exclude-spark", "--upgrade-managed")
        item = next(item for item in upgraded["profiles"] if item["requested_name"] == "ams_luna_low")
        assert item["action"] == "upgraded-managed", item
        assert backup_files(target), "managed upgrade did not create backup"

        legacy = base / "legacy"
        legacy.mkdir()
        legacy_file = legacy / "ams_spark_runner.toml"
        legacy_file.write_text(
            MANAGED
            + '\nname = "ams_spark_runner"\ndescription = "legacy"\nmodel = "gpt-5.3-codex-spark"\n'
            + 'model_reasoning_effort = "medium"\ndeveloper_instructions = "legacy"\n',
            encoding="utf-8",
        )
        preserved = run(legacy)
        legacy_item = next(item for item in preserved["profiles"] if item["requested_name"] == "ams_spark_runner")
        assert str(legacy_item["action"]).startswith("preserved-legacy-managed")
        assert legacy_file.exists()
        preview = run(legacy, "--upgrade-managed", "--dry-run")
        legacy_item = next(item for item in preview["profiles"] if item["requested_name"] == "ams_spark_runner")
        assert legacy_item["action"] == "would-retire-legacy-managed"
        assert legacy_file.exists(), "legacy dry-run removed file"
        retired = run(legacy, "--upgrade-managed")
        legacy_item = next(item for item in retired["profiles"] if item["requested_name"] == "ams_spark_runner")
        assert legacy_item["action"] == "retired-legacy-managed"
        assert not legacy_file.exists()
        assert backup_files(legacy_file), "legacy migration did not create backup"

        invalid = run(base / "invalid-model", "--sol-model", 'bad"model', expect=1)
        assert "Invalid Sol model identifier" in invalid

    print("BOOTSTRAP TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
