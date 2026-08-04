#!/usr/bin/env python3
"""Emit allowlisted routing metadata for one exact Codex subagent rollout."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any, Iterable, NoReturn

THREAD_ID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
MAX_ROLLOUT_BYTES = 64 * 1024 * 1024
MAX_LINE_CHARS = 4 * 1024 * 1024
MAX_DIRECTORIES = 10_000
MAX_ENTRIES = 200_000
MAX_DEPTH = 16


def fail(message: str) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def default_sessions_dir() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home) / "sessions"
    home = os.environ.get("HOME") or os.environ.get("USERPROFILE")
    if not home:
        fail("HOME/USERPROFILE is unset and --sessions-dir was not supplied")
    return Path(home) / ".codex" / "sessions"


def exact_matches(root: Path, thread_id: str) -> list[Path]:
    suffix = f"-{thread_id}.jsonl"
    matches: list[Path] = []
    pending: list[tuple[Path, int]] = [(root, 0)]
    directories = 0
    entries_seen = 0

    while pending:
        directory, depth = pending.pop()
        directories += 1
        if directories > MAX_DIRECTORIES or depth > MAX_DEPTH:
            fail("sessions-tree traversal bound exceeded")
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    entries_seen += 1
                    if entries_seen > MAX_ENTRIES:
                        fail("sessions-tree entry bound exceeded")
                    exact_name = entry.name.startswith("rollout-") and entry.name.endswith(suffix)
                    try:
                        is_link = entry.is_symlink()
                    except OSError:
                        fail("sessions tree could not be enumerated safely")
                    if exact_name and is_link:
                        fail("an exact rollout filename match is redirected")
                    if is_link:
                        continue
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            pending.append((Path(entry.path), depth + 1))
                            continue
                        is_file = entry.is_file(follow_symlinks=False)
                    except OSError:
                        fail("sessions tree could not be enumerated safely")
                    if exact_name:
                        if not is_file:
                            fail("an exact rollout filename match is not a regular file")
                        matches.append(Path(entry.path))
                        if len(matches) > 1:
                            return matches
        except OSError:
            fail("sessions tree could not be enumerated safely")
    return matches


def string_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def unique_required(values: Iterable[str | None], label: str, *, allow_none: bool = False) -> str | None:
    items = list(values)
    if not items:
        fail(f"missing {label}")
    if not allow_none and any(value is None or value == "" for value in items):
        fail(f"missing {label}")
    unique = set(items)
    if len(unique) != 1:
        fail(f"conflicting {label}")
    value = items[0]
    if not allow_none and not value:
        fail(f"missing {label}")
    return value


def inspect_rollout(path: Path, thread_id: str) -> dict[str, Any]:
    try:
        path_info = path.lstat()
    except OSError:
        fail("matched rollout is unavailable")
    if stat.S_ISLNK(path_info.st_mode) or not stat.S_ISREG(path_info.st_mode):
        fail("matched rollout is not a safe regular file")

    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError:
        fail("matched rollout could not be opened safely")

    session_payloads: list[dict[str, Any]] = []
    turn_payloads: list[dict[str, Any]] = []
    try:
        with os.fdopen(descriptor, "r", encoding="utf-8", errors="strict", newline="") as handle:
            opened = os.fstat(handle.fileno())
            if not stat.S_ISREG(opened.st_mode):
                fail("matched rollout is not a regular file")
            if opened.st_size <= 0 or opened.st_size > MAX_ROLLOUT_BYTES:
                fail("matched rollout size is invalid")
            if path_info.st_dev != opened.st_dev or path_info.st_ino != opened.st_ino:
                fail("matched rollout changed before inspection")

            for line in handle:
                if len(line) > MAX_LINE_CHARS:
                    fail("rollout contains an oversized JSONL record")
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    fail("rollout contains invalid JSONL")
                if not isinstance(record, dict):
                    continue
                payload = record.get("payload")
                if not isinstance(payload, dict):
                    continue
                if record.get("type") == "session_meta":
                    session_payloads.append(payload)
                elif record.get("type") == "turn_context":
                    turn_payloads.append(payload)

            final = os.fstat(handle.fileno())
            if opened.st_size != final.st_size or getattr(opened, "st_mtime_ns", None) != getattr(final, "st_mtime_ns", None):
                fail("rollout changed during inspection")
    except UnicodeDecodeError:
        fail("rollout is not valid UTF-8")
    except OSError:
        fail("rollout could not be read")

    try:
        path_final = path.lstat()
    except OSError:
        fail("matched rollout path changed during inspection")
    if stat.S_ISLNK(path_final.st_mode) or path_final.st_dev != path_info.st_dev or path_final.st_ino != path_info.st_ino:
        fail("matched rollout path changed during inspection")

    if len(session_payloads) != 1:
        fail("missing or ambiguous session metadata")
    if not turn_payloads:
        fail("missing turn context")

    session = session_payloads[0]
    observed_thread_id = string_or_none(session.get("id"))
    if observed_thread_id != thread_id:
        fail("session metadata does not identify the requested thread")
    agent_role = string_or_none(session.get("agent_role"))
    if not agent_role:
        fail("missing agent role")

    models = [string_or_none(turn.get("model")) for turn in turn_payloads]
    efforts = [string_or_none(turn.get("effort")) for turn in turn_payloads]
    sandboxes = [
        string_or_none(value.get("type")) if isinstance(value := turn.get("sandbox_policy"), dict) else None
        for turn in turn_payloads
    ]
    permissions = [
        string_or_none(value.get("type")) if isinstance(value := turn.get("permission_profile"), dict) else None
        for turn in turn_payloads
    ]
    working_dirs = [string_or_none(turn.get("cwd")) for turn in turn_payloads]

    return {
        "thread_id": observed_thread_id,
        "parent_thread_id": string_or_none(session.get("parent_thread_id")),
        "agent_role": agent_role,
        "agent_path": string_or_none(session.get("agent_path")),
        "model_provider": string_or_none(session.get("model_provider")),
        "model": unique_required(models, "model"),
        "effort": unique_required(efforts, "effort"),
        "sandbox_policy_type": unique_required(sandboxes, "sandbox policy types", allow_none=True),
        "permission_profile_type": unique_required(permissions, "permission profile types", allow_none=True),
        "cwd": unique_required(working_dirs, "working directories", allow_none=True),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("thread_id", help="exact lowercase subagent thread UUID")
    parser.add_argument("--sessions-dir", type=Path, default=None, help="explicit Codex sessions root")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not THREAD_ID_RE.fullmatch(args.thread_id):
        fail("thread_id must be a lowercase UUID")
    sessions_dir = args.sessions_dir or default_sessions_dir()
    try:
        root_info = sessions_dir.lstat()
    except OSError:
        fail("sessions directory is unavailable")
    if stat.S_ISLNK(root_info.st_mode) or not stat.S_ISDIR(root_info.st_mode):
        fail("sessions directory is not a safe directory")

    matches = exact_matches(sessions_dir, args.thread_id)
    if not matches:
        fail("no rollout filename matched the requested thread id")
    if len(matches) != 1:
        fail("multiple rollout filenames matched the requested thread id")

    print(json.dumps(inspect_rollout(matches[0], args.thread_id), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
