```prompt:ProductArchitecture:sop_phase1_strategic_prioritization
# SOP: Phase 1 Strategic Prioritization (BMC Alignment) — Domain 5: Outcomes
Input: Executive Business Strategy & Business Model Canvas.
Tasks:
1.1 BMC Health Audit: Isolate bleeding block in the 9-box BMC.
1.2 Capability Gap Matrix: Map As-Is vs To-Be software architecture.
1.3 Baseline Telemetry: Extract quantitative baseline drop-off/cost data from DB.
1.4 Prioritization Canvas: Score impact vs effort using WSJF.
1.5 Execution Charter: Calculate daily Cost of Delay for stakeholder sign-off.
🛑 TOLLGATE 1: Signed UX Project Charter or Signed Executive Risk Waiver.
```

```prompt:ProductArchitecture:sop_phase2_market_forensics
# SOP: Phase 2 Market Forensics & Structural Autopsy — Domain 1: Truth
Input: Signed UX Charter & Baseline Data.
Tasks:
2.1 Ecological Mapping: Identify 2 direct competitors, 2 adjacent solutions, 1 graveyard attempt.
2.2 Structural Autopsies: Strip UI visual decoration; map backend logic flowcharts; apply Chesterton's fence to purge competitor tech debt; count clicks/steps.
2.3 Convergence Synthesis: Separate market standards (adopt) vs innovation wedge (diverge).
2.4 Strategic Thesis: Define amputated friction steps and strategic differentiator.
🛑 TOLLGATE 2: Approved Market Thesis Brief.
```

```prompt:ProductArchitecture:sop_phase3_logic_lock
# SOP: Phase 3 Capability Architecture & Logic Lock — Domain 2: Logic
Input: Market Thesis Brief & Layer 0.1/0.2 Laws.
Tasks:
3.1 Information Architecture Map: Embed capability into global IA tree (max depth <= 3).
3.2 System Logic Flow: Routing diagram with <= 3 decision steps, reversibility routes, and state persistence.
3.3 Structural Wireframes: Low-fi layout applying Miller's Law (<=7 items) and Hick's Law (1 primary CTA).
3.4 Logic Lock Negotiation: Tri-Tier Backend dependency alignment (Tier 1 Apex UX, Tier 2 Compromise UX, Tier 3 Fallback UX).
🛑 TOLLGATE 3: Signed Logic Lock Ticket by Lead Backend Engineer.
```

```prompt:ProductArchitecture:sop_phase4_surface_craft
# SOP: Phase 4 Surface Craft & Friction Engineering — Domain 3: Perception
Input: Signed Logic Lock & Layer 0.3 Micro Laws.
Tasks:
4.1 High-Fidelity UI Screens: Apply 8pt grid, semantic color tokens, and Fitts's Law (>=44px hit areas).
4.2 Micro-copy & Interactions: Semantic UI copy (max 60 chars/line) and kinetic response feedback (<=100ms).
4.3 Clickable Prototype: Wire interactive transitions and states.
4.4 Internal Heuristic Validation: Verify prototype beats competitor friction step count and complies with Layer 0.
🛑 TOLLGATE 4: Pass/Fail Friction Report.
```

```prompt:ProductArchitecture:sop_phase5_reality_convergence
# SOP: Phase 5 Reality Constraints & Engineering Convergence — Domain 4: Reality
Input: Validated Prototype & Layer 0.4 Meta Laws.
Tasks:
5.1 Edge Case UI Repository: Design zero-data empty states, timeout screens, and skeleton loaders (>400ms).
5.2 Accessibility Audit: Mechanical verification of WCAG 2.1 AA 4.5:1 contrast, ARIA tags, and keyboard tab-index.
5.3 Dev-Ready Spec Document: Lock grid layouts, responsive breakpoints, and CSS tokens.
5.4 Handoff Ceremony: Final review with frontend engineering.
🛑 TOLLGATE 5: Dev-Accepted Sprint Tickets.
```

```prompt:ProductArchitecture:sop_phase6_bmc_calibration
# SOP: Phase 6 Value Realization & BMC Calibration — Domain 5: Outcomes
Input: Live Production Release & Baseline Telemetry.
Tasks:
6.1 Live QA Sanity Check: Release-day verification of visual and logic integrity.
6.2 Performance Telemetry: Extract 30-day post-launch quantitative metrics.
6.3 BMC Impact Assessment: Compute mathematical delta proving closure of capability gap and BMC stabilization.
6.4 Executive ROI Post-Mortem: Attribute financial returns to design and engineering decisions.
🛑 TOLLGATE 6: Formally Closed Project (return to WBS 1.1).
```
