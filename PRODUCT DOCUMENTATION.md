# Product Documentation

**Product:** Adaptive Master–Subagent Orchestration (AMS)  
**Current release:** 3.08

This document explains what AMS does, how to install it, how to use every supported control, how it chooses agents, how it protects project work, and how to update, repair, recover, or uninstall it.

## Contents

1. [What AMS does](#what-ams-does)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Starting and stopping AMS](#starting-and-stopping-ams)
5. [Project settings](#project-settings)
6. [Command reference](#command-reference)
7. [Intensity modes](#intensity-modes)
8. [Zergling Rush](#zergling-rush)
9. [How AMS chooses models](#how-ams-chooses-models)
10. [How AMS manages work](#how-ams-manages-work)
11. [Spark controls](#spark-controls)
12. [Agent profile management](#agent-profile-management)
13. [Validation, review, and completion](#validation-review-and-completion)
14. [Failure handling](#failure-handling)
15. [Pausing and recovery](#pausing-and-recovery)
16. [Package updates and repair](#package-updates-and-repair)
17. [Uninstall](#uninstall)
18. [Directory structure](#directory-structure)
19. [Troubleshooting](#troubleshooting)

## What AMS does

AMS is a Codex skill for projects that benefit from more than one agent.

It keeps **GPT-5.6 Sol Max** in charge as the manager. Sol Max:

- understands the full objective;
- breaks the work into safe tasks;
- chooses the model and reasoning level for each task;
- decides which tasks may run at the same time;
- prevents two agents from editing the same shared area;
- checks the returned evidence;
- combines accepted work;
- decides whether the project is complete or blocked.

The two main goals are:

1. **Use the least expensive model that can complete each task correctly.**
2. **Finish faster by running independent tasks at the same time when useful.**

The master normally supervises instead of performing routine project work itself. It may directly perform project work only after delegated diagnosis cannot identify the failure, no child route can continue, and a small direct action is required to unblock the objective.

### Direct children only

All AMS workers are direct children of Sol Max. A child cannot create another child, change AMS settings, change the installed AMS package, manage AMS profiles, or decide that the overall project is complete.

### AMS is project-specific

Persistent AMS settings are stored separately in each project. Enabling AMS in one project does not enable it in another project.

## Requirements

- Codex with skill and custom-subagent support
- A top-level GPT-5.6 Sol Max session, or a verified equivalent Sol alias at Max reasoning
- Windows PowerShell 5.1 or newer for the PowerShell installer
- Bash, `curl`, `unzip`, `zipinfo`, and either `sha256sum` or `shasum` for the Bash installer
- Spark access only when Spark routing is enabled and the account supports it
- A Codex restart or reload after installing, updating, repairing, or uninstalling AMS

The installed skill contains Markdown, YAML, and a version file only. Python, PowerShell, and Bash are not required while AMS is running; they are used only for installation or maintenance.

## Installation

The installer scripts are attached to the `ReleaseZip` GitHub release. The commands below do not read installer scripts from the `main` branch.

### Windows PowerShell

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/install.ps1' | iex"
```

### Linux or macOS with Bash

```bash
curl -fsSL 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/install.sh' | bash
```

Both installers:

1. download `adaptive-master-subagent-orchestration-3.08.zip` from the release;
2. verify the pinned SHA-256 checksum;
3. require the exact expected package contents;
4. reject unsafe, redirected, linked, encrypted, unreadable, or oversized archives;
5. prevent two installers from changing the same installation simultaneously;
6. extract into a temporary staging directory;
7. back up an existing AMS skill directory;
8. install the new package;
9. restore the previous installation if replacement fails;
10. preserve unrelated skills, project settings, recovery state, and generated profiles.

Default installation location:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
```

Pinned package SHA-256:

```text
e45eed1762ed24d1a0f671d9fb7424558694f0bef557aaca97f0cc0828d07be6
```

Restart or reload Codex after installation.

### Manual installation

1. Download the release package:

   ```text
   https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/adaptive-master-subagent-orchestration-3.08.zip
   ```

2. Verify its SHA-256 against the value above.
3. Back up an existing AMS skill directory.
4. Extract the archive into `$HOME/.agents/skills/`.
5. Confirm that the resulting directory is:

   ```text
   $HOME/.agents/skills/adaptive-master-subagent-orchestration/
   ```

6. Restart or reload Codex.

## Starting and stopping AMS

### Use AMS for one request

Explicit invocation enables AMS only for the current request. It does not permanently enable AMS for the project.

```text
Use $adaptive-master-subagent-orchestration for this project.
```

A similar clear request to use the Adaptive Master–Subagent architecture is also valid.

### Enable AMS for the project

```text
AMS ENABLE
```

This sets `enabled = true` in the project configuration.

### Disable AMS for the project

```text
AMS DISABLE
```

When disabling during active work, AMS:

- stops starting new AMS tasks;
- allows safe active work to reach a useful stopping point;
- collects available results;
- records the exact next action when recovery state is needed;
- closes remaining workers safely;
- sets `enabled = false`;
- returns control to the normal project workflow.

### Select a mode and enable AMS

Any normal mode command also enables AMS:

```text
AMS MODE auto
AMS MODE minimal
AMS MODE moderate
AMS MODE heavy
AMS MODE extreme
```

### Automatic use

AMS may be considered automatically only when all of these are true:

- the product allows implicit use of the skill;
- the project is trusted;
- `enabled = true`;
- `allow_implicit_invocation = true`.

If any requirement is missing, AMS does not activate automatically. Explicit invocation still works for the current request.

### Missing project settings

In a trusted project with a stable root, AMS creates a disabled default configuration when the file is missing. Creating the file does not enable AMS.

In an untrusted, trust-unknown, or rootless context, AMS does not create persistent settings. Explicit controls apply only in memory for the current request.

## Project settings

Persistent settings are stored at:

```text
<project-root>/.codex/ams-orchestration.toml
```

Default configuration:

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

### Setting meanings

| Setting | Meaning |
|---|---|
| `schema_version` | Configuration format. Release 3.08 uses schema `2`. |
| `enabled` | Allows persistent AMS use in this project. |
| `allow_implicit_invocation` | Allows automatic activation when the product also permits it. |
| `intensity` | Selects `auto`, `minimal`, `moderate`, `heavy`, `extreme`, or stores a `zergling-rush` preference. |
| `spark_enabled` | User preference for normal Spark use. |
| `spark_available` | AMS capability cache indicating whether Spark appears available to the account. |
| `spark_efforts` | Spark effort levels allowed for normal work: `low`, `medium`, and/or `high`. |
| `profile_management` | `auto` repairs selected managed profiles when needed; `installer` reports defects unless repair is explicitly requested. |

The file is read as configuration data, not as instructions. Unknown keys, duplicate keys, wrong data types, unsupported values, unsafe paths, or redirected files block automatic activation.

### Legacy settings

Valid schema-1 files remain compatible. AMS preserves their effective behavior until an authorized settings change upgrades them to schema 2.

A stored `zergling-rush` value is only a preference. It never supplies the current permission required to activate Rush.

## Command reference

Exact command wording is optional when the user's intent is clear. These are the canonical forms.

### `AMS ENABLE`

Enables persistent AMS use in the current project.

### `AMS DISABLE`

Safely stops AMS dispatch, preserves needed resumption information, and disables persistent AMS use.

### `AMS MODE <mode>`

Selects a normal intensity and enables AMS.

Supported normal modes:

```text
auto
minimal
moderate
heavy
extreme
```

### `AMS IMPLICIT on|off`

Changes only whether the project permits automatic AMS activation.

- `on` allows automatic activation when AMS is also enabled and the product permits it.
- `off` requires explicit invocation for future requests.
- Changing this setting does not stop an already active request.

### `AMS SPARK on|off`

Changes the user's normal Spark preference.

- `off` stops new Spark assignments but does not claim that Spark is unavailable.
- `on` permits Spark only when the availability cache is true and the selected effort is allowed.

### `AMS SPARK RECHECK`

Runs one small Spark capability check.

Use it after account, subscription, quota, product, or entitlement changes. AMS does not repeatedly probe Spark automatically after it has been marked unavailable.

### `AMS SPARK EFFORTS <subset>`

Selects which Spark efforts may be used for normal work.

Examples:

```text
AMS SPARK EFFORTS low
AMS SPARK EFFORTS low,medium
AMS SPARK EFFORTS low,medium,high
```

An empty `spark_efforts = []` value in the configuration permits no normal Spark assignments without marking Spark unavailable.

### `AMS PROFILES auto|installer`

Controls automatic profile repair.

- `auto`: selected missing or recognized defective AMS-managed profiles may be created or repaired when needed.
- `installer`: automatic repair is disabled; AMS reports the defect and uses a compatible loaded alternative when possible.

An explicit request to install or repair profiles is allowed in either mode.

### Zergling Rush commands

Current-request activation:

```text
Use Zergling Rush for this task.
AMS ZERGLING RUSH
AMS MODE ZERGLING-RUSH
```

Save the preference:

```text
AMS MODE ZERGLING-RUSH PERSIST
```

Saving the preference does not remove the requirement to confirm Rush again in a future request or session.

## Intensity modes

Intensity changes how readily AMS uses safe parallel work. It does not reduce model quality, validation, safety, ownership rules, or Sol Max's authority.

### `auto`

Recommended default.

Sol Max decides whether the project needs zero, one, or many workers. There is no required agent count and no bias toward maximum activity.

### `minimal`

Uses at most one active child at a time.

Best when reducing usage and coordination matters more than speed. Related work is grouped into larger sequential tasks.

### `moderate`

Uses parallel workers only when the benefit is clear, such as:

- independent tasks;
- specialist work;
- isolated investigation;
- required independent review;
- meaningful critical-path improvement.

### `heavy`

Runs all meaningful ready independent work unless dependencies, file conflicts, tight coupling, or low value make serial work safer or cheaper.

Implementation, testing, research, integration, and review may use separate workers when useful.

### `extreme`

Runs every useful ready independent workstream that can be executed safely.

It may use finer task splitting, parallel investigations, independent replication, and redundant validation. There is no skill-defined agent-count limit; actual Codex capacity and project constraints still apply.

Unlike Rush, `extreme` still chooses the cheapest reliable model for each task and does not authorize pointless work.

## Zergling Rush

Zergling Rush is an experimental high-consumption mode for minimizing wall-clock time instead of usage.

It may use:

- more simultaneous workers;
- stronger models than normal cost-first routing would choose;
- competing approaches to the same problem;
- speculative preparation before dependencies finish;
- duplicate investigations;
- redundant testing and review;
- work that may later be discarded.

### Consent requirement

Rush must be requested clearly in the current user turn every time it activates.

These do **not** count as consent:

- a repository setting;
- an old saved preference;
- asking AMS to be faster;
- selecting `auto` or another normal intensity.

AMS announces that Rush may consume substantially more usage before starting Rush work.

### What Rush does not change

Rush does not permit:

- child agents creating more agents;
- two workers editing the same shared area;
- unauthorized destructive actions;
- skipped safety checks;
- skipped validation;
- unsupported completion claims;
- children changing AMS settings, profiles, or package files;
- routine project work by the master.

### Leaving Rush

Changing mode or disabling AMS stops new Rush-only speculative or duplicate work. Safe active tasks may finish to a useful boundary before AMS applies the new mode.

## How AMS chooses models

Normal modes use the lowest-cost reliable model family and reasoning level.

### Model families

| Family | Typical use |
|---|---|
| **Spark** | Exact commands, downloads, extraction, package deployment, routine tests and builds, formatting, searches, and other bounded text-only work requiring little judgment |
| **Luna** | Clear, repetitive, low-risk work that is inexpensive to retry and easy to verify |
| **Terra** | Normal implementation, bug fixes, tests, documentation, code review, and moderate technical investigation |
| **Sol** | Architecture, security-sensitive work, ambiguous problems, cross-component work, difficult debugging, and expensive-to-fail decisions |

### Reasoning efforts

| Effort | Typical use |
|---|---|
| `low` | Straightforward and tightly scoped work |
| `medium` | Ordinary multi-step work |
| `high` | Multiple dependencies, edge cases, sources, or tradeoffs |
| `xhigh` | Difficult investigation, design, or validation |
| `max` | The hardest bounded work requiring exhaustive checking |

Sol, Terra, and Luna may use Low through Max. Spark uses Low, Medium, or High only.

File count alone does not justify a more expensive model. AMS considers risk, ambiguity, dependencies, novelty, verification difficulty, repetition, coupling, and investigation depth.

### Spark-first mechanical work

When Spark is enabled, available, and allowed at the needed effort, AMS prefers Spark for suitable mechanical work before using Luna, Terra, Sol, or the master.

Spark is not used for:

- architecture decisions;
- threat modeling;
- security judgment;
- broad or ambiguous implementation;
- visual input;
- final project acceptance;
- conclusions requiring heavy interpretation.

A stronger agent may inspect or interpret evidence collected by Spark.

## How AMS manages work

### Task graph

Sol Max tracks:

- project deliverables;
- acceptance criteria;
- dependencies;
- critical-path work;
- ready, active, completed, blocked, and replaced tasks;
- file and surface ownership;
- required testing and review;
- risks and blockers;
- expected model profiles.

### Work orders

Every child receives a bounded work order containing the objective, scope, excluded scope, dependencies, permissions, write ownership, required actions, success criteria, validation, and return requirements.

A child owns only the assigned task. It must report out-of-scope needs to Sol Max instead of expanding its assignment.

### Returned results

Children return structured evidence including:

- completion status;
- requested and observed execution identity when available;
- summary;
- changed files and artifacts;
- validation performed;
- deviations;
- unresolved issues;
- assumptions;
- risks;
- recommended next action.

A child's `complete` status is a claim for Sol Max to verify. It is not project completion.

### File ownership

AMS allows one active writer for each shared mutable area.

It prefers:

- separate files;
- separate directories;
- isolated workspaces;
- serialized changes for manifests, lock files, schemas, interfaces, migrations, indexes, and authoritative state.

Read-only reviewers do not edit. A high-risk implementer is not the only reviewer of its work.

### Git operations

A child may perform a Git or history operation only when its work order explicitly authorizes the exact action. AMS settings, AMS package files, AMS-managed profiles, and AMS recovery records remain master-owned and are excluded from child Git work.

## Spark controls

Spark uses two separate settings:

- `spark_enabled`: the user's preference;
- `spark_available`: AMS's cached capability result.

Normal Spark work requires both to be true and the effort to be present in `spark_efforts`.

### When AMS marks Spark unavailable

AMS sets `spark_available = false` only after strong evidence that the account, entitlement, subscription, quota, product, or Spark family cannot be used beyond one failed attempt.

These do not prove family-wide unavailability:

- a malformed or missing profile;
- one unsupported effort;
- a model-effort mismatch;
- a task-specific failure;
- a temporary transport or capacity error;
- a timeout;
- a generic rate limit.

Those failures are handled for the current task without disabling Spark for the project.

### Rechecking Spark

`AMS SPARK RECHECK` authorizes one smallest safe capability probe. It does not loop. Success sets availability true; authoritative family/account unavailability sets it false; temporary or task-specific failure leaves the cached value unchanged.

## Agent profile management

AMS uses custom agent profiles named:

```text
ams_sol_<effort>
ams_terra_<effort>
ams_luna_<effort>
ams_spark_<effort>
```

Sol, Terra, and Luna support:

```text
low, medium, high, xhigh, max
```

Spark supports:

```text
low, medium, high
```

### Where profiles are stored

Preferred location:

```text
$CODEX_HOME/agents/
```

Project-local profiles may be used only when global profiles are unavailable, deliberate project isolation is needed, or the project provides an authoritative override.

### Automatic profile management

With:

```toml
profile_management = "auto"
```

AMS checks only profiles selected for actual work. It may create a missing managed profile or repair a recognized defective AMS-managed profile.

It does not rewrite unrelated or ambiguous user-created profiles. When a name conflicts, AMS preserves the existing file and uses a compatible loaded profile or a nonconflicting managed name.

### Installer mode

With:

```toml
profile_management = "installer"
```

AMS does not automatically repair profiles. It reports the problem and uses a truthful compatible loaded alternative when possible.

### Explicit install or full repair

A clear request such as:

```text
Install or repair all AMS agent profiles.
```

authorizes AMS to reconcile the verified supported profile matrix. Unsupported model or effort combinations are not invented.

### Profile migration

Release 3.08 recognizes and can safely migrate proven AMS-managed profiles from:

- the original architecture;
- v3.0.0;
- v3.07;
- the current schema.

Managed legacy files are backed up before upgrade. Ambiguous or user-authored files are preserved.

A fresh Codex session may be required before newly created profiles become discoverable.

## Validation, review, and completion

Sol Max accepts work by judging evidence, reconciling conflicting findings, and requesting additional checks when needed.

Children perform executable validation such as:

- tests;
- builds;
- linting;
- formatting checks;
- type checks;
- security checks;
- behavioral reproduction;
- integration work.

The master normally does not run those operations directly.

### Independent review

AMS normally uses a separate read-only reviewer for high-risk:

- implementation;
- architecture;
- security work;
- broad refactoring;
- difficult defects.

Review is proportional and does not repeat recursively without new evidence.

### Complete versus blocked

AMS reports **complete** only when:

- mandatory acceptance criteria are satisfied;
- required tasks are completed or explicitly superseded;
- returned work is verified and integrated;
- required validation passed;
- relevant final scope, regression, architecture, security, and risk review is finished;
- project state and documentation agree;
- all child results are collected and workers are closed.

AMS reports **blocked** when mandatory progress cannot continue because of a real external blocker. It records the blocker, exact resumption action, and resumption condition instead of claiming completion.

A phase, commit, checkpoint, clean workspace, test pass, empty worker list, or handoff is not project completion when required work remains.

## Failure handling

When delegated work fails, AMS first determines why.

If the reason is clear, AMS keeps the correction delegated by:

- fixing the work order;
- retrying with a changed approach;
- reassigning the task;
- increasing reasoning effort;
- moving from Spark or Luna to Terra or Sol when the task requires it.

AMS does not repeat an unchanged failed setup and expect a different result.

The master may directly perform only the smallest required project action when:

1. delegated evidence and additional delegated diagnosis cannot determine the cause;
2. no viable child route can continue;
3. the action is required to unblock or complete the objective.

The fallback reason, evidence, scope, and result are recorded. Project execution returns to children once the cause is understood.

## Pausing and recovery

AMS continues without asking for another prompt when the next action is known, authorized, safe, and useful.

It pauses when:

- user intent is materially unclear;
- the next action is destructive, irreversible, externally visible, or outside authority;
- repeated drift suggests the plan may be wrong;
- materially different valid required paths need user preference.

Before pausing, AMS preserves:

- the last completed action;
- supporting evidence;
- the exact decision required;
- the safest next action;
- the condition needed to resume.

### Recovery process

When resuming, AMS:

1. reads the handoff, original objective, criteria, settings, and saved state;
2. inspects the live project, repository, branch, worktree, user changes, commits, workspaces, artifacts, tests, and validation;
3. treats earlier reports as evidence, not proof;
4. rebuilds the task graph;
5. classifies work as verified, awaiting integration, unverified, partial, ready, blocked, or superseded;
6. resumes from the earliest unfinished or unverified dependency;
7. uses current project settings rather than recreating an old worker roster.

Use an explicit request such as:

```text
Use $adaptive-master-subagent-orchestration to resume this project from the handoff and live repository state.
```

## Package updates and repair

### Update

Rerun the release-hosted installer for the operating system.

PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/install.ps1' | iex"
```

Bash:

```bash
curl -fsSL 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/install.sh' | bash
```

Before changing package instructions, finish or safely pause active AMS work. Restart or reload Codex afterward.

### Package repair

Rerunning the installer replaces the complete skill directory from the verified release package and restores the old directory if replacement fails.

You may also explicitly ask AMS to repair its installed package. Package maintenance requires explicit authority, stops active workers safely, validates the complete replacement, keeps the current session on the old instructions for recovery and reporting, and requires a fresh session before normal work continues.

### Package integrity checks

AMS treats installed skill files as protected. It rejects package files that are redirected, unstable, unexpectedly linked, malformed, mixed across releases, or inconsistent with the package identity.

## Uninstall

The release installers install and update only. They do not provide an uninstall switch.

### Standard uninstall

Standard uninstall removes only the installed AMS skill directory. It preserves:

- per-project AMS settings;
- project recovery state;
- generated AMS agent profiles;
- unrelated skills and profiles.

Stop or safely pause active AMS work before uninstalling.

#### Windows PowerShell

```powershell
$SkillRoot = Join-Path $HOME ".agents\skills\adaptive-master-subagent-orchestration"

if (Test-Path -LiteralPath $SkillRoot) {
    $Item = Get-Item -LiteralPath $SkillRoot -Force
    if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        throw "Refusing to remove a redirected skill path: $SkillRoot"
    }
    if (-not $Item.PSIsContainer) {
        throw "The AMS skill path is not a directory: $SkillRoot"
    }
    Remove-Item -LiteralPath $SkillRoot -Recurse -Force
}
```

#### Bash

```bash
skill_root="$HOME/.agents/skills/adaptive-master-subagent-orchestration"

if [ -L "$skill_root" ]; then
  printf 'Refusing to remove a redirected skill path: %s\n' "$skill_root" >&2
  exit 1
elif [ -e "$skill_root" ] && [ ! -d "$skill_root" ]; then
  printf 'The AMS skill path is not a directory: %s\n' "$skill_root" >&2
  exit 1
elif [ -d "$skill_root" ]; then
  rm -rf -- "$skill_root"
fi
```

Restart or reload Codex after removal.

### Ask AMS to uninstall itself

While the skill is still loaded, an explicit request may use the package-maintenance rules:

```text
Uninstall the Adaptive Master–Subagent Orchestration skill. Preserve project settings, recovery state, and generated profiles.
```

AMS stops active work safely, removes only the verified installed package root, reports remaining components, and requires a reload. Manual removal remains the simplest option.

### Optional full cleanup

Project settings and profiles are intentionally preserved by standard uninstall. Remove them only when you explicitly want to erase them.

#### Remove project settings

From the specific project:

```text
<project-root>/.codex/ams-orchestration.toml
```

Do not delete the whole `.codex` directory because it may contain unrelated project configuration.

#### Remove generated profiles

Generated profiles are normally under:

```text
$CODEX_HOME/agents/
```

Delete only files proven AMS-managed by the exact marker:

```text
# managed-by: adaptive-master-subagent-orchestration
```

Do not remove every `ams_*.toml` file blindly. AMS preserves ambiguous or user-authored profiles even when their filenames look similar.

#### Remove recovery state

AMS uses an existing project-native state system when possible. If it created a separate recovery ledger, remove only the exact path recorded in the project handoff or AMS report. Do not guess or delete unrelated project state.

## Directory structure

### Repository

```text
Codex-Adaptive-Master-Subagent-Orchestration/
├── README.md
├── INSTALLATION.md
├── PRODUCT DOCUMENTATION.md
├── install.ps1
└── install.sh
```

The installable package and installer scripts are attached to the `ReleaseZip` GitHub release rather than duplicated under the repository branch.

### Release assets

```text
ReleaseZip/
├── adaptive-master-subagent-orchestration-3.08.zip
├── install.ps1
└── install.sh
```

### Release package

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

### Installed skill

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

### Generated agent profiles

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

The exact generated set depends on models and efforts supported by the current Codex runtime.

### Project settings

```text
<project-root>/
└── .codex/
    └── ams-orchestration.toml
```

### Temporary installer files

During installation or update, the installers may create a lock plus hidden staging and backup paths under the skill parent directory. Successful completion removes them. A stale lock may remain after a forced termination and should be removed only after confirming that no installer is running.

## Troubleshooting

### AMS does not activate automatically

Check:

```toml
enabled = true
allow_implicit_invocation = true
```

Also confirm that the project is trusted and Codex permits implicit skill use. Explicit invocation works independently of persistent automatic activation.

### A new project has AMS disabled

This is expected. Missing settings are initialized with `enabled = false`. Use:

```text
AMS ENABLE
```

or select a mode.

### Spark is not being used

Check:

```toml
spark_enabled = true
spark_available = true
spark_efforts = ["low", "medium", "high"]
```

Then run:

```text
AMS SPARK RECHECK
```

when account capability may have changed.

### A profile is missing or invalid

With `profile_management = "auto"`, explicitly invoke AMS for work that needs the profile or request:

```text
Install or repair AMS agent profiles.
```

Restart Codex if newly created profiles are not immediately visible.

### The installer reports a checksum mismatch

Do not bypass the check. Confirm that the release asset and installer belong to the same release. Remove any `AMS_RELEASE_URL` or `AMS_EXPECTED_SHA256` test override and run the release-hosted installer again.

### The installer reports an active or stale lock

Confirm that no AMS installer process is running. The lock is normally located under:

```text
$HOME/.agents/skills/.adaptive-master-subagent-orchestration.install.lock
```

Remove it only after confirming that no installation or update is active.

### The skill changed but Codex still shows old behavior

Restart or reload Codex. AMS never loads changed package instructions into the same active session after package mutation.

### A project is blocked instead of complete

Read the reported blocker, exact next action, and resumption condition. Resolve the external requirement, then explicitly ask AMS to resume from the live project state and handoff.
