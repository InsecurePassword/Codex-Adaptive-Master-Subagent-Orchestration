# Adaptive Master–Subagent Orchestration

Version **3.1.0**

## Project description and synopsis

Adaptive Master–Subagent Orchestration is a distributable Codex plugin system for Sol Max-controlled, adaptive zero-to-many direct-child orchestration. The Sol Max root master retains sole authority over task decomposition, model and reasoning selection, spawning, ownership, sequencing, integration, validation, recovery, and final acceptance. Children are direct and non-delegating.

The system routes bounded work across Sol, Terra, Luna, and optional GPT-5.3-Codex-Spark profiles. It includes ownership controls, independent verification, execution-deviation supervision, durable recovery, anti-stall rules, and operator-selectable orchestration intensity. The default `auto` mode preserves the original adaptive behavior: the master chooses the smallest beneficial topology and may naturally use zero, one, or many children.

This release provides three alternative packages. Install only one option.

## Installation options

The options are ordered from the least recurring operational effort to the most manual setup responsibility requested by the operator.

### Option A — Two skills: automated installer and permanent runtime

Included skills:

- `$ams-installer`
- `$ams-orchestration`

Run `$ams-installer` once to create, verify, repair, or upgrade managed agent profiles. Use `$ams-orchestration` for all normal projects and interrupted-project recovery afterward. The runtime contains no bootstrap logic, producing a small recurring context while retaining fully automated in-app installation and maintenance.

Package: `adaptive-master-subagent-orchestration-option-a-two-skill-v3.1.0.zip`

Install from the extracted package root:

```powershell
.\Install-Package.ps1 -UpgradeManaged -Intensity auto -WhatIf
.\Install-Package.ps1 -UpgradeManaged -Intensity auto
```

When using plugin installation without the deterministic profile installer, invoke `$ams-installer` once before `$ams-orchestration`.

### Option B — One unified skill with conditional bootstrap

Included skill:

- `$adaptive-master-subagent-orchestration`

The single skill supports new work, ongoing work, recovery, and profile maintenance. Bootstrap is dormant when profiles are healthy. It runs only when explicitly requested or when a required managed profile is missing, malformed, or undiscoverable.

Package: `adaptive-master-subagent-orchestration-option-b-unified-v3.1.0.zip`

Install from the extracted package root:

```powershell
.\Install-Package.ps1 -UpgradeManaged -Intensity auto -WhatIf
.\Install-Package.ps1 -UpgradeManaged -Intensity auto
```

This is the convenience compromise: one skill to remember, with modestly higher recurring context than Options A or C.

### Option C — Bootstrap-free runtime with mandatory deterministic installer

Included skill:

- `$ams-orchestration`

The runtime contains no bootstrap, repair, migration, or installation procedure. Users must run the deterministic package installer before invoking the skill. Copying `SKILL.md` alone does not create the required profiles.

Package: `adaptive-master-subagent-orchestration-option-c-installer-required-v3.1.0.zip`

Required installation:

```powershell
.\Install-Package.ps1 -UpgradeManaged -Intensity auto -WhatIf
.\Install-Package.ps1 -UpgradeManaged -Intensity auto
```

Option C rejects profile-skipping installation. It provides the smallest runtime context, but the user assumes responsibility for completing deterministic installation first.

### Common installation controls

```powershell
# Exclude optional Spark profiles
.\Install-Package.ps1 -UpgradeManaged -ExcludeSpark

# Install selected Spark reasoning profiles
.\Install-Package.ps1 -UpgradeManaged -SparkEfforts low,medium
```

The installer registers the plugin in the personal Codex marketplace, preserves unrelated marketplace entries, installs profiles under `$CODEX_HOME/agents/`, and creates `$CODEX_HOME/ams-orchestration.toml` only when missing. Restart Codex if newly installed skills or profiles are not immediately discovered.

## Subagent classifications and intended use

### Sol

Use Sol when failure or rework would be expensive or when work is ambiguous, architectural, security-sensitive, cross-component, novel, or difficult to validate.

