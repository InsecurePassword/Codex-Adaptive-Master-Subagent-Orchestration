# AMS intensity control

Read completely when `runtime-core.md` must select, validate, or change orchestration intensity. Intensity controls physical concurrency, logical team shape, routing latitude, and economic restraint. It never changes safety, ownership, authority, validation, or root-only acceptance.

## Modes

### `minimal`

Use the strict root-plus-one shape. At most one non-root session may exist at a time, including probes, managers, workers, integrators, reviewers, or observers. The active session may be one direct worker or one delegated manager doing bounded project work.

When a manager needs a descendant, it records a dispatch request and closes. The root may then run one worker. Afterward, the root resumes that manager session or issues a new superseding manager order for review. Never overlap them.

### `balanced`

Use one of these shapes for an active wave:

```text
Root + up to two direct non-manager sessions
Root + one delegated manager + up to two direct descendants of that manager
```

Do not mix the two shapes in the same active wave. No nested manager is permitted. Choose the smallest useful shape.

### `auto`

Recommended default. Select the smallest effective topology from the current task graph. Direct workers, delegated managers, or manager-worker chains may be used when they add value. AMS defines no fixed logical-depth, manager-count, worker-ratio, or team-shape ceiling in `auto`; runtime capacity, dependencies, ownership, finite allocations, safety, cost, and coordination value govern.

### `heavy`

Use broader useful concurrency and stronger routing than `auto` when this materially reduces critical-path time or increases confidence. Avoid valueless duplication or recursive hierarchy.

### `extreme`

Use aggressive useful parallelism, competing approaches, and redundant validation where expected value remains positive. Continue to prefer the lowest-cost reliable model for each lane unless stronger routing materially improves success or speed. Do not manufacture work merely to fill capacity.

### `zergling-rush`

This is not a normal persisted activation. Load `zergling-rush.md`; current-turn explicit consent is mandatory for every objective. Without consent, fall back in memory to the current non-Rush mode or `auto`.

## Selection

A direct current-turn instruction controls the current objective. Otherwise use valid project settings. `balanced` is accepted as a runtime alias and persists as `moderate`; stored `moderate` behaves as `balanced`.

Select intensity from task coupling, risk, ambiguity, workstream independence, validation burden, expected coordination value, available capacity, and cost. File count alone is not decisive.

Increasing intensity never permits:

- overlapping writers;
- weaker safety, authorization, validation, or acceptance;
- authority or allocation expansion;
- worker delegation;
- non-root control-surface access;
- optional work after acceptance;
- root execution of routine project work.

## Transitions

On a mode decrease, stop new work that exceeds the target shape, let safe useful atomic work reach a boundary, collect evidence, close or cancel excess sessions, preserve lineage, update ownership, and continue. Do not rewrite old parentage.

On a mode increase, recompute the task graph and add only useful lanes. Do not reactivate stale or superseded work without contrary evidence.

A control-only intensity change does not itself create project work. Persist only when explicitly requested or when a documented settings command authorizes it.
