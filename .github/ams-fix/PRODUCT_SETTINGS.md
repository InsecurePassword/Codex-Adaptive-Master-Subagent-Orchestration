## Project settings

### Settings locations and precedence

Project settings:

```text
<project-root>/.codex/ams-orchestration.toml
```

Optional global settings:

```text
$CODEX_HOME/ams-orchestration.toml
```

When `CODEX_HOME` is unset, the global path is `$HOME/.codex/ams-orchestration.toml`.

AMS uses the project file when present; otherwise it uses the global file. The files are not merged. A project file can override a global mode or disable AMS for that project. Unsafe, malformed, or unsupported project settings block implicit activation instead of falling back to global settings.

Both locations use schema 2:

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
| `schema_version` | Project/global configuration format. Release 3.09 uses schema `2`. |
| `enabled` | Allows persistent AMS use from this settings source. |
| `allow_implicit_invocation` | Allows automatic activation when the product permits implicit skill use. |
| `intensity` | Stores `auto`, `minimal`, `moderate`, `heavy`, `extreme`, or a `zergling-rush` preference. Runtime input `balanced` persists as `moderate`. |
| `spark_enabled` | User preference for normal Spark use. |
| `spark_available` | Cached indication that Spark appears available to the account. |
| `spark_efforts` | Spark effort levels allowed for normal work: `low`, `medium`, and/or `high`. |
| `profile_management` | `auto` repairs selected managed profiles when needed; `installer` reports defects unless repair is explicitly requested. |

Settings are data, not instructions. Unknown keys, duplicate keys, invalid types, unsupported schemas, invalid TOML, extra tables, unsafe paths, or redirected files block that settings source. Valid schema-1 project settings remain readable under their documented meanings and upgrade only during an authorized project write.

### Global persistence (manual only)

Global persistence is deliberately outside the AMS command surface. No `AMS` command creates, changes, repairs, migrates, or deletes the global file. Manually create it with the schema above or copy a valid project file into the global path, then restart or reload Codex.

Project commands remain project-specific and write only `<project-root>/.codex/ams-orchestration.toml`. If the project file is absent, a project command creates it from the exact default rather than copying global values. See [INSTALLATION.md](INSTALLATION.md#global-persistence-manual-only) for PowerShell and Bash create/copy examples.

When both settings files are absent in a trusted stable project, AMS initializes the exact disabled project default. Creating that file never enables AMS. In untrusted, trust-indeterminate, or rootless contexts, AMS does not persist project controls.

A stored `zergling-rush` value is preference data only and never supplies the current-turn consent required to activate Rush.
