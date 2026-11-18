---
name: UIUXProMax
status: active
version: 2.6.710
changed_at: 2026-11-08
description: Enterprise UI/UX Design Intelligence Engine, Forensic Diagnostic and
  Layer 0 Governance Linter. Grounded in nextlevelbuilder/ui-ux-pro-max-skill, pbakaus/impeccable,
  emilkowalski/skills, greensock/gsap-skills, enesozturk/dimensional-drawing, VoltAgent/awesome-design-md,
  and nexu-io/open-design, featuring 24 design verbs, 4 Surface Modes, 5 Curated Design Worlds,
  65+ deterministic Anti-Slop & Kinetic rules, StageShow Choreography Module (modules/stageshow), GW-UIUX-STAGE-FIREWALL-01, BM25 search over 21 datasets (including brand
  DESIGN.md archetypes and anti-slop filtered components), Apple CAD dimensional spec sheets,
  and Two-Stage Gate GW-UIUX-01 (P=1).
capabilities:
- instruments
- friction-budgets
- the-reversibility-rule
- state-persistence
- global-ontology
- gestalt-bounding
- latency-budgets
- analytical-forensic-diagnostic
- mcda-decision-science
- impeccable-design-vocabulary
- anti-slop-detector-suite
- surface-modes
- oklch-token-architecture
- typography-governance-suite
- rendered-dom-geometry-auditor
risk_class: TIER_1
approval_checkpoints:
- scope_confirmation
- security_confirmation
domain_adapter_contract:
  version: 3.1.0
  boundary: deterministic_p1_and_agentic_bdi
  mece_demarcation: Canonical owner of UIUXProMax domain operations within the Antigravity
    9-stage enterprise lifecycle.
  validation: pydantic_or_dataclass_schema
---

# UI/UX Pro Max (`UIUXProMax`)

