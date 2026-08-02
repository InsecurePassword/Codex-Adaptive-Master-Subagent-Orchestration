# Installation

AMS 3.09 is installed directly from the repository tree. The installers do not use GitHub Release assets or a package ZIP.

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
- `curl`, `awk`, `sort`, `cmp`, `mktemp`, `wc`, `tr`, `grep`, `head`, `tail`, `od`, `find`, and `dirname`
- either `sha256sum` or `shasum`

Restart or reload Codex after installation or update.

## Direct-tree distribution

The installer reads this repository-root manifest:

```text
https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install-manifest.txt
```

The manifest contains the exact path, byte length, and SHA-256 for every installed runtime file. The installer downloads each file directly from:

```text
adaptive-master-subagent-orchestration/
```

No custom release asset or repository-root archive is required. GitHub's automatically generated `Source code` links are snapshots of the repository and are not used by the installer.

## What the installers verify

Both installers:

1. download the install manifest from the selected repository ref;
2. require manifest format `ams-install-manifest-v1` and version `3.09`;
3. require the exact 28-file AMS runtime/profile set;
4. reject duplicate, escaping, oversized, or malformed manifest entries;
5. download every runtime file directly from the repository tree;
6. verify every file's byte length and SHA-256;
7. download the manifest again and require it to be byte-identical, preventing mixed-generation installation if `main` changes during the operation;
8. require `VERSION = 3.09` and verify all 18 bundled profiles carry the AMS managed marker;
9. stage the complete skill before replacing the installed copy;
10. install or update the complete 18-profile matrix;
11. refuse to overwrite unrecognized or user-authored profile collisions;
12. restore the previous skill and profile state if installation fails;
13. preserve project/global settings, recovery state, model logs, unrelated skills, and unrelated profiles.

## Installed locations

Default skill location:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
```

Default agent-profile location:

```text
$CODEX_HOME/agents/
```

When `CODEX_HOME` is unset:

```text
$HOME/.codex/agents/
```

## Source-tree contents

```text
adaptive-master-subagent-orchestration/
├── SKILL.md
├── VERSION
├── agents/
│   └── openai.yaml
├── assets/
│   └── agent-profiles/
│       └── 18 canonical ams_*.toml profiles
└── references/
    ├── hierarchy-control.md
    ├── intensity-control.md
    ├── package-maintenance.md
    ├── profile-management.md
    ├── project-control.md
    ├── runtime-core.md
    └── zergling-rush.md
```

## Optional environment overrides

Normal public installation should use the defaults above.

| Variable | Purpose |
|---|---|
| `AMS_REPOSITORY_REF` | Repository branch/ref to read; default `main` |
| `AMS_RAW_BASE_URL` | Alternate raw tree base URL for mirrors or testing |
| `AMS_MANIFEST_URL` | Alternate manifest URL |
| `AMS_SKILL_HOME` | Alternate skill parent directory |
| `CODEX_HOME` | Alternate Codex configuration and agent-profile root |

When overriding the source, keep the manifest and file tree from the same immutable or controlled source. The installer rejects hash mismatches and a manifest that changes during download.

## Manual installation with Git

To inspect or copy the entire repository, clone it:

```bash
git clone https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration.git
cd Codex-Adaptive-Master-Subagent-Orchestration
```

Copy the skill tree to the skill directory:

```text
adaptive-master-subagent-orchestration/
    -> $HOME/.agents/skills/adaptive-master-subagent-orchestration/
```

Then copy the 18 files from:

```text
adaptive-master-subagent-orchestration/assets/agent-profiles/
```

into:

```text
$CODEX_HOME/agents/
```

Use the automated installer unless you intentionally want to perform and verify those steps yourself.

## Verify the installed files

### Windows PowerShell

```powershell
$SkillRoot = Join-Path $HOME '.agents\skills\adaptive-master-subagent-orchestration'
$AgentRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'agents' } else { Join-Path $HOME '.codex\agents' }

