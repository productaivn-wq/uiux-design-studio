#!/usr/bin/env python3
"""
uiux_analyzer.py — Analytical UI/UX Forensic Diagnostic & MCDA Decision Science Engine.

Crystallized from the Luxury Maritime CRM (Luxury Maritime Reference Platform)
reconstruction pipeline into UIUXProMax (Section 11).

Bridges:
- BABOK v3.0 / IIBA-CBDA Diagnostic Forensics (DataAnalysisKit)
- 5 Domains of Product Architecture & Layer 0 Laws (UIUXProMax)
- Multi-Criteria Decision Analysis (Dynamic AHP / MCDA Utility Matrix)
- Interactive Generative UI visualizer scaffolding
"""

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ==============================================================================
# 1. UI Control Inventory & Friction Metrics
# ==============================================================================


@dataclass
class UIControlInventory:
    """Quantitative inventory of UI surface elements and cognitive constraints."""

    total_controls: int = 0
    layout_rows: int = 1
    height_px: int = 40
    duplicate_or_redundant: int = 0
    max_parallel_items_in_container: int = 0
    touch_target_violations: int = 0
    contrast_violations: int = 0
    has_horizontal_scrollbar: bool = False

    def compute_cognitive_friction(self) -> float:
        """
        Calculates normalized Cognitive Friction Index (0.0 - 10.0).
        - 0.0 - 3.0: Minimal Friction (Zen, High Focus)
        - 3.1 - 6.0: Moderate Friction (Standard Enterprise Density)
        - 6.1 - 8.0: High Friction (Cognitive Strain, Exceeds Miller's Law)
        - 8.1 - 10.0: Critical Cognitive Overload (User Disorientation)
        """
        # Miller's Law component (Optimal: <= 7 items, Tolerable: <= 9)
        miller_excess = max(0, self.total_controls - 7)
        miller_score = min(4.0, (miller_excess / 7.0) * 2.5)

        # Rule of 6 container saturation
        container_excess = max(0, self.max_parallel_items_in_container - 6)
        container_score = min(2.5, (container_excess / 6.0) * 2.0)

        # Vertical footprint penalty (Headers exceeding 88px)
        height_excess = max(0, self.height_px - 88)
        height_score = min(2.0, (height_excess / 120.0) * 2.0)

        # Redundancy penalty (Duplicate buttons, repeated 'All' tags)
        redundancy_score = min(1.5, self.duplicate_or_redundant * 0.75)

        # Sensory defects (Scrollbars, Touch violations)
        defect_score = (0.5 if self.has_horizontal_scrollbar else 0.0) + min(
            0.5, self.touch_target_violations * 0.1
        )

        total = round(
            miller_score
            + container_score
            + height_score
            + redundancy_score
            + defect_score,
            2,
        )
        return min(10.0, max(0.0, total))

    def audit_layer0_violations(self) -> List[Dict[str, str]]:
        """Audits the inventory against Layer 0 Macro, Meso, and Micro laws."""
        violations = []

        if self.total_controls > 9:
            violations.append(
                {
                    "rule": "RULE-L0-MESO-MILLERS-LAW",
                    "severity": "CRITICAL" if self.total_controls > 15 else "WARNING",
                    "message": f"Total active controls ({self.total_controls}) exceeds Miller's ceiling (7±2). Causes working memory saturation.",
                }
            )

        if self.max_parallel_items_in_container > 6:
            violations.append(
                {
                    "rule": "RULE-L0-MESO-RULE-OF-6",
                    "severity": "WARNING",
                    "message": f"Single container holds {self.max_parallel_items_in_container} parallel controls (>6). Mandates progressive disclosure or steppers.",
                }
            )

        if self.height_px > 120:
            violations.append(
                {
                    "rule": "RULE-L0-MESO-VERTICAL-BUDGET",
                    "severity": "CRITICAL" if self.height_px > 200 else "WARNING",
                    "message": f"Filter/header height ({self.height_px}px) consumes disproportionate vertical space (>120px budget).",
                }
            )

        if self.duplicate_or_redundant > 0:
            violations.append(
                {
                    "rule": "RULE-L0-MESO-REDUNDANT-CONTROLS",
                    "severity": "WARNING",
                    "message": f"Found {self.duplicate_or_redundant} redundant or duplicate interactive controls.",
                }
            )

        if self.has_horizontal_scrollbar:
            violations.append(
                {
                    "rule": "RULE-L0-MICRO-UNINTENDED-SCROLLBAR",
                    "severity": "WARNING",
                    "message": "Unconstrained flex wrap or fixed widths triggered an unintended horizontal scrollbar.",
                }
            )

        if self.touch_target_violations > 0:
            violations.append(
                {
                    "rule": "RULE-L0-MICRO-FITTS",
                    "severity": "WARNING",
                    "message": f"{self.touch_target_violations} controls violate minimum 44x44px touch/click target area.",
                }
            )

        return violations


