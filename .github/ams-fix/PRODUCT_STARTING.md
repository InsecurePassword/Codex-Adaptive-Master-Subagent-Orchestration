## Starting and stopping AMS

### Automatic bootstrap

On every top-level root project turn, Codex sees AMS as an implicit skill and loads its bootstrap before ordinary project work. AMS resolves effective settings in this order:

1. `<project-root>/.codex/ams-orchestration.toml` when present;
2. `$CODEX_HOME/ams-orchestration.toml`, or `$HOME/.codex/ams-orchestration.toml` when `CODEX_HOME` is unset, only when the project file is absent;
3. no persistent settings.

The project file overrides the global file completely. A safe valid global file can enable AMS without creating a project file. An invalid project file blocks implicit activation rather than falling back to global settings.

### Use AMS for one request

```text
Use $adaptive-master-subagent-orchestration for this project.
```

Explicit invocation enables AMS only for the current objective unless the user also issues a project-setting command.

### Enable AMS for the project

```text
AMS ENABLE
```

This creates or updates the project configuration and sets `enabled = true`. It never changes global persistence.

### Disable AMS for the project

```text
AMS DISABLE
```

AMS stops new dispatch, lets safe work reach a useful boundary, collects evidence, records exact resumption information when needed, closes remaining sessions, and persists project `enabled = false`.

### Select a project mode

```text
AMS MODE minimal
AMS MODE balanced
AMS MODE auto
AMS MODE heavy
AMS MODE extreme
```

A normal mode command persists the selected project mode and also sets project `enabled = true`. `moderate` remains accepted as an alias for `balanced`.

### Inspect activation

```text
AMS STATUS
```

Status is read-only. It reports the canonical project and global paths, each file's existence and validity, the effective settings source, effective mode and controls, and the exact reason implicit activation is enabled or blocked. AMS does not search unrelated project policy or configuration files for its state.