Get-Content -LiteralPath (Join-Path $SkillRoot 'VERSION')
Test-Path -LiteralPath (Join-Path $SkillRoot 'references\runtime-core.md') -PathType Leaf
(Get-ChildItem -LiteralPath $AgentRoot -Filter 'ams_*.toml' -File).Count
```

Expected:

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
test -f "$skill_root/references/runtime-core.md"
find "$agent_root" -maxdepth 1 -type f -name 'ams_*.toml' | wc -l
```

Expected version and profile count:

```text
3.09
18
```

## Start using AMS

The skill checks project settings first and the optional global settings only when the project file is absent.

### Project persistence

```text
AMS STATUS
AMS ENABLE
AMS MODE auto
AMS DISABLE
```

Project commands write only:

```text
<project-root>/.codex/ams-orchestration.toml
```

### Global persistence (manual only)

Global path:

```text
$CODEX_HOME/ams-orchestration.toml
```

When `CODEX_HOME` is unset:

```text
$HOME/.codex/ams-orchestration.toml
```

Use the same schema as a project file:

```toml
schema_version = 2
enabled = true
allow_implicit_invocation = true
intensity = "auto"
spark_enabled = true
spark_available = true
spark_efforts = ["low", "medium", "high"]
profile_management = "auto"
```

Project settings override global settings completely. No AMS command creates, changes, repairs, migrates, or deletes the global file.

## Agent profiles

The installer deploys the complete profile matrix:

- Sol, Terra, and Luna: `low`, `medium`, `high`, `xhigh`, and `max`
- Spark: `low`, `medium`, and `high`

Sol, Terra, and Luna profiles can receive temporary worker or delegated-manager authority through bounded work orders. Spark remains worker-only. A differing installed profile is replaced only when its first line proves AMS ownership:

```text
# managed-by: adaptive-master-subagent-orchestration
```

An unrecognized collision fails closed and rolls back the installation.

## Update and repair

Rerun the appropriate one-line installer. It reads the current manifest and tree, stages the complete source, validates every file, and transactionally replaces the installed skill and recognized profiles.

Before updating:

1. finish or safely pause active AMS work;
2. preserve exact resumption state when required;
3. rerun the installer;
4. restart or reload Codex;
5. verify `VERSION = 3.09`, `references/runtime-core.md`, and all 18 profiles.

Do not combine files from different repository states manually.

## Uninstall

Standard uninstall removes only the AMS skill directory. It preserves project/global settings, recovery state, installed profiles, and unrelated files.

### Windows PowerShell

```powershell
$SkillRoot = Join-Path $HOME '.agents\skills\adaptive-master-subagent-orchestration'
if (Test-Path -LiteralPath $SkillRoot) {
    $Item = Get-Item -LiteralPath $SkillRoot -Force
    if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Refusing redirected path: $SkillRoot" }
    if (-not $Item.PSIsContainer) { throw "AMS skill path is not a directory: $SkillRoot" }
    Remove-Item -LiteralPath $SkillRoot -Recurse -Force
}
```

### Bash

```bash
skill_root="$HOME/.agents/skills/adaptive-master-subagent-orchestration"
if [ -L "$skill_root" ]; then
  printf 'Refusing redirected path: %s\n' "$skill_root" >&2
  exit 1
elif [ -e "$skill_root" ] && [ ! -d "$skill_root" ]; then
  printf 'AMS skill path is not a directory: %s\n' "$skill_root" >&2
  exit 1
elif [ -d "$skill_root" ]; then
  rm -rf -- "$skill_root"
fi
```

Restart or reload Codex after removal.

## Troubleshooting

### A manifest or file hash does not match

Do not bypass the check. The repository may have changed during installation, a mirror may be inconsistent, or a download may be corrupt. Rerun the installer. If the error persists, inspect `install-manifest.txt` and the referenced source file on the same ref.

### The installer reports an unexpected manifest path

The manifest must contain exactly the supported 28 runtime/profile paths. Reinstall from the canonical `main` branch or inspect the repository diff before trusting an alternate source.

### A profile collision is rejected

The installer never overwrites a file that does not carry the exact AMS managed marker. Move or rename the user-authored collision, or intentionally reconcile it before rerunning installation.

### Codex still shows old behavior

Restart or reload Codex. A behavior-changing update is not loaded into the already active session.
