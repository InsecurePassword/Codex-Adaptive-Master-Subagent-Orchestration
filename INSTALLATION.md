# Installation

Release 3.09 is distributed as one instruction-only Codex skill package through two synchronized GitHub release channels.

## Recommended one-line installation

### Windows PowerShell

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/install.ps1' | iex"
```

Requirements:

- Windows PowerShell 5.1 or newer
- built-in .NET and PowerShell components

### Linux or macOS with Bash

```bash
curl -fsSL 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/install.sh' | bash
```

Requirements:

- Bash
- `curl`
- `unzip`
- `zipinfo`
- `awk`
- `sort`
- `cmp`
- either `sha256sum` or `shasum`

Restart or reload Codex after installation or update.

## Release channels

### Stable installer channel

The one-line commands download these assets from the `ReleaseZip` release:

```text
ReleaseZip/
├── install.ps1
├── install.sh
└── adaptive-master-subagent-orchestration-3.09.zip
```

Package URL:

```text
https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/adaptive-master-subagent-orchestration-3.09.zip
```

### Numbered audited release

The numbered `3.09` release retains the descriptive audit filename:

```text
https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/3.09/adaptive-master-subagent-orchestration-3.09-virtual-hierarchy-final-audited.zip
```

The two ZIP filenames identify the same audited 3.09 package content. Both installation paths use this SHA-256:

```text
74e48106fc26a6516db3e9f6cc15e66e745d4fe71e24fdee233a6cf972fe4514
```

The archive contains one top-level directory:

```text
adaptive-master-subagent-orchestration/
```

Default install location:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
```

## What the installers verify

Both installers:

1. download `ReleaseZip/adaptive-master-subagent-orchestration-3.09.zip`;
2. verify the pinned SHA-256 checksum;
3. enforce a 10 MiB compressed-size limit and 100 MiB expanded-size limit;
4. reject unreadable, encrypted, redirected, linked, malformed, or unexpected archive entries;
5. allow only the expected package directories and exact required file set;
6. require package `VERSION` to equal `3.09`;
7. use an installation lock to prevent concurrent replacement;
8. extract into a temporary staging directory;
9. back up an existing AMS skill directory;
10. restore the previous installation if replacement fails;
11. preserve unrelated skills, project settings, recovery state, and generated agent profiles.

Required package files:

```text
adaptive-master-subagent-orchestration/
├── SKILL.md
├── VERSION
├── agents/
│   └── openai.yaml
└── references/
    ├── hierarchy-control.md
    ├── intensity-control.md
    ├── package-maintenance.md
    ├── profile-management.md
    ├── project-control.md
    ├── runtime-core.md
    └── zergling-rush.md
```

An archive missing `references/hierarchy-control.md`, reporting another version, or containing any unexpected file or directory is rejected before replacement.

## Optional environment overrides

Normal public installation should use the pinned defaults. The installers also support controlled testing, mirrors, alternate destinations, or authenticated private access:

| Variable | Purpose |
|---|---|
| `GITHUB_TOKEN` | Authenticate GitHub release metadata and asset download when required |
| `AMS_RELEASE_URL` | Override the package URL |
| `AMS_EXPECTED_SHA256` | Override the expected checksum; must be exactly 64 hexadecimal characters |
| `AMS_SKILL_HOME` | Override the destination skill parent directory |

When overriding `AMS_RELEASE_URL`, also provide the checksum for that exact archive through `AMS_EXPECTED_SHA256`. Do not bypass checksum validation.

## Manual download and verification

Download either synchronized 3.09 ZIP listed above.

### Windows PowerShell checksum

```powershell
$Zip = ".\adaptive-master-subagent-orchestration-3.09.zip"
$Expected = "74e48106fc26a6516db3e9f6cc15e66e745d4fe71e24fdee233a6cf972fe4514"
$Actual = (Get-FileHash -LiteralPath $Zip -Algorithm SHA256).Hash.ToLowerInvariant()

if ($Actual -ne $Expected) {
    throw "Checksum mismatch. Expected $Expected; received $Actual."
}
```

### Linux checksum

```bash
printf '%s  %s\n' \
  '74e48106fc26a6516db3e9f6cc15e66e745d4fe71e24fdee233a6cf972fe4514' \
  'adaptive-master-subagent-orchestration-3.09.zip' | sha256sum -c -
```

### macOS without `sha256sum`

```bash
actual="$(shasum -a 256 adaptive-master-subagent-orchestration-3.09.zip | awk '{print $1}')"
test "$actual" = '74e48106fc26a6516db3e9f6cc15e66e745d4fe71e24fdee233a6cf972fe4514'
```

## Manual extraction

Back up any existing AMS skill directory first.

### Windows PowerShell

```powershell
$SkillHome = Join-Path $HOME ".agents\skills"
New-Item -ItemType Directory -Force -Path $SkillHome | Out-Null
Expand-Archive -LiteralPath ".\adaptive-master-subagent-orchestration-3.09.zip" -DestinationPath $SkillHome -Force
```

### Bash

```bash
mkdir -p "$HOME/.agents/skills"
unzip adaptive-master-subagent-orchestration-3.09.zip -d "$HOME/.agents/skills"
```

The resulting directory must be:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
```

Confirm that `VERSION` contains `3.09` and that `references/hierarchy-control.md` exists. Restart or reload Codex afterward.

## Verify the installed package

### Windows PowerShell

```powershell
$SkillRoot = Join-Path $HOME ".agents\skills\adaptive-master-subagent-orchestration"
Get-Content -LiteralPath (Join-Path $SkillRoot "VERSION")
Test-Path -LiteralPath (Join-Path $SkillRoot "references\hierarchy-control.md") -PathType Leaf
```

Expected output includes:

```text
3.09
True
```

### Bash

```bash
skill_root="$HOME/.agents/skills/adaptive-master-subagent-orchestration"
cat "$skill_root/VERSION"
test -f "$skill_root/references/hierarchy-control.md"
```

Expected version:

```text
3.09
```

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

Individual `ams_*.toml` profiles are generated or repaired separately and are not included in the release ZIP.

The default setting is:

```toml
profile_management = "auto"
```

Release 3.09 does not add a permanent manager profile. Sol, Terra, and Luna profiles receive temporary worker or delegated-manager authority through bounded work orders. Spark is worker-only.

Use:

```toml
profile_management = "installer"
```

to disable automatic profile repair. Explicit profile installation or repair may still be requested. A fresh Codex session may be required before newly generated or repaired profiles become available.

## Update and repair

Rerun the one-line installer for the operating system.

The installer validates and stages the complete candidate before replacing the existing skill directory. It restores the previous installation if replacement fails.

Before updating or repairing:

1. finish or safely pause active AMS work;
2. preserve exact resumption state when needed;
3. run the installer;
4. restart or reload Codex;
5. verify `VERSION = 3.09` and `references/hierarchy-control.md` exists.

Do not combine files from different releases.

## Uninstall

Standard uninstall removes only the AMS skill directory. It preserves project settings, recovery state, generated profiles, and unrelated skills.

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
