# AMS request-scoped profile and worker accounting

Read completely only when `request_accounting = true`, the current turn explicitly requests usage for the current objective, and no authoritative project-native accounting supersedes it. The setting never produces a report by itself. This reference is read-only, objective-local, and creates no ledger.

## Boundary

Use the root's live task graph and authorized evidence. Count execution attempts for the current root objective:

- each physically spawned native non-root session counts once;
- each created user-visible app task counts once as an `app-task` transport attempt;
- a retry, replacement, replicated investigation, reviewer, integrator, observer, or manager counts again only when a new physical session or app task was created;
- corrections sent to the same existing app task or resumed native session do not count as a new attempt;
- exclude the root, unspawned plans, unrelated objectives, and tasks never actually created.

Report native requested AMS profiles from dispatch records. App tasks are reported as a separate transport category and include requested/observed model and effort only when truthful evidence exists. Never infer identity from names.

## Output

Return the smallest useful report, normally:

```text
AMS accounting for <objective-id>: <total> execution attempts — native=<N>, app-task=<M>; <profile=count, ...>.
```

When requested, add a compact table by family, effort, temporary role, transport, status, or observed mismatch. Do not include prompts, work-order bodies, logs, tokens, private reasoning, or unrelated history.

If context loss prevents an exact count, report a verified lower bound and missing evidence. Create no accounting log, CSV, task record, or recovery file unless the user separately authorizes an external artifact.
