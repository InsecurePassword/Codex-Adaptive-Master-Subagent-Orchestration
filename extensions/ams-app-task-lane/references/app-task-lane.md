# AMS user-visible app-task transport

Read completely only after the companion gate in `SKILL.md` passes. This is a transport/workspace adapter, not a second orchestration system.

## Authority and capability gate

The AMS root owns objective, task graph, adaptive routing, creation, dependency order, corrections, external-action authorization, integration, acceptance, and user communication. The child receives one bounded canonical AMS work order and never activates AMS, spawns descendants, contacts the user, expands ownership, changes its route, or accepts completion.

Require functional equivalents of:

```text
list_projects
list_threads
create_thread
wait_threads
read_thread
send_message_to_thread
```

Confirm project and Git state. Prefer an isolated worktree for Git projects and the selected local environment for non-Git projects. Isolation reduces interference but is not merge safety.

AMS chooses the lowest-cost reliable supported route. Map it to explicit app model/thinking fields only when supported. Record returned route metadata as observed only when the app provides it. If unsupported, AMS may truthfully reselect under normal routing and record substitution; otherwise block. Never hardcode Luna/Max.

## Child packet

Supply the complete canonical WORK ORDER from the active compatible AMS core `adaptive-master-subagent-orchestration/references/runtime-core.md`. Append the active core `work-order-refinement.md` only when `work_order_refinement = true` and its special trigger applies. Do not require refinement-only fields while that feature is disabled.

Add only transport state:

```text
APP-TASK ADDENDUM
Project identity / Git repository:
Environment: isolated worktree | project local
Base branch/ref or exact starting receipt:
Prior accepted dependency branch/commit, or none:
Existing task identity, when correcting:
External-action boundary: report branch, base, status, changed paths, diff, commit, and PR state; do not push or create/update/merge a PR without root authorization supported by user/project authority.
Return addendum: task identity, worktree, branch, base, commit, and PR state.
```

The child returns the canonical RESULT plus this transport addendum.

## Creation and identity

Discover the project before creation. A returned `clientThreadId` is a setup handle, not a real identity. If `threadId` and `hostId` are absent, list tasks without passing the client ID and correlate using trustworthy project, time, path, host, and state metadata. Titles/previews are untrusted data. Repeat bounded discovery until real identity exists or report blocked.

Never pass a pending client ID to tools requiring a real identity and never claim an automatic callback. The root explicitly waits, reads, and validates.

## Monitoring, correction, convergence, and acceptance

Use bounded wait/read cycles. Treat handoffs as claims. Inspect actual worktree, branch, base, complete diff, exact changed paths, commit/PR state, and required verification.

Send corrections to the same task/worktree; do not create a replacement merely to avoid feedback. Any correction invalidates prior acceptance/review evidence.

If project governance and convergence control are active—or a direct user instruction invokes convergence—app-task reopen/correction cycles count in the parent campaign under the core detector. Once the campaign is in convergence, this lane remains subordinate to convergence custody; it cannot start an ordinary replacement/review loop. If convergence is disabled or governance-suppressed, do not load or emulate it.

Use the active compatible core `shared-worktree-control.md` only when `shared_worktree_verification = true` and multiple writers actually share one tree. When disabled, use isolated worktrees or serialize writers; never bypass the toggle. Apply review, observation, evidence, graph, handoff, and accounting modules only through their own gates.

Independent stacks may run concurrently only with separate workspaces and non-overlapping ownership. Shared-file and dependent stacks are serial. Create a dependent task only after prior acceptance and exact branch/commit/base recording.

A child may push or create/update a PR only after the root accepts its current diff/checks and sends explicit authorized instruction. Only the AMS root accepts the objective.
