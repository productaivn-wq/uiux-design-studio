# UI/UX Forensic Diagnostic & Reconstruction Proposal: {{ title }}

> **Governance Standard**: `UIUXProMax` Section 11 & `DataAnalysisKit` Multi-Criteria Decision Analysis (MCDA) Protocol.
> **Date**: {{ date }}
> **Author**: {{ author }}
> **Target Component / Surface**: `{{ component_path }}`

---

## 1. Executive Summary & Diagnostic Scorecard

- **Current Cognitive Friction Index**: `{{ friction_score }}/10.0` ({{ friction_level }})
- **Total Active Surface Controls**: `{{ total_controls }}` (Miller's Cognitive Ceiling: `7±2`)
- **Vertical Footprint**: `{{ height_px }}px` across `{{ layout_rows }}` stacked rows
- **Recommended Architectural Target**: **{{ recommended_proposal_name }}** (MCDA Score: `{{ recommended_score }}/10.0`)
- **Estimated Reclaimed Viewport**: `{{ reclaimed_viewport_pct }}%`

### Layer 0 Architectural Violations Summary
| Rule ID | Severity | Findings & Degradation Mechanism |
|---|---|---|
{% for v in violations %}
| `{{ v.rule }}` | **{{ v.severity }}** | {{ v.message }} |
{% endfor %}

---

## 2. Ishikawa 6M UI Degeneration Decomposition

| M-Category | Root Cause Mechanism |
|---|---|
| **Measurement** | {{ ishikawa.measurement }} |
| **Machine** | {{ ishikawa.machine }} |
| **Method** | {{ ishikawa.method }} |
| **Material** | {{ ishikawa.material }} |
| **Milieu (Context)** | {{ ishikawa.milieu }} |
| **Man (Cognitive)** | {{ ishikawa.man }} |

---

## 3. Candidate Architectural Proposals

{% for p in proposals %}
### Proposal {{ p.id }}: {{ p.name }}
{{ p.description }}

- **Structural Archetype**: {{ p.archetype }}
- **Vertical Height Budget**: `{{ p.target_height_px }}px`
- **Key Advantage**: {{ p.advantage }}
- **Trade-off / Mitigation**: {{ p.tradeoff }}

{% endfor %}

---

## 4. Multi-Criteria Decision Analysis (MCDA / AHP) Matrix

| Rank | Proposal Option | Screen Economy (25%) | Cognitive Calm (25%) | Triage Velocity (25%) | Brand Coherence (15%) | Low Risk (10%) | **Composite Score** |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|
{% for r in evaluated_proposals %}
| **#{{ r.rank }}** | **{{ r.name }}** | `{{ r.scoreBreakdown.screen_economy.raw }}` | `{{ r.scoreBreakdown.cognitive_calm.raw }}` | `{{ r.scoreBreakdown.triage_velocity.raw }}` | `{{ r.scoreBreakdown.brand_coherence.raw }}` | `{{ r.scoreBreakdown.implementation_risk.raw }}` | **`{{ r.compositeScore }}/10.0`** |
{% endfor %}

### Selection Rationale
**Selected {{ recommended_proposal_name }}** based on superior weighted utility (`{{ recommended_score }}/10.0`) with a margin of `+{{ margin }}` over runner-up.

---

## 5. Deterministic Code Node Verification ($P=1$) Gate Plan
1. **Mechanical Linting**: `python scripts/layer0_validator.py <src>` &rarr; Compliance 1.00.
2. **Regression Testing**: Automated component tests verifying responsive layout and accessibility.
3. **Empirical Proof**: Headless browser snapshot verifying live rendered appearance under Gate `GW-DATA-01`.
