# Adaptive Master–Subagent Orchestration

**Current release: 4.0**

AMS keeps GPT-5.6 Sol Max in charge while routing bounded project work to the lowest-cost reliable model and reasoning effort.

Core invariants remain unchanged:

- the root owns objective, task graph, physical spawning, logical hierarchy, routing, integration, acceptance, and user communication;
- workers are bounded leaves and delegated managers request root-mediated descendants;
- one active writer is allowed per mutable surface;
- profiles select requested model/effort and grant no permissions;
- only the root accepts project completion.

## Install

### Windows PowerShell

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install.ps1' | iex"
```

### Linux or macOS

```bash
curl -fsSL 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install.sh' | bash
```

The standard installer writes the core skill and 18 profiles only. It does not edit general Codex configuration, project settings, operating-system permissions, or install optional companions. See [INSTALLATION.md](INSTALLATION.md).

## Configuration

Project and global files use one extensible contract:

```text
<project-root>/.codex/ams-orchestration.toml
$CODEX_HOME/ams-orchestration.toml
```

A project file completely overrides global; they are not merged. Missing supported fields use current defaults. Unknown fields fail closed, except the retired top-level `schema_version` field, which is ignored and removed on the next authorized write. Configuration is preserved across package operations unless explicitly changed. The exact default and validation rules are normative only in `adaptive-master-subagent-orchestration/references/project-control.md`.

Useful controls:

```text
AMS STATUS
AMS ENABLE | AMS DISABLE
AMS MODE auto|minimal|balanced|moderate|heavy|extreme
AMS GOVERNANCE on|off
AMS ROOT FALLBACK on|off
AMS FEATURE <name> on|off
AMS CONVERGENCE CORRECTIONS <2-12>
AMS CONVERGENCE REDESIGNS <1-12>
AMS CONFIGURATION UPDATE [PROJECT|GLOBAL]
AMS SPARK on|off
AMS SPARK RECHECK
AMS SPARK EFFORTS low,medium,high
AMS PROFILES auto|installer
```

Canonical commands persist project settings. Temporary objective-local overrides must explicitly name the AMS feature or convergence limit; merely requesting an outcome does not enable a disabled module.

## Modular capabilities

| Capability | Default | Loaded only when |
|---|---:|---|
| Convergence control | on | governance permits it and repeated repair/review triggers the detector, or for bounded state/status/finalization |
| Work-order refinement | off | a special high-risk/state-transfer order needs its addendum |
| Evidence-bound review | off | a review is commissioned |
| Shared-worktree verification | off | multiple writers actually share one tree |
| Runtime observation | off | observation is required or evidence conflicts |
| Untrusted-evidence handling | off | untrusted output needs bounded inspection/relay |
| Task-graph safeguards | off | enhanced dependency/ownership admission is required |
| Rejected-approach handoff | off | that bounded handoff context is useful |
| Request accounting | off | the current turn explicitly requests objective-scoped accounting |
| App-task lane | off | the user authorizes it and the compatible companion is available |

A setting alone performs no action. An authoritative project-native equivalent supersedes the optional AMS module.

## Convergence control

Convergence tracks two independent limits:

```toml
convergence_correction_limit = 4
convergence_redesign_limit = 4
```

A redesign starts a new design epoch and resets only that epoch's correction count; it does not reset the parent campaign or redesign count. With defaults, five design epochs allow at most twenty ordinary correction cycles before user intervention is required.

After the first completed correction cycle or redesign, AMS writes one compact tracking record beneath the installed skill. Terminal campaigns become immutable per-campaign history records. The shared package/runtime lock, ownership lease, and generation checks prevent split writers and protect records during reinstall. These files are not a general task or recovery database.

Generic instructions such as “fix everything,” “do not stop,” or “continue until clean” never bypass convergence. A bypass must explicitly name AMS convergence, a limit, or the disclosed intervention boundary.

## Optional companions

- `ams-app-task-lane` — explicit user-visible Codex app-task/worktree transport;
- `ams-runtime-observation` — local rollout-metadata corroboration helpers.

Each requires exact AMS 4.0 compatibility and its own feature gate. Enabled, available, and compatible are distinct. Neither companion may bypass another feature toggle or become a competing orchestrator.

## Routing and intensity

| Family | Typical work |
|---|---|
| Spark | bounded mechanics with little judgment; worker-only |
| Luna | explicit repetitive low-risk work |
| Terra | normal implementation, tests, documentation, review, investigation |
| Sol | ambiguous, architectural, security-sensitive, difficult, expensive-to-fail work |

Normal intensities are `minimal`, `balanced`, `auto`, `heavy`, and `extreme`. Zergling Rush remains a separate explicit-consent mode. Intensity changes topology, not quality, acceptance, or convergence custody.

The separate Sol Ultra directive is a reduced standalone special case and intentionally excludes standard convergence control.

## Requirements

- Codex with skills and custom-subagent support
- top-level GPT-5.6 Sol Max, or verified equivalent at Max reasoning
- Windows PowerShell 5.1+ for Windows installation
- Bash plus the commands listed in [INSTALLATION.md](INSTALLATION.md) for Unix installation

Python is not a core requirement. It is used only by repository release verification and optionally by the separately installed runtime-observation companion.
