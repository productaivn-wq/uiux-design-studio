#!/usr/bin/env python3
"""Unit tests for uiux_analyzer.py (UIUXProMax Section 11)."""

import unittest
from pathlib import Path
import sys

# Add scripts directory to sys.path
SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from uiux_analyzer import (
    UIControlInventory,
    Ishikawa6MUIDecomposition,
    MCDADecisionEngine,
    UIUXReportGenerator,
    run_canonical_demo,
)


class TestUIUXAnalyzer(unittest.TestCase):
    """Test suite for UI/UX Forensic Diagnostic and MCDA Engine."""

    def test_friction_bounds(self):
        clean_inv = UIControlInventory(total_controls=4, layout_rows=1, height_px=40)
        self.assertLessEqual(clean_inv.compute_cognitive_friction(), 3.0)

        cluttered_inv = UIControlInventory(
            total_controls=35,
            layout_rows=6,
            height_px=250,
            duplicate_or_redundant=4,
            max_parallel_items_in_container=15,
            has_horizontal_scrollbar=True,
        )
        self.assertEqual(cluttered_inv.compute_cognitive_friction(), 10.0)

    def test_layer0_violation_audit(self):
        cluttered_inv = UIControlInventory(
            total_controls=24,
            layout_rows=5,
            height_px=240,
            duplicate_or_redundant=2,
            max_parallel_items_in_container=12,
            touch_target_violations=4,
            has_horizontal_scrollbar=True,
        )
        violations = cluttered_inv.audit_layer0_violations()
        rule_ids = {v["rule"] for v in violations}

        self.assertIn("RULE-L0-MESO-MILLERS-LAW", rule_ids)
        self.assertIn("RULE-L0-MESO-RULE-OF-6", rule_ids)
        self.assertIn("RULE-L0-MESO-VERTICAL-BUDGET", rule_ids)
        self.assertIn("RULE-L0-MESO-REDUNDANT-CONTROLS", rule_ids)
        self.assertIn("RULE-L0-MICRO-UNINTENDED-SCROLLBAR", rule_ids)
        self.assertIn("RULE-L0-MICRO-FITTS", rule_ids)

    def test_ahp_weights_consistency(self):
        # 3x3 consistent pairwise comparison matrix
        # C1 is 2x as important as C2, 4x as C3; C2 is 2x as C3
        pairwise = [
            [1.0, 2.0, 4.0],
            [0.5, 1.0, 2.0],
            [0.25, 0.5, 1.0],
        ]
        keys = ["c1", "c2", "c3"]
        weights, cr, is_consistent = MCDADecisionEngine.calculate_ahp_weights(
            pairwise, keys
        )

        self.assertTrue(is_consistent)
        self.assertLess(cr, 0.05)
        self.assertAlmostEqual(sum(weights.values()), 1.0, places=2)
        self.assertGreater(weights["c1"], weights["c2"])
        self.assertGreater(weights["c2"], weights["c3"])

    def test_mcda_evaluation_ranking(self):
        engine = MCDADecisionEngine()
        proposals = [
            {
                "id": "P1",
                "name": "High Utility",
                "scores": {
                    "screen_economy": 9.0,
                    "cognitive_calm": 9.0,
                    "triage_velocity": 9.0,
                    "brand_coherence": 9.0,
                    "implementation_risk": 9.0,
                },
            },
            {
                "id": "P2",
                "name": "Low Utility",
                "scores": {
                    "screen_economy": 4.0,
                    "cognitive_calm": 4.0,
                    "triage_velocity": 4.0,
                    "brand_coherence": 4.0,
                    "implementation_risk": 4.0,
                },
            },
        ]
        evaluated = engine.evaluate_proposals(proposals)
        self.assertEqual(evaluated[0]["id"], "P1")
        self.assertEqual(evaluated[0]["rank"], 1)
        self.assertEqual(evaluated[1]["rank"], 2)
        self.assertAlmostEqual(evaluated[0]["compositeScore"], 9.0, places=1)
        self.assertAlmostEqual(evaluated[1]["compositeScore"], 4.0, places=1)
        self.assertAlmostEqual(evaluated[0]["marginOverRunnerUp"], 5.0, places=1)

    def test_canonical_demo_pipeline(self):
        demo_res = run_canonical_demo()
        self.assertIn("report_markdown", demo_res)
        self.assertIn("visualizer_html", demo_res)
        self.assertGreaterEqual(len(demo_res["evaluated_proposals"]), 3)
        self.assertEqual(demo_res["evaluated_proposals"][0]["id"], "P1")


if __name__ == "__main__":
    unittest.main()
