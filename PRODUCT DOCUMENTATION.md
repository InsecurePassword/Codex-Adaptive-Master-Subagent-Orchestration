# Product Documentation

**Product:** Adaptive Master–Subagent Orchestration (AMS)  
**Current release:** 3.09

This document explains what AMS does, how to install it, how to use every supported control, how virtual hierarchy works, how AMS chooses agents, how it protects project work, and how to update, repair, recover, or uninstall it.

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
11. [How AMS chooses models](#how-ams-chooses-models)
12. [How AMS manages work](#how-ams-manages-work)
13. [Spark controls](#spark-controls)
14. [Agent profile management](#agent-profile-management)
15. [Validation, review, and completion](#validation-review-and-completion)
16. [Failure handling](#failure-handling)
17. [Pausing and recovery](#pausing-and-recovery)
18. [Package updates and repair](#package-updates-and-repair)
19. [Uninstall](#uninstall)
20. [Directory structure](#directory-structure)
21. [Troubleshooting](#troubleshooting)

## What AMS does

AMS is a Codex skill for projects that benefit from coordinated specialist agents.

It keeps **GPT-5.6 Sol Max**, or a verified equivalent Sol alias at Max reasoning, in charge as the root manager. The root:

- understands the complete user objective;
- maintains the global task graph;
- chooses the logical team structure;
- remains the sole physical spawn authority;
- chooses the model and reasoning level for each assignment;
- controls sequencing, concurrency, ownership, retries, cancellation, and reassignment;
- makes integration decisions;
- evaluates evidence and validation;
- decides whether the project is complete, blocked, or requires a user decision;
- communicates with the user.

The root does **not** perform routine project execution. Implementation, inspection, testing, builds, integration work, review, and recovery inspection remain delegated to bounded non-root sessions.

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
- adds hierarchy lineage, custody, allocation, replay, replacement, and recovery rules.

## Requirements

- Codex with skill and custom-subagent support
- A top-level GPT-5.6 Sol Max session, or a verified equivalent Sol alias at Max reasoning
- Spark access only when Spark routing is enabled and the account supports it
- Windows PowerShell 5.1 or newer for the documented Windows installation
- Bash, `curl`, `unzip`, and either `sha256sum` or `shasum` for the documented Unix installation
- A Codex restart or reload after installing, updating, repairing, or uninstalling AMS

The installed skill contains Markdown, YAML, and a version file only. Shell tools are used for installation and maintenance, not while AMS is orchestrating work.

## Installation

### Release identity

Package:

```text
adaptive-master-subagent-orchestration-3.09-virtual-hierarchy-final-audited.zip
```

Download:

```text
https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/3.09/adaptive-master-subagent-orchestration-3.09-virtual-hierarchy-final-audited.zip
```

SHA-256:

```text
3e3e8dc3142d5bc2411a4703982150941816c3669d5f0bb01bab2099f7a88373
```

Default installation location:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
```

Use the platform-specific verified installation procedure in [INSTALLATION.md](INSTALLATION.md). Restart or reload Codex afterward.

### Release-hosted installer channel

The separate `ReleaseZip` release contains pinned PowerShell and Bash installer artifacts. Use those scripts for 3.09 only when their embedded package filename and checksum match the release identity above. The numbered 3.09 package and checksum are the source of truth.

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

### Setting meanings

| Setting | Meaning |
|---|---|
| `schema_version` | Project configuration format. Release 3.09 continues to use schema `2`. |
| `enabled` | Allows persistent AMS use in this project. |
| `allow_implicit_invocation` | Allows automatic activation when the product also permits it. |
| `intensity` | Stores `auto`, `minimal`, `moderate`, `heavy`, `extreme`, or a `zergling-rush` preference. Runtime input `balanced` maps to stored `moderate`. |
| `spark_enabled` | User preference for normal Spark use. |
| `spark_available` | AMS capability cache indicating whether Spark appears available to the account. |
| `spark_efforts` | Spark effort levels allowed for normal work: `low`, `medium`, and/or `high`. |
| `profile_management` | `auto` repairs selected managed profiles when needed; `installer` reports defects unless repair is explicitly requested. |

Settings are read as data, not instructions. Unknown keys, duplicate keys, wrong data types, unsupported schemas, invalid TOML, extra tables, unsafe paths, or redirected files block automatic activation.

### Compatibility

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

Runs one smallest safe Spark capability probe.

Use it after account, subscription, quota, product, or entitlement changes. AMS does not repeatedly probe Spark after it has been marked unavailable.

### `AMS SPARK EFFORTS <subset>`

Selects which Spark efforts may be used for normal work.

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

The active session may be:

- one direct worker; or
- one delegated manager performing bounded work.

If a logical chain requires another session, AMS first collects and closes the active session at a useful boundary. This preserves strict root-plus-one execution.

### `balanced`

Uses the smallest useful small team and selects one shape for each active wave:

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

Recommended default.

AMS selects the smallest effective adaptive topology from the current task graph. It may use direct workers, managers, or manager-worker chains when useful.

AMS defines no fixed logical depth, manager count, worker ratio, or team-shape ceiling in `auto`. Actual runtime capacity, dependencies, ownership, finite allocations, safety, cost, and coordination value govern.

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

A non-root session has exactly one immutable logical parent.

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

- root objective and request ID;
- parent work-order ID;
- requested role and profile;
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

If a manager becomes unavailable, the root preserves the evidence and either resumes the manager or issues a new superseding manager order with explicit custody transfer. A live descendant that needs a new supervisor is closed or superseded and reissued under a new identity and logical parent.

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

### Consent requirement

Rush must be requested clearly in the current user turn every time it activates.

These do not count as consent:

- a repository setting;
- an old saved preference;
- asking AMS to be faster;
- selecting a normal intensity.

AMS announces that Rush may consume substantially more usage before starting Rush work.

### What Rush does not change

Rush does not permit:

- independent spawning by a manager or worker;
- worker delegation;
- authority or allocation amplification;
- two writers on the same mutable surface;
- unauthorized destructive actions;
- skipped safety or validation;
- unsupported completion claims;
- non-root changes to AMS settings, profiles, package files, or recovery state;
- routine project execution by the root.

## How AMS chooses models

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

### Manager routing

There is no permanent manager model family. A delegated manager uses the same Sol/Terra/Luna profile matrix as other sessions. The root chooses a family and effort according to the manager's actual bounded work, ambiguity, risk, and supervisory burden.

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

### When AMS marks Spark unavailable

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

### Rechecking Spark

`AMS SPARK RECHECK` authorizes one smallest safe capability probe. Success sets availability true; authoritative family/account unavailability sets it false; temporary or task-specific failure leaves the cached value unchanged.

Under `minimal`, the probe consumes the single non-root session slot.

## Agent profile management

AMS uses custom profiles named:

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

Project-local profiles may be used only when global profiles are unavailable, deliberate project isolation is needed, or authoritative project instructions provide an override.

### Current profile schema

Release 3.09 managed profiles use:

```text
# managed-by: adaptive-master-subagent-orchestration
# profile-schema: 3
```

The profile enforces the bounded non-root boundary. The work order supplies the temporary `worker` or `delegated-manager` role.

Release 3.09 intentionally does not add a permanent manager profile. This keeps the profile matrix compact and makes management authority revocable for each work order.

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

Release 3.09 can migrate only profiles whose complete content proves recognized AMS provenance, including:

- current schema-3 role-gated profiles;
- exact 3.08 schema-2 direct-child/no-spawn Sol, Terra, Luna, and Spark signatures;
- official earlier v3 managed signatures;
- exact 3.07 Spark schema-1 signatures;
- original narrow marker-only AMS profile or runner signatures.

The 3.08 direct-child profile reference in this migration list is historical provenance, not current behavior.

Managed legacy files are backed up before upgrade. Ambiguous, partially matching, malformed, or user-authored files are preserved.

A fresh Codex session may be required before newly created profiles become discoverable.

## Validation, review, and completion

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

The root evaluates the returned evidence rather than running routine project validation itself.

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

### Durable recovery state

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

### Recovery process

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

Use an explicit request such as:

```text
Use $adaptive-master-subagent-orchestration to resume this project from the handoff and live repository state.
```

## Package updates and repair

### Update

Install the complete verified 3.09 package using [INSTALLATION.md](INSTALLATION.md).

Before changing package instructions:

1. stop new dispatch and package-control starts;
2. finish or roll back atomic AMS control writes;
3. let safe project work reach useful boundaries;
4. collect evidence and preserve exact resumption state;
5. close all non-root sessions;
6. replace the complete package;
7. restart or reload Codex.

Do not combine files from different releases.

### Package repair

A package repair validates and replaces the complete skill directory. Release 3.09 requires:

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

### Package integrity checks

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

### Ask AMS to uninstall itself

While the skill is still loaded, an explicit request may use the package-maintenance rules:

```text
Uninstall the Adaptive Master–Subagent Orchestration skill. Preserve project settings, recovery state, and generated profiles.
```

AMS stops active work safely, removes only the verified installed package root, reports remaining components, and requires a reload. Manual removal remains the simplest option.

### Optional full cleanup

Project settings and profiles are intentionally preserved by standard uninstall. Remove them only when you explicitly want to erase them.

#### Project settings

Remove only the specific file:

```text
<project-root>/.codex/ams-orchestration.toml
```

Do not delete the whole `.codex` directory.

#### Generated profiles

Generated profiles are normally under:

```text
$CODEX_HOME/agents/
```

Delete only files proven AMS-managed by the exact marker:

```text
# managed-by: adaptive-master-subagent-orchestration
```

Do not remove every `ams_*.toml` file blindly. AMS preserves ambiguous or user-authored profiles even when their filenames look similar.

#### Recovery state

AMS uses project-native state when possible. If it created a separate recovery ledger, remove only the exact path recorded in the handoff or AMS report. Do not guess or delete unrelated project state.

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

The numbered installable package is attached to the `3.09` GitHub release. The stable installer scripts are maintained separately under the `ReleaseZip` release.

### Release 3.09 asset

```text
3.09/
└── adaptive-master-subagent-orchestration-3.09-virtual-hierarchy-final-audited.zip
```

### Release package

```text
adaptive-master-subagent-orchestration/
├── SKILL.md
├── VERSION
├── agents/
│   └── openai.yaml
└── references/
    ├── hierarchy-control.md
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
        ├── hierarchy-control.md
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

The exact generated set depends on models and efforts supported by the current Codex runtime. No separate manager profile family is generated.

### Project settings

```text
<project-root>/
└── .codex/
    └── ams-orchestration.toml
```

### Optional recovery ledger

```text
<project-root>/
└── .codex/
    └── ams-recovery.json
```

The ledger is used only when no authoritative project-native state system can preserve required recovery information.

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

### The package reports 3.08 or lacks `hierarchy-control.md`

The installation is not the complete 3.09 package. Reinstall the verified 3.09 archive and confirm:

```text
VERSION = 3.09
references/hierarchy-control.md exists
```

Do not merge files from 3.08 and 3.09.

### The checksum does not match

Do not bypass the check. The expected SHA-256 is:

```text
3e3e8dc3142d5bc2411a4703982150941816c3669d5f0bb01bab2099f7a88373
```

Confirm that the downloaded filename and release tag match the release identity in this document.

### The skill changed but Codex still shows old behavior

Restart or reload Codex. AMS never loads changed package instructions into the same active session after package mutation.

### A project is blocked instead of complete

Read the reported blocker, exact next action, and resumption condition. Resolve the external requirement, then explicitly ask AMS to resume from the live project state and handoff.