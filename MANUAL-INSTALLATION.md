# Manual Installation

Most users should use the interactive remote installer in the main [README](README.md). This guide is for users who clone the repository, install without the remote bootstrap script, work offline, or need the full package layout.

Install exactly one package option.

## Requirements

- Python 3.11 or newer
- Windows PowerShell 5.1+ on Windows, or a POSIX-compatible shell on Linux
- A Codex installation that supports skills and custom agents

`CODEX_HOME` may be set before installation to use a non-default Codex state directory.

## Repository layout

```text
adaptive-master-subagent-orchestration/
|-- README.md
|-- MANUAL-INSTALLATION.md
|-- INSTALLER-USAGE.md
|-- install.ps1
|-- install.sh
|-- adaptive-master-subagent-orchestration-all-options-v3.1.0.zip
|-- adaptive-master-subagent-orchestration-option-a-two-skill/
|   |-- .codex-plugin/
|   |   `-- plugin.json
|   |-- Install-Package.ps1
|   |-- README.md
|   |-- AUDIT.md
|   |-- CHANGELOG.md
|   |-- VERSION
|   |-- PACKAGE-OPTION
|   |-- MANIFEST.sha256
|   |-- assets/
|   |   `-- agent-profiles/
|   |       |-- ams_sol_*.toml
|   |       |-- ams_terra_*.toml
|   |       |-- ams_luna_*.toml
|   |       `-- ams_spark_*.toml
|   |-- config/
|   |   `-- ams-orchestration.example.toml
|   |-- scripts/
|   |   |-- Install-AgentProfiles.ps1
|   |   |-- Set-Intensity.ps1
|   |   |-- bootstrap_profiles.py
|   |   |-- install_package.py
|   |   |-- set_intensity.py
|   |   |-- test_bootstrap.py
|   |   `-- validate_package.py
|   `-- skills/
|       |-- ams-installer/
|       |   |-- SKILL.md
|       |   `-- agents/openai.yaml
|       `-- ams-orchestration/
|           |-- SKILL.md
|           `-- agents/openai.yaml
|-- adaptive-master-subagent-orchestration-option-b-unified/
|   |-- .codex-plugin/plugin.json
|   |-- Install-Package.ps1
|   |-- assets/agent-profiles/
|   |-- config/
|   |-- scripts/
|   `-- skills/
|       `-- adaptive-master-subagent-orchestration/
|           |-- SKILL.md
|           `-- agents/openai.yaml
`-- adaptive-master-subagent-orchestration-option-c-installer-required/
    |-- .codex-plugin/plugin.json
    |-- Install-Package.ps1
    |-- assets/agent-profiles/
    |-- config/
    |-- scripts/
    `-- skills/
        `-- ams-orchestration/
            |-- SKILL.md
            `-- agents/openai.yaml
```

Each option directory is a complete package root. Run its installer from that directory.

## Option A — Recommended

Option A installs `$ams-installer` and `$ams-orchestration`.

### Windows

```powershell
cd .\adaptive-master-subagent-orchestration-option-a-two-skill
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install-Package.ps1 -UpgradeManaged -Intensity auto
```

### Linux

```sh
cd ./adaptive-master-subagent-orchestration-option-a-two-skill
python3 ./scripts/install_package.py --upgrade-managed --intensity auto
```

## Option B — Unified

Option B installs `$adaptive-master-subagent-orchestration`.

### Windows

```powershell
cd .\adaptive-master-subagent-orchestration-option-b-unified
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install-Package.ps1 -UpgradeManaged -Intensity auto
```

### Linux

```sh
cd ./adaptive-master-subagent-orchestration-option-b-unified
python3 ./scripts/install_package.py --upgrade-managed --intensity auto
```

## Option C — Lean runtime

Option C installs `$ams-orchestration` and requires profile installation.

### Windows

```powershell
cd .\adaptive-master-subagent-orchestration-option-c-installer-required
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install-Package.ps1 -UpgradeManaged -Intensity auto
```

### Linux

```sh
cd ./adaptive-master-subagent-orchestration-option-c-installer-required
python3 ./scripts/install_package.py --upgrade-managed --intensity auto
```

## Package installer options

| PowerShell | Python | Purpose |
|---|---|---|
| `-UpgradeManaged` | `--upgrade-managed` | Back up and update older package-managed files |
| `-ExcludeSpark` | `--exclude-spark` | Skip optional Spark profiles |
| `-SparkEfforts low,medium,high` | `--spark-efforts low,medium,high` | Select Spark profiles |
| `-SkipProfiles` | `--skip-profiles` | Skip profile installation where allowed; Option C rejects this |
| `-Intensity <mode>` | `--intensity <mode>` | Set the initial intensity if no user config exists |
| `-WhatIf` | `--dry-run` | Preview changes without installing |

## Validate a package

From the selected option directory:

```sh
python3 ./scripts/validate_package.py
```

The validator checks plugin structure, skill metadata, profile TOML, package checksums, installer behavior, intensity configuration, recovery rules, and option-specific bootstrap boundaries.

## Uninstall

The easiest safe uninstall is menu option **4** in the root remote installer:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://raw.githubusercontent.com/InsecurePassword/adaptive-master-subagent-orchestration/refs/heads/main/install.ps1' | iex"
```

```sh
curl -fsSL https://raw.githubusercontent.com/InsecurePassword/adaptive-master-subagent-orchestration/refs/heads/main/install.sh | sh
```

For non-interactive uninstall and the exact removal scope, see [Installer usage](INSTALLER-USAGE.md).

Restart Codex after installation or removal if the skill list does not update immediately.
