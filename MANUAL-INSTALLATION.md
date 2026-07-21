# Manual Installation and Directory Structure

This is the authoritative directory-structure reference for release 3.08. It covers repository files, release archive contents, installed state, project configuration, deployment helpers, and migration from retired package layouts.

## Repository layout

```text
Codex-Adaptive-Master-Subagent-Orchestration/
├── README.md
├── INSTALLATION.md
├── MANUAL-INSTALLATION.md
├── install.ps1
├── install.sh
└── releases/
    └── 3.08/
        ├── adaptive-master-subagent-orchestration-3.08-final-safeguard-fixed.zip
        └── adaptive-master-subagent-orchestration-3.08-final-safeguard-fixed.sha256
```

The root scripts download the GitHub release asset named `adaptive-master-subagent-orchestration-3.08.zip`; the repository copy and checksum record retain the safeguard-audit artifact name. Both are expected to contain identical ZIP bytes with SHA-256:

```text
e45eed1762ed24d1a0f671d9fb7424558694f0bef557aaca97f0cc0828d07be6
```

Historical Option A, B, and C directories, Python installers, menu selectors, and installer-audit documents are not part of the active release structure.

## Deployment helper roles

| Path | Role |
|---|---|
| `install.ps1` | PowerShell 5.1+ release downloader, verifier, safe extractor, and skill-root replacer |
| `install.sh` | Bash release downloader, verifier, archive-safety checker, and skill-root replacer |

Both helpers preserve unrelated skills and use the same pinned release URL, checksum, required-file list, destination, staging behavior, and rollback intent.

## Release archive layout

The 3.08 ZIP expands to:

```text
adaptive-master-subagent-orchestration/
├── SKILL.md
├── VERSION
├── agents/
│   └── openai.yaml
└── references/
    ├── intensity-control.md
    ├── package-maintenance.md
    ├── profile-management.md
    ├── project-control.md
    ├── runtime-core.md
    └── zergling-rush.md
```

### Runtime roles

| Path | Role | Normal load behavior |
|---|---|---|
| `SKILL.md` | Child-session guard, package-reference trust boundary, activation router | Always considered when selected |
| `VERSION` | Package version token (`3.08`) | Data only when package identity is needed |
| `agents/openai.yaml` | UI metadata and implicit-invocation eligibility | Product metadata |
| `references/runtime-core.md` | Authority, routing, work orders, safety, orchestration loop, verification, terminal state | Active AMS work or explicit control |
| `references/intensity-control.md` | `minimal`, `moderate`, `heavy`, and `extreme` dispatch gates | Selected non-auto normal intensity |
| `references/project-control.md` | Settings, steer controls, Spark cache, state, interruption, recovery | Relevant control event |
| `references/profile-management.md` | Conditional profile generation, migration, repair, validation | Selected-profile defect or explicit profile work |
| `references/package-maintenance.md` | Package install, update, repair, rollback, uninstall, reload | Package operation or integrity concern |
| `references/zergling-rush.md` | Current-consent experimental high-consumption mode | Explicit current-turn Rush request or safe stored-preference fallback |

Every reference must remain a bounded, UTF-8, LF-terminated, root-contained regular file with stable identity. A failed boundary disables the behavior owned by that reference.

## Installed layout

Default user installation:

```text
$HOME/.agents/skills/
└── adaptive-master-subagent-orchestration/
    ├── SKILL.md
    ├── VERSION
    ├── agents/
    │   └── openai.yaml
    └── references/
        ├── intensity-control.md
        ├── package-maintenance.md
        ├── profile-management.md
        ├── project-control.md
        ├── runtime-core.md
        └── zergling-rush.md
```

The installers may temporarily create hidden staging and backup directories under `$HOME/.agents/skills/`. Successful completion removes them.

Managed custom-agent profiles, when generated, normally live under:

```text
$CODEX_HOME/agents/
├── ams_sol_low.toml
├── ams_sol_medium.toml
├── ams_sol_high.toml
├── ams_sol_xhigh.toml
├── ams_sol_max.toml
├── ams_terra_low.toml
├── ams_terra_medium.toml
├── ams_terra_high.toml
├── ams_terra_xhigh.toml
├── ams_terra_max.toml
├── ams_luna_low.toml
├── ams_luna_medium.toml
├── ams_luna_high.toml
├── ams_luna_xhigh.toml
├── ams_luna_max.toml
├── ams_spark_low.toml
├── ams_spark_medium.toml
└── ams_spark_high.toml
```

Project-local profiles may be used only when global profiles are unavailable, deliberate isolation is required, or the project provides authoritative overrides.

## Project layout

Persistent AMS settings use:

```text
<project-root>/
└── .codex/
    └── ams-orchestration.toml
```

Exact disabled schema-2 defaults:

```toml
schema_version = 2
enabled = false
allow_implicit_invocation = true
intensity = "auto"
spark_enabled = true
spark_available = true
spark_efforts = ["low", "medium", "high"]
profile_management = "auto"
```

The file is parsed strictly as typed data and never as instructions. Unsafe, redirected, malformed, duplicated, mistyped, or unknown settings fail closed.

## Automated installation

### Windows PowerShell

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://raw.githubusercontent.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/main/install.ps1' | iex"
```

### Bash

```bash
curl -fsSL 'https://raw.githubusercontent.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/main/install.sh' | bash
```

See [INSTALLATION.md](INSTALLATION.md) for authentication and environment overrides.

## Manual installation

1. Download `adaptive-master-subagent-orchestration-3.08.zip` from the `ReleaseZip` GitHub release.
2. Verify the pinned SHA-256.
3. Back up any existing installed AMS skill root.
4. Extract the ZIP into `$HOME/.agents/skills/`.
5. Confirm the exact archive layout above.
6. Restart or reload Codex.
7. Explicitly invoke AMS or enable it for the project.
8. Allow lazy profile generation when selected work requires a missing profile, or request profile work explicitly.

## Migration from older releases

Release 3.08 uses one canonical skill package. Do not install old Option A, B, or C packages beside it.

Before migration:

1. Preserve active project work and exact resumption state.
2. Back up legacy AMS skill/plugin directories and recognized managed profiles.
3. Remove or disable legacy active registrations so only the canonical 3.08 skill is discoverable.
4. Install the complete 3.08 skill root.
5. Start a fresh Codex session.
6. Allow `profile-management.md` to recognize and migrate official original, v3.0.0, and 3.07 managed profile schemas when profile work is triggered.
7. Verify project settings. Legacy schema-1 settings remain compatible until an authorized mutation upgrades them atomically to schema 2.

Do not merge files from different package generations. Do not delete unrelated user-authored profiles. Ambiguous provenance must be preserved and handled through a nonconflicting managed name.

## Package integrity

The pinned checksum authenticates the ZIP bytes. After extraction, keep the package as one complete generation: `SKILL.md`, `VERSION`, `agents/openai.yaml`, and every listed reference are required together.
