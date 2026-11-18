---
version: "1.0.0"
project: "{{project_name}}"
domain: "{{project_domain}}"
last_audited: "{{audit_date}}"
governing_standard: "UIUX-PRO-MAX-V2"
---

# Product Context & Operational SSOT

## 1. Product Purpose
- **System Identity**: {{system_identity}}
- **Business SSOT**: [Project Charter](PRODUCT.md)
- **Core Value Proposition**: {{core_value_proposition}}
- **Economic Moat**: {{economic_moat}}
- **Friction Budget**: Core workflows achieved in $\le 3$ clicks/actions.

## 2. Platform & Form Factor
- **Platform**: {{target_platform}}
- **Target Devices**: {{target_devices}}
- **Execution Invariant**: Gate `GW-HEADLESS-01` ($P=1$) off-screen headless execution.

## 3. Users & Field Ergonomics
- **User 1: {{primary_user_role}}**:
  - Operational Context: {{primary_user_environment}}
  - Ergonomics: {{primary_user_ergonomics}}
- **User 2: {{secondary_user_role}}**:
  - Operational Context: {{secondary_user_environment}}
  - Ergonomics: {{secondary_user_ergonomics}}

## 4. Surface Modes
- **Mode: Operate (`{{operate_routes}}`)**:
  - Density: High / Tabular ($\eta_{\text{fill}} \ge 85\%$).
  - Invariants: Tabular figures, max 6 items per container (Rule of 6), inline metrics.
- **Mode: Read (`{{read_routes}}`)**:
  - Density: Comfortable / Editorial.
  - Invariants: Measure 60–75ch, line height 1.5–1.7, high contrast.
- **Mode: Persuade (`{{persuade_routes}}`)**:
  - Density: Authoritative / Presentation.
  - Invariants: Single primary CTA (Hick's Law), conversion sections.

## 5. Accessibility & Inclusion
- **Contrast Floor**: WCAG 2.1 AA ($\ge 4.5:1$) baseline.
- **Touch / Click Hit Areas**: Fitts's Law minimum $44\times 44\text{px}$.
- **Reduced Motion**: Respects `prefers-reduced-motion: reduce`.
- **Keyboard Navigation**: Full logical tabindex and visible focus rings.

## 6. Constraints & Anti-References
- ❌ **NO AI Slop**: Hairline borders combined with wide fuzzy shadows ($\ge 24\text{px}$) prohibited.
- ❌ **NO Reflex Beige/Cream**: Warm cream palettes (`#fcfbf9`, `#f5f2eb`) prohibited as root ground.
- ❌ **NO Side-Tab Borders**: Thick 1-sided colored borders on rounded elements prohibited.
- ❌ **NO Eyebrow Pill Chips**: Tracked uppercase badges preceding `<h1>` prohibited.
- ❌ **NO Nested Cards**: Wrapping `.card` components inside parent `.card` containers prohibited.
- ❌ **NO Pulsing Dots**: Decorative pulse animations without live telemetry binding prohibited.
