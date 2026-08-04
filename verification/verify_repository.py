#!/usr/bin/env python3
"""Repository-release verification for AMS 4.0.

This script is repository tooling. It is not installed, loaded, or executed by AMS.
"""
from __future__ import annotations

import hashlib
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "adaptive-master-subagent-orchestration"
MANIFEST = ROOT / "install-manifest.txt"
BASELINE = ROOT / "verification/fixtures/baseline-install-manifest-ams4-conflict-resolved.txt"
EXPECTED_VERSION = "4.0"

PROFILE_EFFORTS = {
    "sol": ("low", "medium", "high", "xhigh", "max"),
    "terra": ("low", "medium", "high", "xhigh", "max"),
    "luna": ("low", "medium", "high", "xhigh", "max"),
    "spark": ("low", "medium", "high"),
}
MODELS = {
    "sol": "gpt-5.6-sol",
    "terra": "gpt-5.6-terra",
    "luna": "gpt-5.6-luna",
    "spark": "gpt-5.3-codex-spark",
}
FEATURES = {
    "convergence-control": "convergence_control",
    "work-order-refinement": "work_order_refinement",
    "review-control": "review_control",
    "shared-worktree-verification": "shared_worktree_verification",
    "runtime-observation": "runtime_observation",
    "untrusted-evidence-handling": "untrusted_evidence_handling",
    "task-graph-safeguards": "task_graph_safeguards",
    "rejected-approach-handoff": "rejected_approach_handoff",
    "request-accounting": "request_accounting",
    "app-task-lane": "app_task_lane",
}
DEFAULTS = {
    "enabled": False,
    "allow_implicit_invocation": True,
    "intensity": "auto",
    "project_governance": True,
    "root_execution_fallback": True,
    "convergence_control": True,
    "convergence_correction_limit": 4,
    "convergence_redesign_limit": 4,
    "spark_enabled": True,
    "spark_available": True,
    "spark_efforts": ["low", "medium", "high"],
    "profile_management": "auto",
    "work_order_refinement": False,
    "review_control": False,
    "shared_worktree_verification": False,
    "runtime_observation": False,
    "untrusted_evidence_handling": False,
    "task_graph_safeguards": False,
    "rejected_approach_handoff": False,
    "request_accounting": False,
    "app_task_lane": False,
}


def fail(message: str) -> None:
    raise AssertionError(message)


def read_safe(path: Path, maximum: int = 1024 * 1024) -> str:
    if path.is_symlink() or not path.is_file():
        fail(f"unsafe or missing file: {path.relative_to(ROOT)}")
    data = path.read_bytes()
    if not data or len(data) > maximum:
        fail(f"unsafe size: {path.relative_to(ROOT)}")
    if data.startswith(b"\xef\xbb\xbf") or b"\x00" in data or b"\r" in data:
        fail(f"unsafe bytes: {path.relative_to(ROOT)}")
    if not data.endswith(b"\n"):
        fail(f"missing final LF: {path.relative_to(ROOT)}")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as error:
        fail(f"invalid UTF-8: {path.relative_to(ROOT)}: {error}")
    raise AssertionError("unreachable")


def parse_manifest(path: Path) -> tuple[str, dict[str, tuple[str, int]]]:
    lines = read_safe(path).splitlines()
    if len(lines) < 3 or lines[0] != "ams-install-manifest-v1":
        fail(f"bad manifest header: {path.relative_to(ROOT)}")
    if not lines[1].startswith("version\t"):
        fail(f"bad manifest version line: {path.relative_to(ROOT)}")
    entries: dict[str, tuple[str, int]] = {}
    for line_number, line in enumerate(lines[2:], 3):
        parts = line.split("\t")
        if len(parts) != 3:
            fail(f"bad manifest line {line_number}: {path.relative_to(ROOT)}")
        digest, length_text, repo_path = parts
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            fail(f"bad digest on manifest line {line_number}")
        if not length_text.isdigit() or int(length_text) <= 0:
            fail(f"bad length on manifest line {line_number}")
        if repo_path in entries:
            fail(f"duplicate manifest path: {repo_path}")
        entries[repo_path] = (digest, int(length_text))
    return lines[1].split("\t", 1)[1], entries


def require(text: str, phrase: str, label: str) -> None:
    if phrase not in text:
        fail(f"{label} missing: {phrase}")


