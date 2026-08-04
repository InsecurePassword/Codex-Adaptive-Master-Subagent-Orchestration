# AMS configuration maintenance

Read completely only for:

```text
AMS CONFIGURATION UPDATE
AMS CONFIGURATION UPDATE PROJECT
AMS CONFIGURATION UPDATE GLOBAL
```

Load `project-control.md` first. Its current master contract, defaults, constraints, precedence, legacy-field rule, and safe-file rules are authoritative.

This command completes a partial configuration or creates a missing one. It never runs implicitly, tracks history, creates a migration ledger, enables AMS, or changes an existing supported value.

## Project target

`AMS CONFIGURATION UPDATE` and `AMS CONFIGURATION UPDATE PROJECT` target `<project-root>/.codex/ams-orchestration.toml`.

When present:

1. parse against the current master contract;
2. ignore the retired top-level `schema_version` field and omit it from output;
3. reject every other unknown/duplicate field, extra table, invalid value, unsafe path, or malformed TOML;
4. preserve every existing supported value;
5. add every missing supported field from current defaults;
6. do not read or merge global settings;
7. perform no write when already complete and no retired field needs removal.

When absent, use a valid global configuration with omitted supported fields resolved from current defaults, or the exact current default if global is absent. An existing invalid/unsafe global file blocks creation.

## Global target

`AMS CONFIGURATION UPDATE GLOBAL` targets `$CODEX_HOME/ams-orchestration.toml`, or `~/.codex/ams-orchestration.toml`. The `GLOBAL` token is mandatory.

When present, apply the same validation, retired-field removal, value preservation, and missing-field completion. When absent, create the exact disabled default.

## Update rules

- Missing supported fields are valid and use current defaults before persistence.
- `schema_version` is ignored and removed only during this or another authorized write.
- Every other unknown field, duplicate, extra table, invalid type/value, unsafe file, or malformed TOML blocks the operation.
- Never delete, rename, normalize, or change an existing supported value.
- Write atomically only when bytes change, then verify.
- Report target, created/updated/unchanged state, fields added, and whether the retired field was removed.

No other command may use this reference to write global settings.
