# Adaptive Master–Subagent Orchestration

**Current release: 3.09**

Adaptive Master–Subagent Orchestration (AMS) is a Codex skill for large or complicated projects.

It keeps **GPT-5.6 Sol Max** in charge as the root manager. Sol Max owns the objective, task graph, routing, physical agent dispatch, integration decisions, validation requirements, acceptance, stoppages, and final response. It does not perform routine project execution.

The main goals are:

1. **Use the least expensive model that can do each task correctly.**
2. **Finish faster by running independent work at the same time when useful.**
3. **Scale from a single worker to a logical development-team hierarchy without depending on nested Codex threads.**

Simple work can go to Spark or Luna, ordinary development work can go to Terra, and difficult or high-risk work can go to Sol.

## What changed in 3.09

Release 3.09 replaces the old direct-child-only orchestration rule with **virtual hierarchy**:

```text
Logical topology

Root Sol Max
├── Delegated manager
│   ├── Worker
│   └── Worker
└── Direct worker
```

Codex sessions may still remain physically flat:

```text
Physical topology

Root Sol Max
├── Manager
├── Worker
├── Worker
└── Direct worker
```

The root remains the sole physical spawn authority. A delegated manager may decompose and supervise only its assigned subgraph and may request root-mediated descendants. A worker is always a leaf and never delegates.

This design does not require a permanent manager profile. Existing Sol, Terra, and Luna profiles may serve as workers or delegated managers according to their bounded work orders. Spark is worker-only.

## Install

The repository-hosted installers download the current AMS package from `main`, verify its SHA-256 checksum, validate the archive, deploy the bundled model profiles, and safely replace an older AMS installation.

### Windows PowerShell

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install.ps1' | iex"
```

### Linux or macOS with Bash

```bash
curl -fsSL 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install.sh' | bash
```

Restart or reload Codex after installation or update.

### Repository files

The repository-root distribution uses these files from `main`:

- [PowerShell installer](https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install.ps1)
- [Bash installer](https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install.sh)
- [AMS 3.09 package](https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/adaptive-master-subagent-orchestration-3.09.zip)
- [Detailed installation guide](INSTALLATION.md)
- [Complete product documentation](PRODUCT%20DOCUMENTATION.md)

The repository-root package is verified by both installer scripts with this SHA-256:

```text
4f587e93cb4cdd633f6c8e642cd8ef0841b2044fadff4f3eec61e56eea16d4a4
```

Default install location:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
```

## Start using AMS

The installed skill bootstraps itself on every top-level root project turn. Before ordinary project work it checks the project settings file first, then the optional global settings file. When the effective settings enable implicit use, AMS loads automatically in the stored mode.

### Use it once

```text
Use $adaptive-master-subagent-orchestration for this project.
```

### Project-specific persistence

From inside a trusted project:

```text
AMS STATUS
AMS ENABLE
AMS MODE auto
AMS DISABLE
```

Project commands write only:

```text
<project-root>/.codex/ams-orchestration.toml
```

`AMS ENABLE` persists `enabled = true`. A normal `AMS MODE ...` command persists the selected mode and also enables AMS. `AMS STATUS` reports the project path, global path, effective source, settings, and any activation blocker.

### Global persistence (manual only)

To supply defaults for every trusted project that has no project settings file, manually create or copy:

```text
$CODEX_HOME/ams-orchestration.toml
```

When `CODEX_HOME` is unset, use:

```text
$HOME/.codex/ams-orchestration.toml
```

Use the same schema as a project file. For persistent auto mode:

```toml
schema_version = 2
enabled = true
allow_implicit_invocation = true
intensity = "auto"
spark_enabled = true
spark_available = true
spark_efforts = ["low", "medium", "high"]
profile_management = "auto"
model_tracking = false
```

A project file overrides the global file completely, so a project can select another mode or disable AMS. Global persistence is manual: no `AMS` command creates, changes, or removes the global file. Restart or reload Codex after changing it.

## Optional model tracking and active topology

Model tracking is off by default. AMS does not load its tracking reference, create `.codex/logs`, or write CSV rows unless the effective configuration contains `model_tracking = true`.

Project controls:

```text
AMS MODELTRACKING on
AMS MODELTRACKING off
AMS MODELTRACKING status
AMS TOPOLOGY
```

`AMS MODELTRACKING on|off` changes only the project tracking setting and never enables, disables, or changes the AMS mode. `status` is read-only and displays up to the last 10 data rows from the current or newest safe log.

Each top-level root session that successfully spawns a non-root session creates one lazy CSV log:

```text
<project-root>/.codex/logs/ams-model-tracking-YYYYMMDDTHHMMSSZ.csv
```

```csv
timestamp,subagent/worker name,model level,reasoning
2026-08-01T21:04:18.337Z,semantic_reviewer,sol,high
```

The CSV records the final AMS-selected profile family and effort, not authoritative proof of the runtime model. `AMS TOPOLOGY` shows only currently open sessions. When tracking is on, active non-root nodes include model/effort annotations; when off, topology remains available without annotations.

## Intensity modes

Intensity controls the size and aggressiveness of the logical team. It does **not** lower safety, ownership, testing, or quality requirements.

| Mode | What it does |
|---|---|
| `minimal` | Strictly permits the root plus one active non-root session. Work remains serial. |
| `balanced` | Uses either up to two direct workers, or one delegated manager with up to two or three non-manager descendants. It does not mix these shapes or add another manager layer. |
| `auto` | Recommended default. Chooses the smallest useful adaptive topology. AMS imposes no fixed logical-depth, manager-count, worker-ratio, or team-shape ceiling. |
| `heavy` | Proactively forms useful managers and parallel lanes. AMS imposes no fixed logical-depth or team-shape ceiling. |
| `extreme` | Runs every useful ready safe lane while remaining cost-first. AMS imposes no fixed logical-depth or team-shape ceiling. |

