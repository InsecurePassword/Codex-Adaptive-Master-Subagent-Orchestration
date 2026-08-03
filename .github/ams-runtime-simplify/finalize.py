from pathlib import Path
import hashlib

root = Path.cwd()
pkg = root / "adaptive-master-subagent-orchestration"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text.rstrip("\n") + "\n", encoding="utf-8", newline="\n")


def replace_one(path: Path, old: str, new: str, label: str) -> None:
    text = read(path)
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    write(path, text.replace(old, new, 1))


skill = pkg / "SKILL.md"
replace_one(
    skill,
    """## Reference trust boundary

Resolve packaged references beneath the installed skill root. Before loading one as instructions, require a regular non-redirected file with stable path/object identity through the bounded read, no path escape or unexpected links, size at most 256 KiB, and UTF-8 without BOM/NUL/CR with final LF. Reject only a file that fails those per-read safety checks. A successful package update creates no special verification or generation-tracking state: do not compare pre/post package contents, compute update-triggered hashes, re-verify, re-audit, reactivate, pause, or request user action solely because an update occurred. Continue ordinary AMS operation and load the currently installed reference normally only when that behavior is later needed.

""",
    "",
    "remove SKILL reference validation",
)
replace_one(
    skill,
    """`runtime-core.md` lazily routes `intensity-control.md`, `hierarchy-control.md`, `profile-management.md`, `project-governance.md`, `root-execution-fallback.md`, and `zergling-rush.md`. Load `project-governance.md` only when effective `project_governance = true`; load `root-execution-fallback.md` only when mandatory progress would otherwise stop, no viable delegated route remains, and effective `root_execution_fallback = true`. Read each selected reference completely. A required unreadable reference fails closed only for the behavior it owns.""",
    """`runtime-core.md` lazily routes `intensity-control.md`, `hierarchy-control.md`, `profile-management.md`, `project-governance.md`, `root-execution-fallback.md`, and `zergling-rush.md`. Load `project-governance.md` only when effective `project_governance = true`; load `root-execution-fallback.md` only when mandatory progress would otherwise stop, no viable delegated route remains, and effective `root_execution_fallback = true`. Read routed references only when needed. An update triggers no additional AMS action.""",
    "simplify SKILL routing",
)

maintenance = pkg / "references/package-maintenance.md"
write(
    maintenance,
    """# AMS package maintenance

Read only for an explicit install, update, repair, rollback, uninstall, or package-integrity request. Do not load this reference merely because package files changed.

## Authority

Require direct user authority before package mutation or uninstall. Prevent concurrent package writes and pause active dispatch only as needed for the mutation. Preserve project state and never create an AMS-specific recovery file.

## Install, update, repair, and rollback

The standard installers read the canonical repository `main` manifest and declared files. During the requested mutation, they verify the download set, version, file lengths and hashes, profile provenance, and transactional replacement. They never edit `$CODEX_HOME/config.toml` or grant sandbox, approval, network, writable-root, or tool permissions.

Stage the complete candidate, back up replaceable files, commit transactionally, and restore the prior state on failure. Replace an existing profile only when it is byte-identical to the current asset or an exact installer-recognized prior official file; otherwise preserve it and report the conflict.

After a successful install, update, repair, or rollback, resume ordinary AMS operation. Perform no follow-up package check unless the user explicitly requests one.

## Uninstall

Standard uninstall removes only the verified AMS skill directory. Preserve project/global settings, installed profiles, and unrelated files unless the user explicitly authorizes separate proven cleanup.
""",
)

replace_one(
    root / "README.md",
    "A successful install or update never triggers AMS re-verification, re-audit, reactivation, a project pause, or a user-action gate. AMS performs no pre/post package comparison or update-triggered hash check after installation; ordinary runtime continues and reads currently installed references only when they are later needed. Package-integrity verification occurs only when directly requested.",
    "Installation and updates end when the installer finishes. AMS performs no follow-up package check unless the user explicitly requests one.",
    "README update behavior",
)