| Profile | Intended use |
|---|---|
| `ams_sol_low` | Small code changes, targeted fixes, quick analysis, straightforward review |
| `ams_sol_medium` | Implementation, debugging, code review, research, architecture documentation |
| `ams_sol_high` | Complex features, multi-file refactoring, security analysis, difficult debugging |
| `ams_sol_xhigh` | Ambiguous design, deep investigation, threat modeling, major project review |
| `ams_sol_max` | Hardest bounded problems, exhaustive debugging, repository-wide review, high-confidence validation |

The root master is Sol Max. `Ultra` is not a child profile; it is an orchestration classification for objectives that justify meaningful parallel workstreams while the Sol Max master retains full authority.

### Terra

Use Terra as the default everyday software-development and technical-analysis family.

| Profile | Intended use |
|---|---|
| `ams_terra_low` | Routine edits, simple scripts, basic documentation, quick questions |
| `ams_terra_medium` | Everyday coding, bug fixes, tests, documentation, summaries |
| `ams_terra_high` | Multi-step coding, moderate debugging, pull-request review, technical analysis |
| `ams_terra_xhigh` | Complex implementation, investigation, or broad review where Sol is unnecessary |
| `ams_terra_max` | Difficult cost-conscious work requiring deep reasoning and thorough checking |

### Luna

Use Luna for explicit, repeatable, high-volume work that is inexpensive to retry and easy to verify.

| Profile | Intended use |
|---|---|
| `ams_luna_low` | Extraction, classification, formatting, boilerplate, short summaries |
| `ams_luna_medium` | Documentation, test scaffolding, data cleanup, repetitive code changes |
| `ams_luna_high` | Well-scoped coding, detailed documentation, batch analysis, routine troubleshooting |
| `ams_luna_xhigh` | Larger repeatable tasks with explicit requirements and clear success criteria |
| `ams_luna_max` | Tightly specified tasks requiring maximum checking at the lowest family cost |

### GPT-5.3-Codex-Spark

Spark is optional, text-only, and supplemental. It is used where latency or separate usage capacity matters and results are mechanically verifiable.

| Profile | Intended use |
|---|---|
| `ams_spark_low` | Exact commands, narrow searches, extraction, formatting checks, mechanical evidence collection |
| `ams_spark_medium` | Multi-command tests, builds, linting, narrow reproduction, log analysis, small exact-scope changes |
| `ams_spark_high` | Bounded diagnosis, edge-case validation, or localized fixes after the failure and ownership surface are defined |

Spark is not used for architecture, security judgment, ambiguous broad debugging, visual inputs, final review, or project acceptance. Work requiring more than Spark High returns to the normal Luna/Terra/Sol routing ladder.

## Orchestration intensity, default, and intensity configuration

`auto` is the default and preserves the original orchestration behavior. It does not target a middle level of delegation. Sol Max determines the appropriate intensity from the task graph, risk, dependencies, ownership, verification needs, and available capacity.

| Intensity | Behavior |
|---|---|
| `auto` | Fully adaptive. The master may naturally choose behavior ranging from master-only execution to extreme parallelism. |
| `minimal` | Strong bias toward master-owned execution; delegate only for clear necessity or substantial advantage. |
| `moderate` | Encourage limited delegation across clear, independent workstreams without aggressive decomposition. |
| `heavy` | Proactively identify safe parallel work and use specialists and independent review more broadly. |
| `extreme` | Seek maximum meaningful safe direct-child parallelism and permit deliberate independent replication when valuable. |

Manual modes are biases, not quotas. They never override Sol Max authority, dependencies, ownership boundaries, model suitability, validation, safety, or completion criteria.

Intensity precedence:

1. Explicit current instruction: `AMS MODE auto|minimal|moderate|heavy|extreme`
2. Project configuration: `<project-root>/.codex/ams-orchestration.toml`
3. User configuration: `$CODEX_HOME/ams-orchestration.toml`
4. Built-in default: `auto`

Configuration file:

```toml
schema_version = 1
intensity = "auto"
```

Set or inspect intensity:

```powershell
.\scripts\Set-Intensity.ps1 -Mode heavy -Scope user
.\scripts\Set-Intensity.ps1 -Mode extreme -Scope project -ProjectRoot C:\path\to\repo
python .\scripts\set_intensity.py --show
```

Live instructions can temporarily override persistent configuration:

