# UI/UX Design Studio (`uiux-design-studio`)

**Standalone Software UI/UX Design Intelligence, OKLCH Design System Generator & Product Architecture Toolkit**
*(Bộ công cụ Thiết kế Giao diện Phần mềm UI/UX, Tạo Hệ thống Thiết kế OKLCH & Kiến trúc Sản phẩm Độc lập)*

---

## 1. What Is Inside This Repository? (Tổng quan Bộ công cụ)

This repository packages two complete, zero-API-key AI UI/UX design skills and their CLI generators so you and your friends can design high-craft software interfaces across **Claude Code, Cursor, Windsurf, Google Antigravity, and OpenAI Codex**:

| Module | Path | Purpose |
| :--- | :--- | :--- |
| **1. `UIUXProMax` (`v2.6.710`)** | [`skills/UIUXProMax/`](skills/UIUXProMax/SKILL.md) | **BM25 Design System Generator & Craft Engine**: 21 curated datasets (79 UI styles, 192 color palettes, 74 font pairings, 22 framework stacks, brand `DESIGN.md` systems like Stripe/Linear/Vercel/Apple HIG, 24 GSAP motion recipes), 5 Curated OKLCH Design Worlds, 24 Design Verbs, 4 Surface Modes, Apple CAD 3D Spec Sheet Generator, and Taste-Skill v2.1. |
| **2. `ProductArchitectureKit` (`v1.1.19`)** | [`skills/ProductArchitectureKit/`](skills/ProductArchitectureKit/SKILL.md) | **5 Domains & 6-Phase Product/UI Execution Pipeline**: Guides product design from Phase 1 (Strategy) & Phase 2 (Market Forensics) $\to$ Phase 3 (IA Tree, Logic Flows & Wireframes) $\to$ Phase 4 (High-Fi Surface Craft) $\to$ Phase 5 (WCAG 2.1 AA & Dev Handoff Specs). |
| **3. Starter Templates** | [`starter-templates/`](starter-templates/) | Ready-to-use `PRODUCT.md`, `DESIGN.md` (with OKLCH token compiler support), `spatial_layout_primitives.css` (`.tsy-stack`, `.tsy-cluster`, `.tsy-split`, `.tsy-subgrid-rows`), and `html_in_canvas_shaders.html`. |
| **4. Live Reference Examples** | [`examples/`](examples/) | Complete reference UI implementations (`saas-landing`, `healthcare-dashboard`, `portfolio-dark`, `xiaomaomi-app.html`) plus generated Apple CAD dimensional spec sheets and compiled OKLCH CSS tokens. |

---

## 2. Quick Installation for Friends (Cài đặt nhanh trong 1 câu lệnh)

Requires **Python 3.10+** (zero external pip packages required for the core BM25 search, design system generator, OKLCH token compiler, MCDA proposal analyzer, and CAD spec generator).

### List Supported AI IDEs
```bash
python install.py --list
```

### Option A: Install into a Specific Project (Recommended)
Copies both skills into your project and optionally creates starter `PRODUCT.md` and `DESIGN.md` files:
```bash
# For Claude Code (.claude/skills/)
python install.py --ide claude --project /path/to/your-app --init-contracts

# For Cursor (.cursor/skills/)
python install.py --ide cursor --project /path/to/your-app --init-contracts

# For Windsurf (.windsurf/skills/)
python install.py --ide windsurf --project /path/to/your-app --init-contracts

# For Google Antigravity (.agent/skills/)
python install.py --ide antigravity --project /path/to/your-app --init-contracts
```

### Option B: Install Globally for Your AI IDE
```bash
python install.py --ide claude --global
python install.py --ide cursor --global
python install.py --ide antigravity --global
```

---

## 3. Designing Software UI from the Command Line (Các câu lệnh Thiết kế UI)

You can run the design generators directly from this repository without any API keys:

### 3.1 Generate a Complete End-to-End Design System
```bash
python skills/UIUXProMax/scripts/search.py "fintech dark dashboard" --design-system --project-name "my-fintech-app" --variance 3 --motion 4 --density 8
```

### 3.2 Search Specific UI/UX Domains (21 Curated Datasets)
```bash
# Search 79 UI Styles
python skills/UIUXProMax/scripts/search.py "luxury minimal editorial" --domain style

# Search 192 Color Palettes
python skills/UIUXProMax/scripts/search.py "saas analytics dark" --domain color

# Search 74 Typography Pairings
python skills/UIUXProMax/scripts/search.py "modern geometric dashboard" --domain typography

# Search Real-World Brand Design Systems (Stripe, Linear, Vercel, Apple HIG, Raycast, Supabase...)
python skills/UIUXProMax/scripts/search.py "stripe linear fintech" --domain brand

# Search Anti-Slop Interactive Components
python skills/UIUXProMax/scripts/search.py "animated beam stepper" --domain component

# Search Stack-Specific UI Rules (react, nextjs, shadcn, html-tailwind, vue, flutter, swiftui...)
python skills/UIUXProMax/scripts/search.py "data table drawer" --stack nextjs
```

### 3.3 Compile `DESIGN.md` into CSS / Tailwind v4 / W3C Tokens
Edit `starter-templates/DESIGN.md` (or your project's `DESIGN.md`) and compile OKLCH tokens while verifying WCAG 2.1 AA optical contrast ($\ge 4.5:1$):
```bash
python skills/UIUXProMax/scripts/design_md_linter.py starter-templates/DESIGN.md --compile-tokens ./examples/compiled-tokens --json
```
Outputs:
- `examples/compiled-tokens/tokens.css` (CSS Custom Properties)
- `examples/compiled-tokens/tailwind-v4.css` (`@theme` directives)
- `examples/compiled-tokens/design-tokens.json` (W3C standard token format)

### 3.4 Generate an Apple CAD 3D Exploded UI Spec Sheet
Creates a standalone interactive HTML/SVG blueprint showing orthographic plan view, elevation profile, and interactive 3D exploded Z-axis layers:
```bash
python skills/UIUXProMax/scripts/dimensional_spec_generator.py --demo --output ./examples/cad-dimensional-spec.html --json
```

### 3.5 Generate a 3-Option UI Architecture Proposal & Interactive Visualizer
Compares candidate UI layouts (e.g., Command Strip vs. Progressive Drawer vs. Faceted Cockpit) using Multi-Criteria Decision Analysis (MCDA):
```bash
python skills/UIUXProMax/scripts/uiux_analyzer.py --demo --out-report ./examples/uiux-proposal-demo.md --out-visualizer ./examples/uiux-visualizer-demo.html
```

---

## 4. Next Steps

Read **[DESIGN_PLAYBOOK.md](DESIGN_PLAYBOOK.md)** for the step-by-step workflow on how to use the **5 Curated Design Worlds**, **4 Surface Modes**, **24 Design Verbs**, and **Layer 0 Architectural Laws** when prompting your AI coding assistant to design software UI.
