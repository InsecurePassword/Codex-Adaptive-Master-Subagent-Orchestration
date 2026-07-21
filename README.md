# Adaptive Master–Subagent Orchestration

**Current release: 3.08**

Adaptive Master–Subagent Orchestration (AMS) is a Codex skill for large or complicated projects.

It keeps **GPT-5.6 Sol Max** in charge as the manager. Sol Max plans the work, assigns tasks to other agents, checks their results, and decides when the project is complete.

The main goals are:

1. **Use the least expensive model that can do each task correctly.**
2. **Finish faster by running independent work at the same time when useful.**

The master agent normally supervises instead of doing routine work itself. Simple work can go to Spark or Luna, ordinary development work can go to Terra, and difficult or high-risk work can go to Sol.

## Install

The installer scripts are attached to the GitHub release. These commands do not use files from the `main` branch.

### Windows PowerShell

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/install.ps1' | iex"
```

### Linux or macOS with Bash

```bash
curl -fsSL 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/install.sh' | bash
```

The installer:

- downloads the 3.08 skill package;
- verifies its SHA-256 checksum;
- checks the package contents before extraction;
- installs it under your user skill directory;
- replaces an older AMS installation safely;
- leaves unrelated skills and project files unchanged.

Default install location:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
```

Restart or reload Codex after installation.

### Release downloads

- [PowerShell installer](https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/install.ps1)
- [Bash installer](https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/install.sh)
- [AMS 3.08 package](https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/adaptive-master-subagent-orchestration-3.08.zip)
- [Detailed installation guide](INSTALLATION.md)
- [Manual installation and directory structure](MANUAL-INSTALLATION.md)

Pinned package SHA-256:

```text
e45eed1762ed24d1a0f671d9fb7424558694f0bef557aaca97f0cc0828d07be6
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

Intensity controls how aggressively AMS runs tasks at the same time. It does **not** lower safety, testing, or quality requirements.

| Mode | What it does |
|---|---|
| `auto` | Recommended default. Sol Max decides how many agents are useful. |
| `minimal` | Uses one worker at a time. Best when reducing usage matters more than speed. |
| `moderate` | Runs a few clearly independent tasks at the same time. |
| `heavy` | Uses more parallel workers when that should noticeably speed up the project. |
| `extreme` | Uses every useful independent workstream it can safely run, while still choosing the cheapest suitable model for each task. |

Change the mode with:

```text
AMS MODE auto
AMS MODE minimal
AMS MODE moderate
AMS MODE heavy
AMS MODE extreme
```

Choosing a mode also enables AMS for that project.

## Zergling Rush

`zergling-rush` is a separate experimental mode for users who want the shortest possible completion time and accept much higher model usage.

It may use:

- more agents;
- stronger models;
- duplicate investigations;
- extra validation;
- speculative work that may be discarded.

Because it can consume substantially more usage, it must be requested directly for the current task. Saving it in project settings is not enough to activate it automatically.

Example:

```text
Use Zergling Rush for this task.
```

Use a normal intensity mode when cost matters.

## How AMS chooses models

| Model family | Typical work |
|---|---|
| **Spark** | Downloads, commands, routine tests, builds, searches, extraction, and other simple mechanical work |
| **Luna** | Clear, repetitive, low-risk work that is easy to check |
| **Terra** | Normal coding, bug fixes, tests, documentation, reviews, and technical investigation |
| **Sol** | Architecture, security-sensitive work, difficult debugging, ambiguous problems, and expensive-to-fail decisions |

AMS chooses the lowest-cost model and reasoning level that should complete the task reliably. A cheaper agent's result still has to be checked before it is accepted.

## Useful project commands

```text
AMS ENABLE
AMS DISABLE
AMS MODE auto|minimal|moderate|heavy|extreme
AMS SPARK on|off
AMS SPARK RECHECK
AMS SPARK EFFORTS low,medium,high
AMS PROFILES auto|installer
```

Most users only need `AMS ENABLE`, `AMS DISABLE`, and `AMS MODE`.

## Safety and control

- Sol Max remains in charge of the full project.
- Subagents cannot create more agents.
- Each subagent receives a limited task.
- Two agents are not allowed to edit the same shared area at the same time.
- A subagent saying it is finished does not make the project complete.
- Sol Max checks the evidence and decides whether the result is acceptable.
- Failed work is normally corrected or reassigned to another subagent instead of being repeated unchanged.
- AMS does not stop at an internal checkpoint while required work remains.

## Requirements

- Codex with skill and custom-subagent support
- A top-level GPT-5.6 Sol Max session
- Windows PowerShell 5.1 or newer for `install.ps1`
- Bash, `curl`, `unzip`, and `zipinfo` for `install.sh`
- Spark access only when you want Spark routing and your account supports it
- A Codex restart or reload after installing or updating AMS

The installed AMS skill contains only Markdown, YAML, and a version file. Python, PowerShell, and Bash are not needed while AMS is running; the scripts are used only for installation and updates.
