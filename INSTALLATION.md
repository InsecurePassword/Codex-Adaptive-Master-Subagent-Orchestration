# Installation

Release 3.08 is distributed as one instruction-only Codex skill package. The PowerShell and Bash installers are attached to the `ReleaseZip` GitHub release.

## Automated installation

### Windows PowerShell

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/install.ps1' | iex"
```

Requirements:

- Windows PowerShell 5.1 or newer
- built-in .NET and PowerShell components only

### Linux or macOS with Bash

```bash
curl -fsSL 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/install.sh' | bash
```

Requirements:

- Bash
- `curl`
- `unzip`
- `zipinfo`
- `sha256sum` or `shasum`

Restart or reload Codex after installation.

## What the installers do

Both installers:

1. download the pinned release package:

   ```text
   https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/adaptive-master-subagent-orchestration-3.08.zip
   ```

2. verify this SHA-256:

   ```text
   e45eed1762ed24d1a0f671d9fb7424558694f0bef557aaca97f0cc0828d07be6
   ```

3. require the exact expected package files and reject unexpected files;
4. reject unreadable, encrypted, linked, redirected, or oversized archives;
5. use an installation lock to prevent concurrent replacement;
6. extract into a temporary staging directory;
7. back up an existing AMS skill directory;
8. install the verified replacement;
9. restore the previous directory if replacement fails;
10. preserve unrelated skills, project settings, recovery state, and generated agent profiles.

Default install location:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
```

## Optional environment overrides

Normal installation should use the pinned defaults. These variables are available for controlled testing, mirrors, alternate installations, or authenticated private deployments:

| Variable | Purpose |
|---|---|
| `GITHUB_TOKEN` | Authenticate GitHub API release lookup and asset download when required |
| `AMS_RELEASE_URL` | Override the package URL |
| `AMS_EXPECTED_SHA256` | Override the expected checksum; must be exactly 64 hexadecimal characters |
| `AMS_SKILL_HOME` | Override the destination skill parent directory |

Do not override the package URL or checksum for normal public installation.

## Manual download and checksum verification

Download:

```text
https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/adaptive-master-subagent-orchestration-3.08.zip
```

### Windows PowerShell

```powershell
$Zip = ".\adaptive-master-subagent-orchestration-3.08.zip"
$Expected = "e45eed1762ed24d1a0f671d9fb7424558694f0bef557aaca97f0cc0828d07be6"
$Actual = (Get-FileHash -LiteralPath $Zip -Algorithm SHA256).Hash.ToLowerInvariant()

if ($Actual -ne $Expected) {
    throw "Checksum mismatch. Expected $Expected; received $Actual."
}
```

### Linux

```bash
printf '%s  %s\n' \
  'e45eed1762ed24d1a0f671d9fb7424558694f0bef557aaca97f0cc0828d07be6' \
  'adaptive-master-subagent-orchestration-3.08.zip' | sha256sum -c -
```

### macOS without `sha256sum`

```bash
actual="$(shasum -a 256 adaptive-master-subagent-orchestration-3.08.zip | awk '{print $1}')"
test "$actual" = 'e45eed1762ed24d1a0f671d9fb7424558694f0bef557aaca97f0cc0828d07be6'
```

## Manual extraction

The archive contains one top-level directory named `adaptive-master-subagent-orchestration`.

### Windows PowerShell

```powershell
$SkillHome = Join-Path $HOME ".agents\skills"
New-Item -ItemType Directory -Force -Path $SkillHome | Out-Null
Expand-Archive -LiteralPath ".\adaptive-master-subagent-orchestration-3.08.zip" -DestinationPath $SkillHome -Force
```

### Bash

```bash
mkdir -p "$HOME/.agents/skills"
unzip adaptive-master-subagent-orchestration-3.08.zip -d "$HOME/.agents/skills"
```

The resulting directory must be:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
```

Restart or reload Codex after installation.

## Start using AMS

Use AMS once without enabling it permanently:

```text
Use $adaptive-master-subagent-orchestration for this project.
```

Enable AMS for the current project:

```text
AMS ENABLE
```

Choose a mode and enable AMS:

```text
AMS MODE auto
```

A trusted project with no AMS configuration receives a disabled default configuration. Creating that file does not enable AMS.

## Agent profiles

Individual `ams_*.toml` profile files are not included in the ZIP.

The default setting is:

```toml
profile_management = "auto"
```

AMS checks only profiles selected for actual work. It may create a missing managed profile or repair a recognized defective AMS-managed profile. A fresh Codex session may be required before new profiles are available.

Use:

```toml
profile_management = "installer"
```

to disable automatic repair. Explicit profile installation or repair may still be requested.

## Update and repair

Rerun the release-hosted installer for the operating system.

The installer validates and stages the complete candidate, backs up the current AMS skill directory, replaces it, and restores the backup if replacement fails.

Finish or safely pause active AMS work before changing package instructions. Restart or reload Codex after the update or repair.

## Uninstall

The release installers install and update only. They do not provide an uninstall switch.

Standard uninstall removes only the AMS skill directory and preserves project settings, project recovery state, generated profiles, and unrelated skills.

Stop or safely pause active AMS work before removal.

### Windows PowerShell

```powershell
$SkillRoot = Join-Path $HOME ".agents\skills\adaptive-master-subagent-orchestration"

if (Test-Path -LiteralPath $SkillRoot) {
    $Item = Get-Item -LiteralPath $SkillRoot -Force
    if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        throw "Refusing to remove a redirected skill path: $SkillRoot"
    }
    if (-not $Item.PSIsContainer) {
        throw "The AMS skill path is not a directory: $SkillRoot"
    }
    Remove-Item -LiteralPath $SkillRoot -Recurse -Force
}
```

### Bash

```bash
skill_root="$HOME/.agents/skills/adaptive-master-subagent-orchestration"

if [ -L "$skill_root" ]; then
  printf 'Refusing to remove a redirected skill path: %s\n' "$skill_root" >&2
  exit 1
elif [ -e "$skill_root" ] && [ ! -d "$skill_root" ]; then
  printf 'The AMS skill path is not a directory: %s\n' "$skill_root" >&2
  exit 1
elif [ -d "$skill_root" ]; then
  rm -rf -- "$skill_root"
fi
```

Restart or reload Codex after removal.

Project settings and generated profiles are preserved intentionally. Complete cleanup instructions are documented in [Product Documentation](PRODUCT%20DOCUMENTATION.md#uninstall).

## More information

See [Product Documentation](PRODUCT%20DOCUMENTATION.md) for every AMS command, intensity modes, Zergling Rush, model routing, Spark controls, profile management, recovery, package maintenance, uninstall, and directory structure.