```text
AMS MODE heavy
AMS MODE auto
```

## Non-intensity configuration and package controls

### Configuration schema

`schema_version` is the only non-intensity field in `ams-orchestration.toml` for this release:

```toml
schema_version = 1
```

It identifies the supported configuration format and must remain `1`. Unknown runtime configuration keys are not silently treated as supported behavior.

### Installer and profile controls

These are installation controls, not runtime intensity settings:

| PowerShell parameter | Purpose |
|---|---|
| `-UpgradeManaged` | Back up and replace older files carrying the package's managed marker. |
| `-ExcludeSpark` | Do not install optional Spark profiles. |
| `-SparkEfforts low,medium,high` | Select which Spark effort profiles to install. |
| `-SkipProfiles` | Skip profile installation where the package permits it. Option C rejects this. |
| `-Intensity <mode>` | Set the initial user intensity only when the configuration file is missing. |
| `-WhatIf` | Preview installation without mutation. |

Python equivalents are available through `scripts/install_package.py` using `--upgrade-managed`, `--exclude-spark`, `--spark-efforts`, `--skip-profiles`, `--intensity`, and `--dry-run`.

### Environment and paths

| Setting | Effect |
|---|---|
| `CODEX_HOME` | Overrides the default Codex state directory. Profiles and user orchestration configuration are installed beneath this path. |
| Project `.codex/` directory | May hold project-level intensity configuration and project-scoped Codex instructions. |
| `agents.max_depth = 1` | Required effective topology limit: root master may create direct children; children may not delegate. |

### Managed-file behavior

Managed files carry a package marker. Installation is idempotent, preserves valid existing profiles, backs up managed files before repair or upgrade, and never silently overwrites unrelated user-authored files. Name collisions receive a nonconflicting managed filename and updated routing map where supported.

## Additional details

### Core authority and safety boundaries

- Sol Max alone controls task decomposition, spawning, model selection, ownership, integration, verification, cancellation, and completion.
- Children receive bounded work orders and do not inherit project-wide authority.
- Parallel writers require non-overlapping ownership or isolated workspaces.
- A child report of `complete` is evidence to inspect, not parent-level acceptance.
- The execution-deviation gate stops repeated unchanged retries, recursive review, speculative scope expansion, validation reduction, and nonproductive orchestration loops.
- The master continues safe unblocked work when one branch is blocked.

### Recovery behavior

Every runtime supports interrupted-project recovery. A handoff is evidence, not authority. The master verifies live branch, `HEAD`, working tree, commits, worktrees, artifacts, state, tests, and prior claims; reconstructs the task graph; resumes from the earliest unfinished or unverified dependency; and does not stop merely because a checkpoint, commit, clean tree, completed phase, or empty worker set exists.

### Work orders and results

Delegated work uses stable IDs, explicit scope, exclusions, dependencies, write ownership, success criteria, validation requirements, expected execution profile, deviation triggers, and a structured result contract. The master independently verifies all accepted child work.

### Validation and release audit

Each package contains `scripts/validate_package.py`, profile-bootstrap regression tests, `MANIFEST.sha256`, and a package audit report. Run:

```powershell
python .\scripts\validate_package.py
```

The validator checks plugin and skill structure, profile TOML, manifests, checksums, option-specific bootstrap boundaries, intensity placement, recovery invariants, deterministic installation behavior, idempotence, collision preservation, upgrade/backup behavior, and ZIP-ready content.

### Distribution and upgrades

Codex plugins use `.codex-plugin/plugin.json` and bundle skills under `skills/`. For Git or marketplace distribution, publish one selected package as the plugin root. Do not install multiple options simultaneously unless intentionally testing them because skill names and managed profiles overlap.

Use `-UpgradeManaged` for upgrades. Disable or uninstall the plugin through Codex/ChatGPT plugin controls. Profiles and orchestration configuration are retained by default because another package or project may depend on them.

### Requirements and limitations

- Python 3.11+ is required for deterministic installation and validation.
- PowerShell 7+ is recommended on Windows.
- Spark access is optional and runtime-dependent.
- The master must never invent model availability or misstate observed model/reasoning usage.
- No open-source license has been selected. Add a license before public open-source release.
