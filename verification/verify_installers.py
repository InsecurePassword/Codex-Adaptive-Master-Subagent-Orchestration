#!/usr/bin/env python3
"""Disposable installer transaction verification.

Repository-release tooling only; never installed or executed by AMS.
"""
from __future__ import annotations

import hashlib
import http.server
import os
import shutil
import socketserver
import subprocess
import tempfile
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


def run(command: list[str], environment: dict[str, str], expect_success: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        text=True,
        capture_output=True,
        env=environment,
        timeout=180,
    )
    if expect_success and result.returncode != 0:
        raise AssertionError(f"command failed {command}:\n{result.stdout}\n{result.stderr}")
    if not expect_success and result.returncode == 0:
        raise AssertionError(f"command unexpectedly succeeded {command}:\n{result.stdout}")
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def patch_bash(path: Path, url: str) -> None:
    text = (ROOT / "install.sh").read_text(encoding="utf-8")
    text = text.replace(
        'raw_base_url="https://github.com/${repo_owner}/${repo_name}/raw/refs/heads/main"',
        f'raw_base_url="{url}"',
    )
    text = text.replace(
        'manifest_url="${raw_base_url}/install-manifest.txt"',
        f'manifest_url="{url}/install-manifest.txt"',
    )
    path.write_text(text, encoding="utf-8", newline="\n")


def patch_powershell(path: Path, url: str) -> None:
    text = (ROOT / "install.ps1").read_text(encoding="utf-8")
    text = text.replace(
        '$RawBaseUrl = "https://github.com/$RepositoryOwner/$RepositoryName/raw/refs/heads/main"',
        f'$RawBaseUrl = "{url}"',
    )
    text = text.replace(
        '$ManifestUrl = "$RawBaseUrl/install-manifest.txt"',
        f'$ManifestUrl = "{url}/install-manifest.txt"',
    )
    path.write_text(text, encoding="utf-8", newline="\n")


def assert_install(skill_home: Path, codex_home: Path) -> tuple[Path, Path]:
    skill = skill_home / "adaptive-master-subagent-orchestration"
    agents = codex_home / "agents"
    if (skill / "VERSION").read_text(encoding="utf-8").strip() != "4.0":
        raise AssertionError("installed version mismatch")
    if len(list(agents.glob("ams_*.toml"))) != 18:
        raise AssertionError("installed profile inventory mismatch")
    return skill, agents


def tracking_record(campaign_id: str = "cvg-test", generation: int = 1) -> str:
    fields = [
        ("campaign_id", campaign_id),
        ("root_objective_id", "objective-test"),
        ("project_root", "/fixture/project"),
        ("state", "monitoring"),
        ("owner_id", "owner-test"),
        ("owner_lease_expires_at", "2026-08-04T01:00:00Z"),
        ("record_generation", str(generation)),
        ("created_at", "2026-08-04T00:00:00Z"),
        ("updated_at", "2026-08-04T00:10:00Z"),
        ("design_epoch_id", "epoch-1"),
        ("redesign_count", "0"),
        ("redesign_limit", "4"),
        ("epoch_correction_count", "1"),
        ("correction_limit", "4"),
        ("candidate_receipt", "b" * 64),
        ("acceptance_boundary", "packet acceptance"),
        ("finding_fingerprints", "none"),
        ("last_resolution_action", "monitor"),
    ]
    return "ams-convergence-tracking-v1\n" + "".join(f"{key}\t{value}\n" for key, value in fields)


def history_record(campaign_id: str = "cvg-done") -> tuple[str, str]:
    receipt = "a" * 64
    fields = [
        ("campaign_id", campaign_id),
        ("root_objective_id", "objective-done"),
        ("project_root", "/fixture/project"),
        ("state", "terminal"),
        ("owner_id", "none"),
        ("owner_lease_expires_at", "none"),
        ("record_generation", "3"),
        ("created_at", "2026-08-04T00:00:00Z"),
        ("updated_at", "2026-08-04T00:30:00Z"),
        ("design_epoch_id", "epoch-1"),
        ("redesign_count", "0"),
        ("redesign_limit", "4"),
        ("epoch_correction_count", "2"),
        ("correction_limit", "4"),
        ("candidate_receipt", "c" * 64),
        ("acceptance_boundary", "packet acceptance"),
        ("finding_fingerprints", "none"),
        ("last_resolution_action", "accepted"),
        ("terminal_disposition", "accept"),
        ("terminal_receipt", receipt),
        ("closed_at", "2026-08-04T00:30:00Z"),
    ]
    text = "ams-convergence-history-v1\n" + "".join(f"{key}\t{value}\n" for key, value in fields)
    return receipt, text


