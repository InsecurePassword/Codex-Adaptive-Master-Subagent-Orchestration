#!/usr/bin/env python3
"""Disposable installer transaction verification.

Repository-release tooling only; never installed or executed by AMS.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import socket
import sys
import time
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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


def campaign_id(root_objective_id: str, project_root: str, acceptance_boundary: str, candidate_surface: str) -> str:
    payload = (
        "ams-convergence-campaign-v1\n"
        f"project_root\t{project_root}\n"
        f"root_objective_id\t{root_objective_id}\n"
        f"acceptance_boundary\t{acceptance_boundary}\n"
        f"candidate_surface\t{candidate_surface}\n"
    ).encode("utf-8")
    return "cvg-" + hashlib.sha256(payload).hexdigest()


def set_owner_only(path: Path, directory: bool) -> None:
    if os.name == "nt":
        user = os.environ.get("USERNAME")
        if not user:
            raise AssertionError("USERNAME unavailable for ACL fixture")
        grant = f"{user}:(OI)(CI)F" if directory else f"{user}:F"
        cleanup = subprocess.run(
            ["icacls.exe", str(path), "/inheritance:r", "/remove:g", "*S-1-1-0"],
            text=True,
            capture_output=True,
        )
        result = subprocess.run(
            ["icacls.exe", str(path), "/grant:r", grant],
            text=True,
            capture_output=True,
        )
        if cleanup.returncode != 0 or result.returncode != 0:
            raise AssertionError(
                f"could not set runtime ACL on {path}: "
                f"{cleanup.stdout}{cleanup.stderr}{result.stdout}{result.stderr}"
            )
    else:
        path.chmod(0o700 if directory else 0o600)


def make_runtime_insecure(path: Path) -> None:
    if os.name == "nt":
        result = subprocess.run(
            ["icacls.exe", str(path), "/grant", "*S-1-1-0:R"],
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            raise AssertionError(f"could not weaken runtime ACL fixture on {path}: {result.stdout}\n{result.stderr}")
    else:
        path.chmod(0o644)


def write_secure(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="\n")
    set_owner_only(path, False)


def make_secure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    current = path
    while current.name in {".runtime", "convergence", "history"}:
        set_owner_only(current, True)
        current = current.parent


def tracking_record(generation: int = 1) -> tuple[str, str]:
    objective = "objective-test"
    project = "/fixture/project"
    boundary = "packet acceptance"
    surface = "audio-routing-core"
    identity = campaign_id(objective, project, boundary, surface)
    fields = [
        ("campaign_id", identity),
        ("root_objective_id", objective),
        ("project_root", project),
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
        ("acceptance_boundary", boundary),
        ("candidate_surface", surface),
        ("finding_fingerprints", "none"),
        ("last_resolution_action", "monitor"),
    ]
    return identity, "ams-convergence-tracking-v1\n" + "".join(f"{key}\t{value}\n" for key, value in fields)


def history_record() -> tuple[str, str, str]:
    receipt = "a" * 64
    objective = "objective-done"
    project = "/fixture/project"
    boundary = "packet acceptance"
    surface = "audio-routing-core"
    identity = campaign_id(objective, project, boundary, surface)
    fields = [
        ("campaign_id", identity),
        ("root_objective_id", objective),
        ("project_root", project),
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
        ("acceptance_boundary", boundary),
        ("candidate_surface", surface),
        ("finding_fingerprints", "none"),
        ("last_resolution_action", "accepted"),
        ("terminal_disposition", "accept"),
        ("terminal_receipt", receipt),
        ("closed_at", "2026-08-04T00:30:00Z"),
    ]
    text = "ams-convergence-history-v1\n" + "".join(f"{key}\t{value}\n" for key, value in fields)
    return identity, receipt, text


def lock_record(owner: str, expires: int, pid: int, host: str | None = None) -> str:
    host_value = host or (os.environ.get("COMPUTERNAME") if os.name == "nt" else socket.gethostname()) or ""
    safe_host = re.sub(r"[^a-z0-9._-]", "", host_value.lower())[:128]
    return (
        "ams-runtime-lock-v1\n"
        f"owner_id\t{owner}\n"
        "purpose\tconvergence\n"
        "campaign_id\tnone\n"
        f"host_id\t{safe_host}\n"
        f"pid\t{pid}\n"
        "acquired_epoch\t1\n"
        f"lease_expires_epoch\t{expires}\n"
    )


def start_http_server() -> tuple[subprocess.Popen[str], str]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        port = int(probe.getsockname()[1])
    process = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1", "--directory", str(ROOT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    url = f"http://127.0.0.1:{port}"
    for _ in range(100):
        if process.poll() is not None:
            raise AssertionError("repository fixture HTTP server exited during startup")
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                return process, url
        except OSError:
            time.sleep(0.02)
    process.terminate()
    process.wait(timeout=5)
    raise AssertionError("repository fixture HTTP server did not start")


def main() -> int:
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
        else:
            executable = shutil.which("bash")
            if not executable:
                raise AssertionError("bash unavailable")
            script = base / "install-test.sh"

        def invoke(expect_success: bool = True) -> subprocess.CompletedProcess[str]:
            server, url = start_http_server()
            try:
                if os.name == "nt":
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
                    patch_bash(script, url)
                    command = [executable, str(script)]
                return run(command, environment, expect_success=expect_success)
            finally:
                server.terminate()
                try:
                    server.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait(timeout=5)

        # Clean install.
        invoke()
        skill, agents = assert_install(skill_home, codex_home)

        # Strict active and immutable history records survive reinstall byte-for-byte.
        convergence = skill / ".runtime/convergence"
        history = convergence / "history"
        make_secure_dir(history)
        tracking_id, tracking_text = tracking_record()
        tracking = convergence / f"{tracking_id}.tracking.log"
        write_secure(tracking, tracking_text)
        history_id, receipt, history_text = history_record()
        history_path = history / f"{history_id}.{receipt}.record.log"
        write_secure(history_path, history_text)
        expected_runtime = {
            tracking.relative_to(skill).as_posix(): tracking.read_bytes(),
            history_path.relative_to(skill).as_posix(): history_path.read_bytes(),
        }
        profile_hashes = {path.name: sha256(path) for path in agents.glob("ams_*.toml")}
        invoke()
        skill, agents = assert_install(skill_home, codex_home)
        for relative, expected in expected_runtime.items():
            if (skill / relative).read_bytes() != expected:
                raise AssertionError(f"runtime record changed during reinstall: {relative}")
        if profile_hashes != {path.name: sha256(path) for path in agents.glob("ams_*.toml")}:
            raise AssertionError("profiles changed during idempotent reinstall")

        # A held shared package/runtime lock prevents another package writer.
        lock_path = skill_home / ".adaptive-master-subagent-orchestration.runtime.lock"
        lock_path.mkdir()
        set_owner_only(lock_path, True)
        write_secure(lock_path / "owner.log", lock_record("external-test", 9999999999, os.getpid()))
        invoke(expect_success=False)
        # The simulated record writer completes while holding the shared lock.
        _, tracking_text_v2 = tracking_record(generation=2)
        write_secure(tracking, tracking_text_v2)
        expected_runtime[tracking.relative_to(skill).as_posix()] = tracking.read_bytes()
        shutil.rmtree(lock_path)
        invoke()

        # An expired same-host lock with a proven-dead PID is quarantined and recovered.
        lock_path.mkdir()
        set_owner_only(lock_path, True)
        write_secure(lock_path / "owner.log", lock_record("dead-owner", 2, 2147483647))
        invoke()
        if lock_path.exists() or list(skill_home.glob(".adaptive-master-subagent-orchestration.runtime.lock.stale.*")):
            raise AssertionError("stale lock or quarantine remained after bounded recovery")
        skill, agents = assert_install(skill_home, codex_home)
        for relative, expected in expected_runtime.items():
            if (skill / relative).read_bytes() != expected:
                raise AssertionError(f"post-lock reinstall lost runtime writer bytes: {relative}")

        # A crash before owner.log publication is recoverable after the initialization grace.
        lock_path.mkdir()
        set_owner_only(lock_path, True)
        os.utime(lock_path, (1, 1))
        invoke()
        if lock_path.exists() or list(skill_home.glob(".adaptive-master-subagent-orchestration.runtime.lock.stale.*")):
            raise AssertionError("ownerless stale lock or quarantine remained after bounded recovery")

        # Runtime records with non-owner access are rejected before replacement.
        make_runtime_insecure(tracking)
        invoke(expect_success=False)
        set_owner_only(tracking, False)
        if tracking.read_bytes() != expected_runtime[tracking.relative_to(skill).as_posix()]:
            raise AssertionError("permission-refusal path mutated the runtime record")

        # Invalid runtime state is rejected before replacement and remains untouched.
        invalid = convergence / "bad.tracking.log"
        write_secure(invalid, "not-a-valid-record\n")
        sentinel = skill / "rollback-sentinel.txt"
        sentinel.write_text("preserve me\n", encoding="utf-8", newline="\n")
        invoke(expect_success=False)
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
        invoke(expect_success=False)
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
            "shared-lock refusal/valid-and-ownerless recovery, permission enforcement, invalid-runtime refusal, and profile-collision rollback"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
