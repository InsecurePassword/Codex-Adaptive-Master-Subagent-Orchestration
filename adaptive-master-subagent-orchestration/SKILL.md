---
name: adaptive-master-subagent-orchestration
description: "Bootstrap AMS before top-level project work and handle every `AMS ...` command. When enabled, keep a Sol Max root in control of model/effort routing and root-spawned bounded subagents, with optional root-mediated logical hierarchy."
---

# Adaptive Master–Subagent Orchestration

AMS keeps GPT-5.6 Sol Max, or a verified equivalent Sol alias at Max reasoning, as the root supervisor. The root owns the objective, task graph, routing, physical dispatch, logical topology, integration decisions, acceptance, and user communication. Bounded non-root sessions perform project work.

## Root guard

If this session is not the current top-level root, stop before reading AMS settings or references. A non-root session receives authority only through its work order and installed profile.

## Bootstrap and persistence

Before ordinary work on each top-level project turn, resolve settings in order:

1. `<project-root>/.codex/ams-orchestration.toml`, when present;
2. `$CODEX_HOME/ams-orchestration.toml`, or `~/.codex/ams-orchestration.toml` when `CODEX_HOME` is unset, only when the project file is absent;
3. no persistent settings.

Project settings completely override global settings; do not merge them. An unsafe or invalid project file blocks implicit activation rather than falling back to global. If both files are absent in a trusted stable project, load `references/project-control.md`, create its exact disabled project default, and stop ordinary implicit activation.

Implicit activation requires product eligibility, a trusted stable project root, and effective `enabled = true` plus `allow_implicit_invocation = true`. Explicit invocation activates AMS for the objective. A direct current-turn instruction clearly naming the AMS behavior changed overrides persistence for that objective; generic quality/completion language is not a convergence override.

Global persistence is never automatic. Normal controls write only the project file. Only `AMS CONFIGURATION UPDATE GLOBAL` may create or complete global configuration; it never enables AMS or changes an existing supported value.

## Project controls

Load `references/project-control.md` before any command below or equivalent settings/status request:

```text
AMS STATUS
AMS ENABLE | AMS DISABLE
AMS MODE auto|minimal|balanced|moderate|heavy|extreme
AMS IMPLICIT on|off
AMS GOVERNANCE on|off
AMS ROOT FALLBACK on|off
AMS FEATURE <name> on|off
AMS CONVERGENCE CORRECTIONS <2-12>
AMS CONVERGENCE REDESIGNS <1-12>
AMS CONFIGURATION UPDATE [PROJECT|GLOBAL]
AMS SPARK on|off
AMS SPARK RECHECK
AMS SPARK EFFORTS low,medium,high
AMS PROFILES auto|installer
```

`AMS STATUS` is read-only. Modes enable AMS. Feature and convergence-limit controls change only named project settings and execute nothing. `AMS CONFIGURATION UPDATE` changes no existing supported value.

## Runtime routing

Load only what the objective requires:

- `references/project-control.md` for settings, status, feature controls, steering, continuity, or recovery;
- `references/configuration-maintenance.md` only for an explicit configuration update;
- `references/runtime-core.md` for active orchestration;
- `references/package-maintenance.md` only for an explicit package operation, downgrade preparation, or integrity request.

`runtime-core.md` owns all active-work capability gates and nested lazy routes. Read every selected reference completely. A required unreadable reference fails closed only for the behavior it owns. Installation or update completion triggers no additional AMS action.
