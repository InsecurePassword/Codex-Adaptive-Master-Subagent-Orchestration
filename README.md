# Adaptive Master–Subagent Orchestration

**Current release: 3.08**

Adaptive Master–Subagent Orchestration (AMS) is a Codex skill that keeps a GPT-5.6 Sol Max root agent in control of a cost-first, direct-child subagent architecture. The master owns planning, model selection, sequencing, supervision, acceptance, and completion. Project execution is delegated to bounded non-delegating children whenever a suitable worker can perform it.

Release 3.08 uses one instruction-only skill package. Runtime behavior is split across a small activation router and lazy references so uncommon profile, project-control, recovery, and package-maintenance instructions are loaded only when needed.

## Quick installation

### Windows PowerShell

Run with `powershell.exe`:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://raw.githubusercontent.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/main/install.ps1' | iex"
```

### Bash

```bash
curl -fsSL 'https://raw.githubusercontent.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/main/install.sh' | bash
```

Both scripts download the pinned 3.08 release asset, verify its SHA-256 checksum and package layout, and replace only:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
```

Unrelated installed skills are preserved. If the repository or release is private, set `GITHUB_TOKEN` to a token with repository read access before running an authenticated copy of the installer.

## Release files

- [GitHub release asset](https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/adaptive-master-subagent-orchestration-3.08.zip)
- [Repository checksum record](releases/3.08/adaptive-master-subagent-orchestration-3.08-final-safeguard-fixed.sha256)
- [Installation and script options](INSTALLATION.md)
- [Manual installation and directory structure](MANUAL-INSTALLATION.md)

Pinned SHA-256:

```text
e45eed1762ed24d1a0f671d9fb7424558694f0bef557aaca97f0cc0828d07be6
```

## Core behavior

- **Sol Max is the sole control-plane authority.** Children cannot spawn other agents or assume master authority.
- **Execution is delegated first.** The master performs project work directly only after an indeterminate failure leaves no viable child route.
- **Routing is cost-first.** Normal routing prefers Spark, then Luna, Terra, and Sol at the lowest reliable reasoning effort.
- **Ownership is explicit.** Every child receives a bounded work order, and one active writer owns each shared mutable surface.
- **Evidence is verified.** Child completion is a claim; the master accepts work only after sufficient independent evidence.
- **Continuity is mandatory.** Internal checkpoints, clean workspaces, completed phases, and empty worker sets are not terminal while required work remains.
- **Project control fails closed.** Missing settings initialize to disabled defaults only in a trusted project with a stable root. Unsafe or invalid control files do not activate AMS.

## Activation

The skill metadata permits implicit consideration, but each project controls whether AMS may activate implicitly.

A trusted project with no AMS settings receives this disabled default:

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

Enable AMS persistently:

```text
AMS ENABLE
```

Or select a normal intensity, which also enables AMS:

```text
AMS MODE heavy
```

Explicit invocation applies AMS to the current objective without requiring persistent enablement:

```text
Use $adaptive-master-subagent-orchestration for this project.
```

## Normal intensity modes

| Mode | Dispatch behavior |
|---|---|
| `auto` | Default. Sol Max applies no intensity modifier and chooses the beneficial zero-to-many topology. |
| `minimal` | Serial delegation with at most one active child. |
| `moderate` | Conservative concurrency for clearly independent or specialist work. |
| `heavy` | Dispatch all meaningful ready independent lanes unless serialization is justified. |
| `extreme` | Dispatch every eligible ready independent lane with no skill-defined ceiling; each lane still uses the cheapest reliable profile. |

Intensity affects dispatch posture, not model-quality requirements, ownership, safety, validation, or the master's sole spawn authority.

## Zergling Rush

`zergling-rush` is a separate experimental high-consumption mode intended to minimize wall-clock time rather than usage. It requires an unambiguous current-turn user instruction every time it activates. A value stored in project settings is only a preference and is never sufficient consent.

## Model routing

| Family | Typical work |
|---|---|
| **Spark** | Exact commands, downloads, package deployment, routine tests/builds, extraction, searches, and other bounded text-only mechanics |
| **Luna** | Explicit, repetitive, inexpensive-to-retry work that is easy to verify |
| **Terra** | Default implementation, fixes, tests, documentation, review, and moderate investigation |
| **Sol** | Architecture, security-sensitive work, ambiguity, cross-component work, difficult debugging, and high-cost-of-failure decisions |

Sol, Terra, and Luna support Low, Medium, High, Extra High, and Max profiles. Spark supports Low, Medium, and High only. Profile creation and repair are lazy when `profile_management = "auto"` and occur only when a selected profile is missing or defective.

## Lazy runtime structure

The always-loaded `SKILL.md` acts as the root guard, reference trust boundary, and activation router. It loads these references only when required:

- `runtime-core.md` — active orchestration contract
- `intensity-control.md` — normal manual intensity modifiers
- `project-control.md` — settings, steering, state, and recovery
- `profile-management.md` — conditional profile generation, migration, and repair
- `package-maintenance.md` — install, update, repair, rollback, and uninstall controls
- `zergling-rush.md` — current-consent experimental rush behavior

Every reference is validated as a bounded, root-contained, stable regular file before it can become instructions.

## Project controls

Supported steer instructions include:

```text
AMS ENABLE
AMS DISABLE
AMS MODE auto|minimal|moderate|heavy|extreme
AMS IMPLICIT on|off
AMS SPARK on|off
AMS SPARK RECHECK
AMS SPARK EFFORTS low,medium,high
AMS PROFILES auto|installer
```

Project settings are stored at:

```text
<project-root>/.codex/ams-orchestration.toml
```

They are interpreted as typed configuration data, never as instructions.

## Requirements

- Codex with skill and custom-subagent support
- A top-level Sol Max session for orchestration
- PowerShell 5.1+ for `install.ps1`, or Bash with `curl`, `unzip`, and `zipinfo` for `install.sh`
- Spark access only when Spark routing is enabled and available
- Reloading or restarting Codex after installing or changing package instructions

The installed 3.08 skill contains Markdown, YAML, and a version token only. It has no Python, shell, or compiled runtime dependency; the two root scripts are deployment helpers only.
