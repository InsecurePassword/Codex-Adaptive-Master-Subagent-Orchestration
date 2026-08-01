# AMS model tracking

Load this reference only when effective settings have `model_tracking = true` and a CSV row or model-annotated topology is needed. Reuse it after loading. Never newly load it while tracking is false. If tracking is turned off after this file was loaded, stop using it for new rows and annotations.

This feature records the final AMS capability profile selected for each successfully started non-root physical session. It does not verify the model actually executed and does not track work orders, messages, results, completion, recovery, or historical topology.

## CSV log

The log is root-owned AMS control output. Non-root sessions must not own, edit, or include it in commands or Git/history.

Write one log per top-level root session under:

```text
<project-root>/.codex/logs/
```

Create it lazily on the first successful non-root spawn. Choose the path once and retain it for the root session:

```text
ams-model-tracking-YYYYMMDDTHHMMSSZ.csv
```

Use the first tracked spawn time in UTC. Create the file exclusively; on a collision add `-01`, `-02`, and so on. Use UTF-8 without BOM and LF endings.

The header is exactly:

```csv
timestamp,subagent/worker name,model level,reasoning
```

After `spawn_agent` succeeds, write one row. On the first row, create the file with its header and first row in one write. Serialize and flush later appends.

Use the leaf name from the returned canonical `task_name`.

```csv
2026-08-01T21:04:18.337Z,semantic_reviewer,sol,high
```

Derive `model level` and `reasoning` from the final canonical AMS capability profile selected after any reroute or substitution:

```text
model level: sol | terra | luna | spark | unknown
reasoning:   low | medium | high | xhigh | max | unknown
```

Never infer either value from an icon, generated nickname, output style, duration, or the root model. The row records AMS's routing choice, not authoritative runtime identity.

Do not log planned work, failed spawns, root activity, later turns on an existing physical session, results, completion, or termination. Each newly spawned replacement receives its own row.

Require the directory and file to remain regular, non-redirected, and beneath the trusted project root. Serialize writes so rows cannot interleave.

A logging failure does not block valid orchestration. Report it once for the root session and do not claim the row was written.

## Topology annotations

`runtime-core.md` owns active topology membership and logical layout.

When tracking is on, annotate the active non-root nodes supplied by `runtime-core.md` with the model level and reasoning from the root's current routing state:

```text
Root
├── manager_a [sol / high]
│   └── worker_a1 [terra / medium]
└── worker_b [spark / low]
```

Do not change topology membership or lineage. Do not reconstruct annotations from CSV history. Use `unknown` when the current selected profile cannot be established.
