#!/usr/bin/env python3
"""Measure revision-specific AMS-authored context without claiming provider tokens."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE = REPO_ROOT / "adaptive-master-subagent-orchestration"
BUDGET_PATH = REPO_ROOT / "tools" / "context-budget.json"
BASELINE_PATH = REPO_ROOT / "tools" / "context-baseline-pr44-pre-corrections.json"

SCENARIOS = {
    "bootstrap_skill": ["SKILL.md"],
    "active_core": ["SKILL.md", "references/project-control.md", "references/runtime-core.md"],
    "active_governance": ["SKILL.md", "references/project-control.md", "references/runtime-core.md", "references/project-governance.md"],
}

LAZY_REFERENCES = [
    "references/feature-control.md",
    "references/convergence-control.md",
    "references/work-order-refinement.md",
    "references/review-control.md",
    "references/shared-worktree-control.md",
    "references/surface-identity.md",
    "references/runtime-observation.md",
    "references/evidence-handling.md",
    "references/task-graph-safeguards.md",
    "references/handoff-control.md",
    "references/request-accounting.md",
]

COMPANIONS = {
    "ams_app_task_lane": [
        REPO_ROOT / "extensions" / "ams-app-task-lane" / "COMPATIBILITY",
        REPO_ROOT / "extensions" / "ams-app-task-lane" / "SKILL.md",
        REPO_ROOT / "extensions" / "ams-app-task-lane" / "references" / "app-task-lane.md",
    ],
    "ams_runtime_observation": [
        REPO_ROOT / "extensions" / "ams-runtime-observation" / "COMPATIBILITY",
        REPO_ROOT / "extensions" / "ams-runtime-observation" / "SKILL.md",
    ],
}


def token_estimates(size: int) -> dict[str, object]:
    return {"estimated_tokens": math.ceil(size / 4), "conservative_token_range": [math.ceil(size / 6), math.ceil(size / 2)]}


def metrics(paths: Iterable[Path]) -> dict[str, object]:
    components=[]; combined=b""
    for path in paths:
        data=path.read_bytes(); text=data.decode("utf-8"); combined += data
        components.append({"path": path.relative_to(REPO_ROOT).as_posix(), "characters": len(text), "bytes": len(data), "lines": len(text.splitlines()), "sha256": hashlib.sha256(data).hexdigest()})
    size=len(combined)
    return {"components": components, "characters": len(combined.decode("utf-8")), "bytes": size, "lines": sum(int(x["lines"]) for x in components), "sha256": hashlib.sha256(combined).hexdigest(), **token_estimates(size)}


def baseline_scenarios() -> tuple[str, dict[str,int]]:
    baseline=json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    sizes={p:int(v["bytes"]) for p,v in baseline["components"].items()}
    return str(baseline["baseline"]), {name:sum(sizes[p] for p in paths) for name,paths in SCENARIOS.items()}


def build_report() -> dict[str, object]:
    source, baseline=baseline_scenarios()
    scenarios={name:metrics([PACKAGE/p for p in paths]) for name,paths in SCENARIOS.items()}
    for name,item in scenarios.items():
        item["baseline_bytes"]=baseline[name]; item["delta_bytes"]=int(item["bytes"])-baseline[name]
    return {
        "measurement":"UTF-8 bytes with offline token estimates only",
        "comparison_baseline":source,
        "boundary":{
            "bootstrap_skill":"always-loaded SKILL.md",
            "active_core":"SKILL.md + project-control.md + runtime-core.md",
            "active_governance":"active_core + project-governance.md",
            "lazy_references":"incremental only when selected",
            "companions":"separate skills excluded from core manifest",
        },
        "scenarios":scenarios,
        "lazy_references":{p:metrics([PACKAGE/p]) for p in LAZY_REFERENCES},
        "companions":{name:metrics(paths) for name,paths in COMPANIONS.items()},
    }


def check_budget(report:dict[str,object])->list[str]:
    budget=json.loads(BUDGET_PATH.read_text(encoding="utf-8")); problems=[]
    for name,maximum in budget["scenario_max_bytes"].items():
        actual=int(report["scenarios"][name]["bytes"])
        if actual>int(maximum): problems.append(f"{name}: {actual} > {maximum}")
    for name,maximum in budget["scenario_max_delta_bytes"].items():
        actual=int(report["scenarios"][name]["delta_bytes"])
        if actual>int(maximum): problems.append(f"{name} delta: {actual} > {maximum}")
    for path,maximum in budget["lazy_reference_max_bytes"].items():
        actual=int(report["lazy_references"][path]["bytes"])
        if actual>int(maximum): problems.append(f"{path}: {actual} > {maximum}")
    for name,maximum in budget["companion_max_bytes"].items():
        actual=int(report["companions"][name]["bytes"])
        if actual>int(maximum): problems.append(f"companion {name}: {actual} > {maximum}")
    return problems


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--json",action="store_true"); parser.add_argument("--check",action="store_true"); args=parser.parse_args()
    report=build_report(); problems=check_budget(report) if args.check else []; report["budget_check"]={"passed":not problems,"problems":problems}
    if args.json: print(json.dumps(report,indent=2,sort_keys=True))
    else:
        for name,item in report["scenarios"].items(): print(f"{name}: {item['bytes']} bytes; delta={item['delta_bytes']:+d}; ~{item['estimated_tokens']} tokens")
        for path,item in report["lazy_references"].items(): print(f"lazy {path}: {item['bytes']} bytes; ~{item['estimated_tokens']} tokens")
        for name,item in report["companions"].items(): print(f"companion {name}: {item['bytes']} bytes; ~{item['estimated_tokens']} tokens")
        for problem in problems: print(f"error: {problem}")
    return 1 if problems else 0

if __name__=="__main__": raise SystemExit(main())