# ==============================================================================
# 2. Ishikawa 6M UI Degeneration Decomposition
# ==============================================================================


@dataclass
class Ishikawa6MUIDecomposition:
    """Ishikawa 6M root cause decomposition for degraded user interfaces."""

    measurement: str = "No vertical pixel budget or control count ceiling enforced during feature growth."
    machine: str = "Unconstrained CSS flex-wrap container overflowing boundary, triggering native grey scrollbars."
    method: str = "Ad-hoc addition of filter tags directly into flat DOM rather than hierarchical or drawer encapsulation."
    material: str = "Low-contrast dark grey badges, inconsistent border radius, and missing visual priority hierarchy."
    milieu: str = "High-distraction operational environment (e.g. tablet on marina dock, glare, rapid triage needed)."
    man: str = "Operator working memory overwhelmed by 20+ parallel visual stimuli without primary focal point."

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


# ==============================================================================
# 3. Dynamic AHP & Multi-Criteria Decision Analysis (MCDA) Engine
# ==============================================================================

DEFAULT_UIUX_CRITERIA: Dict[str, Dict[str, Any]] = {
    "screen_economy": {
        "name": "Screen Real Estate & Vertical Economy",
        "description": "Reduction of vertical pixel footprint, freeing table/workspace viewport.",
        "weight": 0.25,
    },
    "cognitive_calm": {
        "name": "Cognitive Calm & Anti-Overwhelm",
        "description": "Adherence to Miller's 7±2 and Rule of 6, reduction of visual stimuli.",
        "weight": 0.25,
    },
    "triage_velocity": {
        "name": "Triage Velocity & 1-Click Access",
        "description": "Direct, immediate access to high-frequency filters without buried sub-menus.",
        "weight": 0.25,
    },
    "brand_coherence": {
        "name": "Brand Coherence & Luxury Polish",
        "description": "Sleek, bespoke aesthetics aligned with high-end luxury tokens and typography.",
        "weight": 0.15,
    },
    "implementation_risk": {
        "name": "Implementation & Regression Safety",
        "description": "Simplicity of implementation, zero regression risk, low refactor blast radius.",
        "weight": 0.10,
    },
}


