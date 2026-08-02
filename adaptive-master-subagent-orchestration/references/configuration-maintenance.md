# AMS configuration maintenance

Read completely only for an explicit command:

```text
AMS CONFIGURATION UPDATE
AMS CONFIGURATION UPDATE PROJECT
AMS CONFIGURATION UPDATE GLOBAL
```

Load `project-control.md` first. Its current schema-2 default, supported fields, value constraints, precedence, and safe control-file rules are authoritative.

This command updates an existing incomplete configuration as well as creating a missing configuration. It never runs implicitly and never changes an existing supported value.

## Project target

`AMS CONFIGURATION UPDATE` and `AMS CONFIGURATION UPDATE PROJECT` target:

```text
<project-root>/.codex/ams-orchestration.toml
```

When the project file exists:

1. parse it as schema 2;
2. reject unknown or duplicate keys, extra tables, invalid values, unsafe paths, and malformed TOML;
3. preserve every existing supported value;
4. add every currently supported missing field from the exact current default;
5. do not read or merge the global file;
6. perform no write when already complete.

When the project file is absent:

1. if the global file is absent, use the exact current default;
2. if the global file exists and is valid, resolve its omitted supported fields from the current default and use that complete result;
3. if the global file exists but is invalid or unsafe, reject without writing and report the global defect;
4. create one complete project override only from the valid source selected above.

## Global target

`AMS CONFIGURATION UPDATE GLOBAL` targets:

```text
$CODEX_HOME/ams-orchestration.toml
```

or `~/.codex/ams-orchestration.toml` when `CODEX_HOME` is unset.

The `GLOBAL` token is mandatory for a global write.

When the global file exists, preserve every existing supported value and add every missing supported field from the exact current default. When absent, the explicit command may create the exact disabled default.

## Update rules

- `schema_version = 2` is mandatory.
- Missing supported settings are valid and resolve from the exact current default.
- Unknown keys, duplicate keys, extra tables, invalid types or values, unsafe files, and unsupported schemas block the operation.
- Never delete, rename, normalize, or change an existing supported value.
- Never enable AMS or change existing intensity, governance, fallback, Spark, or profile-management choices.
- Write atomically only when bytes must change, then verify the result.
- If already complete, perform no write.
- Report the target, whether it was created, updated, or unchanged, and the exact fields added.

No other AMS command may use this reference as authority to write global settings.