> **Authoritative Upstream Reference**: Grounded in and modeled after [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (120,000+ GitHub Stars), the #1 gold-standard AI skill for UI/UX intelligence across Claude Code, Cursor, Windsurf, and Antigravity.

---

## 1. Architectural Overview & Separation of Concerns

`UIUXProMax` provides an enterprise-grade design intelligence engine that cleanly decouples **creative UI/UX reasoning** ($P \in (0, 1)$ Agent Node) from **immutable architectural laws & mechanical linting** ($P = 1$ Code Node).

```
                      +-------------------------------------------------------------+
                      |                      Agent Node P in (0, 1)                 |
                      |  192 Reasoning Rules | 79 Styles | 192 Palettes | 74 Fonts  |
                      |          BM25 Search Engine (scripts/search.py)             |
                      +------------------------------+------------------------------+
                                                     |
                                                     v
                      +-------------------------------------------------------------+
                      |                The 5 Domains of Product Architecture        |
                      |  Domain 1: Truth (Human)        Domain 2: Logic (System)    |
                      |  Domain 3: Perception (Surface) Domain 4: Reality (Machine) |
                      |                    Domain 5: Outcomes (Business)            |
                      +------------------------------+------------------------------+
                                                     |
                                                     v
                      +-------------------------------------------------------------+
                      |                Layer 0 Immutable Architectural Laws         |
                      |  Macro (Friction/Undo)           Meso (Miller/Hick/Rule of 6)|
                      |  Micro (8pt/Fitts/WCAG)          Meta (WCAG 2.1 AA/Skeletons)|
                      +------------------------------+------------------------------+
                                                     |
                                                     v
                      +-------------------------------------------------------------+
                      |                   Code Node Engine P = 1                    |
                      |  scripts/layer0_validator.py  --> Gate GW-UIUX-01 (PASS/FAIL)|
                      +-------------------------------------------------------------+
```

---

## 2. The 5 Domains of Product Architecture

Every product capability and interface decision strictly optimizes exactly one of these five mutually exclusive domains:

1. **Truth (Domain 1 - Optimizes for the Human)**:
   - Extracts revealed preferences from empirical behavior rather than stated opinions.
   - Mitigates *Desirability Risk*.
   - Instruments: Qualitative fieldwork, Customer Journey Maps (CJM), user friction audits.
2. **Logic (Domain 2 - Optimizes for the System)**:
   - Structures invisible mathematics, routing, and information architecture.
   - Mitigates *Utility Risk*.
   - Instruments: Master Information Architecture Document (IAD), state machines (FSM), Kahn DAG execution, Separation of Duties (SOD).
3. **Perception (Domain 3 - Optimizes for the Surface)**:
   - Renders logic into sensory interfaces (colors, typography, visual weight, rhythm).
   - Mitigates *Aesthetic & Trust Risk*.
   - Instruments: Design tokens, obsidian/champagne gold harmony, typography scale, micro-interactions.
4. **Reality (Domain 4 - Optimizes for the Machine & Law)**:
   - Enforces physical hardware constraints, network latency, and legal accessibility compliance.
   - Mitigates *Feasibility & Legal Risk*.
   - Instruments: WCAG 2.1 AA (4.5:1 optical contrast), headless execution, skeleton loaders ($>400\text{ms}$), Decree 13/GDPR privacy.
5. **Outcomes (Domain 5 - Optimizes for the Business)**:
   - Aligns software capabilities to the Business Model Canvas (BMC) and Customer Lifetime Value (CLV).
   - Mitigates *Viability Risk*.
   - Instruments: Revenue conversion moats, warranty claim margins ($\ge 30\%$), deposit gates.

---

## 3. Layer 0 Infrastructure Track (Immutable Architectural Laws)

Layer 0 operates permanently as mandatory constraints:

### 3.1 Layer 0.1: Macro-Level Laws (Routing & Architecture)
- **Friction Budgets**: Core Use Cases mathematically achievable in $\le 3$ system decisions or clicks.
- **The Reversibility Rule**: Zero logical dead-ends. Every destructive action requires an explicit escape route or 1-click 'Undo' path.
- **State Persistence**: Interrupted workflows retain inputted form data globally (`localStorage` / URL hash) without forcing a restart.
- **Global Ontology**: Master IAD defining navigation hierarchies, entity schemas, and breadcrumbs.

### 3.2 Layer 0.2: Meso-Level Laws (Cognitive & Compositional)
- **Miller's Law**: Maximum $7 \pm 2$ distinct groups of information or parallel choices per view.
- **Rule of 6 (Anti-Overwhelm Ceiling)**: Form inputs, visible table columns, card metrics, and action toolbars are capped at $\le 6$ items per container. Workflows exceeding 6 parameters mandate multi-step Stepper forms (3–5 fields/step) or progressive disclosure tabs.
- **Hick's Law**: Exactly 1 primary Call-to-Action (CTA) per screen or drawer view. Secondary actions require progressive disclosure or secondary styling.
- **Gestalt Bounding**: Elements triggering related backend endpoints must share spatial proximity and a bounding container.
- **Anti-Void Invariant (`RULE-L0-MESO-EMPTY-VOID`)**: Flex column containers (`flex-direction: column`) MUST NOT declare unconstrained `justify-content: space-between|space-around|space-evenly` inside bounded height cards. Unconstrained spacing tears apart visual proximity and produces massive dead-pixel chasms. Stacks must rely on deterministic gaps (`gap: var(--tsy-space-*)`) and anchor footers via `margin-top: auto`.
- **Deviation Mechanism (Shatter Request)**: Formal waiver (`<!-- @shatter-request: reason -->`) required to bypass Meso-level density limits for Expert/Enterprise modes.

### 3.3 Layer 0.3: Micro-Level Laws (Perceptual & Sensory)
- **Spatial & Morphological**: Strict 8pt grid alignments (`mod 8 == 0` or 4px micro-step), spatial padding tokens (`--tsy-space-*`), $z$-index elevation scale.
- **Aspect Ratio Harmonization Invariant (`RULE-L0-MICRO-ASPECT-FIT`)**: Embedded graphic elements (SVGs, charts, canvases) must align with container aspect ratios ($\Delta_{AR} \le 0.25$). Panoramic SVGs ($AR \ge 2.0$) must span full-width rows (`grid-column: 1 / -1`) or refactor internal geometry rather than letterboxing inside multi-column cards.
- **Pixel Budget & Fill Factor Floor (`RULE-L0-MICRO-PIXEL-FILL-FACTOR`)**: Visual cards in enterprise dashboards and executive infographics must maintain an active surface density $\eta_{\text{fill}} \ge 85\%$. Data tables must be enriched with inline sparkbars, quantile markers, and 2D scatter coordinates to maximize Edward Tufte's data-ink ratio.
- **Fitts's Law**: Minimum $44 \times 44\text{px}$ interactive touch/click hit areas for buttons, links, inputs, and tab triggers.
- **Chromatic & Optical**: Semantic color tokens. Red (`#DC2626`) is strictly reserved for Critical/Destructive actions only. Neutral borders and dark luxury obsidian palettes.
- **Typographic & Glyphic**: Modular typography scale, line heights ($1.5$ body, $1.2$ headings), and character-length limits (max 60–75 chars per line for prose).
- **Kinetic & Temporal**: Smooth easing curves (`cubic-bezier(0.16, 1, 0.3, 1)`), interaction states (Hover, Active, Focus-visible), visual response SLA $\le 100\text{ms}$.

### 3.4 Layer 0.4: Meta-Level Laws (Regulatory & Machine)
- **Legal Accessibility (WCAG 2.1 AA)**: Mandatory 4.5:1 optical contrast ratio for normal text, 3:1 for large text and UI components. ARIA tagging, focus visible rings, keyboard `tabindex` sequencing.
- **Latency Budgets**: Any backend API call taking $> 400\text{ms}$ automatically mandates a visual skeleton loader (e.g. champagne shimmer placeholder).
- **Data Privacy (GDPR/Decree 13)**: Prohibits pre-checked consent checkboxes and pre-filled PII in onboarding forms.

---

## 4. BM25 Search Engine & Design System Generator

`UIUXProMax` bundles a blazing-fast, zero-dependency BM25 CLI search engine over 17 curated datasets:

### 4.1 CLI Quick Reference
```bash
# 1. Search styles by keyword
python skills/UIUXProMax/scripts/search.py "luxury dark minimal" --domain style

# 2. Search color palettes
python skills/UIUXProMax/scripts/search.py "yacht luxury obsidian" --domain color

# 3. Search UX guidelines for specific patterns
python skills/UIUXProMax/scripts/search.py "form validation error" --domain ux

# 4. Search font pairings
python skills/UIUXProMax/scripts/search.py "editorial premium" --domain typography

# 5. Search data visualization charts
python skills/UIUXProMax/scripts/search.py "engine operating hours comparison" --domain chart

# 6. Stack-specific recommendations
python skills/UIUXProMax/scripts/search.py "modal drawer" --stack html-tailwind

# 7. Generate a complete end-to-end design system
python skills/UIUXProMax/scripts/search.py "luxury yacht crm" --design-system --project-name "maritime-crm" --variance 3 --motion 4 --density 8
```

### 4.2 Available Search Domains
| Domain | Source CSV | Coverage | Key Columns |
|---|---|---|---|
| `style` | `styles.csv` | 79 UI Styles | Style Category, Keywords, Best For, Framework Compatibility, CSS Keywords |
| `color` | `colors.csv` | 192 Palettes | Product Type, Primary, Secondary, Accent, Background, Destructive, Notes |
| `chart` | `charts.csv` | 25 Chart Types | Data Type, Best Chart Type, When to Use/NOT Use, A11y Notes |
| `landing` | `landing.csv` | Conversion Patterns | Pattern Name, Conversion Optimization, Section Order, Primary CTA |
| `product` | `products.csv` | Industry Blueprints | Product Type, Primary/Secondary Style, Dashboard Style, Color Focus |
| `ux` | `ux-guidelines.csv` | 119 UX Rules | Category, Issue, Description, Do, Don't, Code Good/Bad, Severity |
| `typography` | `typography.csv` | 74 Font Pairings | Heading/Body Fonts, Mood Keywords, Google Fonts URL, Tailwind Config |
| `icons` | `icons.csv` | Icon Taxonomy | Icon Name, Library (Lucide/Phosphor), Allowed Contexts, Semantic Role |
| `gsap` | `motion.csv` | GSAP Snippets | Animation Name, Code, Performance, Duration, Easing |
| `react` | `react-performance.csv` | Performance Rules | Component Pattern, Anti-pattern, Memoization, Virtualization |

---

## 5. Deterministic Code Engine ($P=1$): `layer0_validator.py`

All UI modifications must pass mechanical Layer 0 linting before release.

### 5.1 Invocation
```bash
# Scan a specific directory
python skills/UIUXProMax/scripts/layer0_validator.py path/to/templates_or_src

# Scan single file
python skills/UIUXProMax/scripts/layer0_validator.py path/to/file.html
```

### 5.2 Automated Rule Verifications
| Rule ID | Layer | Check Description |
|---|---|---|
| `RULE-L0-MICRO-FITTS` | Micro (0.3) | Ensures interactive elements have `min-height: 44px`, `min-width: 44px` or `p-3/py-3`. |
| `RULE-L0-MICRO-8PT-GRID` | Micro (0.3) | Spacing/margins/paddings must be multiples of 8px (or 4px micro-step). |
| `RULE-L0-MICRO-SUBPIXEL` | Micro (0.3) | Flags fractional pixels (e.g. `0.25px`, `1.5px`) causing rendering blur. |
| `RULE-L0-MICRO-CONTRAST` | Micro (0.3) | Optical luminance contrast linter (WCAG AA $\ge 4.5:1$). |
| `RULE-L0-MESO-HICKS-LAW` | Meso (0.2) | Flags multiple primary CTAs within the same container. |
| `RULE-L0-MESO-RULE-OF-6` | Meso (0.2) | Flags forms with $>6$ inputs lacking multi-step steppers or tabs. |
| `RULE-L0-MACRO-BLOCKING-UI` | Macro (0.1) | Prohibits primitive `window.prompt()` / `alert()` blocking main thread. |
| `RULE-L0-MICRO-COLOR-INVARIANT` | Micro (0.3) | Prohibits hardcoded white `#fff` in JS templates that break light mode. |
| `RULE-L0-MICRO-ANTI-BLOWOUT` | Micro (0.3) | Enforces `min-inline-size: 0` / `min-width: 0` on flex/grid layout slots. |
| `RULE-L0-MICRO-ZERO-ROOT-MARGIN`| Micro (0.3) | Flags reusable components declaring root margins (Component Layout Agnosticism). |
| `RULE-SLOP-HAIRLINE-WIDE-SHADOW`| Anti-Slop (0.3) | Flags hairline borders ($\le 1\text{px}$) paired with wide diffuse shadows ($\ge 24\text{px}$). |
| `RULE-SLOP-SIDE-TAB` | Anti-Slop (0.3) | Flags 1-sided thick border ($\ge 3\text{px}$) on rounded element (`radius \ge 4px`). |
| `RULE-SLOP-AI-BEIGE` | Anti-Slop (0.3) | Flags warm cream/beige background hexes (`#fcfbf9`, `#f5f2eb`) as root background. |
| `RULE-SLOP-HERO-EYEBROW-CHIP` | Anti-Slop (0.2) | Flags hero eyebrow uppercase pill chips sitting directly above `<h1>`. |
| `RULE-SLOP-ITALIC-SERIF-HERO` | Anti-Slop (0.3) | Flags italic serif display headlines on `<h1>` on generic interfaces. |
| `RULE-SLOP-ICON-TILE-STACK` | Anti-Slop (0.2) | Flags symmetrical rounded icon tiles stacked vertically above headings. |
| `RULE-SLOP-AI-PALETTE` | Anti-Slop (0.3) | Flags canonical AI violet/purple gradients (`#7c3aed`, `#8b5cf6`, `#6366f1`). |
| `RULE-SLOP-GRADIENT-TEXT` | Anti-Slop (0.3) | Flags `background-clip: text` paired with linear gradients on headings/metrics. |
| `RULE-SLOP-NESTED-CARDS` | Anti-Slop (0.2) | Flags card containers nested directly inside card containers (framing exhaustion). |
| `RULE-SLOP-PULSING-DOT` | Anti-Slop (0.3) | Flags decorative pulsing status dots lacking live telemetry bindings. |
| `RULE-SLOP-BOUNCE-EASING` | Anti-Slop (0.3) | Flags bounce/elastic easing in favor of smooth cubic-bezier curves. |
| `RULE-SLOP-NUMBERED-SECTION-LABELS`| Anti-Slop (0.2)| Flags artificial numbered section labels (`01`, `02`) beside headings. |

---

## 6. End-to-End Execution Protocol (The 5-Step Craft Cycle)

When designing, refactoring, or reviewing any user interface:

1. **Step 1: Discover & Search**
   - Query BM25 via `scripts/search.py` for target product domain, color palette, typography pairing, and style guide.
2. **Step 2: Align the 5 Domains**
   - Verify Truth (user desire), Logic (routing $\le 3$ clicks), Perception (tokens), Reality (accessibility), and Outcomes (business conversion).
3. **Step 3: Establish Design Tokens**
   - Lock in Obsidian Dark / Champagne Gold luxury palette, 8pt spacing scale, 44px touch targets.
4. **Step 4: Surface Craft & Anti-Overwhelm**
   - Apply Rule of 6 (steppers for $>6$ inputs), 1 primary CTA, and champagne shimmer skeletons for async calls $>400\text{ms}$.
5. **Step 5: Deterministic Gate Verification (Gate `GW-UIUX-01`)**
   - Run `python skills/UIUXProMax/scripts/layer0_validator.py <src_dir>`.
   - Zero blocking errors required for task completion.

---

## 7. Crystallized Design System Preset: Luxury Maritime Atelier

Crystallized from the Luxury Maritime Atelier Reference Platform (Enterprise Luxury Maritime Reference) for reuse across luxury maritime, yachting, concierge, private aviation, and high-touch UHNWI asset management projects.

### 7.1 Architecture & Token Reference
- **Preset File**: [`templates/base/luxury_maritime_tokens.css`](file:///skills/UIUXProMax/templates/base/luxury_maritime_tokens.css)
- **JSON Descriptor**: [`templates/base/luxury_maritime_preset.json`](file:///skills/UIUXProMax/templates/base/luxury_maritime_preset.json)
- **Style Identifier**: `luxury-maritime-atelier`

### 7.2 Core Aesthetic Tokens
| Token Category | Token Variable | Hex / Value | Description |
|---|---|---|---|
| **Canvas** | `--tsy-canvas-ivory` | `#F4F2ED` | Warm luxury linen canvas; eliminates glare while maintaining warmth |
| **Card Surface** | `--tsy-card-ivory` | `#FFFEFB` | Tactile paper surface for cards and data panels |
| **Navigation Sidebar** | `--tsy-navy-sidebar` | `#17212C` | Deep marine navy permanent anchor |
| **Primary Accent** | `--tsy-gold-primary` | `#8A6D3B` | Sculpted warm bronze gold |
| **Highlight Accent** | `--tsy-gold-light` | `#B9A57F` | Champagne gold highlight for active states and dividers |
| **Critical Alert** | `--tsy-red-overdue` | `#962D22` | Signal crimson for SLA breaches and overdue tickets |
| **In-Service State** | `--tsy-color-success`| `#1B8A5A` | Deep sea emerald for healthy vessels |
| **FLS VIP Shield** | `--shield-bg` / `--shield-text` | `#2A2824` / `#E4C09F` | Cryptographic owner PII masking for non-executive roles |

### 7.3 Triple-Typography Hierarchy
1. **Editorial / Display**: `'Cormorant Garamond', Georgia, serif` — Used for masthead titles, vessel names, and roman numeral nav counters (`01`, `02`, `03`).
2. **Body & Controls**: `'Be Vietnam Pro', -apple-system, sans-serif` — Used for data tables, form controls, and bilingual Vietnamese/English diacritics.
3. **Technical Monospace**: `'JetBrains Mono', monospace` — Used for Hull Identification Numbers (HIN), ticket codes, engine hours, and GPS coordinates.

### 7.4 Dual-UI Operational Paradigm
- **80% Deck 1-Tap Mode (Mobile $\le 768\text{px}$)**: Outdoor high-sunlight contrast, $\ge 48\times 48\text{px}$ touch targets, 1-tap defect logging, offline sync resilience.
- **20% Desktop Governance Mode ($\ge 1024\text{px}$)**: 3-pane split screen, executive command dashboard, multi-boat fleet overview, financial settlement drawers, cryptographic audit logs.

---

## 8. Spatial Layout Composition Engine (`spatial_layout_primitives.css`)

Crystallized from the Luxury Maritime CRM layout system (`@atelier/design-system` v1.3.0) to govern nested layout hierarchies ("layouts within layouts") and deterministic pixel distribution across complex web applications.

### 8.1 Core Principles of Layout Composition
1. **Component Layout Agnosticism**: Reusable components (`.card`, `.btn`, `.chip`, `.table`) must never declare outer root margins. Spacing is strictly owned and distributed by parent layout primitives.
2. **Defensive Anti-Blowout Invariant**: All layout slots and flex/grid children automatically declare `min-inline-size: 0; min-width: 0; box-sizing: border-box;` to prevent preformatted content or long URLs from expanding past allocated tracks.
3. **Discrete 8pt/4pt Rhythm**: Spatial gutters strictly quantized to `--tsy-gutter-page` (32px), `--tsy-gutter-layout` (24px), `--tsy-gutter-panel` (16px), `--tsy-gutter-nested` (8px), and `--tsy-gutter-compact` (4px).
4. **CSS Subgrid Multi-Tier Alignment**: Synchronizes headers, content bodies, and action footers across multi-column decks (`.tsy-subgrid-card-deck` + `.tsy-subgrid-rows`).

### 8.2 Layout Primitive Catalog
| Primitive | Class Name | Function & Sizing Behavior |
|---|---|---|
| **Stack** | `.tsy-stack` | Vertical linear distribution with `data-gap` variants (`compact`, `nested`, `panel`, `layout`, `page`). |
| **Cluster** | `.tsy-cluster` | Horizontal wrapping flow for action bars, tags, and status chips with uniform inline and block gaps. |
| **Split** | `.tsy-split` | Deterministic column ratio locks (`data-ratio="1-1"`, `"2-1"`, `"3-1"`, `"golden"`, `"main-side"`, `"side-main"`). |
| **Grid** | `.tsy-grid` | Fluid auto-fit 2D tracks (`.tsy-grid-auto-fit`, `.tsy-grid-cols-4`, `.tsy-grid-cols-12`). |
| **Subgrid** | `.tsy-subgrid-rows` | Subgrid track inheritance across card decks, guaranteeing row synchronization. |
| **Frame** | `.tsy-frame` | Aspect-ratio containment (`1:1`, `4:3`, `16:9`, `21:9`) with object-fit protection. |
| **Container Slot** | `.tsy-container-slot` | Container Query context root (`container-type: inline-size`) for slot-level responsiveness. |

---

## 9. The Evidence-Based Quality Control (EBQC) Framework

Crystallized from the Luxury Maritime CRM verification harness (`tests/ebqc_verification_suite.py` and `walkthrough.md`) to establish an unyielding, mathematically verifiable quality gate for all interface releases.

### 9.1 The 4 Core Gate Pillars
1. **MECE Boundaries**: Workspace filesystem depth $\le 3$ across canonical zones (`00_INBOX`, `10_ACTIVE_TIMEBOUND`, `20_ACTIVE_CONTINUOUS`, `30_REFERENCE`, `40_ARCHIVE`). Zero desktop pollution.
2. **UTOP Traceability**: 100% bidirectional traceability link graph: $\text{BPMN (L3)} \to \text{Use Case (L5)} \to \text{Slices} \to \text{Tests} \to \text{Code}$.
3. **Specifications Baseline**: Strict Pydantic schema validation, immutable data contracts, and zero mock leakage in production paths.
4. **UC 3.0 Structural Compliance**: Ivar Jacobson Use Case 3.0 standard: every workflow explicitly defines Basic Flow (F1), Alternate Flows (Flow Alt), and Exception Loops (Flow Exc) with zero dead-ends.

### 9.2 The Mathematical Acceptance Gate
Releases require an **Evidence Alignment Index (EAI)** exceeding the gold standard threshold:
$$\text{EAI} = \frac{\sum \text{Checks Passed}}{\sum \text{Checks Total}} \ge 0.980 \quad (\text{Gold Baseline: } 0.995)$$

### 9.3 The 20 Review Agent Personas Matrix (`AGT-01` .. `AGT-20`)
Every critical vertical slice is audited against the 20 distinct review perspectives:
- **`AGT-01`**: Primary Actor & Canonical Role Alignment
- **`AGT-02`**: Level 1 Goal & Active Verb-Phrase Compliance
- **`AGT-03`**: Preconditions & Environmental Trigger State
- **`AGT-04`**: Success Guarantee (Postcondition) Commit
- **`AGT-05`**: Minimum Guarantee & Safety Lock Rollback
- **`AGT-06`**: Basic Flow F1 Sequential Execution
- **`AGT-07`**: Alternate Flow (Flow Alt) Branching
- **`AGT-08`**: Exception Loop (Flow Exc) Rework Handling
- **`AGT-09`**: Vertical Slices Completeness (Presentation $\to$ DB)
- **`AGT-10`**: Field-Level Security (FLS) & VIP Privacy Shield
- **`AGT-11`**: Status-Action & Button Governance
- **`AGT-12`**: Business Rules Engine (R1..R12)
- **`AGT-13`**: Separation of Duties (SoD: Requester $\ne$ Approver)
- **`AGT-14`**: Database Schema & Entity Integrity
- **`AGT-15`**: Playwright End-User Interaction Realism
- **`AGT-16`**: Video Stream EBML & Codec Integrity
- **`AGT-17`**: Non-Trivial Physical Artifact Size Threshold ($>50\text{KB}$)
- **`AGT-18`**: UTOP Upstream Traceability
- **`AGT-19`**: MECE Zone & Zero-Desktop Invariant
- **`AGT-20`**: EBQC Quality Gate & System Certification Auditor

---

## 10. Infographic & Presentation Deck Typography & Pixel Distribution Architecture

Governs executive infographics, technical slide decks, and visual proof reports rendered as standalone HTML or high-resolution vector PDF / 2x Retina PNG artifacts (`RULE-L0-MICRO-INFOGRAPHIC-DENSITY` & `RULE-L0-MESO-PRINT-TYPOGRAPHY`).

### 10.1 Floor Font Size Invariant for A4 / Presentation Decks (`RULE-L0-MICRO-SUBMINIMUM-FONT`)
Tiny micro-fonts ($< 8.0\text{pt}$ or $< 11\text{px}$) create unreadable interfaces and leave dead empty visual voids across high-resolution displays. On presentation decks and infographics:
- **Absolute Floor**: Font sizes $< 8.0\text{pt}$ ($< 10.7\text{px}$) are **strictly prohibited**.
- **Footnotes & Meta Badges**: Minimum **`8.0pt – 8.5pt`** (`10.7px – 11.3px`) with uppercase letter-spacing $\ge 0.05\text{em}$.
- **Body Prose, Table Cells & Feature Lists**: **`9.0pt – 10.5pt`** (`12.0px – 14.0px`) with line-height $\ge 1.40$.
- **Section Headers & Card Titles**: **`11.0pt – 13.0pt`** (`14.7px – 17.3px`) with semi-bold to bold weight (`700`–`800`).
- **Key Metric Numbers (KPI Values)**: **`20.0pt – 32.0pt`** (`26.7px – 42.7px`) with bold weight (`850`–`900`).
- **Deck Masthead Titles**: **`16.0pt – 22.0pt`** (`21.3px – 29.3px`) with tight letter-spacing (`-0.03em`).

### 10.2 Pixel Distribution & Fill Factor Law (`RULE-L0-MICRO-INFOGRAPHIC-DENSITY`)
- **Active Surface Density Floor**: Infographic canvases must maintain an active information surface density $\eta_{\text{fill}} \ge 90\%$. Empty voids, blank margins $> 10\text{mm}$, or trailing dead card bottoms are prohibited.
- **Card Track Height Synchronization**: Multi-column grid cards must stretch to fill $100\%$ of their grid row track (`height: 100%`). Internal elements must be distributed with balanced vertical rhythm using structured components (step timelines, comparison matrices, metric bars, inline sparkbars).
- **Proportional White Space vs Void**: Intentional micro-whitespace (padding, margins $\le 10\text{px}$) provides cognitive breathing room; massive macro-voids ($> 40\text{px}$ empty vertical space) indicate poor information hierarchy and incomplete data-ink utilization (Edward Tufte Law).

### 10.3 Visual Proof & Mobile Screenshot Cropping Law (`RULE-L0-MICRO-FOCAL-CROP`)
- **Anti-Blank Screenshot Invariant**: Web and mobile screenshots often contain large blank headers or empty whitespace. Inserting raw uncropped screenshots into infographic cards wastes pixel real-estate.
- **Focal-Point Framing**: Mobile and web proofs must be cropped or zoomed into the **exact interactive focal point** (e.g., article headline, body paragraphs, interactive button, or transaction receipt), framed inside dark glassmorphism containers with subtle borders (`rgba(255, 255, 255, 0.15)`), eliminating all glaring white voids.

### 10.4 Deterministic Vertical Pixel Budgeting Architecture (`RULE-L0-MESO-VERTICAL-BUDGET`)

#### Why Traditional UI/UX Frameworks Fail on Vertical Space
Modern UI/UX design frameworks (Tailwind, Radix, Figma web presets, and upstream `nextlevelbuilder`) were engineered exclusively for **scrollable web applications** where the Y-axis is infinite (`height: auto`, `overflow-y: auto`). On the scrolling web:
- Vertical space is never "budgeted" because content simply pushes the document height down.
- Design rules focus overwhelmingly on horizontal 12-column grids, flex rows, and responsive breakpoints.

However, **presentation slide decks, technical infographics, executive one-pagers, and printable A4 sheets** are **Rigidly Bounded 2D Canvases** ($W \times H = \text{constant}$). In a bounded frame, vertical space is a **Zero-Sum Equation**:
$$H_{\text{canvas}} = H_{\text{masthead}} + H_{\text{kpi}} + H_{\text{middle\_content}} + H_{\text{footer}} + \sum \text{gutters}$$

If an interface does not strictly budget the vertical axis, CSS flexbox defaults to content-shrink:
1. **The Dead Bottom Chasm**: If content is concise, cards collapse to their natural height, dumping $200\text{px} - 400\text{px}$ of barren dead space at the bottom.
2. **The Space-Between Rupture**: If an engineer naively attempts `justify-content: space-between`, flexbox arbitrarily tears apart semantic groupings, scattering headers, content blocks, and footers across the screen with enormous voids.
3. **The Bottom Overflow/Clipping**: If content is slightly tall and fixed heights are uncoordinated, footers clip off the printable edge.

#### Canonical 3-Strata Vertical Budget Allocations
Every fixed-height canvas (16:9 slides, 297×210mm A4 sheets, 1920×1080 screens) must allocate its vertical height $H_{\text{total}}$ according to the **3-Strata Budget Contract**:

| Strata Tier | Component Role | Height Budget (% of $H$) | Flex / Grid Contract | Mandatory Behaviors |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1: Top Masthead** | Title, Subtitle, Status Badges | **$8\% - 12\%$** | `flex: 0 0 auto;` | Compact line-height (1.1–1.2); badges grouped inline (`cluster`); no trailing margins. |
| **Tier 2: Metric Strip (KPIs)** | High-level summary numbers | **$12\% - 16\%$** | `flex: 0 0 auto;` | 3–4 horizontal metric cards with 24–32pt figures; tightly coupled labels (9pt). |
| **Tier 3: Middle Core Arena** | Primary data grids, cards, tables | **$66\% - 74\%$** | `flex: 1 1 0; min-height: 0;` (or `1fr`) | **Must be an elastic absorber**: fills 100% of remaining vertical slack. Nested cards must declare `height: 100%` with flex columns. |
| **Tier 4: Bottom Provenance** | System hashes, audit seals, date | **$4\% - 6\%$** | `flex: 0 0 auto; margin-top: auto;` | Anchored cleanly to frame bottom; 8.0–8.5pt monospace text; single-line horizontal alignment. |

#### Implementation Patterns

**Pattern A: Flexbox 3-Strata Architecture (Recommended for Dynamic Content)**
```css
.canvas-frame {
  display: flex;
  flex-direction: column;
  height: 100vh; /* or 792px / 210mm */
  padding: 24px;
  box-sizing: border-box;
  overflow: hidden;
}

.frame-masthead { flex: 0 0 auto; margin-bottom: 12px; }
.frame-kpi-strip { flex: 0 0 auto; margin-bottom: 16px; }

/* The Core Middle Arena absorbs ALL remaining vertical space */
.frame-middle-arena {
  flex: 1 1 0;
  min-height: 0; /* Prevents overflow blowout */
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.frame-middle-arena .card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.frame-footer {
  flex: 0 0 auto;
  margin-top: auto;
  padding-top: 8px;
}
```

**Pattern B: CSS Subgrid 4-Row Architecture (Recommended for High Precision Tables)**
```css
.canvas-frame {
  display: grid;
  grid-template-rows: auto auto 1fr auto;
  height: 100vh;
  gap: 12px;
  padding: 24px;
  box-sizing: border-box;
}
```

---

## 11. The Analytical UI/UX Forensic Diagnostic & MCDA Decision Science Engine

Crystallized from the Luxury Maritime CRM reconstruction pipeline (Enterprise Reference Architecture), this capability bridges `DataAnalysisKit`'s diagnostic forensics and Multi-Criteria Decision Analysis with `UIUXProMax`'s 5 Domains of Product Architecture and Layer 0 mechanical laws.

### 11.1 The Problem with Opinion-Based UI/UX
Traditional interface redesigns frequently degrade into subjective aesthetic debates ("I think blue looks cleaner", "let's hide this behind a hamburger menu"). In high-touch enterprise, maritime, or operational environments, subjective redesigns introduce severe operational regressions, working memory overload, and disrupted muscle memory.

The **Analytical UI/UX Forensic Diagnostic Pipeline** transforms interface redesign into a deterministic, evidence-based science.

### 11.2 The 6-Stage Re-Engineering Protocol

```
+---------------------------------------------------------------------------------+
| Stage 1: Forensic UI Control & Pixel Intake (Inventory, Y-axis, Redundancies)   |
+---------------------------------------+-----------------------------------------+
                                        |
                                        v
+---------------------------------------------------------------------------------+
| Stage 2: Ishikawa 6M UI Degeneration Decomposition                              |
| (Measurement · Machine · Method · Material · Milieu · Man)                      |
+---------------------------------------+-----------------------------------------+
                                        |
                                        v
+---------------------------------------------------------------------------------+
| Stage 3: Cognitive & Morphological Law Checks                                   |
| (Miller's 7±2 · Rule of 6 · Hick's Law · Fitts's Law · Layer 0 Invariants)      |
+---------------------------------------+-----------------------------------------+
                                        |
                                        v
+---------------------------------------------------------------------------------+
| Stage 4: Divergent 3-Proposal Architectural Synthesis                           |
| (e.g., Unified Command Strip vs Progressive Drawer vs Faceted Cockpit)          |
+---------------------------------------+-----------------------------------------+
                                        |
                                        v
+---------------------------------------------------------------------------------+
| Stage 5: Multi-Criteria Decision Analysis (Dynamic AHP / MCDA Utility Matrix)   |
| (Weighted Criteria: Screen Economy, Calm, Velocity, Brand, Risk)                |
+---------------------------------------+-----------------------------------------+
                                        |
                                        v
+---------------------------------------------------------------------------------+
| Stage 6: Interactive Prototyping & Code Node Verification (P=1)                 |
| (Generative UI Sandbox · layer0_validator.py · Vitest/Playwright Proof)        |
+---------------------------------------------------------------------------------+
```

### 11.3 CLI Usage
```bash
# 1. Run canonical evaluation demo and display ranking
python skills/UIUXProMax/scripts/uiux_analyzer.py --demo

# 2. Output structured JSON for automation pipelines
python skills/UIUXProMax/scripts/uiux_analyzer.py --demo --json

# 3. Export standardized markdown report and HTML visualizer
python skills/UIUXProMax/scripts/uiux_analyzer.py --demo \
  --out-report ./uiux_proposal.md \
  --out-visualizer ./uiux_visualizer.html
```

### 11.4 Decision Criteria & Weights Taxonomy
When evaluating candidate UI architectures, the MCDA engine applies 5 standardized criteria:
1. **Screen Real Estate & Vertical Economy ($w = 0.25$)**: Reclaiming vertical space to expose core tables and cards.
2. **Cognitive Calm & Anti-Overwhelm ($w = 0.25$)**: Eliminating visual clutter, enforcing Miller's $7\pm 2$ ceiling.
3. **Triage Velocity & 1-Click Access ($w = 0.25$)**: Direct access to primary workflows without multi-click nested menus.
4. **Brand Coherence & Luxury Polish ($w = 0.15$)**: Visual harmony with high-touch luxury tokens and typography.
5. **Implementation & Regression Safety ($w = 0.10$)**: Low refactoring blast radius, zero state regressions.

### 11.5 Standard Templates
- Proposal Document Template: [`templates/base/uiux_reconstruction_proposal_template.md`](file:///skills/UIUXProMax/templates/base/uiux_reconstruction_proposal_template.md)

---

## 12. The 24 Design Vocabulary Verbs & 4 Surface Modes (Impeccable Paradigm)

To eliminate generic AI design slop and under-specified prompt sampling, UI mutations are decomposed into **24 discrete, single-responsibility verbs** across 6 functional categories:

### 12.1 The 24 Design Vocabulary Verbs
| Category | Verbs | Operational Scope |
| :--- | :--- | :--- |
| **CREATE** | `impeccable`, `shape` | `impeccable`: End-to-end craft generation pass from scratch.<br/>`shape`: UX wire-framing, information priority, and mental models *before* CSS. |
| **EVALUATE** | `critique`, `audit` | `critique`: Perceptual review, visual weight, whitespace balance, cognitive calm.<br/>`audit`: Mechanical verification (WCAG 2.1 AA, Fitts's Law, token adherence). |
| **REFINE** | `typeset`, `layout`, `colorize`, `animate`, `delight`, `bolder`, `quieter`, `overdrive` | `typeset`: Modular typography hierarchy, line length (60–75ch), tabular figures.<br/>`layout`: Spatial rhythm, 8pt grid, vertical budgeting, layout primitives.<br/>`colorize`: Semantic palette allocation, contrast harmony, anti-slop rules.<br/>`animate`: Purposeful cubic-bezier transitions, GPU-accelerated motion.<br/>`delight`: Signature tactile micro-interactions and celebratory milestone feedback.<br/>`bolder`: Visual amplification, contrast injection, assertive hierarchy.<br/>`quieter`: Visual noise suppression, cognitive calming, whitespace expansion.<br/>`overdrive`: High-craft technical showcase (WebGL, canvas shaders, morphing SVGs). |
| **SIMPLIFY** | `distill`, `clarify`, `adapt` | `distill`: Ruthless subtraction of redundant card containers and wrapper bloat.<br/>`clarify`: Plain-language microcopy, jargon elimination, transparent helper text.<br/>`adapt`: Poly-device container query metamorphosis (desktop cockpit vs mobile deck). |
| **HARDEN** | `polish`, `optimize`, `harden`, `onboard` | `polish`: Pre-release craftsmanship sweep, subpixel alignment, token reconciliation.<br/>`optimize`: Skeleton loaders (>400ms), list virtualization, bundle footprint trimming.<br/>`harden`: Defensive UI (text truncation, `min-w-0`, empty states, i18n overflow).<br/>`onboard`: First-run experience, time-to-value acceleration, guided discovery. |
| **SYSTEM** | `init`, `extract`, `document`, `live`, `generate` | `init`: Bootstrap root `PRODUCT.md` and `DESIGN.md` contracts.<br/>`extract`: Harvest recurring styles and components into centralized tokens.<br/>`document`: Living design system documentation generated from source code.<br/>`live`: Headless DOM bounding inspection and computed style tuning.<br/>`generate`: Divergent multi-variant synthesis (Variants A, B, C) for comparative review. |

### 12.2 The 4 Surface Modes
Applications must not be treated as monolithic targets. Surface Mode is assigned at the view or component route:
1. **`Persuade`** (Marketing / Pricing / Checkout): Decisive conversion velocity, single dominant primary CTA (Hick's Law), bold emotional typography, social proof.
2. **`Operate`** (Back-Office / Cockpits / CRM): Task velocity, high data density ($\eta_{\text{fill}} \ge 85\%$), tabular alignment, inline sparkbars, muted neutral tones, strict 8pt grid, defensive anti-blowout (`min-w-0`), zero decorative badges.
3. **`Read`** (Documentation / Spec Vaults): Reading comfort, constrained measure (60–75ch), line height $1.5\text{--}1.7$, high contrast, sticky table of contents, anchored search.
4. **`Experience`** (Digital Twins / Luxury Showrooms / Portfolios): Minimal receded UI chrome, full-bleed media canvas, editorial serifs, fluid ambient physics, bespoke tactile tokens.

---

## 13. The 5 Curated Design Worlds & OKLCH Token Architecture

To eliminate statistical monoculture (the median SaaS purple-gradient template), `UIUXProMax` standardizes **5 Curated Design Worlds** utilizing the perceptually uniform **OKLCH** color space ($\text{oklch}(L \quad C \quad H)$):

| World Identifier | Target Domains | Palette Highlights | Typography Pairings | Morphology & Radii |
| :--- | :--- | :--- | :--- | :--- |
| **`luxury-maritime-atelier`** | Yachting, Private Aviation, High-Touch Concierge | Warm Linen Ivory `oklch(95.8% 0.008 85)`, Marine Navy `oklch(22.5% 0.032 245)`, Bronze Gold `oklch(53.2% 0.092 78.5)` | Cormorant Garamond (Editorial) + Be Vietnam Pro (Body) + JetBrains Mono (HIN) | 4px card radii, 1px bronze borders, dual-UI 80% deck touch targets ($\ge 48\text{px}$) |
| **`obsidian-enterprise-density`** | Project Management, Trading Desks, SOC Telemetry | Deep Obsidian `oklch(16% 0.015 250)`, Card Slate `oklch(22% 0.02 250)`, Cyan Glow `oklch(75% 0.16 210)` | Plus Jakarta Sans + JetBrains Mono (Tabular Numerals) | 6px radii, 4pt micro-grid, active surface density $\ge 85\%$, inline sparklines |
| **`swiss-bauhaus-modernist`** | Architecture Portfolios, Legal Auditing, Tech Specs | Pure Chalk `oklch(98% 0 0)`, Carbon Ink `oklch(15% 0 0)`, International Orange `oklch(62% 0.22 35)` | Neue Haas Grotesk / Inter tight tracking (`-0.02em`), high display contrast | 0px orthogonal radii, 1px solid hairline grid lines, zero drop shadows |
| **`warm-editorial-linen`** | Knowledge Repositories, Research Papers, Policy Vaults | Oatmeal Paper `oklch(94% 0.015 75)`, Charcoal Ink `oklch(20% 0.01 60)`, Terracotta `oklch(55% 0.14 42)` | Newsreader / Merriweather + Plus Jakarta Sans | 8px soft card radii, generous 24pt/32pt margins, warm bookish cadence |
| **`industrial-neo-brutalist`** | Developer CLI Tooling, Hardware Diagnostics, B2B Labs | Voltage Yellow `oklch(92% 0.19 105)`, Void Black `oklch(10% 0 0)`, Pure White `oklch(100% 0 0)` | Space Grotesk + Space Mono (Weight 700/800 headings) | 0px/2px radii, heavy 2px/3px solid black borders, hard unblurred drop shadows |

---

## 14. Workspace SSOT Governance: `PRODUCT.md` & `DESIGN.md`

Every governed project repository establishes two root-level Single Source of Truth contracts:

```
+-------------------------------------------------------------------------------+
|                       ROOT-LEVEL DESIGN SYSTEM CONTRACTS                      |
+-------------------------------------------------------------------------------+
| 1. PRODUCT.md (The Product Context SSOT)                                     |
|    • Non-visual operational reality: Product purpose, primary personas,       |
|      field ergonomics, active surface modes, and anti-slop blacklist.         |
| 2. DESIGN.md (The Visual Contract SSOT per Google @google/design.md standard) |
|    • Machine-readable YAML frontmatter with OKLCH token ramps, radii scale,   |
|      typography scale, elevation shadows, and component state contracts.      |
|    • Derived target: tokens.css is automatically compiled from DESIGN.md.     |
+-------------------------------------------------------------------------------+
```

### Deterministic SSOT Linter (`scripts/design_md_linter.py`, $P=1$)
Validates `PRODUCT.md` and `DESIGN.md` against structural schemas, OKLCH regex syntax, and non-duplication invariants without external LLM API calls:
```bash
python skills/UIUXProMax/scripts/design_md_linter.py <workspace_root>
```

---

## MECE Boundary & DRY Delegation Contract (`mece_demarcation_contract`)

- **Scope Demarcation**: Canonical owner of UIUXProMax domain operations within the Antigravity 9-stage enterprise lifecycle.
- **DRY SSOT Invariant**: Zero duplicate business logic; shared persistence and telemetry delegate to `TaskManager` and `QualityGate`.
## 15. Taste-Skill v2.1 Absorption (`design-taste-frontend` & `output-enforcement`)

Vendored in `vendor/taste_skill_v2/` (`https://github.com/Leonxlnx/taste-skill`):
- **Consolidated Sub-Skills**: `taste-skill` (`design-taste-frontend` v2.1), `redesign-skill`, `soft-skill`, `minimalist-skill`, and `output-enforcement` (zero-truncation / anti-lazy-placeholder enforcement).
- **3-Wave AI Tell Detector**:
  - **Wave 1 (Classic Slop)**: Neon/purple-blue gradients, glowing dark-mode cards, default Inter/Roboto typography without hierarchy, generic hero banners (`"The future of..."`).
  - **Wave 2 (Component Slop)**: Identical 3-card Bento grids, unmotivated glassmorphism, floating pill navbars with generic Lucide icon rows, symmetrical SaaS pricing tables.
  - **Wave 3 (Structural & Lazy Output Slop)**: Truncated files (`// ... rest of code`, `/* ... existing code ... */`, `<!-- ... rest of`), unstyled fallback states, and decorative fake metrics.
- **7 App Screen Archetypes**: Analytical Workbench, Command Center, Editorial Narrative, Spatial Canvas, Transactional Checkout, High-Density Data Grid, and Conversational Studio.
- **10 `.mjs` CDP / Lint / Draw Tools (`vendor/taste_skill_v2/scripts/`)**: Deterministic layout inspection, typography hierarchy verification, contrast/spacing auditing, and curated reference matching across `library/*.json` (247+100 curated references) and `references/*.md`.

---

## 16. Deterministic Typography Governance (`v2.1.0` · `SPEC-TYPOGRAPHY-001`)

`scripts/layer0_validator.py` and `scripts/design_md_linter.py` enforce 5 deterministic ($P = 1$) typography invariants across `.css`, `.scss`, `.html`, `.htm`, `.jinja`, `.jinja2`, `.js`, `.jsx`, `.ts`, and `.tsx` production files:

1. **`RULE-L0-MICRO-SUBMINIMUM-FONT` (`ERROR`)**: Enforces a universal web/app legibility floor of `>= 11px` (`0.6875rem` at `16px` root, `8.25pt`) across CSS rules, inline JSX `style={{ fontSize: ... }}`, HTML `style="font-size: ..."`, and Tailwind arbitrary micro-classes (`text-[9px]`, `text-[10px]`), while preserving `< 8.0pt` (`10.67px`) checks for `@page` / `.slide` presentation decks. `font-size: 0` is exempt strictly when paired with `.sr-only` or `layer0-ignore-subminimum`.
2. **`RULE-L0-MICRO-ARBITRARY-TEXT-SIZE` (`ERROR`)**: Prohibits arbitrary Tailwind dimensional font-size utilities (`text-[9px]`, `text-[13px]`, `md:text-[0.8rem]`, `text-[clamp(...)]`, `text-[length:...]`) while never false-positiving on color or wrap tokens (`text-[#8A6D3B]`, `text-[oklch(...)]`, `text-[var(--bronze)]`, `text-[balance]`).
3. **`RULE-L0-MICRO-MONO-OVERUSE` (`ERROR`)**: Prohibits `font-mono` on interactive `<button>` and `<Btn>` elements (unless opted out via `data-mono-allowed` or `layer0-ignore-mono`), reserving monospace strictly for tabular IDs, HINs, code, and timestamps.
4. **`RULE-L0-MICRO-TYPOGRAPHY-SPRAWL` (`ERROR`)**: Caps suite-wide distinct static `px` font-size steps at `<= 8` (7-step modular scale recommended, `>= 11px` floor).
5. **`RULE-L0-MICRO-FONT-FAMILY-SPRAWL` (`ERROR`)**: Enforces the **3-Font Triad Ceiling** (`<= 3` distinct custom non-system font families across Google Fonts URLs, `@font-face`, CSS `font-family`, and Tailwind v4 `@theme` `--font-*:` definitions).

---

## 17. Two-Stage Deterministic Gate (`GW-UIUX-01` · `v2.5.0` · `SPEC-TYPOGRAPHY-002 & SPEC-RESPONSIVE-REGRESSION-004`)

`UIUXProMax` `v2.5.0` upgrades Gate `GW-UIUX-01` from a single static source scan to a mandatory **Two-Stage Deterministic Verification Pipeline** ($P = 1$) across the full 9-viewport responsive + desktop continuum (`360x800`..`1440x900`):

1. **Stage 1 — Static AST / Token / CSS Linter (`scripts/layer0_validator.py` & `scripts/design_md_linter.py`)**:
   - Scans `.css`, `.scss`, `.html`, `.jsx`, `.tsx` source trees and `DESIGN.md` / `PRODUCT.md` contracts for token sprawl, sub-11px micro-fonts, arbitrary `text-[...]` font sizes, monospace button misuse, 3-font triad ceiling, anti-slop layout heuristics, and **`RULE-L0-MICRO-FLEX-WRAP-MINW0-COLLAPSE` (`ERROR`)** (flags elements combining `flex-wrap`, `flex-1`, and `min-w-0` without an explicit width/basis floor).
2. **Stage 2 — Headless Playwright Rendered DOM Geometry & Visual Screenshot Gate (`scripts/rendered_layout_auditor.py`)**:
   - Launches off-screen headless Chromium (`headless=True`, `--window-position=-32000,-32000` per `GW-HEADLESS-01`) across 9 default responsive + desktop viewports (`360x800`, `390x844`, `540x800`, `768x1024`, `1024x768`, `1240x800`, `1280x800`, `1366x768`, `1440x900`; selectable via `--profile {full,responsive,desktop}`) and SPA routes (`--routes #dashboard,#fleet,...`), saving full-viewport PNG proofs (`--screenshot-dir`) and enforcing 10 `ERROR`-severity Senior UI/UX Rendered Geometry Rules:
     - **`RULE-L0-RENDER-UNINTENDED-HSCROLL` (`ERROR`)**: Flags chrome landmarks (`html`, `body`, `aside`, `header`, `nav`, `main`, `[data-testid*="sidebar"]`, `[data-testid="brand-logo"]`) where `scrollWidth > clientWidth + 2`.
     - **`RULE-L0-RENDER-OUT-OF-VIEWPORT` (`ERROR`)**: Flags visible elements (`rect.width > 0 && rect.height > 0`) where `rect.left < -1` or `rect.right > window.innerWidth + 1`, unless contained inside an intentional horizontal scroll wrapper (`overflowX` in `{'auto', 'scroll'}`) whose own bounding box stays within `[-1, window.innerWidth + 1]`.
     - **`RULE-L0-RENDER-CRITICAL-TRUNCATION` (`ERROR`)**: Flags visible critical UX landmarks (`[data-testid="brand-logo"] *`, `aside nav *`, `header .eyebrow`, `h1`, `h2`, `h3`, `.eyebrow`, `[data-testid="stat-card"] *`, `button`) where `computedStyle.textOverflow === 'ellipsis'` and `scrollWidth > clientWidth + 2` (unless opted out via `data-allow-truncate="true"`).
     - **`RULE-L0-RENDER-SERIF-LINING-NUMS` (`ERROR`)**: Flags visible `.font-display` elements containing digits (`/\d/`) when `computedStyle.fontVariantNumeric` lacks `lining-nums` (unless opted out via `data-allow-oldstyle-nums="true"`).
     - **`RULE-L0-RENDER-CHROME-DIVIDER-ALIGNMENT` (`ERROR`)**: Ensures visible split-shell `<aside>` header dividers align within `<= 1.5px` of external top `<header>` bottom borders with `borderBottomWidth >= 0.5px` and alpha `>= 0.14` (unless opted out via `data-allow-header-offset="true"`).
     - **`RULE-L0-RENDER-TOP-RHYTHM-ALIGNMENT` (`ERROR`)**: Ensures the first visible item inside `<aside> <nav>` aligns within `<= 4.0px` of `<main>`'s topmost visible interactive/heading/top-bordered landmark when `<nav>` and `<main>` share the same top horizon (unless opted out via `data-allow-rhythm-offset="true"`).
     - **`RULE-L0-RENDER-SIBLING-STAT-BASELINE` (`ERROR`)**: Ensures sibling `[data-testid="stat-card"]` cards on the same row align their `[data-stat-value], .font-display` numeral baselines within `<= 2.0px`.
     - **`RULE-L0-RENDER-TOOLBAR-ORPHAN-WRAP` (`ERROR`)**: Flags `[data-testid="role-lens-badge"]` and `[data-toolbar-inline="true"]` elements that orphan-wrap below sibling flex controls (`select, input, button`) at desktop widths `>= 1240px`.
     - **`RULE-L0-RENDER-INTERACTIVE-OVERLAP` (`ERROR`)**: Flags 2D bounding-box collisions (`overlapX > 1.5px && overlapY > 1.5px`) between visible non-ancestor/non-descendant interactive controls (`button`, `input`, `select`, `textarea`, `a[href]`, `[role="tab"]`, `[role="button"]`, `[role="combobox"]`, `[role="switch"]`) within the same overlay stratum across `360x800`..`1440x900`.
     - **`RULE-L0-RENDER-FLEX-WRAP-COLLAPSE` (`ERROR`)**: Flags `flex-wrap` items (`overflowX === 'visible'`) whose bounding width collapses narrower than their visible in-flow children (`child.right > item.right + 2px` or `child.left < item.left - 2px`), preventing responsive sibling collisions.

```bash
# Stage 1: Static AST & Token Linter
python skills/UIUXProMax/scripts/layer0_validator.py <src_dir>

# Stage 2: Headless Rendered DOM Geometry & Visual Screenshot Gate (Full 9-Viewport Continuum)
python skills/UIUXProMax/scripts/rendered_layout_auditor.py http://127.0.0.1:4173 --routes "#dashboard,#fleet,#incidents,#admin,#whats-new" --profile full --screenshot-dir ./artifacts/ui_audit --json
```

---

## 18. Brand `DESIGN.md` Catalog, OKLCH Contrast Math & Token Compiler (`v2.5.0`)

Absorbed from `VoltAgent/awesome-design-md`, `nexu-io/open-design`, and `google-labs-code/design.md`:

1. **Curated Brand Design System Domain (`--domain brand` · `data/brands.csv`)**:
   - Indexes exemplar real-world design systems (*Stripe*, *Linear*, *Vercel*, *Anthropic Claude*, *Apple HIG*, *Mercury*, *Supabase*, *Raycast*, *Wise*, *Oura*, *Porsche Digital Atelier*, *Teenage Engineering*) with OKLCH surface/text/accent tokens, triple-font stacks, radius contracts, brand-specific `Don'ts`, and `Agent Prompt Guides`.
   ```bash
   python skills/UIUXProMax/scripts/search.py "fintech payment stripe" --domain brand
   ```
2. **OKLCH Luminance Contrast Math & Deterministic Token Compiler (`scripts/design_md_linter.py`)**:
   - Computes exact **OKLCH $\to$ Oklab $\to$ Linear sRGB WCAG 2.1 AA contrast ratios** ($\ge 4.5:1$ primary text, $\ge 3.0:1$ secondary text) across `DESIGN.md` surface/text pairs.
   - Compiles `DESIGN.md` YAML frontmatter directly into `tokens.css`, `tailwind-v4.css` (`@theme`), and W3C `design-tokens.json` (`od-design-system-project/v1` schema), and supports semantic token diffing (`--diff`):
   ```bash
   python skills/UIUXProMax/scripts/design_md_linter.py <DESIGN.md> --compile-tokens ./dist/tokens --json
   python skills/UIUXProMax/scripts/design_md_linter.py <DESIGN.md> --diff ./BASELINE_DESIGN.md
   ```

---

## 19. Kinetic Physics, GSAP 3.13+ Lifecycle & Scroll-World Scrub Governance (`v2.5.0`)

Absorbed from `emilkowalski/skills`, `greensock/gsap-skills`, and `oso95/scroll-world`:

- **Deterministic `DET P=1` Linter Rules (`scripts/layer0_validator.py`)**:
  - **`RULE-L0-KINETIC-SCALE-FLOOR` (`ERROR`)**: Bans `scale(0)` / `scale-0` on UI entry animations; enforces Emil Kowalski's `scale >= 0.95` floor.
  - **`RULE-L0-KINETIC-NO-EASE-IN-UI` (`WARNING`)**: Flags `ease-in` or `power*.in` on UI transitions; mandates `cubic-bezier(0.16, 1, 0.3, 1)` or iOS sheet curve `cubic-bezier(0.32, 0.72, 0, 1)`.
  - **`RULE-L0-GSAP-REACT-CLEANUP` (`ERROR`)**: Bans raw `gsap.to|from|fromTo|timeline` inside React `useEffect` without `@gsap/react` `useGSAP()` or `gsap.context()` cleanup.
  - **`RULE-L0-GSAP-SCROLLTRIGGER-CONFLICT` (`ERROR`)**: Bans declaring both `scrub` and `toggleActions` on the same `scrollTrigger`.
  - **`RULE-L0-SCROLL-VIDEO-SCRUB-SAFE` (`ERROR`)**: Requires `!video.seeking` frame-latch guards and `prefers-reduced-motion` poster fallbacks when scrubbing `video.currentTime` (paired with `ffmpeg -c:v libx264 -g 8 -keyint_min 8 -crf 20 -an -movflags +faststart`).
  - **`RULE-L0-OVERDRIVE-SURFACE-GATE` (`ERROR`)**: Blocks WebGL/WebGPU shader contexts (`DavidHDev/canvas-ui`) inside `Operate` and `Read` surface modes (`data-surface-mode="experience"` required).
- **24 Canonical Motion Recipes (`data/motion.csv`)**: Includes `Origin-Aware Popover`, `iOS Drawer Sheet Physics`, `Blur-Bridge State Morph`, `React useGSAP + contextSafe`, `ScrollTrigger.batch()`, `GSAP Flip Filterable Bento`, and `Scroll-World GOP-8 Video Scrub`.

---

## 20. Apple CAD Dimensional Spec Generator & Anti-Slop Component Registry (`v2.5.0`)

Absorbed from `enesozturk/dimensional-drawing`, `DavidHDev/react-bits`, `magicuidesign/magicui`, and `DavidHDev/canvas-ui`:

1. **Deterministic CAD Dimensional Spec Sheet Generator (`scripts/dimensional_spec_generator.py`, $P=1$)**:
   - Generates self-contained, single-file monochrome HTML+SVG engineering blueprints featuring **Orthographic Plan View**, **Elevation Profile**, **Interactive CSS 3D Exploded Z-Axis Stack**, and **Algebraic Token Invariants** ($H_{\text{total}} = 2 S_1 + \sum H_i + \sum S_2$, concentric radii $R_2 = R_1 - B - \Delta$, 8pt quantization, Fitts $\ge 44\times 44\text{px}$):
   ```bash
   python skills/UIUXProMax/scripts/dimensional_spec_generator.py --demo --output ./cad_spec.html --json
   ```
2. **Anti-Slop Filtered Component Domain (`--domain component` · `data/components.csv`)**:
   - Provides CSP-safe Vanilla HTML/SVG/JS and React/Tailwind recipes for `AnimatedBeam` (SVG DAG topology connector), `Dimensional CAD Blueprint`, `DecryptedText`, `NumberTicker` (`tabular-nums lining-nums`), `Rule-of-6 Stepper`, `SVG Architectural Grid`, `Origin-Aware Popover`, `HTML-in-Canvas Glass Shader` (`templates/overdrive/html_in_canvas_shaders.html`), and `Scroll-World Scrub Canvas`.
   ```bash
   python skills/UIUXProMax/scripts/search.py "animated beam svg connector" --domain component
   ```

