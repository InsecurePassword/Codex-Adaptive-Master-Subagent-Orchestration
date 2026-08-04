---
name: ams-app-task-lane
description: "Explicit companion transport for AMS 4.0 to create and supervise user-visible Codex app tasks without changing AMS core authority."
---

# AMS user-visible app-task lane

Compatibility marker: `4.0` from sibling `COMPATIBILITY`.

This companion is invoked only by the active compatible AMS core route in `adaptive-master-subagent-orchestration/references/runtime-core.md`. Activate only when AMS is active, `app_task_lane = true` or an explicit objective-local override applies, the current user request explicitly authorizes a user-visible app task, compatibility matches, and no authoritative project-native task transport supersedes it. The setting alone creates nothing; implicit invocation remains disabled.

This companion never replaces or independently activates AMS. The Sol Max root remains sole orchestrator, model/effort selector, task-graph owner, correction owner, integration authority, acceptor, and user communicator.

Before use, read this companion's `references/app-task-lane.md` completely. Every optional AMS capability used inside the lane must independently pass its own core setting/override and trigger. If tools or a truthful route are unavailable, report the lane blocked rather than inventing identity, callback, routing, worktree, branch, or completion evidence.
