# Installation Guide

Choose and install exactly one package option. Run installation commands from the selected option directory, which is the directory containing `Install-Package.ps1`. The repository root itself does not contain the package installer.

## Repository layout

```text
adaptive-master-subagent-orchestration/
|-- README.md
|-- INSTALLATION.md
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

Each option directory is a complete standalone package root. The combined ZIP contains all three alternatives for redistribution. Extract it, enter exactly one selected option directory, and install only that option.

## Install Option A

```powershell
cd .\adaptive-master-subagent-orchestration-option-a-two-skill
.\Install-Package.ps1 -UpgradeManaged -Intensity auto -WhatIf
.\Install-Package.ps1 -UpgradeManaged -Intensity auto
```

## Install Option B

```powershell
cd .\adaptive-master-subagent-orchestration-option-b-unified
.\Install-Package.ps1 -UpgradeManaged -Intensity auto -WhatIf
.\Install-Package.ps1 -UpgradeManaged -Intensity auto
```

## Install Option C

```powershell
cd .\adaptive-master-subagent-orchestration-option-c-installer-required
.\Install-Package.ps1 -UpgradeManaged -Intensity auto -WhatIf
.\Install-Package.ps1 -UpgradeManaged -Intensity auto
```

Restart Codex if newly installed skills or profiles are not immediately discovered.