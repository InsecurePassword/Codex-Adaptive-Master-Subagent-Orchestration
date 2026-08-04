---
name: ams-runtime-observation
description: "Optional AMS 4.0 local rollout-metadata corroboration companion with bounded allowlisted output."
---

# AMS runtime-observation companion

Compatibility marker: `4.0` from sibling `COMPATIBILITY`.

Use only when active compatible AMS has `runtime_observation = true` or an explicit objective-local override, core `runtime-observation.md` has exhausted public metadata, local corroboration is required or evidence conflicts, and no project-native observer supersedes it. This skill never activates AMS, selects routing, grants permissions, or inspects arbitrary sessions.

Resolve the absolute directory containing this active companion `SKILL.md`. Choose only the matching helper beneath that exact root:

```text
<companion-root>/tools/inspect-agent-runtime.py
<companion-root>/tools/Inspect-AgentRuntime.ps1
```

Verify the selected helper is a regular non-redirected file beneath the companion root. Execute its absolute path, for example:

```text
python3 <absolute-companion-root>/tools/inspect-agent-runtime.py <thread-id> [--sessions-dir <dir>]
powershell.exe -NoProfile -ExecutionPolicy Bypass -File <absolute-companion-root>/tools/Inspect-AgentRuntime.ps1 -ThreadId <thread-id> [-SessionsDir <dir>]
```

Never fall back to a project-relative `tools/` path. Require one exact lowercase UUID and accept only the helper's allowlisted JSON. Local metadata corroborates runtime records; it is not cryptographic attestation.
