# Adaptive Master–Subagent Orchestration

Version **3.1.0**

Adaptive Master–Subagent Orchestration lets a Sol Max Codex session act as the master for a flexible group of direct subagents. The master decides when delegation is useful, how many agents to use, which model and reasoning level each task needs, and whether the returned work is acceptable.

The system supports Sol, Terra, Luna, and optional GPT-5.3-Codex-Spark profiles. It also includes safe parallel work, independent review, project recovery, and user-selectable orchestration intensity.

## Quick installation

The installer asks which package to install. Press **Enter** to choose **Option A**, the recommended package. Menu option **4** removes package-managed files.

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

The commands above work when the repository is public. For authenticated private-repository commands, automation variables, and uninstall details, see [Installer usage](INSTALLER-USAGE.md). For clone-based or offline setup, see [Manual installation](MANUAL-INSTALLATION.md).

## Choose a package

Install only one option.

| Option | Included skills | Best for |
|---|---|---|
| **A — Recommended** | `$ams-installer` and `$ams-orchestration` | Most users. Installation and repair stay separate from the smaller runtime skill. |
| **B — Unified** | `$adaptive-master-subagent-orchestration` | Users who prefer one skill. It checks profiles only when installation or repair is needed. |
| **C — Lean runtime** | `$ams-orchestration` | Users who want the smallest runtime skill and are comfortable using the external installer for setup and repair. |

All three options provide the same orchestration rules, intensity modes, model routing, validation requirements, and recovery behavior.

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

The master may complete simple work itself or launch multiple direct children when that improves speed or quality. Children cannot create their own agents.

## Model routing

The Sol Max master selects the lowest-cost profile that can reliably complete each task.

| Family | Typical use |
|---|---|
| **Sol** | Architecture, security-sensitive work, difficult debugging, major reviews, and other high-cost-of-failure tasks |
| **Terra** | Everyday implementation, bug fixes, testing, documentation, and technical analysis |
| **Luna** | Clear, repeatable, high-volume work that is easy to verify |
| **Spark** | Fast text-only commands, tests, searches, log review, and small bounded fixes |

Sol, Terra, and Luna provide Low, Medium, High, Extra High, and Max profiles. Spark provides Low, Medium, and High profiles. Spark is optional and is not used for architecture, security decisions, visual work, or final acceptance.

The root master remains Sol Max. `Ultra` describes a project that benefits from several parallel workstreams; it is not a child profile.

## Orchestration intensity

`auto` is the default. It preserves the original behavior: Sol Max decides how much delegation the project actually needs.

| Mode | Effect |
|---|---|
| `auto` | Fully adaptive. The master may use no children, one child, or many children. |
| `minimal` | Strong preference for master-only work. |
| `moderate` | Limited delegation for clear independent tasks. |
| `heavy` | More active parallel work and independent review. |
| `extreme` | Maximum useful safe parallelism, including independent replication when it adds value. |

Intensity is a preference, not an agent quota. The master still controls the final topology and must respect dependencies, write ownership, model suitability, validation, and safety.

Override the current task with:

```text
AMS MODE heavy
```

Persistent configuration can be stored at either:

```text
$CODEX_HOME/ams-orchestration.toml
<project-root>/.codex/ams-orchestration.toml
```

```toml
schema_version = 1
intensity = "auto"
```

Precedence is: current prompt, project configuration, user configuration, then the built-in `auto` default.

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
| `GITHUB_TOKEN` | Read the installer and package while the repository is private |

Advanced package flags, folder layouts, validation commands, and direct installer commands are documented in [Manual installation](MANUAL-INSTALLATION.md).

## Safety and project control

- Sol Max alone controls decomposition, spawning, routing, ownership, integration, validation, and completion.
- Each child receives a bounded work order and may edit only its assigned scope.
- Parallel writers must use separate paths or isolated workspaces.
- A child reporting `complete` does not make the project complete; the master verifies the result.
- The master stops repeated retries, recursive review, scope drift, and other nonproductive loops.
- Recovery checks the live repository instead of blindly trusting a handoff or earlier completion claim.

## Requirements

- Codex with custom-agent and skill support
- Python 3.11 or newer for package installation and validation
- Windows PowerShell 5.1+ or a POSIX-compatible Linux shell
- Spark access only if Spark profiles are selected

No open-source license has been selected yet. Keep the repository private or add a license before public open-source distribution.

## More information

- [Installer usage](INSTALLER-USAGE.md) — private-repository commands, automation, and uninstall scope
- [Manual installation](MANUAL-INSTALLATION.md) — repository tree, direct package installation, and validation
- [Option A package](adaptive-master-subagent-orchestration-option-a-two-skill/)
- [Option B package](adaptive-master-subagent-orchestration-option-b-unified/)
- [Option C package](adaptive-master-subagent-orchestration-option-c-installer-required/)
