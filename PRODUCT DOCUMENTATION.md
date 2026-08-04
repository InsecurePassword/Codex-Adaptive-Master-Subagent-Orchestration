# Product Documentation

**Product:** Adaptive Master–Subagent Orchestration
**Release:** 4.0

## Product boundary

AMS keeps a GPT-5.6 Sol Max root in control of objective, task graph, physical dispatch, logical hierarchy, adaptive model/effort routing, ownership, integration, acceptance, and user communication. Workers are leaves; delegated managers request root-mediated descendants. Profiles remain permission-neutral.

## Components and state

Core installation writes:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
$CODEX_HOME/agents/ams_*.toml
```

It does not edit general Codex configuration or operating-system permissions. Project/global AMS configuration is user-owned and preserved. The only AMS-specific durable runtime state is convergence tracking/history under the skill's `.runtime/convergence/`, governed by `adaptive-master-subagent-orchestration/references/convergence-control.md`.

## Configuration and controls

The one master contract, exact defaults, precedence, legacy `schema_version` handling, validation, and controls are normative in `adaptive-master-subagent-orchestration/references/project-control.md`. Missing supported fields resolve from current defaults; other unknown fields fail closed. Project settings completely override global settings.

## Runtime architecture

`adaptive-master-subagent-orchestration/SKILL.md` is the bootstrap/router. `adaptive-master-subagent-orchestration/references/runtime-core.md` owns active authority, adaptive routing, canonical work orders/results, module gates, lightweight convergence detection, and completion. Rare behavior is isolated in one lazy reference per capability. Repository verification and size measurement remain outside the install manifest.

## Governance and convergence

Governance adds lifecycle, proportional review, convergence, acceptance, and handoff behavior while preserving core authority. Direct current-turn instructions may invoke a named governance capability while full governance is off.

Convergence counts ordinary correction cycles per design epoch and material redesigns per parent campaign. It uses a shared package/runtime lock, owner lease, generation fencing, bounded tracking records, and immutable terminal history records. Pre-trigger campaigns are finalized on acceptance, cancellation, supersession, disable, or explicit override. Root fallback cannot preempt active convergence and always retains its independent-validation requirement.

The separate Sol Ultra directive intentionally excludes standard convergence control and operates under its own reduced standalone contract.

## Optional capabilities

Feature names, persistent controls, and temporary override grammar are normative in `adaptive-master-subagent-orchestration/references/feature-control.md`. Optional capabilities load only when enabled or explicitly overridden, operationally triggered, and not superseded by a trusted project-native equivalent. App-task and local rollout observation are separate compatibility-gated companions.

## Package operations

Installers verify the manifest twice, lengths/hashes, version, profiles, runtime-state format, and exact preservation. They acquire the same package/runtime lock used by convergence state. Supported downgrade preparation exports runtime state before invoking an older installer; direct downgrade may destroy it.

## Directory structure

```text
Codex-Adaptive-Master-Subagent-Orchestration/
├── README.md
├── INSTALLATION.md
├── PRODUCT DOCUMENTATION.md
├── SOL-ULTRA-AMS-EXTREME-ORCHESTRATION-PROMPT.md
├── install-manifest.txt
├── install.ps1
├── install.sh
├── adaptive-master-subagent-orchestration/
│   ├── SKILL.md
│   ├── VERSION
│   ├── agents/openai.yaml
│   ├── assets/agent-profiles/
│   └── references/
└── extensions/
    ├── ams-app-task-lane/
    └── ams-runtime-observation/
```
