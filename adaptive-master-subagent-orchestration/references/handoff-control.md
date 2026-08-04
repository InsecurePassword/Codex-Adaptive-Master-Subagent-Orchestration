# AMS rejected-approach handoff control

Read completely only when `rejected_approach_handoff = true`, AMS is creating a user-visible handoff, rejected-approach context is useful, and no authoritative project-native handoff supersedes it. The setting never creates a handoff.

Add one optional section:

```text
Rejected approaches / do not repeat:
- <approach> — <decisive evidence or user decision>; reconsider only if <condition>.
```

Include at most three entries. Flatten each to one line, remove control characters, bound each to 160 characters, deduplicate exact normalized entries, and omit the section when empty. Include only approaches explicitly rejected by the user or contradicted by current evidence. Omit speculation, secrets, raw logs, full history, duplicate notes, and facts already present in authoritative state.

When convergence is active, its separate compact campaign receipt is mandatory under `convergence-control.md`; do not consume this three-entry budget for campaign state.

This reference authorizes no handoff file, cursor, general recovery ledger, or durable memory.