class MCDADecisionEngine:
    """Multi-Criteria Decision Analysis engine for evaluating UI/UX architectural proposals."""

    def __init__(self, criteria: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        self.criteria = criteria or DEFAULT_UIUX_CRITERIA
        self._normalize_weights()

    def _normalize_weights(self) -> None:
        total_w = sum(c["weight"] for c in self.criteria.values())
        if total_w <= 0:
            raise ValueError("Total criteria weight must be > 0")
        for key in self.criteria:
            self.criteria[key]["weight"] = round(
                self.criteria[key]["weight"] / total_w, 4
            )

    @staticmethod
    def calculate_ahp_weights(
        pairwise_matrix: List[List[float]],
        criteria_keys: List[str],
    ) -> Tuple[Dict[str, float], float, bool]:
        """
        Calculates Saaty Analytic Hierarchy Process (AHP) priority weights and Consistency Ratio (CR).
        Returns: (weights_dict, consistency_ratio, is_consistent)
        """
        n = len(pairwise_matrix)
        if n == 0 or len(criteria_keys) != n:
            raise ValueError("Pairwise matrix dimension must match criteria count")

        # Column sums
        col_sums = [sum(pairwise_matrix[r][c] for r in range(n)) for c in range(n)]

        # Normalized matrix & priority vector
        weights: List[float] = []
        for r in range(n):
            norm_row_sum = sum(pairwise_matrix[r][c] / col_sums[c] for c in range(n))
            weights.append(norm_row_sum / n)

        # Principal Eigenvalue (lambda_max)
        lambda_max = sum(col_sums[c] * weights[c] for c in range(n))

        # Consistency Index (CI) & Ratio (CR)
        random_indices = {
            1: 0.0,
            2: 0.0,
            3: 0.58,
            4: 0.90,
            5: 1.12,
            6: 1.24,
            7: 1.32,
            8: 1.41,
        }
        ci = (lambda_max - n) / (n - 1) if n > 1 else 0.0
        ri = random_indices.get(n, 1.45)
        cr = round(ci / ri, 4) if ri > 0 else 0.0

        weights_dict = {criteria_keys[i]: round(weights[i], 4) for i in range(n)}
        is_consistent = cr <= 0.10

        return weights_dict, cr, is_consistent

    def evaluate_proposals(
        self,
        proposals: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Scores candidate proposals across criteria and returns ranked results with composite scores.
        Each proposal must have 'id', 'name', 'description', and scores (1.0-10.0) for each criterion key.
        """
        results = []
        for prop in proposals:
            composite = 0.0
            score_breakdown = {}

            for crit_key, crit_meta in self.criteria.items():
                raw_score = float(
                    prop.get("scores", {}).get(crit_key, prop.get(crit_key, 5.0))
                )
                weight = crit_meta["weight"]
                weighted_contribution = raw_score * weight
                composite += weighted_contribution
                score_breakdown[crit_key] = {
                    "raw": raw_score,
                    "weight": weight,
                    "weighted": round(weighted_contribution, 3),
                }

            item = dict(prop)
            item["compositeScore"] = round(composite, 2)
            item["scoreBreakdown"] = score_breakdown
            results.append(item)

        results.sort(key=lambda x: x["compositeScore"], reverse=True)

        # Compute rank and margin
        for idx, res in enumerate(results):
            res["rank"] = idx + 1
            if idx == 0 and len(results) > 1:
                res["marginOverRunnerUp"] = round(
                    results[0]["compositeScore"] - results[1]["compositeScore"], 2
                )

        return results


# ==============================================================================
# 4. Standardized Markdown Report & HTML Visualizer Scaffolder
# ==============================================================================


class UIUXReportGenerator:
    """Generates standardized Markdown diagnostic and proposal reports."""

    @staticmethod
    def generate_markdown(
        title: str,
        current_inventory: UIControlInventory,
        ishikawa: Ishikawa6MUIDecomposition,
        proposals: List[Dict[str, Any]],
        evaluated_proposals: List[Dict[str, Any]],
        criteria: Dict[str, Dict[str, Any]],
    ) -> str:
        winner = evaluated_proposals[0] if evaluated_proposals else {}
        friction = current_inventory.compute_cognitive_friction()
        violations = current_inventory.audit_layer0_violations()

        md = []
        md.append(f"# UI/UX Forensic Diagnostic & Reconstruction Proposal: {title}\n")
        md.append(
            "> **Governance Protocol**: Crystallized `UIUXProMax` Section 11 & `DataAnalysisKit` MCDA Engine.\n"
        )
        md.append("## 1. Executive Summary & Diagnostic Scorecard\n")
        md.append(
            f"- **Current Cognitive Friction Index**: `{friction}/10.0` "
            + ("🔴 CRITICAL OVERLOAD" if friction >= 7.0 else "🟡 MODERATE FRICTION")
            + "\n"
        )
        md.append(
            f"- **Total Active Controls**: `{current_inventory.total_controls}` (Miller Ceiling: `7±2`)\n"
        )
        md.append(
            f"- **Vertical Footprint**: `{current_inventory.height_px}px` across `{current_inventory.layout_rows}` rows\n"
        )
        md.append(
            f"- **Recommended Architecture**: **{winner.get('name', 'N/A')}** "
            f"(MCDA Score: `{winner.get('compositeScore', '0.0')}/10.0`)\n\n"
        )

        # Layer 0 Violations
        md.append("### Layer 0 Architectural Violations\n")
        if violations:
            md.append("| Rule ID | Severity | Diagnostic Findings |\n|---|---|---|\n")
            for v in violations:
                md.append(f"| `{v['rule']}` | **{v['severity']}** | {v['message']} |\n")
        else:
            md.append("✅ Zero Layer 0 violations detected.\n")
        md.append("\n---\n\n")

        # Ishikawa 6M
        md.append("## 2. Ishikawa 6M UI Degeneration Decomposition\n\n")
        md.append("| M-Category | Root Cause Mechanism |\n|---|---|\n")
        for k, v in ishikawa.to_dict().items():
            md.append(f"| **{k.capitalize()}** | {v} |\n")
        md.append("\n---\n\n")

        # Architectural Proposals
        md.append("## 3. Candidate Architectural Proposals\n\n")
        for prop in proposals:
            md.append(f"### Proposal {prop.get('id')}: {prop.get('name')}\n")
            md.append(f"{prop.get('description', '')}\n\n")
            md.append(
                f"- **Structural Archetype**: {prop.get('archetype', 'Modular Pattern')}\n"
            )
            md.append(
                f"- **Vertical Height Target**: `{prop.get('target_height_px', 'N/A')}px`\n"
            )
            md.append(f"- **Primary Advantage**: {prop.get('advantage', 'N/A')}\n\n")

        md.append("---\n\n")

        # MCDA Evaluation Matrix
        md.append("## 4. Multi-Criteria Decision Analysis (MCDA / AHP) Matrix\n\n")
        criteria_headers = " | ".join(
            f"{c['name']} ({int(c['weight'] * 100)}%)" for c in criteria.values()
        )
        md.append(f"| Rank | Proposal | {criteria_headers} | **Weighted Score** |\n")
        md.append(f"|:---:|---|{'---|' * len(criteria)}:---:|\n")

        for res in evaluated_proposals:
            scores_str = " | ".join(
                f"`{res['scoreBreakdown'][k]['raw']}`" for k in criteria
            )
            md.append(
                f"| **#{res['rank']}** | **{res['name']}** | {scores_str} | **`{res['compositeScore']}/10.0`** |\n"
            )

        md.append("\n### Strategic Selection Rationale\n")
        md.append(
            f"**Selected {winner.get('name')}** due to highest overall utility score (`{winner.get('compositeScore')}/10.0`). "
            f"Outperformed alternative proposals by a margin of `+{winner.get('marginOverRunnerUp', 0.0)}` points.\n\n"
        )

        return "".join(md)

    @staticmethod
    def generate_html_visualizer(
        title: str,
        proposals: List[Dict[str, Any]],
        evaluated_proposals: List[Dict[str, Any]],
        current_inventory: UIControlInventory,
    ) -> str:
        """Generates a self-contained, interactive HTML sandbox previewing the proposals."""
        winner = evaluated_proposals[0] if evaluated_proposals else {}
        props_json = json.dumps(evaluated_proposals, indent=2)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>UI/UX Reconstruction Sandbox: {title}</title>
  <style>
    :root {{
      --bg: #0F172A;
      --card-bg: #1E293B;
      --accent: #D4AF37;
      --text: #F8FAFC;
      --text-muted: #94A3B8;
      --border: rgba(255, 255, 255, 0.12);
      --font-body: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    body {{
      margin: 0;
      padding: 24px;
      background: var(--bg);
      color: var(--text);
      font-family: var(--font-body);
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
      padding-bottom: 16px;
      margin-bottom: 24px;
    }}
    .title {{ font-size: 20px; font-weight: 700; color: var(--accent); margin: 0; }}
    .badge {{
      background: rgba(212, 175, 55, 0.15);
      color: var(--accent);
      padding: 4px 12px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
      border: 1px solid var(--accent);
    }}
    .tabs {{
      display: flex;
      gap: 8px;
      margin-bottom: 24px;
    }}
    .tab-btn {{
      background: var(--card-bg);
      color: var(--text-muted);
      border: 1px solid var(--border);
      padding: 10px 18px;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.2s ease;
    }}
    .tab-btn.active {{
      background: var(--accent);
      color: #000;
      border-color: var(--accent);
    }}
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 20px;
    }}
    .metrics-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .metric-card {{
      background: rgba(0, 0, 0, 0.25);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 16px;
    }}
    .metric-value {{ font-size: 24px; font-weight: 800; color: var(--accent); }}
    .metric-label {{ font-size: 12px; color: var(--text-muted); margin-top: 4px; }}
  </style>
</head>
<body>
  <div class="header">
    <h1 class="title">UI/UX Reconstruction Sandbox: {title}</h1>
    <span class="badge">UIUXProMax + DataAnalysisKit</span>
  </div>

  <div class="metrics-grid">
    <div class="metric-card">
      <div class="metric-value">{current_inventory.total_controls} &rarr; &le; 8</div>
      <div class="metric-label">Visible Controls (Miller's Ceiling)</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">{current_inventory.height_px}px &rarr; 88px</div>
      <div class="metric-label">Vertical Footprint Reduction</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">{current_inventory.compute_cognitive_friction()} &rarr; 1.8</div>
      <div class="metric-label">Cognitive Friction Score</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">#{winner.get("rank", 1)} {winner.get("name", "P1")}</div>
      <div class="metric-label">MCDA Recommended Architecture</div>
    </div>
  </div>

  <div class="card">
    <h3>Proposals Multi-Criteria Evaluation (MCDA)</h3>
    <pre style="background: rgba(0,0,0,0.4); padding: 12px; border-radius: 6px; overflow-x: auto; font-size: 13px;">{props_json}</pre>
  </div>
</body>
</html>
"""
        return html


# ==============================================================================
# 5. Canonical Demo & CLI Entrypoint
# ==============================================================================


def run_canonical_demo() -> Dict[str, Any]:
    """Runs the canonical Incident Queue Filter Reconstruction demo."""
    # 1. Physical Inventory of messy UI
    inventory = UIControlInventory(
        total_controls=24,
        layout_rows=5,
        height_px=240,
        duplicate_or_redundant=2,
        max_parallel_items_in_container=12,
        touch_target_violations=4,
        contrast_violations=2,
        has_horizontal_scrollbar=True,
    )

    # 2. Ishikawa 6M
    ishikawa = Ishikawa6MUIDecomposition(
        measurement="No vertical pixel ceiling (240px consumed by 5 stacked rows).",
        machine="Unconstrained flex wrap spilling to native horizontal scrollbars.",
        method="Flat concatenation of status tags without segmented progressive disclosure.",
        material="Mismatched badge padding and grey-on-dark contrast fatigue.",
        milieu="Outdoor high-glare tablet viewing on marina pontoon requiring instant triage.",
        man="Cognitive overload from scanning 24 items simultaneously against Miller's Law.",
    )

    # 3. Formulate 3 Proposals
    proposals = [
        {
            "id": "P1",
            "name": "Proposal 1: Unified Luxury Command Strip",
            "description": "Dense, 2-tier fixed toolbar (88px). Tier 1: Search + Preset Segmented Controls. Tier 2: Status chips with count badges.",
            "archetype": "Segmented Command Strip",
            "target_height_px": 88,
            "advantage": "Zero sub-menus, 100% 1-click filter velocity, 63% vertical space reclaimed.",
            "scores": {
                "screen_economy": 8.5,
                "cognitive_calm": 9.0,
                "triage_velocity": 9.5,
                "brand_coherence": 9.2,
                "implementation_risk": 9.5,
            },
        },
        {
            "id": "P2",
            "name": "Proposal 2: Progressive Filter Drawer / Popover",
            "description": "Ultra-minimal 1-tier header (44px) with Search and an 'All Filters (N)' button triggering a right-side slide-over drawer.",
            "archetype": "Off-canvas Drawer",
            "target_height_px": 44,
            "advantage": "Maximum screen real estate, cleanest initial view for executive presentation.",
            "scores": {
                "screen_economy": 9.8,
                "cognitive_calm": 9.5,
                "triage_velocity": 6.0,
                "brand_coherence": 9.5,
                "implementation_risk": 7.5,
            },
        },
        {
            "id": "P3",
            "name": "Proposal 3: Dual-Axis Command Cockpit",
            "description": "Vertical left rail for persistent taxonomy filters (Model, Status, Priority) paired with a compact top bar for search.",
            "archetype": "Faceted 2-Pane Cockpit",
            "target_height_px": 44,
            "advantage": "High visibility of deep facets for desktop power users.",
            "scores": {
                "screen_economy": 7.0,
                "cognitive_calm": 8.0,
                "triage_velocity": 8.8,
                "brand_coherence": 8.5,
                "implementation_risk": 6.5,
            },
        },
    ]

    # 4. Run MCDA Evaluation
    engine = MCDADecisionEngine()
    evaluated = engine.evaluate_proposals(proposals)

    # 5. Generate Markdown Report
    report_md = UIUXReportGenerator.generate_markdown(
        title="Incident Queue Header & Filter De-Cluttering",
        current_inventory=inventory,
        ishikawa=ishikawa,
        proposals=proposals,
        evaluated_proposals=evaluated,
        criteria=engine.criteria,
    )

    # 6. Generate HTML Visualizer
    visualizer_html = UIUXReportGenerator.generate_html_visualizer(
        title="Incident Queue Header & Filter De-Cluttering",
        proposals=proposals,
        evaluated_proposals=evaluated,
        current_inventory=inventory,
    )

    return {
        "inventory": asdict(inventory),
        "friction_score": inventory.compute_cognitive_friction(),
        "violations": inventory.audit_layer0_violations(),
        "evaluated_proposals": evaluated,
        "report_markdown": report_md,
        "visualizer_html": visualizer_html,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="UIUXProMax Analytical Forensic & MCDA Engine (Section 11)"
    )
    parser.add_argument(
        "--demo", action="store_true", help="Run canonical Incident Queue demo"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )
    parser.add_argument(
        "--out-report", type=str, help="Path to write generated markdown report"
    )
    parser.add_argument(
        "--out-visualizer", type=str, help="Path to write generated HTML visualizer"
    )
    args = parser.parse_args()

    if args.demo or len(sys.argv) == 1:
        result = run_canonical_demo()

        if args.out_report:
            Path(args.out_report).write_text(
                result["report_markdown"], encoding="utf-8"
            )
            print(f"Report written to {args.out_report}")

        if args.out_visualizer:
            Path(args.out_visualizer).write_text(
                result["visualizer_html"], encoding="utf-8"
            )
            print(f"Visualizer written to {args.out_visualizer}")

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("\n=== UI/UX Analytical Diagnostic & MCDA Evaluation ===")
            print(f"Current Cognitive Friction: {result['friction_score']}/10.0")
            print(f"Layer 0 Violations Detected: {len(result['violations'])}")
            print("\nMCDA Proposals Ranking:")
            for p in result["evaluated_proposals"]:
                print(
                    f"  #{p['rank']} {p['name']} -> Score: {p['compositeScore']}/10.0 (Margin: +{p.get('marginOverRunnerUp', 0.0)})"
                )
            print(
                f"\nRecommended Architecture: {result['evaluated_proposals'][0]['name']}"
            )

        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
