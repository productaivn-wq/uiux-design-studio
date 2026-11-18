---
version: "1.0.0"
world_id: "obsidian-enterprise-density"
color_space: "oklch"
tokens:
  colors:
    surface:
      canvas: "oklch(16% 0.015 250)"
      card: "oklch(22% 0.02 250)"
      card_elevated: "oklch(26% 0.025 250)"
      sidebar: "oklch(14% 0.015 250)"
      header: "oklch(16% 0.015 250 / 0.95)"
      backdrop: "oklch(10% 0.01 250 / 0.75)"
    text:
      primary: "oklch(96% 0.005 250)"
      secondary: "oklch(80% 0.015 250)"
      muted: "oklch(65% 0.02 250)"
      inverse: "oklch(16% 0.015 250)"
    accent:
      primary: "oklch(75% 0.16 210)"
      light: "oklch(85% 0.12 210)"
      glow: "oklch(75% 0.16 210 / 0.15)"
    state:
      danger: "oklch(55% 0.22 25)"
      success: "oklch(68% 0.16 150)"
      warning: "oklch(78% 0.18 70)"
    border:
      subtle: "oklch(28% 0.02 250)"
      card: "oklch(32% 0.025 250)"
      accent: "oklch(75% 0.16 210 / 0.45)"
  typography:
    fonts:
      editorial: "'Plus Jakarta Sans', -apple-system, sans-serif"
      body: "'Plus Jakarta Sans', -apple-system, sans-serif"
      mono: "'JetBrains Mono', monospace"
    scale:
      xs: "0.75rem"
      sm: "0.875rem"
      base: "1.000rem"
      lg: "1.125rem"
      xl: "1.250rem"
      2xl: "1.500rem"
      3xl: "1.875rem"
      4xl: "2.250rem"
  shape:
    radii:
      none: "0px"
      xs: "2px"
      sm: "4px"
      md: "6px"
      lg: "8px"
      full: "9999px"
    border_widths:
      hairline: "1px"
      focus: "2px"
  shadows:
    sm: "0 1px 2px oklch(10% 0.01 250 / 0.25)"
    card: "0 2px 4px oklch(10% 0.01 250 / 0.35)"
    hover: "0 4px 12px oklch(10% 0.01 250 / 0.45)"
    drawer: "-4px 0 24px oklch(10% 0.01 250 / 0.65)"
  layout:
    max_width: "1600px"
    sidebar_width: "260px"
    gutters:
      page: "24px"
      layout: "16px"
      panel: "12px"
      nested: "8px"
      compact: "4px"
---

# Design System Specification: {{project_name}}

## 1. Visual World Architecture
The **{{world_name}}** visual system governs optical rendering across all {{project_name}} interfaces.

## 2. Spatial Layout Primitives (`spatial_layout_primitives.css`)
Layouts are constructed exclusively from standardized spatial primitives:
1. `.tsy-stack`: Vertical cadence distribution with deterministic gap tokens (`data-gap="panel|layout|page"`).
2. `.tsy-cluster`: Horizontal tag and button distribution with defensive flex-wrap.
3. `.tsy-split`: Column split ratios (`data-ratio="golden|main-side|1-1"`).
4. `.tsy-subgrid-card-deck`: Subgrid track synchronization across header, body, and footer.
- **Component Layout Agnosticism**: Reusable components (`.card`, `.btn`, `.chip`, `.table`) declare `margin: 0`. Spacing is strictly governed by parent primitives.
- **Anti-Blowout Defensive Invariant**: All layout slots declare `min-inline-size: 0; min-width: 0; box-sizing: border-box;`.

## 3. Component Inventory & Interactive Contracts

### 3.1 Primary Action Button (`.btn-primary`)
- **Default**: Background `var(--accent-primary)`, Text `var(--text-inverse)`, Padding `8px 16px`, Radius `var(--radius-sm)`.
- **Hover**: Background `var(--accent-light)`, Transform `translateY(-1px)`.
- **Active**: Transform `translateY(0px)`.
- **Focus-Visible**: Outline `2px solid var(--accent-light)`, Outline-offset `2px`.

## 4. Layer 0 Mechanical Linting Rules
All UI deliverables must satisfy `layer0_validator.py` ($P = 1$):
- `RULE-L0-MICRO-FITTS`: Interactive touch/click targets $\ge 44\times 44\text{px}$.
- `RULE-L0-MICRO-8PT-GRID`: Spacing must satisfy `mod 8 == 0` or 4px micro-steps.
- `RULE-L0-MICRO-CONTRAST`: WCAG 2.1 AA luminance contrast $\ge 4.5:1$.
- `RULE-L0-MESO-HICKS-LAW`: Max 1 primary CTA per container or drawer.
- `RULE-L0-MESO-RULE-OF-6`: Forms exceeding 6 inputs mandate multi-step steppers or tabs.
