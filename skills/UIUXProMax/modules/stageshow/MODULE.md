---
name: stageshow
description: Governed StageShow Showcase, Choreography, Rehearsal & Framing Submodule under UIUXProMax (GW-UIUX-STAGE-FIREWALL-01).
version: 1.0.0
status: Active
risk_class: TIER_1
upstream: https://github.com/benjitaylor/skills (MIT, v0.1.0)
capabilities:
- stageshow-kit-primitives
- stageshow-17-framing-recipes
- stageshow-14-bento-rules
- stageshow-virtual-clock-rehearsal
- stageshow-slidewright-embed
---

# StageShow Module (`UIUXProMax/modules/stageshow`)

Canonical home of the MIT-clean StageShow engine (`vendor/stageshow/`), governed by **`GW-UIUX-STAGE-FIREWALL-01`**:
- **Production App UI (`Operate` / `Read`)**: May use the 12 production-safe motion primitives (`Collapse`, `Connector`, `Count`, `Expand`, `Fly`, `Follow`, `Popover`, `Roll`, `Scroll`, `States`, `Stream`, `Swap`), atomic controls/parts (`Facepile`, `Meter`, `Chart`, `Code`), `6` `EASE` curves, and `text-box: trim-both cap alphabetic`.
- **Stage Showcase Mode (`[data-stage-ui="true"]` / `.ss-stage`)**: Unlocks faux OS shells (`Window`, `Phone`, `Keyboard`), simulated DOM `<Cursor>`, wireframe `<Bar>` string-budget placeholders, and `10-40%` intentional off-stage hero bleed (`[data-crop]`), while strictly forbidding `<h1>`-`<h6>` heading leaks.
- **LegalOps Firewall**: `assets/app-icons.ts` (non-MIT macOS bundle PNGs) and all `16` third-party commercial product UI clones are hard-excluded (`0` bytes); generic choreography mechanics live in `extracted_choreography_patterns.json`.