def main() -> int:
    handler = lambda *args, **kwargs: QuietHandler(  # noqa: E731
        *args,
        directory=str(ROOT),
        **kwargs,
    )
    server = Server(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}"
    try:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            skill_home = base / "skills"
            codex_home = base / "codex"
            home = base / "home"
            home.mkdir()
            environment = os.environ.copy()
            environment.update(
                {
                    "HOME": str(home),
                    "AMS_SKILL_HOME": str(skill_home),
                    "CODEX_HOME": str(codex_home),
                }
            )

            if os.name == "nt":
                executable = shutil.which("powershell.exe") or shutil.which("powershell")
                if not executable:
                    raise AssertionError("PowerShell unavailable on Windows verification host")
                script = base / "install-test.ps1"
                patch_powershell(script, url)
                command = [
                    executable,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script),
                ]
            else:
                executable = shutil.which("bash")
                if not executable:
                    raise AssertionError("bash unavailable")
                script = base / "install-test.sh"
                patch_bash(script, url)
                command = [executable, str(script)]

            # Clean install.
            run(command, environment)
            skill, agents = assert_install(skill_home, codex_home)

            # Strict active and immutable history records survive reinstall byte-for-byte.
            convergence = skill / ".runtime/convergence"
            history = convergence / "history"
            history.mkdir(parents=True)
            tracking = convergence / "cvg-test.tracking.log"
            tracking.write_text(tracking_record(), encoding="utf-8", newline="\n")
            receipt, history_text = history_record()
            history_path = history / f"cvg-done.{receipt}.record.log"
            history_path.write_text(history_text, encoding="utf-8", newline="\n")
            expected_runtime = {
                tracking.relative_to(skill).as_posix(): tracking.read_bytes(),
                history_path.relative_to(skill).as_posix(): history_path.read_bytes(),
            }
            profile_hashes = {path.name: sha256(path) for path in agents.glob("ams_*.toml")}
            run(command, environment)
            skill, agents = assert_install(skill_home, codex_home)
            for relative, expected in expected_runtime.items():
                if (skill / relative).read_bytes() != expected:
                    raise AssertionError(f"runtime record changed during reinstall: {relative}")
            if profile_hashes != {path.name: sha256(path) for path in agents.glob("ams_*.toml")}:
                raise AssertionError("profiles changed during idempotent reinstall")

            # A held shared package/runtime lock prevents another package writer.
            lock_path = skill_home / ".adaptive-master-subagent-orchestration.runtime.lock"
            lock_path.mkdir()
            (lock_path / "owner.log").write_text(
                "ams-runtime-lock-v1\nowner_id\texternal-test\npurpose\ttest\ncampaign_id\tnone\n"
                "acquired_epoch\t1\nlease_expires_epoch\t9999999999\n",
                encoding="utf-8",
                newline="\n",
            )
            run(command, environment, expect_success=False)
            # The simulated record writer completes while holding the shared lock.
            tracking.write_text(tracking_record(generation=2), encoding="utf-8", newline="\n")
            expected_runtime[tracking.relative_to(skill).as_posix()] = tracking.read_bytes()
            shutil.rmtree(lock_path)
            run(command, environment)
            skill, agents = assert_install(skill_home, codex_home)
            for relative, expected in expected_runtime.items():
                if (skill / relative).read_bytes() != expected:
                    raise AssertionError(f"post-lock reinstall lost runtime writer bytes: {relative}")

            # Invalid runtime state is rejected before replacement and remains untouched.
            invalid = convergence / "bad.tracking.log"
            invalid.write_text("not-a-valid-record\n", encoding="utf-8", newline="\n")
            sentinel = skill / "rollback-sentinel.txt"
            sentinel.write_text("preserve me\n", encoding="utf-8", newline="\n")
            run(command, environment, expect_success=False)
            skill, agents = assert_install(skill_home, codex_home)
            if sentinel.read_text(encoding="utf-8") != "preserve me\n":
                raise AssertionError("installer mutated skill after runtime-state refusal")
            if invalid.read_text(encoding="utf-8") != "not-a-valid-record\n":
                raise AssertionError("installer mutated invalid runtime evidence")
            invalid.unlink()

            # A customized profile blocks replacement and the transaction rolls back.
            conflict = agents / "ams_terra_low.toml"
            original_conflict = conflict.read_text(encoding="utf-8")
            conflict.write_text(original_conflict + "# user modification\n", encoding="utf-8", newline="\n")
            conflict_hash = sha256(conflict)
            run(command, environment, expect_success=False)
            skill, agents = assert_install(skill_home, codex_home)
            if (skill / "rollback-sentinel.txt").read_text(encoding="utf-8") != "preserve me\n":
                raise AssertionError("profile-collision rollback lost existing skill")
            if sha256(agents / "ams_terra_low.toml") != conflict_hash:
                raise AssertionError("profile-collision rollback changed customized profile")
            for relative, expected in expected_runtime.items():
                if (skill / relative).read_bytes() != expected:
                    raise AssertionError(f"rollback changed runtime record: {relative}")
            conflict.write_text(original_conflict, encoding="utf-8", newline="\n")

            print(
                "PASS: clean install, idempotent reinstall, strict runtime preservation, "
                "shared-lock refusal, invalid-runtime refusal, and profile-collision rollback"
            )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
