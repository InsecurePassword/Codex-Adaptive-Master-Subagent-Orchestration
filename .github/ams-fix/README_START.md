## Start using AMS

The installed skill bootstraps itself on every top-level root project turn. Before ordinary project work it checks the project settings file first, then the optional global settings file. When the effective settings enable implicit use, AMS loads automatically in the stored mode.

### Use it once

```text
Use $adaptive-master-subagent-orchestration for this project.
```

### Project-specific persistence

From inside a trusted project:

```text
AMS STATUS
AMS ENABLE
AMS MODE auto
AMS DISABLE
```

Project commands write only:

```text
<project-root>/.codex/ams-orchestration.toml
```

`AMS ENABLE` persists `enabled = true`. A normal `AMS MODE ...` command persists the selected mode and also enables AMS. `AMS STATUS` reports the project path, global path, effective source, settings, and any activation blocker.

### Global persistence (manual only)

To supply defaults for every trusted project that has no project settings file, manually create or copy:

```text
$CODEX_HOME/ams-orchestration.toml
```

When `CODEX_HOME` is unset, use:

```text
$HOME/.codex/ams-orchestration.toml
```

Use the same schema as a project file. For persistent auto mode:

```toml
schema_version = 2
enabled = true
allow_implicit_invocation = true
intensity = "auto"
spark_enabled = true
spark_available = true
spark_efforts = ["low", "medium", "high"]
profile_management = "auto"
```

A project file overrides the global file completely, so a project can select another mode or disable AMS. Global persistence is manual: no `AMS` command creates, changes, or removes the global file. Restart or reload Codex after changing it.
