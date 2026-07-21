# Installation

Release 3.08 is distributed as one instruction-only Codex skill package. Root-level PowerShell and Bash helpers download the pinned GitHub release asset and install it into the current user's Codex skill directory.

## Automated installation

### Windows PowerShell

Run with `powershell.exe`:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://raw.githubusercontent.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/main/install.ps1' | iex"
```

The PowerShell helper requires Windows PowerShell 5.1 or newer and uses only built-in .NET and PowerShell functionality.

### Bash

```bash
curl -fsSL 'https://raw.githubusercontent.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/main/install.sh' | bash
```

The Bash helper requires `curl`, `unzip`, `zipinfo`, and either `sha256sum` or `shasum`.

### Private repository or release access

The installers pass `GITHUB_TOKEN` to the release download when it is set:

```powershell
$env:GITHUB_TOKEN = "<token-with-repository-read-access>"
```

```bash
export GITHUB_TOKEN="<token-with-repository-read-access>"
```

When the installer script itself is not anonymously readable, retrieve it from an authenticated checkout or the GitHub Contents API, then execute the local copy.

## What the scripts do

Both installers:

1. Download this pinned release asset:

   ```text
   https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/adaptive-master-subagent-orchestration-3.08.zip
   ```

2. Verify SHA-256:

   ```text
   e45eed1762ed24d1a0f671d9fb7424558694f0bef557aaca97f0cc0828d07be6
   ```

3. Reject unexpected top-level paths, traversal, duplicate paths, symbolic links, missing required files, excessive entries, and excessive expanded size.
4. Extract the package into a staging directory under the destination skill directory.
5. Replace only:

   ```text
   $HOME/.agents/skills/adaptive-master-subagent-orchestration/
   ```

6. Restore the prior skill directory if replacement fails.
7. Leave unrelated installed skills, project settings, durable project state, and generated agent profiles unchanged.

## Optional environment overrides

| Variable | Purpose |
|---|---|
| `GITHUB_TOKEN` | Authenticate the release download when required |
| `AMS_RELEASE_URL` | Override the pinned release URL for testing or mirrors |
| `AMS_EXPECTED_SHA256` | Override the pinned checksum; must be 64 hexadecimal characters |
| `AMS_SKILL_HOME` | Override the destination skill parent directory |

Overrides are intended for controlled testing, mirrors, or private deployments. Normal installation should use the pinned defaults.

## Manual download and verification

Release URL:

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

### macOS or Linux

```bash
printf '%s  %s\n' \
  'e45eed1762ed24d1a0f671d9fb7424558694f0bef557aaca97f0cc0828d07be6' \
  'adaptive-master-subagent-orchestration-3.08.zip' | sha256sum -c -
```

On macOS without `sha256sum`:

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

The resulting root must be:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
```

Restart or reload Codex after installation.

## Initialize or enable a project

In a trusted project with a stable root, implicit consideration creates a disabled project configuration when none exists. Creation does not enable AMS.

Enable it persistently:

```text
AMS ENABLE
```

Select a normal intensity and enable it:

```text
AMS MODE auto
```

Use it for one objective without persistent enablement:

```text
Use $adaptive-master-subagent-orchestration for this objective.
```

## Profile setup

Individual `ams_*.toml` profile files are not shipped. With `profile_management = "auto"`, AMS checks only profiles selected for actual work and generates or repairs recognized managed profiles lazily. A fresh Codex session may be required before newly created profiles become discoverable.

Set `profile_management = "installer"` to disable automatic profile repair and report defects instead.

## Update and repair

Rerun either installer to replace the installed 3.08 skill root from the pinned release. The helper stages the candidate, verifies it, backs up the existing skill, and restores the backup if replacement fails.

A package change alters runtime instructions. Finish or safely pause active AMS work and restart or reload Codex after replacement.

## Uninstall

The download helpers install and update only. To uninstall manually:

```powershell
Remove-Item -LiteralPath (Join-Path $HOME ".agents\skills\adaptive-master-subagent-orchestration") -Recurse -Force
```

```bash
rm -rf "$HOME/.agents/skills/adaptive-master-subagent-orchestration"
```

Uninstalling the skill preserves project settings, durable project state, and generated profiles unless their removal is separately authorized.

See [Manual Installation and Directory Structure](MANUAL-INSTALLATION.md) for the full layout and migration notes.
