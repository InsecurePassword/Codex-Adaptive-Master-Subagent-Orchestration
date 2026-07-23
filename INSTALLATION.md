# Installation

AMS 3.09 is distributed directly from the repository root on the `main` branch. The installer scripts and package ZIP are versioned together in the repository, so installation does not depend on GitHub Releases.

## Recommended one-line installation

### Windows PowerShell

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install.ps1' | iex"
```

Requirements:

- Windows PowerShell 5.1 or newer
- built-in .NET and PowerShell components

### Linux or macOS with Bash

```bash
curl -fsSL 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install.sh' | bash
```

Requirements:

- Bash
- `curl`
- `unzip`
- `zipinfo`
- `awk`
- `sort`
- `cmp`
- `mktemp`
- either `sha256sum` or `shasum`

Restart or reload Codex after installation or update.

## Repository distribution

The files used by the installer are stored at the repository root:

```text
Codex-Adaptive-Master-Subagent-Orchestration/
├── adaptive-master-subagent-orchestration-3.09.zip
├── install.ps1
└── install.sh
```

Package URL:

```text
https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/adaptive-master-subagent-orchestration-3.09.zip
```

Package SHA-256:

```text
f35aa28cad7c2691e80823e36ca276cbee8b20de067600fd8edb8f2aaf10fe4b
```

The archive contains one top-level directory:

```text
adaptive-master-subagent-orchestration/
```

Default skill location:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
```

Default agent-profile location:

```text
$CODEX_HOME/agents/
```

When `CODEX_HOME` is not set, both installers use:

```text
$HOME/.codex/agents/
```

## What the installers verify

Both installers:

1. download the repository-root `adaptive-master-subagent-orchestration-3.09.zip` from `main`;
2. verify its pinned SHA-256 checksum;
3. enforce a 10 MiB compressed-size limit and 100 MiB expanded-size limit;
4. reject unreadable, encrypted, redirected, linked, malformed, or unexpected archive entries;
5. allow only the expected package directories and exact required file set;
6. require package `VERSION` to equal `3.09`;
7. verify that all bundled profile files carry the AMS managed marker;
8. use an installation lock to prevent concurrent replacement;
9. extract into a temporary staging directory;
10. back up an existing AMS skill directory and recognized AMS-managed profiles;
11. install or update the complete 18-profile matrix;
12. refuse to overwrite unrecognized or user-authored profile collisions;
13. restore the previous skill and profile state if installation fails;
14. preserve unrelated skills, project settings, recovery state, and unrelated profiles.

## Package contents

The ZIP contains exactly these runtime files and profile assets:

```text
adaptive-master-subagent-orchestration/
├── SKILL.md
├── VERSION
├── agents/
│   └── openai.yaml
├── assets/
│   └── agent-profiles/
│       ├── ams_sol_low.toml
│       ├── ams_sol_medium.toml
│       ├── ams_sol_high.toml
│       ├── ams_sol_xhigh.toml
│       ├── ams_sol_max.toml
│       ├── ams_terra_low.toml
│       ├── ams_terra_medium.toml
│       ├── ams_terra_high.toml
│       ├── ams_terra_xhigh.toml
│       ├── ams_terra_max.toml
│       ├── ams_luna_low.toml
│       ├── ams_luna_medium.toml
│       ├── ams_luna_high.toml
│       ├── ams_luna_xhigh.toml
│       ├── ams_luna_max.toml
│       ├── ams_spark_low.toml
│       ├── ams_spark_medium.toml
│       └── ams_spark_high.toml
└── references/
    ├── hierarchy-control.md
    ├── intensity-control.md
    ├── package-maintenance.md
    ├── profile-management.md
    ├── project-control.md
    ├── runtime-core.md
    └── zergling-rush.md
```

An archive reporting another version, omitting a required profile or reference, or containing an unexpected file or directory is rejected before replacement.

## Optional environment overrides

Normal public installation should use the pinned repository defaults. The installers also support controlled testing, mirrors, and alternate destinations:

| Variable | Purpose |
|---|---|
| `AMS_PACKAGE_URL` | Override the package URL |
| `AMS_EXPECTED_SHA256` | Override the expected checksum; must be exactly 64 hexadecimal characters |
| `AMS_SKILL_HOME` | Override the destination skill parent directory |
| `CODEX_HOME` | Override the Codex configuration and agent-profile root |

