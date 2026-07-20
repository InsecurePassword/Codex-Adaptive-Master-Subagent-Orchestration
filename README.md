# Adaptive Master–Subagent Orchestration

Version **3.1.0**

Adaptive Master–Subagent Orchestration is a skill that lets a Sol Max Codex session manage a flexible group of direct subagents. The master decides when delegation is useful, how many agents to use, which model and reasoning level each task needs, and whether the returned work is acceptable.

The system supports Sol, Terra, Luna, and (if available) optional GPT-5.3-Codex-Spark profiles. It also includes safe parallel work, independent review, project recovery, and user-selectable activity levels.

## Quick installation

The installer asks which package to install. Press **Enter** to choose. **Option A** is the recommended package for most users, while **Option B** is the simplest and requires the least amount of configuration. Menu option **4** removes package-managed files.

### Windows

Run from Windows PowerShell or Command Prompt:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://raw.githubusercontent.com/InsecurePassword/adaptive-master-subagent-orchestration/refs/heads/main/install.ps1' | iex"
```

### Linux

```sh
curl -fsSL https://raw.githubusercontent.com/InsecurePassword/adaptive-master-subagent-orchestration/refs/heads/main/install.sh | sh
```

The installer downloads the repository, checks the selected package, installs its profiles and skills, and keeps unrelated Codex files unchanged.

For automation variables and uninstall details, see [Installer usage](INSTALLER-USAGE.md). For clone-based or offline setup, see [Manual installation](MANUAL-INSTALLATION.md).

## Choose a package

Install only one option.

| Option | Included skills | Best for |
|---|---|---|
| **A-Recommended** | `$ams-installer` and `$ams-orchestration` | Most users. Installation and repair stay separate from the smaller runtime skill. |
| **B-Unified** | `$adaptive-master-subagent-orchestration` | Users who prefer one skill. It checks profiles only when installation or repair is needed. |
| **C-Lean runtime** | `$ams-orchestration` | Users who want the smallest runtime skill and are comfortable using the external installer for setup and repair. |

All three options provide the same orchestration rules, intensity modes, model routing, validation requirements, and recovery behavior.  **Option B** requires the least amount of configuration, but may consume more tokens than the other options.

## Use the skill

After installation, restart Codex if the new skill is not immediately visible.

For Options A and C:

```text
Use $ams-orchestration to complete this project.
```

For Option B:

```text
Use $adaptive-master-subagent-orchestration to complete this project.
```

Option A also installs `$ams-installer`. Use it only to check, repair, or upgrade the managed profiles.

The master may complete simple work itself or launch multiple direct subagents when that improves speed or quality. Subagents cannot create their own agents.

## Model routing

The Sol Max master selects the lowest-cost profile that can reliably complete each task.

| Family | Typical use |
|---|---|
| **Sol** | Architecture, security-sensitive work, difficult debugging, major reviews, and other tasks where mistakes would be expensive |
| **Terra** | Everyday implementation, bug fixes, testing, documentation, and technical analysis |
| **Luna** | Clear, repeatable, high-volume work that is easy to verify |
| **Spark** | Fast text-only commands, tests, searches, log review, and small, clearly defined fixes |

Sol, Terra, and Luna provide Low, Medium, High, Extra High, and Max profiles. Spark provides Low, Medium, and High profiles. Spark is optional (if available) and is not used for architecture, security decisions, visual work, or final acceptance.

Sol Max is always the master agent. `Ultra` refers only to the Codex reasoning setting and is not an orchestration mode. The highest orchestration intensity is `extreme`.

## Orchestration intensity

By default, the skill runs in **Auto** mode. No configuration is required.

| Mode | Effect |
|---|---|
| `auto` | Fully adaptive. The master may use no children, one child, or many children. |
| `minimal` | Strong preference for master-only work. |
| `moderate` | Limited delegation for clear independent tasks. |
| `heavy` | More active parallel work and independent review. |
| `extreme` | Maximum useful safe parallelism, including two agents checking the same important task when that adds confidence. |

Intensity is a preference, not a required agent count. The master still decides the final agent setup and must respect dependencies, file ownership, model suitability, validation, and safety.

If you want to change the default behavior, create an `ams-orchestration.toml` file in **one** of the following locations:

**For all projects (global default):**

```text
$CODEX_HOME/ams-orchestration.toml
```

**For a single project only (overrides the global setting):**

```text
<project-root>/.codex/ams-orchestration.toml
```

Example:

```toml
schema_version = 1
intensity = "auto"
```

Replace `auto` with one of:

- `auto` *(recommended)*
- `minimal`
- `moderate`
- `heavy`
- `extreme`

When both files exist, the project configuration takes precedence over the global configuration.

## Installer configuration

The remote installers support these environment variables:

| Variable | Purpose |
|---|---|
| `AMS_INSTALL_OPTION` | Select `A`, `B`, `C`, or `UNINSTALL` without the menu |
| `AMS_INTENSITY` | Set the initial intensity |
| `AMS_EXCLUDE_SPARK=1` | Skip optional Spark profiles |
| `AMS_SPARK_EFFORTS` | Choose `low`, `medium`, and/or `high` Spark profiles |
| `AMS_UNINSTALL_FORCE=1` | Confirm non-interactive uninstall |
| `CODEX_HOME` | Use a non-default Codex state directory |

Advanced package flags, folder layouts, validation commands, and direct installer commands are documented in [Manual installation](MANUAL-INSTALLATION.md).

## Safety and project control

- Sol Max alone controls how work is split, when agents are started, which models are used, who owns each change, how results are combined, and when the project is complete.
- Each subagent receives a clear, limited task and may edit only its assigned files or area.
- Subagents writing at the same time must use separate files or isolated workspaces.
- A subagent reporting `complete` does not finish the project; the master still checks the result.
- The master stops repeated retries, repeated reviews, work expanding beyond the request, and other unproductive loops.
- Recovery checks the live repository instead of blindly trusting a handoff or earlier completion claim.

## Requirements

- Codex with custom-agent and skill support
- Python 3.11 or newer for package installation and validation
- Windows PowerShell 5.1+ or a POSIX-compatible Linux shell
- Spark access only if Spark profiles are selected

No license has been selected. Add one before redistributing the project.

## More information

- [Installer usage](INSTALLER-USAGE.md) — automation and uninstall scope
- [Manual installation](MANUAL-INSTALLATION.md) — repository tree, direct package installation, and validation
- [Option A package](adaptive-master-subagent-orchestration-option-a-two-skill/)
- [Option B package](adaptive-master-subagent-orchestration-option-b-unified/)
- [Option C package](adaptive-master-subagent-orchestration-option-c-installer-required/)
