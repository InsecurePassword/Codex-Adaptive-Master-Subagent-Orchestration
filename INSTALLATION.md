# Installation

Release 3.09 is distributed as one instruction-only Codex skill package.

## Release identity

Package:

```text
adaptive-master-subagent-orchestration-3.09-virtual-hierarchy-final-audited.zip
```

Download:

```text
https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/3.09/adaptive-master-subagent-orchestration-3.09-virtual-hierarchy-final-audited.zip
```

SHA-256:

```text
3e3e8dc3142d5bc2411a4703982150941816c3669d5f0bb01bab2099f7a88373
```

The archive contains one top-level directory named:

```text
adaptive-master-subagent-orchestration
```

Default install location:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
```

Restart or reload Codex after installation or update.

## Windows PowerShell installation

Requirements:

- Windows PowerShell 5.1 or newer
- built-in .NET and PowerShell components

Run:

```powershell
$ErrorActionPreference = "Stop"

$ReleaseUrl = "https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/3.09/adaptive-master-subagent-orchestration-3.09-virtual-hierarchy-final-audited.zip"
$ExpectedSha256 = "3e3e8dc3142d5bc2411a4703982150941816c3669d5f0bb01bab2099f7a88373"
$Zip = Join-Path $env:TEMP "adaptive-master-subagent-orchestration-3.09.zip"
$SkillHome = Join-Path $HOME ".agents\skills"
$SkillRoot = Join-Path $SkillHome "adaptive-master-subagent-orchestration"
$Backup = "$SkillRoot.backup-3.09"
$Stage = Join-Path $env:TEMP "adaptive-master-subagent-orchestration-3.09-stage"

Invoke-WebRequest -UseBasicParsing -Uri $ReleaseUrl -OutFile $Zip

