#!/usr/bin/env python3
"""Repository-only contract-model scenarios for AMS 4.0 interactions."""
from __future__ import annotations

import unittest
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "adaptive-master-subagent-orchestration"
DEFAULTS = {
    "enabled": False,
    "allow_implicit_invocation": True,
    "intensity": "auto",
    "project_governance": True,
    "root_execution_fallback": True,
    "convergence_control": True,
    "convergence_correction_limit": 4,
    "convergence_redesign_limit": 4,
    "spark_enabled": True,
    "spark_available": True,
    "spark_efforts": ["low", "medium", "high"],
    "profile_management": "auto",
    "work_order_refinement": False,
    "review_control": False,
    "shared_worktree_verification": False,
    "runtime_observation": False,
    "untrusted_evidence_handling": False,
    "task_graph_safeguards": False,
    "rejected_approach_handoff": False,
    "request_accounting": False,
    "app_task_lane": False,
}


def resolve(data: dict[str, object], defaults: dict[str, object] = DEFAULTS) -> dict[str, object]:
    material = dict(data)
    material.pop("schema_version", None)  # retired legacy artifact, no active meaning
    unknown = set(material) - set(defaults)
    if unknown:
        raise ValueError(f"unknown: {sorted(unknown)}")
    return {**defaults, **material}


@dataclass
class Campaign:
    correction_limit: int = 4
    redesign_limit: int = 4
    redesign_count: int = 0
    correction_count: int = 0
    tracked: bool = False
    terminal: str | None = None

    def correction(self) -> str:
        self.correction_count += 1
        self.tracked = True
        return "converge" if self.correction_count >= self.correction_limit else "monitoring"

    def redesign(self) -> str:
        self.tracked = True
        if self.redesign_count >= self.redesign_limit:
            return "intervention-required"
        self.redesign_count += 1
        self.correction_count = 0
        return "new-epoch"

    def finalize(self, disposition: str) -> str:
        if not self.tracked:
            return "no-record"
        self.terminal = disposition
        return "history-published"


class ContractScenarios(unittest.TestCase):
    def test_missing_fields_resolve_from_current_defaults(self) -> None:
        resolved = resolve({"enabled": True})
        self.assertTrue(resolved["enabled"])
        self.assertEqual(resolved["convergence_redesign_limit"], 4)

    def test_retired_schema_version_is_ignored_for_any_value(self) -> None:
        self.assertTrue(resolve({"schema_version": 2, "enabled": True})["enabled"])
        self.assertFalse(resolve({"schema_version": "retired"})["enabled"])

    def test_other_unknown_fields_fail_until_supported(self) -> None:
        with self.assertRaises(ValueError):
            resolve({"future_feature": True})
        future = {**DEFAULTS, "future_feature": False}
        self.assertTrue(resolve({"future_feature": True}, future)["future_feature"])

    def test_correction_and_redesign_limits_are_independent(self) -> None:
        campaign = Campaign()
        for _ in range(4):
            state = campaign.correction()
        self.assertEqual(state, "converge")
        self.assertEqual(campaign.redesign(), "new-epoch")
        self.assertEqual(campaign.correction_count, 0)
        self.assertEqual(campaign.redesign_count, 1)

    def test_default_hard_boundary_is_twenty_correction_cycles(self) -> None:
        campaign = Campaign()
        cycles = 0
        while True:
            for _ in range(campaign.correction_limit):
                campaign.correction()
                cycles += 1
            state = campaign.redesign()
            if state == "intervention-required":
                break
        self.assertEqual(cycles, 20)
        self.assertEqual(campaign.redesign_count, 4)

    def test_pretrigger_acceptance_and_cancellation_finalize_tracking(self) -> None:
        accepted = Campaign()
        accepted.correction()
        self.assertEqual(accepted.finalize("accept"), "history-published")
        self.assertEqual(accepted.terminal, "accept")
        cancelled = Campaign()
        cancelled.redesign()
        self.assertEqual(cancelled.finalize("cancelled"), "history-published")

    def test_governance_gate_and_direct_named_capability(self) -> None:
        def enabled(governance: bool, feature: bool, trigger: bool, direct_named: bool = False) -> bool:
            return direct_named or (governance and feature and trigger)
        self.assertFalse(enabled(False, True, True))
        self.assertTrue(enabled(False, True, True, direct_named=True))

    def test_generic_completion_language_is_not_an_override(self) -> None:
        def override(text: str) -> bool:
            lowered = text.lower()
            names_convergence = "convergence" in lowered and any(
                token in lowered for token in ("limit", "bypass", "override", "intervention")
            )
            return names_convergence
        for phrase in (
            "fix everything",
            "do not stop until no issues remain",
            "continue until clean",
        ):
            self.assertFalse(override(phrase))
        self.assertTrue(override("Override AMS convergence limit for this objective"))

    def test_fallback_is_suppressed_during_convergence(self) -> None:
        def fallback(enabled: bool, active: bool, terminal: str | None) -> bool:
            return enabled and (not active or terminal in {"failed", "blocked"})
        self.assertFalse(fallback(True, True, None))
        self.assertFalse(fallback(True, True, "intervention-required"))
        self.assertTrue(fallback(True, True, "failed"))

    def test_feature_combinations_do_not_imply_each_other(self) -> None:
        settings = resolve(
            {
                "app_task_lane": True,
                "shared_worktree_verification": False,
                "work_order_refinement": False,
            }
        )
        self.assertTrue(settings["app_task_lane"])
        self.assertFalse(settings["shared_worktree_verification"])
        self.assertFalse(settings["work_order_refinement"])

    def test_every_optional_feature_has_a_runtime_route(self) -> None:
        core = (PACKAGE / "references/runtime-core.md").read_text(encoding="utf-8")
        for token in (
            "work-order-refinement.md",
            "task-graph-safeguards.md",
            "shared-worktree-control.md",
            "evidence-handling.md",
            "runtime-observation.md",
            "request-accounting.md",
            "ams-app-task-lane",
        ):
            self.assertIn(token, core)
        governance = (PACKAGE / "references/project-governance.md").read_text(encoding="utf-8")
        self.assertIn("review-control.md", governance)
        self.assertIn("handoff-control.md", governance)

    def test_status_and_recovery_route_to_convergence_state_reader(self) -> None:
        control = (PACKAGE / "references/project-control.md").read_text(encoding="utf-8")
        core = (PACKAGE / "references/runtime-core.md").read_text(encoding="utf-8")
        self.assertIn("state-reader/status section of `convergence-control.md`", control)
        self.assertIn("On startup, compaction recovery, or `AMS STATUS`", core)

    def test_companion_availability_is_not_enablement(self) -> None:
        def usable(enabled: bool, available: bool, compatible: bool, user: bool) -> bool:
            return enabled and available and compatible and user
        self.assertFalse(usable(True, False, False, True))
        self.assertFalse(usable(True, True, True, False))
        self.assertTrue(usable(True, True, True, True))

    def test_sol_ultra_is_standalone_from_standard_convergence(self) -> None:
        ultra = (ROOT / "SOL-ULTRA-AMS-EXTREME-ORCHESTRATION-PROMPT.md").read_text(encoding="utf-8")
        self.assertIn("AMS Extreme standalone directive", ultra)
        self.assertIn("standard AMS convergence-control module is excluded", ultra)
        self.assertIn("report the exact decision required from the user", ultra)


if __name__ == "__main__":
    unittest.main()
