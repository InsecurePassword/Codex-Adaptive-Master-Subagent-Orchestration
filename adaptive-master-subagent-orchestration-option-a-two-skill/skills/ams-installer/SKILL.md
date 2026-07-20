---
name: ams-installer
description: Install, verify, repair, or upgrade Adaptive Master–Subagent custom-agent profiles and persistent intensity configuration. Use explicitly for setup or maintenance, not project execution.
---

Manage only the Adaptive Master–Subagent installation. Do not modify a project repository unless the user explicitly selects a project-local profile destination or project intensity configuration.

**Module version: 3.1.0**

1. Resolve this skill's plugin root from the loaded `SKILL.md` path. The canonical profile assets are under `<plugin-root>/assets/agent-profiles/`; deterministic utilities are under `<plugin-root>/scripts/`.
2. Inspect `$CODEX_HOME/agents/` (normally `~/.codex/agents/`) and any explicitly selected project-local registry.
3. Prefer `python <plugin-root>/scripts/bootstrap_profiles.py`; use the bundled PowerShell wrapper when appropriate. Run a dry-run first for repair, migration, or managed upgrade operations.
4. Create only missing namespaced profiles. Preserve valid existing definitions by default. Back up before repairing malformed managed profiles, upgrading managed profiles, or retiring a managed legacy `ams_spark_runner`.
5. Never overwrite unrelated user-authored content. Use the bootstrap utility's nonconflicting-name behavior and report the resulting routing name.
6. Install only runtime-supported model identifiers and efforts. Never invent availability. Spark is optional; use `--exclude-spark` or `--spark-efforts` when needed.
7. Verify TOML validity, required fields, profile-name consistency, model/reasoning fields, Spark workspace restrictions, and effective discoverability when observable.
8. Ensure effective `agents.max_depth = 1` without making unrelated global changes; prefer a project-local override when appropriate. Treat thread limits as ceilings, not targets.
9. When explicitly asked to set intensity, use `<plugin-root>/scripts/set_intensity.py` or its PowerShell wrapper. Supported values are `auto`, `minimal`, `moderate`, `heavy`, and `extreme`; default is `auto`. Preserve an existing valid configuration unless the user requests a change.
10. Report exact files created, preserved, repaired, upgraded, backed up, renamed, retired, or blocked. Do not claim a profile is usable merely because its file exists when runtime availability cannot be observed.