When overriding `AMS_PACKAGE_URL`, also provide the checksum for that exact archive through `AMS_EXPECTED_SHA256`. Do not bypass checksum validation.

## Manual download and verification

Download the repository-root package:

```text
https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/adaptive-master-subagent-orchestration-3.09.zip
```

### Windows PowerShell checksum

```powershell
$Zip = ".\adaptive-master-subagent-orchestration-3.09.zip"
$Expected = "f35aa28cad7c2691e80823e36ca276cbee8b20de067600fd8edb8f2aaf10fe4b"
$Actual = (Get-FileHash -LiteralPath $Zip -Algorithm SHA256).Hash.ToLowerInvariant()

if ($Actual -ne $Expected) {
    throw "Checksum mismatch. Expected $Expected; received $Actual."
}
```

### Linux checksum

```bash
printf '%s  %s\n' \
  'f35aa28cad7c2691e80823e36ca276cbee8b20de067600fd8edb8f2aaf10fe4b' \
  'adaptive-master-subagent-orchestration-3.09.zip' | sha256sum -c -
```

### macOS without `sha256sum`

```bash
actual="$(shasum -a 256 adaptive-master-subagent-orchestration-3.09.zip | awk '{print $1}')"
test "$actual" = 'f35aa28cad7c2691e80823e36ca276cbee8b20de067600fd8edb8f2aaf10fe4b'
```

## Manual extraction

Manual extraction installs the skill files but does not deploy the bundled profiles into `$CODEX_HOME/agents/`. Use the installer unless you intend to place and verify those profiles yourself.

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

Confirm that `VERSION` contains `3.09`, `references/hierarchy-control.md` exists, and all 18 files exist under `assets/agent-profiles/`. Restart or reload Codex afterward.

## Verify the installed package

### Windows PowerShell

```powershell
$SkillRoot = Join-Path $HOME ".agents\skills\adaptive-master-subagent-orchestration"
$AgentRoot = if ($env:CODEX_HOME) {
    Join-Path $env:CODEX_HOME "agents"
} else {
    Join-Path $HOME ".codex\agents"
}

Get-Content -LiteralPath (Join-Path $SkillRoot "VERSION")
Test-Path -LiteralPath (Join-Path $SkillRoot "references\hierarchy-control.md") -PathType Leaf
(Get-ChildItem -LiteralPath $AgentRoot -Filter "ams_*.toml" -File).Count
```

Expected output includes:

```text
3.09
True
18
```

### Bash

```bash
skill_root="$HOME/.agents/skills/adaptive-master-subagent-orchestration"
agent_root="${CODEX_HOME:-$HOME/.codex}/agents"

cat "$skill_root/VERSION"
test -f "$skill_root/references/hierarchy-control.md"
find "$agent_root" -maxdepth 1 -type f -name 'ams_*.toml' | wc -l
```

Expected version and profile count:

```text
3.09
18
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

The installer deploys the complete default profile matrix from the package into the effective Codex agent registry.

- Sol, Terra, and Luna include `low`, `medium`, `high`, `xhigh`, and `max`.
- Spark includes `low`, `medium`, and `high`.
- Sol, Terra, and Luna profiles can receive temporary worker or delegated-manager authority through bounded work orders.
- Spark remains worker-only.
- No permanent manager profile family is created.

A byte-identical installed profile is left unchanged. A differing profile is replaced only when its first line proves it is AMS-managed:

```text
# managed-by: adaptive-master-subagent-orchestration
```

An unrecognized or user-authored collision causes installation to fail closed and roll back.

A fresh Codex session may be required before newly installed or updated profiles become discoverable.

## Update and repair

Rerun the one-line installer for the operating system.

The installer validates and stages the complete candidate before replacing the existing skill and profile matrix. It restores the previous installation if replacement fails.

Before updating or repairing:

1. finish or safely pause active AMS work;
2. preserve exact resumption state when needed;
3. run the installer;
4. restart or reload Codex;
5. verify `VERSION = 3.09`, `references/hierarchy-control.md` exists, and 18 AMS profiles are present.

Do not combine files from different package generations.

## Uninstall

Standard uninstall removes only the AMS skill directory. It preserves project settings, recovery state, generated or installed AMS profiles, and unrelated skills.

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

Project settings and installed profiles are preserved intentionally. Complete cleanup instructions are documented in [Product Documentation](PRODUCT%20DOCUMENTATION.md#uninstall).
