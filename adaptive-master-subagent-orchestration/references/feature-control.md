# AMS modular feature control

Read completely only for `AMS FEATURE <name> on|off`, convergence-limit controls, feature/companion status, or an AMS/project-native capability conflict. It changes settings only; it never performs a feature.

Mapped fields are Boolean and resolve through `project-control.md`. `convergence-control` is the sole default-on module; all others default off. `true` permits only the documented trigger. `false` causes no AMS module action or reference load. There is no `auto` state.

```text
convergence-control            -> convergence_control
work-order-refinement          -> work_order_refinement
review-control                 -> review_control
shared-worktree-verification   -> shared_worktree_verification
runtime-observation            -> runtime_observation
untrusted-evidence-handling    -> untrusted_evidence_handling
task-graph-safeguards          -> task_graph_safeguards
rejected-approach-handoff      -> rejected_approach_handoff
request-accounting             -> request_accounting
app-task-lane                  -> app_task_lane
```

`AMS FEATURE <name> on|off` persists only the mapped project Boolean. Reject unknown names, duplicate tokens, missing state, or extra arguments without writing. It never enables AMS or executes the feature.

`AMS CONVERGENCE CORRECTIONS <2-12>` and `AMS CONVERGENCE REDESIGNS <1-12>` persist only their named project limits. Reject Boolean, fractional, signed, out-of-range, duplicate, missing, or extra values. They never enable AMS, toggle convergence, reset state, or load response logic.

A temporary objective-local override must be explicit about the AMS control, for example:

```text
Override AMS feature request-accounting on for this objective.
Override AMS convergence corrections to 3 for this objective.
```

Equivalent wording is valid only when it unambiguously names AMS, the feature or convergence limit, the temporary on/off/value, and the current objective. Mere requests such as “show worker usage,” “review this,” “use an app task,” or “fix everything and do not stop” are operational triggers, not feature enablement or convergence bypass. Canonical `AMS ...` commands persist; temporary overrides do not.

Turning a feature off stops new activation at a safe boundary. Existing authorized ownership, evidence, cleanup, and state-finalization obligations remain. Disabling convergence or governance finalizes any tracked campaign as `user-disabled`, `user-override`, or `terminal-pending-history`; the settings change itself is not vetoed by record-maintenance failure.

For companions, enabled, available, and compatible are distinct. App-task use requires a compatible `ams-app-task-lane` marker `4.0`. Local rollout inspection requires compatible `ams-runtime-observation` marker `4.0`; public observation can operate without it. Missing/incompatible companions cause no silent substitute.

An explicit, current, trusted project-native workflow supersedes the equivalent AMS module on conflict. Map its evidence without duplication or weakening. Mere file presence is not authority. A defective mandatory mechanism blocks the capability unless direct user authority selects another path. `AMS STATUS` reports owner and blocker.
