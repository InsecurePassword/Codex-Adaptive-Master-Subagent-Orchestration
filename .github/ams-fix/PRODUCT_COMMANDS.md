## Command reference

Clear equivalent wording is valid. Every command below invokes AMS. Except for `AMS STATUS`, controls persist only to the trusted project's `.codex/ams-orchestration.toml`; none writes global persistence.

### `AMS STATUS`

Read-only inspection of the canonical project and global settings paths. Reports source precedence, effective settings, mode, and exact activation blockers without searching unrelated files.

### `AMS ENABLE`

Creates or updates project settings and persists `enabled = true`.

### `AMS DISABLE`

Safely stops new AMS dispatch, preserves required resumption information, closes remaining sessions, and persists project `enabled = false`.

### `AMS MODE <mode>`

Persists the selected project intensity and `enabled = true`.

```text
auto
minimal
balanced
moderate
heavy
extreme
```

`moderate` is a compatibility alias for `balanced` and remains the schema-2 storage token.

### `AMS IMPLICIT on|off`

Persists project `allow_implicit_invocation`. Changing it does not automatically stop a currently active objective.

### `AMS SPARK on|off`

Persists the project's normal Spark preference. `off` does not claim that Spark is unavailable.

### `AMS SPARK RECHECK`

Runs one smallest safe Spark capability probe and updates the project availability cache only when the evidence supports it.

### `AMS SPARK EFFORTS <subset>`

Persists the allowed project Spark efforts:

```text
AMS SPARK EFFORTS low
AMS SPARK EFFORTS low,medium
AMS SPARK EFFORTS low,medium,high
```

An empty `spark_efforts = []` value permits no normal Spark assignment without marking Spark unavailable.

### `AMS PROFILES auto|installer`

Persists project profile-management behavior. `auto` permits selected managed-profile repair; `installer` reports defects unless repair is explicitly requested.

### Zergling Rush commands

Current-objective activation:

```text
Use Zergling Rush for this task.
AMS ZERGLING RUSH
AMS MODE ZERGLING-RUSH
```

Save the project preference:

```text
AMS MODE ZERGLING-RUSH PERSIST
```

A saved preference does not remove the requirement for current-turn Rush consent.
