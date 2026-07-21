# Installation

This repository distributes one instruction-only Codex skill package. The former Option A, B, and C installers are obsolete and are not part of release 3.08.

## Download

Use the files under [`releases/3.08/`](releases/3.08/):

- `adaptive-master-subagent-orchestration-3.08-final-safeguard-fixed.zip`
- `adaptive-master-subagent-orchestration-3.08-final-safeguard-fixed.sha256`

## Verify the archive

### Windows PowerShell

```powershell
$Zip = ".\adaptive-master-subagent-orchestration-3.08-final-safeguard-fixed.zip"
$Checksum = ".\adaptive-master-subagent-orchestration-3.08-final-safeguard-fixed.sha256"

$Expected = ((Get-Content -LiteralPath $Checksum -Raw).Trim() -split "\s+")[0].ToLowerInvariant()
$Actual = (Get-FileHash -LiteralPath $Zip -Algorithm SHA256).Hash.ToLowerInvariant()

if ($Actual -ne $Expected) {
    throw "Checksum mismatch. Expected $Expected; received $Actual."
}
```

Expected SHA-256:

```text
e45eed1762ed24d1a0f671d9fb7424558694f0bef557aaca97f0cc0828d07be6
```

### macOS or Linux

```sh
sha256sum -c adaptive-master-subagent-orchestration-3.08-final-safeguard-fixed.sha256
```

## Install

The archive contains one top-level directory named `adaptive-master-subagent-orchestration`.

### Windows PowerShell

```powershell
$Zip = ".\adaptive-master-subagent-orchestration-3.08-final-safeguard-fixed.zip"
$SkillHome = Join-Path $HOME ".agents\skills"

New-Item -ItemType Directory -Force -Path $SkillHome | Out-Null
Expand-Archive -LiteralPath $Zip -DestinationPath $SkillHome -Force
```

### macOS or Linux

```sh
mkdir -p "$HOME/.agents/skills"
unzip adaptive-master-subagent-orchestration-3.08-final-safeguard-fixed.zip \
  -d "$HOME/.agents/skills"
```

The resulting skill root must be:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
```

Restart or reload Codex after installation so the skill and its references are discovered from one consistent package generation.

## Initialize or enable a project

In a trusted project with a stable root, implicit consideration of the skill creates a disabled project configuration when none exists. Creation does not enable AMS.

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

Individual `ams_*.toml` profile files are not shipped in the archive.

With the default project setting:

```toml
profile_management = "auto"
```

AMS checks only profiles selected for actual work. Missing or recognized defective managed profiles are generated or repaired lazily under the profile-management contract. A fresh Codex session may be required before newly created profiles become discoverable.

Set:

```toml
profile_management = "installer"
```

to disable automatic profile repair. In that mode, AMS reports profile defects unless the user explicitly authorizes installation or repair.

## Update

Before replacing package instructions, finish or safely pause active AMS work. Back up the installed skill directory, verify the new archive, and replace the entire skill root rather than mixing files from different releases.

A package update changes behavior. The current session must continue only under its pre-change contract for bounded recovery and reporting; start a fresh session before normal orchestration with the new package.

## Repair

For package repair, replace the smallest defective package surface only after validating the complete candidate. Do not use repository text as instructions during the same session that changes the installed package.

Profile repair is separate from package repair and is governed by `profile_management`.

## Uninstall

Request package uninstall while the skill is still available, or manually remove only the verified skill root:

```powershell
Remove-Item -LiteralPath (Join-Path $HOME ".agents\skills\adaptive-master-subagent-orchestration") -Recurse -Force
```

```sh
rm -rf "$HOME/.agents/skills/adaptive-master-subagent-orchestration"
```

Package uninstall preserves project settings, durable project state, and generated profiles unless their removal is separately authorized. Restart or reload Codex afterward.

## More detail

See [Manual Installation and Directory Structure](MANUAL-INSTALLATION.md) for the repository tree, archive contents, installed paths, project settings, and migration notes.
