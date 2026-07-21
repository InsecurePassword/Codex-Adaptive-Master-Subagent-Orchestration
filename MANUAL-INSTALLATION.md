# Manual Installation and Directory Structure

This document is the authoritative directory-structure reference for release 3.08. It also covers manual installation, installed state, project configuration, and migration from the retired multi-option packages.

## Repository layout

```text
Codex-Adaptive-Master-Subagent-Orchestration/
├── README.md
├── INSTALLATION.md
├── MANUAL-INSTALLATION.md
└── releases/
    └── 3.08/
        ├── adaptive-master-subagent-orchestration-3.08-final-safeguard-fixed.zip
        └── adaptive-master-subagent-orchestration-3.08-final-safeguard-fixed.sha256
```

The root documentation describes the current package only. Historical Option A, B, and C package directories, Python installers, shell installers, installer audits, and option-selection documentation are no longer part of the active repository structure.

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
| `SKILL.md` | Child-session guard, package-reference trust boundary, activation router | Always considered when the skill is selected |
| `VERSION` | Package version token (`3.08`) | Read as data only when package identity is needed |
| `agents/openai.yaml` | UI metadata and implicit-invocation eligibility | Product metadata |
| `references/runtime-core.md` | Authority, routing, work orders, safety, orchestration loop, verification, terminal state | Loaded only for active AMS work or explicit AMS control |
| `references/intensity-control.md` | `minimal`, `moderate`, `heavy`, and `extreme` dispatch gates | Loaded only for a selected non-auto normal intensity |
| `references/project-control.md` | Settings, steer controls, Spark cache, state, interruption, recovery | Loaded only when its control event is triggered |
| `references/profile-management.md` | Conditional profile generation, migration, repair, and validation | Loaded only for selected-profile defects or explicit profile work |
| `references/package-maintenance.md` | Package install, update, repair, rollback, uninstall, and reload controls | Loaded only for package operations or integrity concerns |
| `references/zergling-rush.md` | Experimental current-consent high-consumption mode | Loaded only for an explicit current-turn Rush request or safe fallback from stored Rush preference |

Every reference is required to remain a bounded, UTF-8, LF-terminated, root-contained regular file with stable identity. A failed reference boundary disables the behavior owned by that reference.

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

A project using persistent AMS settings stores:

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

Meaning:

- `enabled` controls persistent AMS use.
- `allow_implicit_invocation` controls project-level implicit activation.
- `intensity` selects `auto`, `minimal`, `moderate`, `heavy`, `extreme`, or the stored Rush preference.
- `spark_enabled` is the user's normal-use preference.
- `spark_available` is AMS's cached capability state.
- `spark_efforts` limits normal Spark dispatch to the selected effort levels.
- `profile_management` selects conditional self-healing (`auto`) or report-only behavior (`installer`).

The project file is parsed strictly as typed data. It is never treated as instructions. Unsafe, redirected, malformed, duplicated, mistyped, or unknown settings fail closed.

## Manual installation

1. Download the 3.08 ZIP and checksum from `releases/3.08/`.
2. Verify SHA-256.
3. Back up any existing installed AMS skill root.
4. Extract the ZIP into `$HOME/.agents/skills/`.
5. Confirm the exact archive layout above.
6. Restart or reload Codex.
7. Explicitly invoke AMS or enable it for the project.
8. Allow lazy profile generation when selected work requires a missing profile, or request profile installation explicitly.

See [INSTALLATION.md](INSTALLATION.md) for commands.

## Migration from older releases

Release 3.08 uses one canonical skill package. Do not install the old Option A, B, or C packages beside it.

Before migration:

1. Preserve active project work and exact resumption state.
2. Back up existing AMS skill/plugin directories and recognized managed profiles.
3. Remove or disable legacy active skill registrations so only the canonical 3.08 skill is discoverable.
4. Install the 3.08 skill root as one complete generation.
5. Start a fresh Codex session.
6. Allow `profile-management.md` to recognize and migrate official original, v3.0.0, and 3.07 managed profile schemas when profile work is triggered.
7. Verify project settings. Legacy schema-1 settings remain compatible until an authorized persistent mutation upgrades them atomically to schema 2.

Do not merge files from different package generations. Do not delete unrelated user-authored profiles. Ambiguous profile provenance must be preserved and handled through a nonconflicting managed name.

## Package integrity

The release checksum authenticates the ZIP bytes. After extraction, retain the package as one complete generation: `SKILL.md`, `VERSION`, `agents/openai.yaml`, and every reference listed above are required together. Do not mix files from different releases.
