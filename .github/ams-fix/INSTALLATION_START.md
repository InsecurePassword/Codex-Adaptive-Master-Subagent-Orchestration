## Start using AMS

The installed skill is visible for implicit invocation and bootstraps AMS before ordinary work on every top-level root project turn. It checks the project configuration first and the optional global configuration only when the project file is absent.

### Use AMS once

```text
Use $adaptive-master-subagent-orchestration for this project.
```

### Project-specific persistence

From inside a trusted project:

```text
AMS STATUS
AMS ENABLE
AMS MODE auto
```

These commands write only:

```text
<project-root>/.codex/ams-orchestration.toml
```

`AMS ENABLE` sets `enabled = true`. `AMS MODE auto` sets `enabled = true` and `intensity = "auto"`. `AMS STATUS` is read-only. Project commands never modify global persistence.

### Global persistence (manual only)

Global settings supply defaults to trusted projects that do not contain a project settings file. The path is:

```text
$CODEX_HOME/ams-orchestration.toml
```

When `CODEX_HOME` is unset, use:

```text
$HOME/.codex/ams-orchestration.toml
```

The global and project files use the same schema. Project settings override global settings completely; the files are not merged. An invalid project file blocks implicit activation instead of falling back to global settings. To opt one project out of a globally enabled configuration, create a valid project file with `enabled = false`.

No AMS command creates, changes, repairs, migrates, or deletes the global file. Create or copy it manually, then restart or reload Codex.

#### Create a global auto-mode file with Windows PowerShell

```powershell
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$GlobalConfig = Join-Path $CodexHome 'ams-orchestration.toml'
New-Item -ItemType Directory -Force -Path $CodexHome | Out-Null

$Content = @'
schema_version = 2
enabled = true
allow_implicit_invocation = true
intensity = "auto"
spark_enabled = true
spark_available = true
spark_efforts = ["low", "medium", "high"]
profile_management = "auto"
'@

[IO.File]::WriteAllText(
    $GlobalConfig,
    $Content.TrimStart() + "`n",
    [Text.UTF8Encoding]::new($false)
)
```

#### Copy a project configuration with Windows PowerShell

```powershell
$ProjectConfig = 'G:\path\to\project\.codex\ams-orchestration.toml'
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
New-Item -ItemType Directory -Force -Path $CodexHome | Out-Null
Copy-Item -LiteralPath $ProjectConfig -Destination (Join-Path $CodexHome 'ams-orchestration.toml')
```

#### Create a global auto-mode file with Bash

```bash
codex_home="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$codex_home"
cat > "$codex_home/ams-orchestration.toml" <<'EOF'
schema_version = 2
enabled = true
allow_implicit_invocation = true
intensity = "auto"
spark_enabled = true
spark_available = true
spark_efforts = ["low", "medium", "high"]
profile_management = "auto"
EOF
```

#### Copy a project configuration with Bash

```bash
codex_home="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$codex_home"
cp /path/to/project/.codex/ams-orchestration.toml "$codex_home/ams-orchestration.toml"
```
