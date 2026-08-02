# Adaptive Master–Subagent Orchestration

**Current release: 3.09**

Adaptive Master–Subagent Orchestration (AMS) is a Codex skill that keeps **GPT-5.6 Sol Max** in charge while routing bounded project work to the lowest-cost reliable subagent model and reasoning effort.

The two core functions are:

1. **Sol Max controls orchestration.** The root owns the objective, task graph, physical spawning, logical hierarchy, routing, integration decisions, acceptance, and user communication. Workers are bounded leaves; delegated managers may request root-mediated descendants.
2. **AMS controls requested model and reasoning effort.** Every non-root dispatch uses an explicit `ams_<family>_<effort>` profile. AMS reports the requested profile after spawn without claiming that the runtime identity was independently observable.

Profiles do not grant sandbox, approval, network, writable-root, tool, or other permission overrides. Spark inherits the same platform/user/work-order permissions as every other model.

## Install

The installers fetch each required file directly from the canonical `main` repository tree through `install-manifest.txt`. They do not use GitHub Release assets or a package ZIP.

### Windows PowerShell

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install.ps1' | iex"
```

### Linux or macOS

```bash
curl -fsSL 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install.sh' | bash
```

The installer writes only:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
$CODEX_HOME/agents/ams_*.toml
```

When `CODEX_HOME` is unset, profiles use `$HOME/.codex/agents/`. The installer does **not** edit `$CODEX_HOME/config.toml`, project settings, or operating-system permissions.

For a complete source copy:

```bash
git clone https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration.git
```

See [INSTALLATION.md](INSTALLATION.md) for exact validation, profile-collision, update, repair, and uninstall behavior.

## Persistence and settings

AMS checks project settings first, then global settings only when the project file is absent:

```text
<project-root>/.codex/ams-orchestration.toml
$CODEX_HOME/ams-orchestration.toml
```

The global file is manual only. Project commands write only the current project file. If a project command creates that file while global settings are active, AMS copies the valid effective global values first and changes only the requested project setting.

Schema 2 default:

```toml
schema_version = 2
enabled = false
allow_implicit_invocation = true
intensity = "auto"
project_governance = true
spark_enabled = true
spark_available = true
spark_efforts = ["low", "medium", "high"]
profile_management = "auto"
```

Existing schema-2 files created before `project_governance` was added may omit that key. AMS resolves the omitted value as `true` and persists it during the next authorized project-settings write.

Useful commands:

```text
AMS STATUS
AMS ENABLE
AMS DISABLE
AMS MODE auto|minimal|balanced|moderate|heavy|extreme
AMS IMPLICIT on|off
AMS GOVERNANCE on|off
AMS SPARK on|off
AMS SPARK RECHECK
AMS SPARK EFFORTS low,medium,high
AMS PROFILES auto|installer
```

## Optional project governance

`project_governance = true` is the default. It adds AMS project-wide acceptance tracking, proportional independent review, continuous-delivery posture, deviation handling, and continuity through existing project-native state or a user-visible handoff.

Disable it for one project with:

```text
AMS GOVERNANCE off
```

Disabling governance does not change Sol-root control, model/reasoning routing, work orders, virtual hierarchy, root-only physical spawning, one-writer safety, or truthful completion.

## Model and effort routing

| Family | Typical work |
|---|---|
| **Spark** | Exact commands, searches, extraction, routine tests/builds, formatting, and bounded mechanics. Worker-only. |
| **Luna** | Clear, repetitive, low-risk work that is easy to verify. |
| **Terra** | Normal implementation, fixes, tests, documentation, review, and moderate investigation. |
| **Sol** | Architecture, security-sensitive work, ambiguity, difficult debugging, and expensive-to-fail decisions. |

Sol, Terra, and Luna support `low`, `medium`, `high`, `xhigh`, and `max`; Spark supports `low`, `medium`, and `high`.

After a successful spawn AMS reports, for example:

```text
semantic_reviewer started: ams_sol_xhigh
```

That is the requested profile, not proof of observed runtime identity.

## Virtual hierarchy and root boundary

- The root is the sole physical spawn authority.
- Workers never delegate.
- Delegated managers request descendants through the root and remain bounded to their work orders.
- Every non-root session has an immutable logical parent.
- One active writer is allowed per mutable surface.
- Only the root accepts project completion and communicates with the user.
- The root remains a management lane and does not take over project execution while a compliant delegated route exists.

## Intensity modes

| Mode | Posture |
|---|---|
| `minimal` | Root plus at most one active non-root session. |
| `balanced` | One small bounded direct-worker or manager team shape. |
| `auto` | Smallest useful adaptive topology. |
| `heavy` | Proactively forms useful managers and parallel lanes. |
| `extreme` | Dispatches every useful ready safe lane while remaining cost-first. |

`moderate` remains the schema-2 storage/command alias for `balanced`.

## Zergling Rush

Zergling Rush is a separate explicit-consent mode that may use stronger models, duplicate investigation, speculative preparation, and redundant validation to reduce wall-clock time. It never changes root authority, permissions, ownership, safety, or completion rules.

## Profile and installer safety

The installer deploys all 18 global profiles. A byte-identical profile is left unchanged. An exact prior official Spark profile may be upgraded to remove its former sandbox override. Any other differing, customized, marker-only, malformed, or user-authored profile is preserved and blocks replacement until the user reviews and reconciles it.

Standard uninstall removes only the skill directory and deliberately leaves settings and installed profiles for troubleshooting or reinstall.

## Requirements

- Codex with skills and custom-subagent support
- a top-level GPT-5.6 Sol Max session, or verified equivalent Sol alias at Max reasoning
- Windows PowerShell 5.1+ for the PowerShell installer
- Bash plus `curl`, `awk`, `sort`, `cmp`, `mktemp`, `wc`, `tr`, `grep`, `head`, `tail`, `od`, `find`, `dirname`, and either `sha256sum` or `shasum`
- restart or reload Codex after installation or update
