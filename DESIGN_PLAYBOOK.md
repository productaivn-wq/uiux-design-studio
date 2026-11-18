# Software UI/UX Design Playbook (`DESIGN_PLAYBOOK.md`)

A practical guide for designing high-craft web, desktop, and mobile software interfaces using **UIUXProMax** and **ProductArchitectureKit**.

---

## Step 1: Choose Your Surface Mode (4 Surface Modes)

Never design an entire application as a single monolithic aesthetic. Assign every screen or route to one of the **4 Surface Modes**:

1. **`Persuade` (Landing Pages, Pricing, Onboarding)**:
   - **Goal**: High conversion clarity.
   - **Rules**: Exactly **1 primary Call-to-Action (CTA)** per screen (Hick's Law); bold display typography; authentic product proof instead of generic stock illustrations.
2. **`Operate` (Dashboards, CRM, Admin Cockpits, IDE Tools)**:
   - **Goal**: High task velocity and cognitive calm.
   - **Rules**: Active surface density $\eta_{\text{fill}} \ge 85\%$; tabular numerals (`font-variant-numeric: tabular-nums lining-nums`); strict 8pt/4pt spatial grid; max 6 items/inputs per group (**Rule of 6** — use steppers or tabs for $>6$ fields); defensive `min-w-0` on flex/grid children.
3. **`Read` (Documentation, Knowledge Bases, Reports)**:
   - **Goal**: Effortless long-form comprehension.
   - **Rules**: Line width constrained to **60–75 characters (`60ch–75ch`)**; generous line-height (`1.5–1.7`); sticky table of contents.
4. **`Experience` (3D Showcases, Digital Twins, Creative Studios)**:
   - **Goal**: Immersive visual storytelling.
   - **Rules**: Minimal receded UI chrome; full-bleed canvas; bespoke motion choreography (`templates/overdrive/html_in_canvas_shaders.html`).

---

## Step 2: Pick a Curated OKLCH Design World (Or Search 192 Palettes)

To avoid generic AI purple-gradient templates ("AI Slop"), start with one of the **5 Curated OKLCH Design Worlds** or run `scripts/search.py`:

| World ID | Best For | Key Palette (`oklch`) & Typography |
| :--- | :--- | :--- |
| **`obsidian-enterprise-density`** | SaaS Dashboards, FinTech, DevTools, PM Cockpits | Deep Obsidian `oklch(16% 0.015 250)`, Card Slate `oklch(22% 0.02 250)`, Cyan Accent `oklch(75% 0.16 210)` · *Plus Jakarta Sans + JetBrains Mono* |
| **`luxury-maritime-atelier`** | Concierge Apps, High-Touch CRM, Hospitality, Executive Portals | Warm Linen Ivory `oklch(95.8% 0.008 85)`, Marine Navy `oklch(22.5% 0.032 245)`, Bronze Gold `oklch(53.2% 0.092 78.5)` · *Cormorant Garamond + Be Vietnam Pro + JetBrains Mono* |
| **`swiss-bauhaus-modernist`** | Architecture, Legal Tech, Specification Platforms | Pure Chalk `oklch(98% 0 0)`, Carbon Ink `oklch(15% 0 0)`, International Orange `oklch(62% 0.22 35)` · *Inter / Neue Haas Grotesk (0px radii, 1px hairline grids)* |
| **`warm-editorial-linen`** | Research Tools, Note-Taking, Publishing, AI Writing Studios | Oatmeal Paper `oklch(94% 0.015 75)`, Charcoal Ink `oklch(20% 0.01 60)`, Terracotta `oklch(55% 0.14 42)` · *Newsreader + Plus Jakarta Sans* |
| **`industrial-neo-brutalist`** | Hardware Diagnostics, CLI Dashboards, Web3/Engineering Labs | Voltage Yellow `oklch(92% 0.19 105)`, Void Black `oklch(10% 0 0)`, Pure White `oklch(100% 0 0)` · *Space Grotesk + Space Mono* |

---

## Step 3: Lock Your Contracts (`PRODUCT.md` & `DESIGN.md`)

1. Copy `starter-templates/PRODUCT.md` and `starter-templates/DESIGN.md` to your project root.
2. Compile your `DESIGN.md` tokens into CSS and Tailwind v4:
   ```bash
   python skills/UIUXProMax/scripts/design_md_linter.py DESIGN.md --compile-tokens ./src/styles/tokens
   ```
3. Include `starter-templates/spatial_layout_primitives.css` in your app to compose layouts using deterministic primitives:
   - `.tsy-stack` (vertical flow with `data-gap="compact|nested|panel|layout|page"`)
   - `.tsy-cluster` (horizontal wrapping pill/button bars)
   - `.tsy-split` (2-column ratios: `1-1`, `2-1`, `3-1`, `golden`, `main-side`)
   - `.tsy-subgrid-card-deck` + `.tsy-subgrid-rows` (multi-card row alignment)

---

## Step 4: Prompt Your AI Assistant with the 24 Design Verbs

When asking Claude, Cursor, Windsurf, or Antigravity to design or refine a screen, use explicit verbs from `UIUXProMax`:

- **Create from scratch**:
  - `shape`: *"Shape the information architecture, user flow (<=3 clicks), and wireframe hierarchy for the billing screen before writing CSS."*
  - `impeccable`: *"Execute an impeccable UI generation pass in `Operate` surface mode using `DESIGN.md` tokens."*
- **Refine specific layers**:
  - `typeset`: *"Typeset this view: enforce <=3 font families, >=11px legibility floor, 60-75ch prose measure, and `tabular-nums lining-nums` on all KPI numbers."*
  - `layout`: *"Refactor this screen's layout using `.tsy-stack`, `.tsy-split`, and the 3-Strata Vertical Budget so there are zero empty bottom voids."*
  - `colorize`: *"Apply semantic OKLCH tokens from `DESIGN.md`; remove all generic purple gradients and reserve red strictly for destructive actions."*
  - `animate`: *"Add purposeful `cubic-bezier(0.16, 1, 0.3, 1)` transitions and `scale >= 0.95` entry animations."*
- **Simplify & Harden**:
  - `distill`: *"Distill this view: remove nested cards-inside-cards, eyebrow pill chips, and redundant wrapper borders."*
  - `harden`: *"Harden this UI for responsive viewports (360px to 1440px): add `min-w-0` anti-blowout guards, skeleton loaders for >400ms calls, and 44x44px touch targets."*

---

## Step 5: Verify Design Craft (Optional Local Audit)

To check if your HTML/CSS/React components follow the **Layer 0 Design Laws** (8pt grid, $\ge 44\times 44\text{px}$ hit targets, WCAG 2.1 AA contrast, Typography Governance, and Anti-Slop rules):
```bash
python skills/UIUXProMax/scripts/layer0_validator.py ./src
```