def main() -> int:
    version, entries = parse_manifest(MANIFEST)
    if version != EXPECTED_VERSION or read_safe(PACKAGE / "VERSION").strip() != EXPECTED_VERSION:
        fail("version mismatch")

    actual = {
        path.relative_to(ROOT).as_posix()
        for path in PACKAGE.rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    if set(entries) != actual:
        fail(
            "manifest inventory mismatch: "
            f"missing={sorted(actual - set(entries))}, extra={sorted(set(entries) - actual)}"
        )
    if len(entries) != 42:
        fail(f"expected 42 core files, got {len(entries)}")
    for relative, (digest, size) in entries.items():
        data = (ROOT / relative).read_bytes()
        if len(data) != size or hashlib.sha256(data).hexdigest() != digest:
            fail(f"manifest bytes mismatch: {relative}")
        if any(part in relative for part in ("/verification/", "/tests/", "/tools/")):
            fail(f"repository-only tooling leaked into installed core: {relative}")

    # Model/effort profiles must remain byte-identical to the immediate working baseline.
    _, baseline_entries = parse_manifest(BASELINE)
    for relative, baseline_record in baseline_entries.items():
        if "/assets/agent-profiles/" in relative and entries.get(relative) != baseline_record:
            fail(f"profile drifted: {relative}")
    profiles = sorted((PACKAGE / "assets/agent-profiles").glob("*.toml"))
    if len(profiles) != 18:
        fail(f"expected 18 profiles, got {len(profiles)}")
    forbidden = {
        "sandbox_mode",
        "approval_policy",
        "network_access",
        "writable_roots",
        "tools",
        "tool_grants",
    }
    for profile in profiles:
        data = tomllib.loads(read_safe(profile))
        match = re.fullmatch(
            r"ams_(sol|terra|luna|spark)_(low|medium|high|xhigh|max)\.toml",
            profile.name,
        )
        if not match:
            fail(f"bad profile name: {profile.name}")
        family, effort = match.groups()
        if effort not in PROFILE_EFFORTS[family]:
            fail(f"unsupported effort: {profile.name}")
        if data.get("model") != MODELS[family] or data.get("model_reasoning_effort") != effort:
            fail(f"bad route: {profile.name}")
        if forbidden & set(data):
            fail(f"permission override: {profile.name}")

    control = read_safe(PACKAGE / "references/project-control.md")
    default_match = re.search(
        r"(?:The )?current exact default(?: is)?:\n\n```toml\n(.*?)```",
        control,
        re.DOTALL | re.IGNORECASE,
    )
    if not default_match:
        fail("configuration default block missing")
    if tomllib.loads(default_match.group(1)) != DEFAULTS:
        fail("configuration defaults do not match the contract")
    require(control, "Ignore retired top-level `schema_version` regardless of value", "legacy field contract")
    require(control, "never branch on it", "legacy field contract")
    require(control, "Ignore no other unknown field", "unknown-field contract")
    require(control, "load the state-reader/status section of `convergence-control.md`", "status routing")
    require(control, "named governance capability despite governance being off", "direct governance routing")

    feature = read_safe(PACKAGE / "references/feature-control.md")
    for name, field in FEATURES.items():
        require(feature, f"{name}", "feature mapping")
        require(feature, f"-> {field}", "feature mapping")
    require(feature, "Mere requests such as", "temporary override boundary")
    require(feature, "fix everything and do not stop", "generic completion boundary")

    core = read_safe(PACKAGE / "references/runtime-core.md")
    governance = read_safe(PACKAGE / "references/project-governance.md")
    convergence = read_safe(PACKAGE / "references/convergence-control.md")

    # Every optional capability must have an explicit incoming route.
    routes = {
        "work-order-refinement.md": "work-order-refinement.md",
        "task-graph-safeguards.md": "task-graph-safeguards.md",
        "shared-worktree-control.md": "shared-worktree-control.md",
        "evidence-handling.md": "evidence-handling.md",
        "runtime-observation.md": "runtime-observation.md",
        "request-accounting.md": "request-accounting.md",
        "app-task companion": "ams-app-task-lane",
    }
    for label, token in routes.items():
        require(core, token, f"runtime route for {label}")
    require(governance, "review-control.md", "review route")
    require(governance, "handoff-control.md", "handoff route")

    # Convergence must be detectable before the lazy response is loaded and finalizable before trigger.
    for phrase in (
        "## Lightweight convergence detector",
        "Generic quality/completion language—including “fix everything,” “do not stop,”",
        "After the first completed correction cycle or any redesign",
        "Whenever a tracked campaign reaches acceptance, cancellation, supersession/new objective",
        "On startup, compaction recovery, or `AMS STATUS`",
        "Once response custody begins",
    ):
        require(core, phrase, "core convergence detector")
    for phrase in (
        "create or update tracking state after the first completed correction cycle",
        "finalize a tracked campaign at any terminal boundary",
        "ams-convergence-tracking-v1",
        "ams-convergence-history-v1",
        "record_generation",
        "terminal-pending-history",
        "Finalization applies whenever a tracked campaign closes",
        "enumerate at most 128 safe `*.tracking.log` files",
        "shared package/runtime lock",
    ):
        require(convergence, phrase, "convergence state contract")
    if "convergence.log" in convergence:
        fail("obsolete shared convergence append log remains")

    # Canonical work order and result envelopes remain unique in the active core.
    if core.count("WORK ORDER\nID:") != 1 or core.count("RESULT\nWork-order ID") != 1:
        fail("canonical work-order/result envelope is duplicated or missing")
    refinement = read_safe(PACKAGE / "references/work-order-refinement.md")
    review = read_safe(PACKAGE / "references/review-control.md")
    if "WORK ORDER\nID:" in refinement or "WORK ORDER\nID:" in review:
        fail("optional module duplicates canonical work order")
    require(refinement, "WORK ORDER ADDENDUM", "work-order refinement addendum")
    require(review, "REVIEW ADDENDUM", "review addendum")
    require(review, "REVIEW RESULT ADDENDUM", "review result addendum")

    # Enhanced surface identity remains lazy and shared by the two relevant modules.
    surface = read_safe(PACKAGE / "references/surface-identity.md")
    shared = read_safe(PACKAGE / "references/shared-worktree-control.md")
    graph = read_safe(PACKAGE / "references/task-graph-safeguards.md")
    require(surface, "AMS canonical mutable-surface identity", "surface identity")
    require(shared, "surface-identity.md", "shared-tree surface route")
    require(graph, "surface-identity.md", "task-graph surface route")

    # Root fallback remains unavailable during convergence custody and keeps independent validation.
    root_fallback = read_safe(PACKAGE / "references/root-execution-fallback.md")
    require(root_fallback, "active convergence control", "fallback convergence precedence")
    require(root_fallback, "`intervention-required` does not authorize fallback", "fallback intervention boundary")
    require(root_fallback, "independent validation", "fallback independent validation")

    # Companion boundaries and path safety.
    for name in ("ams-app-task-lane", "ams-runtime-observation"):
        extension = ROOT / "extensions" / name
        if read_safe(extension / "COMPATIBILITY").strip() != EXPECTED_VERSION:
            fail(f"companion compatibility mismatch: {name}")
        require(read_safe(extension / "agents/openai.yaml"), "allow_implicit_invocation: false", f"{name} implicit policy")
    observation_skill = read_safe(ROOT / "extensions/ams-runtime-observation/SKILL.md")
    for phrase in (
        "Resolve the absolute directory containing this active companion `SKILL.md`",
        "absolute-companion-root",
        "Never fall back to a project-relative",
    ):
        require(observation_skill, phrase, "runtime-observation helper path")
    app_skill = read_safe(ROOT / "extensions/ams-app-task-lane/SKILL.md")
    require(app_skill, "active compatible AMS core route", "app-task invocation bridge")
    require(app_skill, "must independently pass its own core setting/override and trigger", "app-task feature gate")

    # Sol Ultra is intentionally standalone and excludes the standard convergence subsystem.
    ultra = read_safe(ROOT / "SOL-ULTRA-AMS-EXTREME-ORCHESTRATION-PROMPT.md")
    require(ultra, "AMS Extreme standalone directive", "Sol Ultra boundary")
    require(ultra, "standard AMS convergence-control module is excluded", "Sol Ultra convergence exclusion")
    require(ultra, "report the exact decision required from the user", "Sol Ultra loop disposition")

    # Package-operation contracts and source hygiene.
    package_maintenance = read_safe(PACKAGE / "references/package-maintenance.md")
    for phrase in (
        "shared package/runtime lock",
        "Downgrade export and import",
        "convergence tracking/history",
    ):
        require(package_maintenance, phrase, "package maintenance")
    if not (ROOT / ".gitignore").is_file():
        fail(".gitignore missing")
    gitignore = read_safe(ROOT / ".gitignore")
    require(gitignore, "adaptive-master-subagent-orchestration/.runtime/", "runtime ignore")
    if (ROOT / "reports").exists():
        fail("generated reports directory remains in source candidate")

    bash = read_safe(ROOT / "install.sh", maximum=2 * 1024 * 1024)
    powershell = read_safe(ROOT / "install.ps1", maximum=2 * 1024 * 1024)
    for text, label in ((bash, "Bash installer"), (powershell, "PowerShell installer")):
        for phrase in (
            ".runtime.lock",
            "ams-convergence-tracking-v1",
            "ams-convergence-history-v1",
            "record_generation",
            "terminal_receipt",
        ):
            require(text, phrase, label)
    require(bash, "iconv", "Bash UTF-8 validation")

    # Every text source is strict UTF-8/LF and markdown fences are balanced.
    source_roots = [PACKAGE, ROOT / "extensions"]
    for source_root in source_roots:
        for path in sorted(source_root.rglob("*")):
            if path.is_file() and path.suffix.lower() in {".md", ".toml", ".yaml", ".yml", ".py", ".ps1"}:
                text = read_safe(path, maximum=2 * 1024 * 1024)
                if path.suffix.lower() == ".md" and text.count("```") % 2:
                    fail(f"unbalanced markdown fence: {path.relative_to(ROOT)}")

    print("PASS: AMS 4.0 package, routes, profiles, convergence state, companions, and source hygiene")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
