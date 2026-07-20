# Manual Installation

Most users should use the root installer described in the main [README](README.md). This guide is for cloned repositories, offline installation, direct package installation, and installer validation.

Install exactly one package option.

## Requirements

- Python 3.11 or newer
- Windows PowerShell 5.1+ on Windows, or a POSIX-compatible shell on Linux
- A Codex installation that supports skills and custom agents

`CODEX_HOME` may be set to use a non-default Codex state directory. The root installers also accept `AMS_HOME` or their platform-specific home-directory argument for test or alternate installations.

## Repository layout

```text
adaptive-master-subagent-orchestration/
|-- README.md
|-- INSTALLATION.md
|-- INSTALLER-USAGE.md
|-- INSTALLER-AUDIT.md
|-- MANUAL-INSTALLATION.md
|-- install.ps1
|-- install.sh
|-- scripts/
|   |-- audit_installers.py
|   |-- audit_markdown.py
|   `-- process_utils.py
|-- tests/
|   `-- test_installers.py
|-- adaptive-master-subagent-orchestration-option-a-two-skill/
|   |-- Install-Package.ps1
|   |-- MANIFEST.sha256
|   |-- assets/agent-profiles/
|   |-- config/
|   |-- scripts/
|   |   |-- Install-AgentProfiles.ps1
|   |   |-- Set-Intensity.ps1
|   |   |-- bootstrap_profiles.py
|   |   |-- install_package.py
|   |   |-- process_utils.py
|   |   |-- set_intensity.py
|   |   |-- test_bootstrap.py
|   |   |-- test_installation.py
|   |   |-- test_intensity.py
|   |   `-- validate_package.py
|   `-- skills/
|-- adaptive-master-subagent-orchestration-option-b-unified/
|   `-- ...same installer and validation structure...
`-- adaptive-master-subagent-orchestration-option-c-installer-required/
    `-- ...same installer and validation structure...
```

Each option directory is a complete package root.

## Root installer without the menu

### Windows

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Option A
```

### Linux

```sh
sh ./install.sh --option A
```

Use `B` or `C` for another package. See [Installer usage](INSTALLER-USAGE.md) for all command-line options, environment variables, offline ZIP installation, and uninstall commands.

## Direct package installation

### Option A — Recommended

Installs `$ams-installer` and `$ams-orchestration`.

```powershell
cd .\adaptive-master-subagent-orchestration-option-a-two-skill
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install-Package.ps1 -UpgradeManaged -Intensity auto
```

```sh
cd ./adaptive-master-subagent-orchestration-option-a-two-skill
python3 -B -E -s -S ./scripts/install_package.py --upgrade-managed --intensity auto
```

### Option B — Unified

Installs `$adaptive-master-subagent-orchestration`.

```powershell
cd .\adaptive-master-subagent-orchestration-option-b-unified
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install-Package.ps1 -UpgradeManaged -Intensity auto
```

```sh
cd ./adaptive-master-subagent-orchestration-option-b-unified
python3 -B -E -s -S ./scripts/install_package.py --upgrade-managed --intensity auto
```

### Option C — Lean runtime

Installs `$ams-orchestration` and requires managed profile installation.

```powershell
cd .\adaptive-master-subagent-orchestration-option-c-installer-required
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install-Package.ps1 -UpgradeManaged -Intensity auto
```

```sh
cd ./adaptive-master-subagent-orchestration-option-c-installer-required
python3 -B -E -s -S ./scripts/install_package.py --upgrade-managed --intensity auto
```

## Package installer options

| PowerShell | Python | Purpose |
|---|---|---|
| `-HomeDirectory <path>` | `--home <path>` | Use an alternate installation home |
| `-UpgradeManaged` | `--upgrade-managed` | Back up and update older package-managed files |
| `-ExcludeSpark` | `--exclude-spark` | Skip optional Spark profiles and remove previously managed Spark profiles |
| `-SparkEfforts low,medium,high` | `--spark-efforts low,medium,high` | Select Spark profiles |
| `-SkipProfiles` | `--skip-profiles` | Skip profile installation where allowed; Option C rejects this |
| `-Intensity <mode>` | `--intensity <mode>` | Set the initial intensity if no user configuration exists |
| `-WhatIf` | `--dry-run` | Preview changes without installing |
| `-Uninstall -Force` | `--uninstall --yes` | Remove package-managed installation data |

## Validate installation tooling

Run the complete repository-level audit:

```sh
python3 -B -E -s -S ./scripts/audit_installers.py
```

Run one package's installation-tool audit:

```sh
python3 -B -E -s -S ./scripts/validate_package.py --scripts-only
```

Run the complete package validator, including package and skill structure:

```sh
python3 -B -E -s -S ./scripts/validate_package.py
```

The scripts-only audit checks manifests, plugin metadata, Python and shell syntax, profile installation, intensity handling, dry-runs, updates, option replacement, rollback, locks, timeouts, and uninstall behavior.

## Offline installation

Pass a repository ZIP to the root installer:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Option A -ArchivePath .\repository.zip
```

```sh
sh ./install.sh --option A --archive-path ./repository.zip
```

The installer validates archive paths and the selected package manifest before installing.

## Uninstall

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Option Uninstall -Force
```

```sh
sh ./install.sh --option UNINSTALL --force
```

The uninstall path removes package-managed files while preserving pre-existing unmarked user configuration, unrelated profiles, marketplace entries, plugins, and project-level `.codex` configuration.

Restart Codex after installation, package switching, or removal if the skill list does not update immediately.