installation = root / "INSTALLATION.md"
replace_one(
    installation,
    "Installation does not trigger AMS re-verification, reactivation, or a project pause. Ordinary runtime reads installed references only when they are later needed.",
    "Installation ends when the installer completes; AMS performs no automatic follow-up.",
    "INSTALLATION opening behavior",
)
replace_one(
    installation,
    "During an explicitly requested update, AMS quiesces package writers and the installer performs the required manifest and hash validation. After success, do not compare pre/post package state, run post-update hashes, re-verify, re-audit, reactivate, pause the project, or request user action solely because the package changed. Resume ordinary AMS operation; references are read normally only when later needed. A user may separately request package-integrity verification.",
    "After the installer completes, resume normal work. AMS performs no follow-up package check unless the user explicitly requests one.",
    "INSTALLATION update behavior",
)

replace_one(
    root / "PRODUCT DOCUMENTATION.md",
    "Package mutation requires direct user authority. The installer validates the package during the requested mutation; success does not trigger a second AMS verification, audit, activation check, project halt, or user-action gate. AMS performs no pre/post package comparison or post-update hash pass. Ordinary runtime continues and reads the currently installed references only when their behavior is later needed. Package-integrity verification occurs only on direct user request. The standard installer uses only canonical `main`, validates the exact 31-file set, and never edits general Codex configuration or permissions.",
    "Package mutation requires direct user authority. The installer validates the requested mutation before replacing files. After completion, AMS performs no follow-up package check unless the user explicitly requests one. The standard installer uses only canonical `main`, validates the exact 31-file set, and never edits general Codex configuration or permissions.",
    "PRODUCT update behavior",
)

replace_one(
    root / "install.ps1",
    '    Write-Host "Installation complete. AMS performs no automatic post-update re-verification or project pause."',
    '    Write-Host "Installation complete."',
    "PowerShell completion output",
)
replace_one(
    root / "install.sh",
    "printf 'Installation complete. AMS performs no automatic post-update re-verification or project pause.\\n'",
    "printf 'Installation complete.\\n'",
    "Bash completion output",
)

profile_names = [
    *(f"ams_sol_{e}.toml" for e in ("low", "medium", "high", "xhigh", "max")),
    *(f"ams_terra_{e}.toml" for e in ("low", "medium", "high", "xhigh", "max")),
    *(f"ams_luna_{e}.toml" for e in ("low", "medium", "high", "xhigh", "max")),
    *(f"ams_spark_{e}.toml" for e in ("low", "medium", "high")),
]
required = {
    "SKILL.md",
    "VERSION",
    "agents/openai.yaml",
    "references/configuration-maintenance.md",
    "references/hierarchy-control.md",
    "references/intensity-control.md",
    "references/package-maintenance.md",
    "references/profile-management.md",
    "references/project-control.md",
    "references/project-governance.md",
    "references/root-execution-fallback.md",
    "references/runtime-core.md",
    "references/zergling-rush.md",
    *(f"assets/agent-profiles/{name}" for name in profile_names),
}
observed = {p.relative_to(pkg).as_posix() for p in pkg.rglob("*") if p.is_file()}
if observed != required or len(required) != 31:
    raise SystemExit(
        f"package inventory mismatch: missing={sorted(required-observed)} extra={sorted(observed-required)}"
    )

lines = ["ams-install-manifest-v1", "version\t3.09"]
for rel in sorted(required):
    data = (pkg / rel).read_bytes()
    lines.append(
        f"{hashlib.sha256(data).hexdigest()}\t{len(data)}\tadaptive-master-subagent-orchestration/{rel}"
    )
write(root / "install-manifest.txt", "\n".join(lines))

skill_text = read(skill)
for forbidden in (
    "Reference trust boundary",
    "stable path/object identity",
    "package-generation",
    "pre/post package",
    "update-triggered hash",
    "re-verify",
    "re-audit",
):
    if forbidden in skill_text:
        raise SystemExit(f"unwanted SKILL runtime validation remains: {forbidden}")
if "An update triggers no additional AMS action." not in skill_text:
    raise SystemExit("minimal update rule missing from SKILL")
if (
    "Perform no follow-up package check unless the user explicitly requests one."
    not in read(maintenance)
):
    raise SystemExit("package-maintenance follow-up rule missing")

print("MANIFEST_FILES=31")
print(f"SKILL_BYTES={skill.stat().st_size}")
print(f"PACKAGE_MAINTENANCE_BYTES={maintenance.stat().st_size}")
