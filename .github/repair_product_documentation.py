from pathlib import Path

path = Path("PRODUCT DOCUMENTATION.md")
text = path.read_bytes().decode("utf-8", errors="replace")

start_marker = "## Directory structure"
end_marker = "## Troubleshooting"
start = text.find(start_marker)
end = text.find(end_marker, start + len(start_marker))

if start < 0 or end < 0:
    raise SystemExit("Directory/troubleshooting section boundaries were not found")
if text.find(start_marker, start + 1) >= 0 or text.find(end_marker, end + 1) >= 0:
    raise SystemExit("Directory/troubleshooting section boundaries are not unique")

directory_section = """## Directory structure

### Repository

```text
Codex-Adaptive-Master-Subagent-Orchestration/
|-- README.md
|-- INSTALLATION.md
|-- PRODUCT DOCUMENTATION.md
|-- adaptive-master-subagent-orchestration-3.09.zip
|-- install.ps1
|-- install.sh
`-- adaptive-master-subagent-orchestration/
    |-- SKILL.md
    |-- VERSION
    |-- agents/
    |   `-- openai.yaml
    |-- assets/
    |   `-- agent-profiles/
    |       `-- 18 canonical ams_*.toml profiles
    `-- references/
        |-- hierarchy-control.md
        |-- intensity-control.md
        |-- package-maintenance.md
        |-- profile-management.md
        |-- project-control.md
        |-- runtime-core.md
        `-- zergling-rush.md
```

### Installed skill

```text
$HOME/.agents/skills/
`-- adaptive-master-subagent-orchestration/
    |-- SKILL.md
    |-- VERSION
    |-- agents/
    |   `-- openai.yaml
    |-- assets/
    |   `-- agent-profiles/
    |       `-- 18 canonical ams_*.toml profiles
    `-- references/
        |-- hierarchy-control.md
        |-- intensity-control.md
        |-- package-maintenance.md
        |-- profile-management.md
        |-- project-control.md
        |-- runtime-core.md
        `-- zergling-rush.md
```

### Installed agent profiles

```text
$CODEX_HOME/agents/
|-- ams_sol_low.toml
|-- ams_sol_medium.toml
|-- ams_sol_high.toml
|-- ams_sol_xhigh.toml
|-- ams_sol_max.toml
|-- ams_terra_low.toml
|-- ams_terra_medium.toml
|-- ams_terra_high.toml
|-- ams_terra_xhigh.toml
|-- ams_terra_max.toml
|-- ams_luna_low.toml
|-- ams_luna_medium.toml
|-- ams_luna_high.toml
|-- ams_luna_xhigh.toml
|-- ams_luna_max.toml
|-- ams_spark_low.toml
|-- ams_spark_medium.toml
`-- ams_spark_high.toml
```

When `CODEX_HOME` is unset, the installer uses `$HOME/.codex/agents/`.

### Project settings and optional recovery

```text
<project-root>/
`-- .codex/
    |-- ams-orchestration.toml
    `-- ams-recovery.json  # only when no project-native state system is sufficient
```"""

text = text[:start] + directory_section + "\n\n" + text[end:]

for forbidden in (
    "\ufffd",
    "ReleaseZip",
    "/releases/download/",
    "virtual-hierarchy-final-audited",
    "74e48106fc26a6516db3e9f6cc15e66e745d4fe71e24fdee233a6cf972fe4514",
):
    if forbidden in text:
        raise SystemExit(f"Forbidden or corrupted content remains: {forbidden!r}")

for required in (
    "f35aa28cad7c2691e80823e36ca276cbee8b20de067600fd8edb8f2aaf10fe4b",
    "adaptive-master-subagent-orchestration/assets/agent-profiles/",
    "ams_spark_high.toml",
    "raw/refs/heads/main/install.ps1",
    "raw/refs/heads/main/adaptive-master-subagent-orchestration-3.09.zip",
):
    if required not in text:
        raise SystemExit(f"Required public content is missing: {required}")

path.write_text(text, encoding="utf-8", newline="\n")
