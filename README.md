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
f35aa28cad7c2691e80823e36ca276cbee8b20de067600fd8edb8f2aaf10fe4b
```

Default install location:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
```

## Start using AMS

### Use it once

Use AMS for only the current request:

```text
Use $adaptive-master-subagent-orchestration for this project.
```

### Enable it for a project

From inside the project, tell Codex:

```text
AMS ENABLE
```

Disable it later with:

```text
AMS DISABLE
```

AMS stores its settings separately for each project. A new project starts with AMS disabled unless you explicitly enable it or invoke the skill for a task.

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
AMS ENABLE
AMS DISABLE
AMS MODE auto|minimal|balanced|moderate|heavy|extreme
AMS IMPLICIT on|off
AMS SPARK on|off
AMS SPARK RECHECK
AMS SPARK EFFORTS low,medium,high
AMS PROFILES auto|installer
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