$ActualSha256 = (Get-FileHash -LiteralPath $Zip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($ActualSha256 -ne $ExpectedSha256) {
    throw "Checksum mismatch. Expected $ExpectedSha256; received $ActualSha256."
}

Remove-Item -LiteralPath $Stage -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $Stage | Out-Null
Expand-Archive -LiteralPath $Zip -DestinationPath $Stage -Force

$Candidate = Join-Path $Stage "adaptive-master-subagent-orchestration"
$Required = @(
    "SKILL.md",
    "VERSION",
    "agents\openai.yaml",
    "references\hierarchy-control.md",
    "references\intensity-control.md",
    "references\package-maintenance.md",
    "references\profile-management.md",
    "references\project-control.md",
    "references\runtime-core.md",
    "references\zergling-rush.md"
)

foreach ($RelativePath in $Required) {
    if (-not (Test-Path -LiteralPath (Join-Path $Candidate $RelativePath) -PathType Leaf)) {
        throw "The release package is missing required file: $RelativePath"
    }
}

$Version = (Get-Content -LiteralPath (Join-Path $Candidate "VERSION") -Raw).Trim()
if ($Version -ne "3.09") {
    throw "Unexpected package version: $Version"
}

New-Item -ItemType Directory -Force -Path $SkillHome | Out-Null
Remove-Item -LiteralPath $Backup -Recurse -Force -ErrorAction SilentlyContinue

if (Test-Path -LiteralPath $SkillRoot) {
    Move-Item -LiteralPath $SkillRoot -Destination $Backup
}

try {
    Move-Item -LiteralPath $Candidate -Destination $SkillRoot
    Remove-Item -LiteralPath $Backup -Recurse -Force -ErrorAction SilentlyContinue
}
catch {
    Remove-Item -LiteralPath $SkillRoot -Recurse -Force -ErrorAction SilentlyContinue
    if (Test-Path -LiteralPath $Backup) {
        Move-Item -LiteralPath $Backup -Destination $SkillRoot
    }
    throw
}
finally {
    Remove-Item -LiteralPath $Stage -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $Zip -Force -ErrorAction SilentlyContinue
}
```

## Linux or macOS installation

Requirements:

- Bash
- `curl`
- `unzip`
- `sha256sum` or `shasum`

Run:

```bash
set -euo pipefail

release_url='https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/3.09/adaptive-master-subagent-orchestration-3.09-virtual-hierarchy-final-audited.zip'
expected_sha256='3e3e8dc3142d5bc2411a4703982150941816c3669d5f0bb01bab2099f7a88373'
zip_path="$(mktemp -t ams-3.09.XXXXXX.zip)"
stage="$(mktemp -d -t ams-3.09.XXXXXX)"
skill_home="$HOME/.agents/skills"
skill_root="$skill_home/adaptive-master-subagent-orchestration"
backup="$skill_root.backup-3.09"

cleanup() {
  rm -f -- "$zip_path"
  rm -rf -- "$stage"
}
trap cleanup EXIT

curl -fL --retry 3 --output "$zip_path" "$release_url"

if command -v sha256sum >/dev/null 2>&1; then
  actual_sha256="$(sha256sum "$zip_path" | awk '{print $1}')"
else
  actual_sha256="$(shasum -a 256 "$zip_path" | awk '{print $1}')"
fi

if [ "$actual_sha256" != "$expected_sha256" ]; then
  printf 'Checksum mismatch. Expected %s; received %s.\n' "$expected_sha256" "$actual_sha256" >&2
  exit 1
fi

unzip -q "$zip_path" -d "$stage"
candidate="$stage/adaptive-master-subagent-orchestration"

required_files='SKILL.md
VERSION
agents/openai.yaml
references/hierarchy-control.md
references/intensity-control.md
references/package-maintenance.md
references/profile-management.md
references/project-control.md
references/runtime-core.md
references/zergling-rush.md'

while IFS= read -r relative_path; do
  [ -f "$candidate/$relative_path" ] || {
    printf 'The release package is missing required file: %s\n' "$relative_path" >&2
    exit 1
  }
done <<EOF
$required_files
EOF

version="$(tr -d '\r\n' < "$candidate/VERSION")"
[ "$version" = '3.09' ] || {
  printf 'Unexpected package version: %s\n' "$version" >&2
  exit 1
}

mkdir -p "$skill_home"
rm -rf -- "$backup"

if [ -e "$skill_root" ]; then
  mv -- "$skill_root" "$backup"
fi

if mv -- "$candidate" "$skill_root"; then
  rm -rf -- "$backup"
else
  rm -rf -- "$skill_root"
  if [ -e "$backup" ]; then
    mv -- "$backup" "$skill_root"
  fi
  exit 1
fi
```

## Verify the installed package

Confirm the version:

### Windows PowerShell

```powershell
Get-Content -LiteralPath "$HOME\.agents\skills\adaptive-master-subagent-orchestration\VERSION"
```

### Bash

```bash
cat "$HOME/.agents/skills/adaptive-master-subagent-orchestration/VERSION"
```

Expected output:

```text
3.09
```

Confirm that the new hierarchy reference exists:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/references/hierarchy-control.md
```

## Release-hosted installer channel

The repository also documents PowerShell and Bash installer scripts hosted under the separate `ReleaseZip` release:

```text
https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/install.ps1
https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/install.sh
```

Those scripts are pinned artifacts. Use them for release 3.09 only when their embedded package filename and SHA-256 match the 3.09 release identity at the top of this document. Do not assume that the moving installer channel and the numbered package release are synchronized.

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

AMS checks only profiles selected for actual work. It may create a missing managed profile or repair a recognized defective AMS-managed profile. Release 3.09 does not add a permanent manager profile. Sol, Terra, and Luna profiles receive worker or delegated-manager authority through bounded work orders. Spark is worker-only.

Use:

```toml
profile_management = "installer"
```

to disable automatic repair. Explicit profile installation or repair may still be requested.

A fresh Codex session may be required before newly generated or repaired profiles become available.

## Update and repair

To update or repair AMS:

1. finish or safely pause active AMS work;
2. install the complete verified 3.09 package using the instructions above;
3. preserve the previous directory until the replacement succeeds;
4. restart or reload Codex;
5. confirm that `VERSION` reports `3.09`.

Do not combine files from different releases. Release 3.09 adds `references/hierarchy-control.md`; an installation missing that file is incomplete.

## Uninstall

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