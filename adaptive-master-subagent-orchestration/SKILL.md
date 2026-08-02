---
name: adaptive-master-subagent-orchestration
description: "Bootstrap AMS before top-level project work and handle every `AMS ...` command. When enabled, keep a Sol Max root in control of model/effort routing and root-spawned bounded subagents, with optional root-mediated logical hierarchy."
---

# Adaptive Master–Subagent Orchestration

AMS keeps GPT-5.6 Sol Max, or a verified equivalent Sol alias at Max reasoning, as the root supervisor. The root owns the objective, task graph, model/reasoning selection, physical dispatch, logical topology, integration decisions, acceptance, and user communication. Bounded non-root sessions perform project work.

## Root guard

If this session was spawned, forked, parented, delegated, or otherwise is not the current top-level root, stop before reading AMS settings or references. A non-root session receives its authority only through its work order and installed profile.

## Bootstrap and persistence

Before ordinary work on each top-level project turn, resolve AMS settings in this order:

1. `<project-root>/.codex/ams-orchestration.toml`, when present;
2. `$CODEX_HOME/ams-orchestration.toml`, or `~/.codex/ams-orchestration.toml` when `CODEX_HOME` is unset, only when the project file is absent;
3. no persistent settings.

Project settings override global settings completely; the files are not merged. An unsafe or invalid project file blocks implicit activation instead of falling back to global settings. If both files are absent in a trusted stable project, load `references/project-control.md`, create its exact disabled project default, and stop ordinary implicit activation.

Implicit activation requires product-level implicit-skill eligibility, a trusted stable project root, and effective settings with `enabled = true` and `allow_implicit_invocation = true`. Explicit invocation activates AMS for the current objective. Direct current-turn user instructions override persisted settings for that objective.

Global persistence is never automatic. Normal AMS commands write only the current trusted project's settings file; only explicit `AMS CONFIGURATION UPDATE GLOBAL` may create or update the global schema-2 file, and it never enables AMS or changes an existing value.

## Project controls

Load `references/project-control.md` before acting on any command below or equivalent settings/status wording:

```text
AMS STATUS
AMS ENABLE
AMS DISABLE
AMS MODE auto|minimal|balanced|moderate|heavy|extreme
AMS IMPLICIT on|off
AMS GOVERNANCE on|off
AMS ROOT FALLBACK on|off
AMS CONFIGURATION UPDATE [PROJECT|GLOBAL]
AMS SPARK on|off
AMS SPARK RECHECK
AMS SPARK EFFORTS low,medium,high
AMS PROFILES auto|installer
```

`AMS STATUS` is read-only. Normal mode commands also enable AMS. Governance and root fallback are independent project controls. `AMS CONFIGURATION UPDATE` is explicit maintenance and changes no existing setting value.

## Reference trust boundary

Resolve packaged references beneath the installed skill root. Before loading one as instructions, require a regular non-redirected file with stable path/object identity, no path escape or unexpected links, size at most 256 KiB, UTF-8 without BOM/NUL/CR and with final LF, and matching package identity when observable. Reject unsafe or changed references. After a behavior-changing package mutation, retain only the pre-change contract required for bounded reporting and require reload.

## Runtime routing

Load only what the objective requires:

- `references/project-control.md` for settings, status, steering, Spark state, continuity, or recovery from user/project-native evidence;
- `references/configuration-maintenance.md` only for an explicit `AMS CONFIGURATION UPDATE [PROJECT|GLOBAL]`;
- `references/runtime-core.md` for active orchestration;
- `references/package-maintenance.md` only for an explicit install, update, repair, rollback, uninstall, or package-integrity request.

`runtime-core.md` lazily routes `intensity-control.md`, `hierarchy-control.md`, `profile-management.md`, `project-governance.md`, `root-execution-fallback.md`, and `zergling-rush.md`. Load `project-governance.md` only when effective `project_governance = true`; load `root-execution-fallback.md` only when mandatory progress would otherwise stop, no viable delegated route remains, and effective `root_execution_fallback = true`. Read each selected reference completely. A required unreadable reference fails closed only for the behavior it owns.