`moderate` remains accepted as a backward-compatible alias for `balanced`. Schema-2 project settings continue to store the legacy value `moderate` so existing projects remain compatible.

Change the mode with:

```text
AMS MODE minimal
AMS MODE balanced
AMS MODE auto
AMS MODE heavy
AMS MODE extreme
```

Choosing a normal mode also enables AMS for that project.

## Zergling Rush

`zergling-rush` is a separate experimental mode for users who want the shortest possible completion time and accept much higher model usage.

It may use:

- more agents and logical managers;
- stronger models;
- duplicate investigations;
- extra validation;
- speculative work that may be discarded.

AMS imposes no Zergling Rush logical-depth or team-shape limit. Actual Codex capacity, finite root-recorded allocations, dependencies, one-writer ownership, safety, and useful supervision still govern.

Because Zergling Rush can consume substantially more usage, it must be requested directly for the current task. A stored preference is not current consent.

```text
Use Zergling Rush for this task.
```

## Sol Ultra with AMS Extreme

Use [SOL-ULTRA-AMS-EXTREME-ORCHESTRATION-PROMPT.md](SOL-ULTRA-AMS-EXTREME-ORCHESTRATION-PROMPT.md) when the top-level Codex root runs GPT-5.6 Sol with the `ultra` setting and every observable agent or session dispatch must remain under AMS control.

Codex `ultra` and AMS `extreme` are separate controls. `ultra` supplies the root's native multi-agent execution capacity; `extreme` tells AMS to dispatch every useful ready safe lane while preserving cost-first routing, one-writer ownership, safety, and validation. The prompt binds native Sol Ultra fan-out to the AMS task graph and root-only physical spawn gate.

For persistent Extreme mode in the current trusted project, run:

```text
AMS STATUS
AMS MODE extreme
```

`AMS MODE extreme` enables AMS and writes only `<project-root>/.codex/ams-orchestration.toml`. For a session-only override, do not run the persistence command; the prompt explicitly selects Extreme for the current objective.

Start a top-level Sol Ultra Codex session, attach or paste the complete prompt file, and issue the objective in the same turn or immediately after it. When the file is available inside the working tree, use:

```text
Use $adaptive-master-subagent-orchestration.
Read and apply SOL-ULTRA-AMS-EXTREME-ORCHESTRATION-PROMPT.md as the controlling session-level orchestration directive.
Then complete this objective: <objective>
```

The prompt does not grant Zergling Rush consent, weaken validation, or authorize overlapping writers. Every observable direct worker, delegated manager, root-mediated descendant, retry, replacement, replicated investigation, reviewer, and native Ultra child must pass through AMS before project work begins.

## How AMS chooses models

| Model family | Typical work |
|---|---|
| **Spark** | Commands, routine tests, builds, searches, extraction, and other bounded text-only mechanical work. Spark is always a leaf worker. |
| **Luna** | Clear, repetitive, low-risk work that is easy to check. |
| **Terra** | Normal coding, bug fixes, tests, documentation, reviews, and technical investigation. |
| **Sol** | Architecture, security-sensitive work, difficult debugging, ambiguous problems, and expensive-to-fail decisions. |

AMS chooses the lowest-cost model and reasoning level that should complete the task reliably. A cheaper agent's result still has to be checked before it is accepted.

## Hierarchy and control

- The root is the only physical spawn authority and the only agent that communicates with the user.
- Every non-root session has one immutable logical parent recorded in its work order.
- A delegated manager may request descendants only within its assigned scope, ownership, allowed shape, and remaining allocation.
- Managers do not independently spawn agents. The root validates each dispatch request and performs the physical spawn.
- Workers are leaves and cannot delegate.
- Authority, permissions, scope, ownership, and allocation may narrow down the chain but never expand.
- One active writer is allowed for each shared mutable surface across the entire logical tree.
- Worker completion is a leaf claim; manager completion is a validated-subgraph claim; only the root can declare project completion.
- The root changes routing, sequencing, ownership, assignments, and recovery flow instead of taking over routine execution.

## Useful project commands

```text
AMS STATUS
AMS ENABLE
AMS DISABLE
AMS MODE auto|minimal|balanced|moderate|heavy|extreme
AMS IMPLICIT on|off
AMS SPARK on|off
AMS SPARK RECHECK
AMS SPARK EFFORTS low,medium,high
AMS PROFILES auto|installer
AMS MODELTRACKING on|off|status
AMS TOPOLOGY
```

Most users only need `AMS ENABLE`, `AMS DISABLE`, and `AMS MODE`.

## Requirements

- Codex with skill and custom-subagent support
- A top-level GPT-5.6 Sol Max session, or a verified equivalent Sol alias at Max reasoning
- Windows PowerShell 5.1 or newer for the PowerShell installer
- Bash, `curl`, `unzip`, `zipinfo`, `awk`, `sort`, `cmp`, and either `sha256sum` or `shasum` for the Bash installer
- Spark access only when Spark routing is enabled and the account supports it
- A Codex restart or reload after installing or updating AMS

The installed AMS package contains Markdown, YAML, TOML, and a version file. PowerShell and Bash are not needed while AMS is running; shell tools are used only for installation and maintenance.
