# Product Documentation

**Product:** Adaptive Master–Subagent Orchestration (AMS)  
**Current release:** 3.09

This document describes every supported AMS control, the 3.09 virtual-hierarchy model, model and profile routing, installation and maintenance, recovery, completion rules, and uninstall behavior.

## Contents

1. [What AMS does](#what-ams-does)
2. [What changed in 3.09](#what-changed-in-309)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Starting and stopping AMS](#starting-and-stopping-ams)
6. [Project settings](#project-settings)
7. [Command reference](#command-reference)
8. [Intensity modes](#intensity-modes)
9. [Virtual hierarchy](#virtual-hierarchy)
10. [Zergling Rush](#zergling-rush)
11. [Model and effort routing](#model-and-effort-routing)
12. [How AMS manages work](#how-ams-manages-work)
13. [Spark controls](#spark-controls)
14. [Agent profile management](#agent-profile-management)
15. [Validation and completion](#validation-and-completion)
16. [Failure handling](#failure-handling)
17. [Pausing and recovery](#pausing-and-recovery)
18. [Package updates and repair](#package-updates-and-repair)
19. [Uninstall](#uninstall)
20. [Directory structure](#directory-structure)
21. [Troubleshooting](#troubleshooting)

## What AMS does

AMS is a Codex skill for projects that benefit from coordinated specialist agents.

It keeps **GPT-5.6 Sol Max**, or a verified equivalent Sol alias at Max reasoning, in charge as the root manager. The root:

- owns the complete user objective;
- maintains the global task graph;
- chooses the logical team structure;
- remains the sole physical spawn authority;
- chooses the model and reasoning level for each assignment;
- controls sequencing, concurrency, ownership, retries, cancellation, and reassignment;
- makes integration decisions;
- evaluates returned evidence and validation;
- decides whether the project is complete, blocked, or requires a user decision;
- communicates with the user.

The root does **not** perform routine project execution. Implementation, repository inspection, testing, builds, integration work, review, and recovery inspection remain delegated to bounded non-root sessions.

The main goals are:

1. **Use the least expensive model that can complete each task correctly.**
2. **Finish faster by running independent work at the same time when useful.**
3. **Support development-team hierarchy without requiring physically nested Codex threads.**

AMS is project-specific. Persistent settings for one project do not enable AMS in another project.

## What changed in 3.09

Release 3.09 replaces the old direct-child-only behavior with **root-mediated virtual hierarchy**.

A logical team may look like:

```text
Root Sol Max
├── Delegated manager A
│   ├── Worker A1
│   └── Worker A2
├── Delegated manager B
│   └── Worker B1
└── Direct worker C
```

The physical Codex topology may remain flat:

```text
Root Sol Max
├── Manager A
├── Worker A1
├── Worker A2
├── Manager B
├── Worker B1
└── Worker C
```

The root remains the only agent that physically spawns sessions. A delegated manager may request descendants, supervise its assigned subgraph, reconcile evidence, and request corrections. It cannot independently spawn agents, expand its authority, communicate with the user, or declare project completion.

Release 3.09 also:

- adds `references/hierarchy-control.md`;
- makes `balanced` the user-facing name for the previous `moderate` compatibility mode;
- keeps `moderate` as a backward-compatible command and schema-2 storage token;
- removes routine root execution fallback;
- keeps workers as non-delegating leaves;
- keeps Spark worker-only;
- uses existing Sol, Terra, and Luna profiles for either worker or delegated-manager roles through bounded work orders;
- adds hierarchy lineage, custody, allocation, replay, replacement, and recovery rules;
- upgrades managed profiles to role-neutral bounded-session schema 3 with Codex V2 dispatch safeguards.

## Requirements

- Codex with skill and custom-subagent support
- A top-level GPT-5.6 Sol Max session, or a verified equivalent Sol alias at Max reasoning
- Windows PowerShell 5.1 or newer for the PowerShell installer
- Bash, `curl`, `unzip`, `zipinfo`, `awk`, `sort`, `cmp`, and either `sha256sum` or `shasum` for the Bash installer
- Spark access only when Spark routing is enabled and the account supports it
- A Codex restart or reload after installing, updating, repairing, or uninstalling AMS

The installed skill contains Markdown, YAML, TOML agent profiles, and a version file. Shell tools are used for installation and maintenance, not while AMS is orchestrating project work.

## Installation

### Recommended one-line installation

Windows PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install.ps1' | iex"
```

Linux or macOS:

```bash
curl -fsSL 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install.sh' | bash
```

Restart or reload Codex afterward.

### Repository distribution

AMS 3.09 is distributed directly from the repository root on the `main` branch. Installation does not depend on GitHub Release assets.

```text
Codex-Adaptive-Master-Subagent-Orchestration/
├── adaptive-master-subagent-orchestration-3.09.zip
├── install.ps1
└── install.sh
```

Package URL:

```text
https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/adaptive-master-subagent-orchestration-3.09.zip
```

Package SHA-256:

```text
f35aa28cad7c2691e80823e36ca276cbee8b20de067600fd8edb8f2aaf10fe4b
```

Default skill location:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
```

Default profile location:

```text
$CODEX_HOME/agents/
```

When `CODEX_HOME` is unset, the profile location is `$HOME/.codex/agents/`.

The installers verify the checksum, exact package inventory, archive integrity, file-size limits, symbolic-link safety, managed-profile markers, and `VERSION = 3.09`. They transactionally install the skill and complete 18-profile matrix while preserving unrelated skills, project settings, recovery state, and user-authored profiles.

See [INSTALLATION.md](INSTALLATION.md) for manual verification, environment overrides, update, repair, and uninstall commands.

## Starting and stopping AMS

### Use AMS for one request

Explicit invocation enables AMS only for the current request:

```text
Use $adaptive-master-subagent-orchestration for this project.
```

A similarly clear request to use the Adaptive Master–Subagent architecture is also valid.

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

- stops starting new AMS work;
- lets safe productive work reach an atomic or useful boundary;
- collects and reconciles available evidence;
- records the exact next action when recovery state is needed;
- closes sessions that no longer fit;
- sets `enabled = false`;
- returns control to the normal project workflow.

### Select a mode and enable AMS

Any normal mode command also enables AMS:

```text
AMS MODE minimal
AMS MODE balanced
AMS MODE auto
AMS MODE heavy
AMS MODE extreme
```

`AMS MODE moderate` remains accepted as an alias for `balanced`.

### Automatic use

AMS may be considered automatically only when all of these are true:

- the product allows implicit skill use;
- the project is trusted;
- `enabled = true`;
- `allow_implicit_invocation = true`.

If any requirement is missing, AMS does not activate automatically. Explicit invocation still works for the current request.

### Missing project settings

In a trusted project with a stable root, AMS creates a disabled default configuration when the file is missing. Creating the file never enables AMS.

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

| Setting | Meaning |
|---|---|
| `schema_version` | Project configuration format. Release 3.09 continues to use schema `2`. |
| `enabled` | Allows persistent AMS use in this project. |
| `allow_implicit_invocation` | Allows automatic activation when the product also permits it. |
| `intensity` | Stores `auto`, `minimal`, `moderate`, `heavy`, `extreme`, or a `zergling-rush` preference. Runtime input `balanced` maps to stored `moderate`. |
| `spark_enabled` | User preference for normal Spark use. |
| `spark_available` | Cached indication that Spark appears available to the account. |
| `spark_efforts` | Spark effort levels allowed for normal work: `low`, `medium`, and/or `high`. |
| `profile_management` | `auto` repairs selected managed profiles when needed; `installer` reports defects unless repair is explicitly requested. |

Settings are read as data, not instructions. Unknown keys, duplicate keys, wrong data types, unsupported schemas, invalid TOML, extra tables, unsafe paths, or redirected files block automatic activation.

Valid schema-1 project settings remain readable under their documented meanings and upgrade only during an authorized settings write.

For schema 2:

- `balanced` is the runtime and reporting name;
- `moderate` is the persisted compatibility token;
- either command selects the same behavior.

A stored `zergling-rush` value is only a preference. It never supplies the current-turn consent required to activate Rush.

## Command reference

Clear equivalent wording is valid. These are the canonical forms.

### `AMS ENABLE`

Enables persistent AMS use in the current project.

### `AMS DISABLE`

Safely stops new AMS dispatch, preserves required resumption information, closes remaining sessions, and disables persistent AMS use.

### `AMS MODE <mode>`

Selects a normal intensity and enables AMS.

Supported input:

```text
auto
minimal
balanced
moderate
heavy
extreme
```

`moderate` is a compatibility alias for `balanced`.

### `AMS IMPLICIT on|off`

Changes whether the project permits automatic AMS activation.

- `on` allows automatic activation when AMS is enabled and the product permits it.
- `off` requires explicit invocation for future requests.
- Changing this setting does not automatically stop a currently active request.

### `AMS SPARK on|off`

Changes the user's normal Spark preference.

- `off` stops new Spark assignments but does not claim that Spark is unavailable.
- `on` permits Spark only when the availability cache is true and the selected effort is allowed.

### `AMS SPARK RECHECK`

Runs one smallest safe Spark capability probe. Success sets `spark_available = true`; authoritative family/account unavailability sets it false; temporary or task-specific failure leaves the cached value unchanged.

### `AMS SPARK EFFORTS <subset>`

Selects which Spark efforts may be used for normal work:

```text
AMS SPARK EFFORTS low
AMS SPARK EFFORTS low,medium
AMS SPARK EFFORTS low,medium,high
```

An empty `spark_efforts = []` value permits no normal Spark assignment without marking Spark unavailable.

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

Saving the preference does not remove the requirement to confirm Rush in a future request or session.

## Intensity modes

Intensity changes useful team formation, not task quality, safety, ownership, validation, model requirements, or root authority.

Logical reporting depth is separate from physical Codex session topology. The root may physically spawn every session while AMS records manager-worker relationships.

### `minimal`

Maintains at most one active non-root session, including probes, managers, workers, integrators, reviewers, and observers.

The active session may be one direct worker or one delegated manager performing bounded work. If another session is needed, AMS first collects and closes the active session at a useful boundary. This preserves strict root-plus-one execution.

### `balanced`

Uses one of these shapes for each active wave:

```text
Root + up to two direct non-manager sessions
```

or:

```text
Root + one logical manager + up to three active non-manager descendants
```

The manager shape normally uses two or three descendants. AMS does not mix the two shapes or add another manager layer in `balanced`. Probes, implementers, testers, integrators, reviewers, and observers consume worker slots. Smaller shapes are valid; AMS does not create unnecessary agents.

`moderate` selects this exact behavior.

### `auto`

Recommended default. AMS selects the smallest effective adaptive topology from the current task graph. It may use direct workers, managers, or manager-worker chains when useful.

AMS defines no fixed logical depth, manager count, worker ratio, or team-shape ceiling in `auto`. Runtime capacity, dependencies, ownership, finite allocations, safety, cost, and coordination value govern.

### `heavy`

Proactively forms useful managers and parallel lanes when they materially improve speed, isolation, context control, or review.

AMS defines no fixed logical depth, manager count, worker ratio, or agent ceiling. It avoids speculative or duplicate work without clear value.

### `extreme`

Dispatches every useful ready safe lane, including deliberate high-value replication and independent validation.

AMS defines no fixed logical depth, team shape, or agent ceiling. `extreme` remains cost-first and rejects zero-value work.

### Mode changes

When a mode changes, AMS:

1. stops new dispatch inconsistent with the new posture;
2. lets safe active work reach a useful boundary;
3. collects evidence;
4. cancels only unsafe or now-valueless work;
5. preserves existing lineage;
6. issues new IDs for any required reparenting or replacement;
7. updates ownership and continues under the new mode.

Changing intensity never grants destructive authority, overlapping writers, weaker validation, unsupported models, or project-completion authority to a non-root agent.

## Virtual hierarchy

### Physical and logical topology

All sessions may remain physical children of the root. Logical hierarchy is recorded through work-order lineage.

The root owns:

- the user objective;
- global task graph and topology;
- physical dispatch;
- global routing and sequencing;
- ownership and allocation records;
- integration decisions;
- acceptance and completion;
- user communication.

Every non-root session has exactly one immutable logical parent.

### Roles and authority

Valid role/authority pairs are:

```text
worker / none
delegated-manager / request
```

A worker:

- performs bounded assigned work;
- is a leaf;
- never delegates;
- reports through its logical parent.

A delegated manager:

- owns only its assigned subgraph;
- may perform bounded work assigned directly to it;
- may decompose its subgraph;
- may request root-mediated descendants;
- consolidates descendant evidence;
- requests correction or replacement when needed;
- reports a validated-subgraph claim to its logical parent.

A delegated manager cannot:

- independently spawn a session;
- expand scope, permissions, ownership, authority, or allocation;
- change AMS settings, profiles, package files, or recovery ledgers;
- communicate with the user;
- accept the complete project;
- declare root completion.

Spark is always `worker / none`.

### Root-mediated dispatch

A manager returns a structured dispatch request containing:

- root objective and unique request ID;
- parent work-order ID;
- requested role and capability profile;
- objective and scope;
- requested ownership;
- dependencies and success criteria;
- requested descendant allocation and delegable scope when the descendant is another manager.

The root validates:

- request-ID uniqueness and replay safety;
- lineage;
- scope and ownership;
- dependencies;
- remaining allocation;
- selected intensity and allowed shape;
- runtime capacity;
- profile suitability;
- safety and expected value.

The root may accept, narrow, reroute, delay, flatten, or reject the request. The root assigns the descendant work-order ID and records lineage, ownership, and allocation before physical spawn.

### Authority and allocation

Authority, permissions, scope, ownership, and allocation may narrow down the chain but never expand.

Each accepted descendant consumes or partitions its parent's finite allocation. A child manager receives only an unallocated remainder. Allocation constrains active work rather than imposing a logical-depth limit.

### Lineage, replay, and replacement

- Every non-root order has one immutable logical parent.
- Exact request or result replays reuse the recorded decision.
- Conflicting reuse of an ID is a deviation.
- A replacement receives a new work-order ID.
- Reparenting closes or supersedes the old order and issues a new order; lineage is never rewritten in place.
- Late results from closed or superseded orders remain evidence only until explicitly reconciled.
- Ownership and allocation are released only after session closure and proof that no live writer remains.

### Result custody

Worker results normally flow through their logical parent. The root relays physical results to the manager without accepting them on the manager's behalf.

A manager must collect, reconcile, and disclose descendant evidence before claiming its subgraph complete. Uncollected, conflicting, inaccessible, or orphaned work cannot support completion.

If a manager becomes unavailable, the root preserves evidence and either resumes the manager or issues a new superseding manager order with explicit custody transfer. A live descendant that needs a new supervisor is closed or superseded and reissued under a new identity and logical parent.

### Completion levels

Completion is hierarchical:

- worker completion is a leaf claim;
- manager completion is a validated-subgraph claim;
- only root completion is project completion.

A local block affects one session. A chain block affects one manager subgraph after authorized reroutes are exhausted. A project block exists only when no compliant route can make mandatory progress or a genuine user decision is required.

### Ownership safety

AMS permits one active writer per shared mutable surface across the entire logical tree. A manager may subdivide only its assigned surface and cannot overlap active writers.

Circular, orphaned, or rewritten lineage; authority or allocation amplification; unmanaged recursion; duplicated allocation; bypassed logical-parent review; or a management layer without real supervisory value is a deviation.

## Zergling Rush

Zergling Rush is an experimental high-consumption mode for minimizing wall-clock time instead of usage.

It may use:

- more simultaneous workers and managers;
- stronger models than normal cost-first routing would choose;
- competing approaches;
- speculative preparation;
- duplicate investigations;
- redundant testing and review;
- work that may later be discarded.

AMS defines no Rush logical-depth, manager-count, worker-ratio, or team-shape limit. The root may keep all sessions physically flat while recording any useful logical hierarchy.

Actual runtime capacity, root-recorded finite allocations, dependencies, one-writer ownership, safety, and coherent supervision still govern. A deeper management layer must add real supervisory or context value; Rush does not authorize recursive make-work.

Rush must be requested clearly in the current user turn every time it activates. A repository setting, old saved preference, vague request to go faster, or normal intensity selection is not consent.

Rush does not permit independent spawning by a manager or worker, worker delegation, authority amplification, overlapping writers, unauthorized destructive actions, skipped safety or validation, unsupported completion claims, non-root AMS control changes, or routine project execution by the root.

## Model and effort routing

Normal modes use the lowest-cost reliable model family and reasoning level.

### Model families

| Family | Typical use |
|---|---|
| **Spark** | Exact commands, downloads, extraction, routine tests and builds, formatting, searches, and bounded text-only mechanical work. Spark is always a leaf worker. |
| **Luna** | Clear, repetitive, low-risk work that is inexpensive to retry and easy to verify. |
| **Terra** | Normal implementation, bug fixes, tests, documentation, code review, and moderate technical investigation. |
| **Sol** | Architecture, security-sensitive work, ambiguous problems, cross-component work, difficult debugging, and expensive-to-fail decisions. |

### Reasoning efforts

| Effort | Typical use |
|---|---|
| `low` | Straightforward and tightly scoped work. |
| `medium` | Ordinary multi-step work. |
| `high` | Multiple dependencies, edge cases, sources, or tradeoffs. |
| `xhigh` | Difficult investigation, design, or validation. |
| `max` | The hardest bounded work requiring exhaustive checking. |

Sol, Terra, and Luna may use Low through Max. Spark uses Low, Medium, or High only.

File count alone does not justify a more expensive route. AMS considers risk, ambiguity, dependencies, novelty, verification difficulty, repetition, coupling, and investigation depth.

There is no permanent manager model family. A delegated manager uses the same Sol/Terra/Luna profile matrix as other sessions. The root chooses a family and effort according to the manager's bounded work, ambiguity, risk, and supervisory burden.

If no compatible manager-capable profile is available, AMS flattens or reassigns the subgraph. It never uses Spark or a worker-only profile as a manager.

## How AMS manages work

### Task graph

The root tracks:

- project deliverables and acceptance criteria;
- dependencies and critical path;
- ready, active, completed, blocked, replaced, and superseded work;
- logical lineage and physical session identity when observable;
- delegated and delegable scope;
- ownership and remaining descendant allocation;
- required testing and review;
- risks and blockers;
- expected execution profiles;
- evidence custody and acceptance status.

### Work orders

Every non-root session receives a bounded work order containing:

- stable work-order ID;
- root objective;
- immutable logical parent;
- role and matching delegation authority;
- capability profile;
- objective and scope;
- excluded scope;
- dependencies;
- permissions and tools;
- write ownership;
- required actions;
- success criteria;
- validation requirements;
- allowed deviations;
- return requirements.

A session owns only its assigned work. Out-of-scope needs return through the logical parent instead of expanding the assignment.

### Returned results

Sessions return structured evidence including:

- completion status;
- requested and observed execution identity when available;
- summary;
- changed files and artifacts;
- validation performed;
- deviations;
- unresolved issues;
- assumptions;
- risks;
- recommended parent action.

Managers also identify descendant orders, reconciled evidence, outstanding descendants, custody state, and the recommended root action for their subgraph.

A session's `complete` status is a claim for its parent to evaluate. It is never automatic project completion.

### Git operations

A non-root session may perform a Git or history operation only when its work order explicitly authorizes the exact action. AMS settings, package files, managed profiles, global orchestration state, and recovery records remain root-owned and are excluded from project-agent Git operations unless the user explicitly makes a safely separated control artifact part of the project.

## Spark controls

Spark uses two separate settings:

- `spark_enabled`: the user's preference;
- `spark_available`: AMS's cached capability result.

Normal Spark work requires both to be true and the selected effort to appear in `spark_efforts`.

Spark is always a leaf worker. A Spark order claiming delegated-manager authority is invalid and must be rejected or rerouted.

AMS sets `spark_available = false` only after strong evidence that the account, entitlement, subscription, quota, product, or Spark family is unavailable beyond one task attempt.

These do not prove family-wide unavailability:

- a malformed or missing profile;
- one unsupported effort;
- a model-effort mismatch;
- a task-specific failure;
- a temporary transport or capacity error;
- a timeout;
- a generic rate limit.

Those failures are handled for the current route without disabling Spark for the project.

`AMS SPARK RECHECK` authorizes one smallest safe capability probe. Under `minimal`, the probe consumes the single non-root session slot.

## Agent profile management

The package includes the complete canonical profile matrix under:

```text
adaptive-master-subagent-orchestration/assets/agent-profiles/
```

The installer deploys all 18 profiles to `$CODEX_HOME/agents/`, or `$HOME/.codex/agents/` when `CODEX_HOME` is unset:

```text
ams_<sol|terra|luna>_<low|medium|high|xhigh|max>
ams_spark_<low|medium|high>
```

The packaged model defaults are `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, and `gpt-5.3-codex-spark`. Runtime availability is still verified before routing; an unavailable family or effort does not authorize silent rewriting of the canonical package asset.

Every managed file begins with:

```text
# managed-by: adaptive-master-subagent-orchestration
# profile-schema: 3
```

Each profile includes its exact discoverable role name, model, reasoning effort, bounded non-root developer instructions, and Codex V2 guidance overrides. Explicit AMS custom-role dispatch uses `fork_turns = "none"` so the root supplies the compact work order directly instead of forwarding root-only orchestration context.

Sol, Terra, and Luna profiles are role-neutral: a work order temporarily assigns `worker / none` or `delegated-manager / request`. Spark remains `worker / none` only. No permanent manager-profile family exists.

During installation:

- byte-identical profiles remain unchanged;
- a differing file is replaced only when its exact managed marker proves AMS ownership;
- unrecognized or user-authored collisions fail closed;
- skill and profile changes roll back together on failure.

After installation, `profile_management = "auto"` permits selected missing or recognized defective AMS profiles to be restored from the exact bundled asset. `profile_management = "installer"` disables automatic repair but still allows an explicit repair request. Ambiguous files are preserved.

A fresh Codex session may be required before newly installed or repaired profiles become discoverable.

## Validation and completion

The root accepts work by judging evidence, reconciling conflicting findings, and requesting additional delegated checks when needed.

Non-root sessions perform executable validation such as:

- tests;
- builds;
- linting;
- formatting checks;
- type checks;
- security checks;
- behavioral reproduction;
- integration work.

The root evaluates returned evidence rather than running routine project validation itself.

AMS normally uses a separate read-only reviewer for high-risk implementation, architecture, security work, broad refactoring, and difficult defects. Review is proportional and does not repeat recursively without new evidence.

AMS reports **complete** only when:

- mandatory acceptance criteria are satisfied;
- required tasks are completed or explicitly superseded;
- every required subgraph has reconciled evidence;
- returned work is verified and accepted;
- required integration and validation passed;
- relevant final scope, regression, architecture, security, and risk review is finished;
- project state and documentation agree;
- all required results are collected;
- no unresolved live writer or descendant remains;
- non-root sessions are closed or deliberately preserved with an explicit continuation contract.

AMS reports **blocked** only when mandatory progress cannot continue because of a genuine external blocker or required user decision. It records the blocker, exact resumption action, and resumption condition instead of claiming completion.

A phase, commit, checkpoint, clean workspace, test pass, empty worker list, manager completion, or handoff is not project completion when required work remains.

## Failure handling

When delegated work fails, AMS determines whether the problem is local, chain-wide, or project-wide.

If the cause is clear, AMS keeps correction delegated by:

- repairing the work order;
- changing the approach;
- reassigning or replacing the session;
- increasing reasoning effort;
- moving Spark or Luna work to Terra or Sol when the task requires it;
- flattening a manager subgraph when supervision no longer adds value;
- creating or changing a manager layer when it materially improves control.

AMS does not repeat an unchanged failed setup and expect a different result.

If the cause is unclear, the root delegates bounded diagnosis. The root changes routing, sequencing, ownership, allocation, assignments, and recovery flow but does not take over routine project execution.

A local policy classification, unavailable tool, refusal, timeout, or task failure does not automatically stop the manager chain or entire project. The parent and root evaluate compliant reroutes before escalating the block.

## Pausing and recovery

AMS continues without asking for another prompt when the next action is known, authorized, safe, and useful.

It pauses when:

- user intent is materially unclear;
- the next action is destructive, irreversible, externally visible, or outside authority;
- repeated drift suggests the plan may be wrong;
- materially different valid required paths need user preference;
- no compliant route can make mandatory progress.

Before pausing, AMS preserves:

- the last completed action;
- supporting evidence;
- logical lineage and custody state;
- ownership and live-writer state;
- remaining allocation where needed;
- the exact decision required;
- the safest next action;
- the condition needed to resume.

AMS prefers an existing authoritative project-native task, issue, journal, checkpoint, or handoff system. It does not create a competing ledger.

When no existing system can preserve required resumption state, AMS may use:

```text
<project-root>/.codex/ams-recovery.json
```

The root alone owns this ledger. It records only what recovery requires, including objective, criteria, settings, package identity, work-order state, logical parentage, role, allowed shape, delegated scope, allocation, ownership, evidence custody, blockers, and exact next action.

For a proven pre-3.09 recovery record, missing hierarchy fields mean:

```text
logical parent = root
role = worker
delegation authority = none
descendant allocation = none
```

AMS never infers manager authority from a legacy record.

When resuming, the root:

1. reads the handoff, objective, criteria, settings, active package identity, and root-owned recovery state;
2. commissions bounded inspection of the live repository, workspaces, user changes, commits, artifacts, tests, and validation;
3. evaluates returned evidence and treats earlier reports as evidence rather than proof;
4. rebuilds the task graph and logical reporting tree without rewriting historical lineage;
5. classifies work as verified, awaiting integration, unverified, partial, ready, blocked, or superseded;
6. reclaims stale ownership only after delegated evidence proves no live writer remains;
7. resumes from the earliest unfinished or unverified dependency;
8. creates the useful current topology instead of recreating an old roster;
9. issues new IDs for replacements or reparented work.

## Package updates and repair

Rerun the one-line installer for the operating system.

Before changing package instructions:

1. stop new dispatch and package-control starts;
2. finish or roll back atomic AMS control writes;
3. let safe project work reach useful boundaries;
4. collect evidence and preserve exact resumption state;
5. close all non-root sessions;
6. replace the complete package;
7. restart or reload Codex.

Do not combine files from different releases.

Release 3.09 requires:

```text
SKILL.md
VERSION
agents/openai.yaml
references/hierarchy-control.md
references/intensity-control.md
references/package-maintenance.md
references/profile-management.md
references/project-control.md
references/runtime-core.md
references/zergling-rush.md
```

An installation missing `hierarchy-control.md` is incomplete and must not improvise manager behavior.

AMS may repair its installed package only with explicit user authority. The current session remains on the old loaded instructions for recovery and reporting, and a fresh session is required before normal work continues.

AMS treats installed skill files as protected. It rejects package files that are redirected, unstable, unexpectedly linked, malformed, mixed across releases, or inconsistent with the package identity.

## Uninstall

Standard uninstall removes only the installed AMS skill directory. It preserves:

- per-project AMS settings;
- project recovery state;
- generated AMS agent profiles;
- unrelated skills and profiles.

Stop or safely pause active AMS work before uninstalling.

### Windows PowerShell

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

### Bash

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

While the skill is still loaded, an explicit request may use the package-maintenance rules:

```text
Uninstall the Adaptive Master–Subagent Orchestration skill. Preserve project settings, recovery state, and generated profiles.
```

### Optional full cleanup

Remove project settings only from the specific project:

```text
<project-root>/.codex/ams-orchestration.toml
```

Do not delete the whole `.codex` directory.

Generated profiles are normally under:

```text
$CODEX_HOME/agents/
```

Delete only files proven AMS-managed by the exact marker:

```text
# managed-by: adaptive-master-subagent-orchestration
```

Do not remove every `ams_*.toml` file blindly.

If AMS created a separate recovery ledger, remove only the exact path recorded in the handoff or AMS report. Do not guess or delete unrelated project state.

## Directory structure

### Repository

```text
Codex-Adaptive-Master-Subagent-Orchestration/
|-- README.md
|-- INSTALLATION.md
|-- PRODUCT DOCUMENTATION.md
|-- adaptive-master-subagent-orchestration-3.09.zip
|-- install.ps1
|-- install.sh
`-- adaptive-master-subagent-orchestration/
    |-- SKILL.md
    |-- VERSION
    |-- agents/
    |   `-- openai.yaml
    |-- assets/
    |   `-- agent-profiles/
    |       `-- 18 canonical ams_*.toml profiles
    `-- references/
        |-- hierarchy-control.md
        |-- intensity-control.md
        |-- package-maintenance.md
        |-- profile-management.md
        |-- project-control.md
        |-- runtime-core.md
        `-- zergling-rush.md
```

### Installed skill

```text
$HOME/.agents/skills/
`-- adaptive-master-subagent-orchestration/
    |-- SKILL.md
    |-- VERSION
    |-- agents/
    |   `-- openai.yaml
    |-- assets/
    |   `-- agent-profiles/
    |       `-- 18 canonical ams_*.toml profiles
    `-- references/
        |-- hierarchy-control.md
        |-- intensity-control.md
        |-- package-maintenance.md
        |-- profile-management.md
        |-- project-control.md
        |-- runtime-core.md
        `-- zergling-rush.md
```

### Installed agent profiles

```text
$CODEX_HOME/agents/
|-- ams_sol_low.toml
|-- ams_sol_medium.toml
|-- ams_sol_high.toml
|-- ams_sol_xhigh.toml
|-- ams_sol_max.toml
|-- ams_terra_low.toml
|-- ams_terra_medium.toml
|-- ams_terra_high.toml
|-- ams_terra_xhigh.toml
|-- ams_terra_max.toml
|-- ams_luna_low.toml
|-- ams_luna_medium.toml
|-- ams_luna_high.toml
|-- ams_luna_xhigh.toml
|-- ams_luna_max.toml
|-- ams_spark_low.toml
|-- ams_spark_medium.toml
`-- ams_spark_high.toml
```

When `CODEX_HOME` is unset, the installer uses `$HOME/.codex/agents/`.

### Project settings and optional recovery

```text
<project-root>/
`-- .codex/
    |-- ams-orchestration.toml
    `-- ams-recovery.json  # only when no project-native state system is sufficient
```

## Troubleshooting

### AMS does not activate automatically

Check:

```toml
enabled = true
allow_implicit_invocation = true
```

Also confirm that the project is trusted and Codex permits implicit skill use. Explicit invocation works independently of persistent automatic activation.

### A new project has AMS disabled

This is expected. Missing settings are initialized with `enabled = false`. Use `AMS ENABLE` or select a mode.

### `balanced` is stored as `moderate`

This is expected for schema-2 compatibility. `balanced` and `moderate` select the same runtime behavior. AMS reports the mode as `balanced` while preserving `moderate` in the existing schema.

### A manager cannot spawn an agent

This is expected. Managers never physically spawn sessions. A manager returns a structured dispatch request, and the root validates the request and performs the physical spawn.

### AMS is physically flat

This is expected. Physical session topology and logical management topology are separate. Work-order lineage determines the logical parent even when every session is a direct physical child of the root.

### A manager profile is missing

Release 3.09 does not use a permanent manager profile. Sol, Terra, or Luna profiles receive delegated-manager authority through a valid bounded work order. Spark cannot be a manager.

### Spark is not being used

Check:

```toml
spark_enabled = true
spark_available = true
spark_efforts = ["low", "medium", "high"]
```

Run `AMS SPARK RECHECK` when account capability may have changed.

### A profile is missing or invalid

Rerun the repository-hosted installer. It restores the complete canonical matrix from the package while refusing to overwrite unrecognized or user-authored collisions.

With `profile_management = "auto"`, AMS may also restore a selected missing or recognized defective profile from the exact installed package asset. Restart Codex if a newly installed or repaired profile is not immediately visible.

### The package reports 3.08 or lacks `hierarchy-control.md`

The installation is not the complete 3.09 package. Reinstall the verified archive and confirm:

```text
VERSION = 3.09
references/hierarchy-control.md exists
```

Do not merge files from 3.08 and 3.09.

### The checksum does not match

Do not bypass the check. The expected SHA-256 for the repository-root package is:

```text
f35aa28cad7c2691e80823e36ca276cbee8b20de067600fd8edb8f2aaf10fe4b
```

Confirm that the package came from:

```text
https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/adaptive-master-subagent-orchestration-3.09.zip
```

### The installer reports an unexpected directory entry

The 3.09 archive may contain only these directory entries:

```text
adaptive-master-subagent-orchestration/
adaptive-master-subagent-orchestration/agents/
adaptive-master-subagent-orchestration/assets/
adaptive-master-subagent-orchestration/assets/agent-profiles/
adaptive-master-subagent-orchestration/references/
```

Any other directory entry is rejected.

### The skill changed but Codex still shows old behavior

Restart or reload Codex. AMS never loads changed package instructions into the same active session after package mutation.

### A project is blocked instead of complete

Read the reported blocker, exact next action, and resumption condition. Resolve the external requirement, then explicitly ask AMS to resume from the live project state and handoff.
