---
name: adaptive-master-subagent-orchestration
description: "Bootstrap AMS on every top-level project turn: read this skill before project work to resolve global or project persistence, and use it for every `AMS ...` command or AMS status/configuration request. When enabled, run Sol Max-led adaptive orchestration with root-managed sessions and optional logical manager-worker chains."
---

# Adaptive Master–Subagent Orchestration

AMS keeps Sol Max, or a verified equivalent, as the root supervisor while bounded non-root sessions perform project work. It routes each task to the lowest-cost reliable model, runs useful independent lanes in parallel, supports root-mediated virtual manager-worker hierarchies, preserves one-writer ownership, and accepts completion only from reconciled evidence and required validation.

## Bootstrap and persistence

On every top-level root project turn, before ordinary project work, resolve the effective AMS settings in this order:

1. `<project-root>/.codex/ams-orchestration.toml`, when present;
2. `$CODEX_HOME/ams-orchestration.toml`, or `~/.codex/ams-orchestration.toml` when `CODEX_HOME` is unset, only when the project file is absent;
3. no persistent settings.

The project file overrides the global file completely; settings are not merged. An unsafe or invalid project file blocks implicit activation instead of falling back to global settings. A safe valid global file may enable AMS for a trusted project without creating a project file. If both files are absent in a trusted stable project, load `references/project-control.md`, create its exact disabled project default, and stop ordinary implicit activation.

Implicit activation requires product-level implicit-skill eligibility, a stable trusted project root, and effective settings with `enabled = true` and `allow_implicit_invocation = true`. Explicit invocation activates AMS for the current objective. Direct current-turn user instructions override stored settings for that objective.

Global persistence is manual only. AMS commands never create, modify, or delete the global file. Every canonical control command remains project-specific.

## Project controls

Use this skill for every command beginning with `AMS ` and every AMS status, activation, mode, or settings question. Load `references/project-control.md` before acting.

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
```

`AMS ENABLE`, normal `AMS MODE ...`, and the other setting commands persist to the project file when the project root is trusted and stable. `AMS MODE ...` also enables AMS. `AMS STATUS` is read-only and reports the project path, global path, effective source, effective settings, and any activation blocker. No command writes global persistence.

## Root authority and delegated roles

If this session was spawned, forked, parented, delegated, or otherwise is not the current top-level root, stop before reading AMS settings or references. Non-root sessions receive all authority through their work order and agent profile.

The root alone owns the user objective, physical spawning, global routing, integration decisions, acceptance, completion, recovery control, and user communication. Workers are non-delegating leaves. Delegated managers may request root-mediated descendants within their assigned scope and allocation, but never physically spawn, expand authority, contact the user, or declare project completion. Spark is worker-only.

## Reference trust boundary

Resolve packaged references beneath the installed skill root. Before loading one as instructions, require a regular non-redirected file with stable path/object identity, no path escape or unexpected links, size at most 256 KiB, UTF-8 without BOM/NUL/CR and with final LF, and matching package identity when observable. Reject unsafe or changed references. After behavior-changing package mutation, retain only the pre-change contract needed for bounded reporting/recovery and require reload.

## Runtime routing

Load only what the objective requires:

- `references/project-control.md` for settings, status, steering, Spark state, interruption, durable state, or recovery;
- `references/runtime-core.md` for active orchestration or project-facing recovery;
- `references/package-maintenance.md` for install, update, repair, rollback, uninstall, package-integrity suspicion, or reload-required recovery.

`runtime-core.md` routes `intensity-control.md`, `hierarchy-control.md`, `profile-management.md`, and `zergling-rush.md` lazily. Read each selected reference completely. A required unreadable reference fails closed only for the behavior it owns. Control-only actions create no project work lanes, and package maintenance is exclusive with active dispatch or other AMS control writes.
