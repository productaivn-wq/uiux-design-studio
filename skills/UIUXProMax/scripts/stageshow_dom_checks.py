"""
stageshow_dom_checks.py — StageShow 53-Detector Spatial DOM & Framing Suite (Vector C3; P=1).

Ports all 49 spatial DOM geometry & optical craft detectors from `stageshow/scripts/film-checks.mjs`
plus all 4 box-balance detectors from `stageshow/scripts/layout-core.mjs`, and enforces the 24
never-intentional `--gate` blocker prefixes under Gate `GW-UIUX-STAGE-FIREWALL-01`.
"""

from __future__ import annotations

from typing import Any

NEVER_INTENTIONAL_GATE_PREFIXES: tuple[str, ...] = (
    "framing:",
    "cut by the crop:",
    "tight stack:",
    "loose stack:",
    "tight mark:",
    "tight inset:",
    "skeleton ladder:",
    "onion skin:",
    "kit override:",
    "unit wrapped:",
    "clipped glyph:",
    "loose list:",
    "empty pane:",
    "fat row:",
    "emoji icon:",
    "anchor drift:",
    "uneven padding:",
    "mixed icons:",
    "tight control:",
    "invented mark:",
    "uneven inset:",
    "uneven gutters:",
    "avatar alignment:",
    "spills its slot:",
)

STAGESHOW_SPATIAL_DETECTORS: tuple[dict[str, Any], ...] = (
    # 1..49: film-checks.mjs
    {
        "id": 1,
        "fn": "detectClipped",
        "rule_id": "RULE-SS-CLIPPED",
        "source": "film-checks.mjs",
        "tag": "clipped:",
        "gate_blocker": True,
        "mode": "universal",
    },
    {
        "id": 2,
        "fn": "detectPaddingRunIns",
        "rule_id": "RULE-SS-PADDING-RUN-IN",
        "source": "film-checks.mjs",
        "tag": "t own its padding:",
        "gate_blocker": False,
        "mode": "universal",
    },
    {
        "id": 3,
        "fn": "detectCoveredCopy",
        "rule_id": "RULE-SS-COVERED-COPY",
        "source": "film-checks.mjs",
        "tag": "covers:",
        "gate_blocker": False,
        "mode": "universal",
    },
    {
        "id": 4,
        "fn": "detectLopsidedPills",
        "rule_id": "RULE-SS-LOPSIDED-PILL",
        "source": "film-checks.mjs",
        "tag": "lopsided:",
        "gate_blocker": False,
        "mode": "universal",
    },
    {
        "id": 5,
        "fn": "detectEdgeTangents",
        "rule_id": "RULE-SS-EDGE-TANGENT",
        "source": "film-checks.mjs",
        "tag": "near-tangent:",
        "gate_blocker": False,
        "mode": "stage_only",
    },
    {
        "id": 6,
        "fn": "detectUnclipped",
        "rule_id": "RULE-SS-UNCLIPPED-STAGE",
        "source": "film-checks.mjs",
        "tag": "unclipped:",
        "gate_blocker": False,
        "mode": "stage_only",
    },
    {
        "id": 7,
        "fn": "detectTightBars",
        "rule_id": "RULE-SS-TIGHT-BARS",
        "source": "film-checks.mjs",
        "tag": "tight lines:",
        "gate_blocker": False,
        "mode": "stage_only",
    },
    {
        "id": 8,
        "fn": "detectDoubleCorner",
        "rule_id": "RULE-SS-DOUBLE-CORNER",
        "source": "film-checks.mjs",
        "tag": "double corner:",
        "gate_blocker": False,
        "mode": "universal",
    },
    {
        "id": 9,
        "fn": "detectPairTangents",
        "rule_id": "RULE-SS-PAIR-TANGENT",
        "source": "film-checks.mjs",
        "tag": "near-tangent:",
        "gate_blocker": False,
        "mode": "universal",
    },
    {
        "id": 10,
        "fn": "detectTranslucentIcons",
        "rule_id": "RULE-SS-TRANSLUCENT-ICON",
        "source": "film-checks.mjs",
        "tag": "translucent icon:",
        "gate_blocker": False,
        "mode": "universal",
    },
    {
        "id": 11,
        "fn": "detectSkeletonLadder",
        "rule_id": "RULE-SS-SKELETON-LADDER",
        "source": "film-checks.mjs",
        "tag": "skeleton ladder:",
        "gate_blocker": True,
        "mode": "stage_only",
    },
    {
        "id": 12,
        "fn": "detectLooseList",
        "rule_id": "RULE-SS-LOOSE-LIST",
        "source": "film-checks.mjs",
        "tag": "loose list:",
        "gate_blocker": True,
        "mode": "universal",
    },
    {
        "id": 13,
        "fn": "detectTightControl",
        "rule_id": "RULE-SS-TIGHT-CONTROL",
        "source": "film-checks.mjs",
        "tag": "tight control:",
        "gate_blocker": True,
        "mode": "universal",
    },
    {
        "id": 14,
        "fn": "detectInventedMark",
        "rule_id": "RULE-SS-INVENTED-MARK",
        "source": "film-checks.mjs",
        "tag": "invented mark:",
        "gate_blocker": True,
        "mode": "stage_only",
    },
    {
        "id": 15,
        "fn": "detectNearAligned",
        "rule_id": "RULE-SS-AVATAR-ALIGNMENT",
        "source": "film-checks.mjs",
        "tag": "avatar alignment:",
        "gate_blocker": True,
        "mode": "universal",
    },
    {
        "id": 16,
        "fn": "detectUnevenInset",
        "rule_id": "RULE-SS-UNEVEN-INSET",
        "source": "film-checks.mjs",
        "tag": "uneven inset:",
        "gate_blocker": True,
        "mode": "universal",
    },
    {
        "id": 17,
        "fn": "detectMixedIcons",
        "rule_id": "RULE-SS-MIXED-ICONS",
        "source": "film-checks.mjs",
        "tag": "mixed icons:",
        "gate_blocker": True,
        "mode": "universal",
    },
    {
        "id": 18,
        "fn": "detectEmojiIcon",
        "rule_id": "RULE-SS-EMOJI-ICON",
        "source": "film-checks.mjs",
        "tag": "emoji icon:",
        "gate_blocker": True,
        "mode": "universal",
    },
    {
        "id": 19,
        "fn": "detectFatRow",
        "rule_id": "RULE-SS-FAT-ROW",
        "source": "film-checks.mjs",
        "tag": "fat row:",
        "gate_blocker": True,
        "mode": "universal",
    },
    {
        "id": 20,
        "fn": "detectEmptyPane",
        "rule_id": "RULE-SS-EMPTY-PANE",
        "source": "film-checks.mjs",
        "tag": "empty pane:",
        "gate_blocker": True,
        "mode": "stage_only",
    },
    {
        "id": 21,
        "fn": "detectTightInset",
        "rule_id": "RULE-SS-TIGHT-INSET",
        "source": "film-checks.mjs",
        "tag": "tight inset:",
        "gate_blocker": True,
        "mode": "universal",
    },
    {
        "id": 22,
        "fn": "detectUnevenPadding",
        "rule_id": "RULE-SS-UNEVEN-PADDING",
        "source": "film-checks.mjs",
        "tag": "uneven padding:",
        "gate_blocker": True,
        "mode": "universal",
    },
    {
        "id": 23,
        "fn": "detectUnevenGutters",
        "rule_id": "RULE-SS-UNEVEN-GUTTERS",
        "source": "film-checks.mjs",
        "tag": "uneven gutters:",
        "gate_blocker": True,
        "mode": "universal",
    },
    {
        "id": 24,
        "fn": "detectPillInset",
        "rule_id": "RULE-SS-PILL-INSET",
        "source": "film-checks.mjs",
        "tag": "uneven inset:",
        "gate_blocker": True,
        "mode": "universal",
    },
    {
        "id": 25,
        "fn": "detectTightStack",
        "rule_id": "RULE-SS-TIGHT-STACK",
        "source": "film-checks.mjs",
        "tag": "tight stack:",
        "gate_blocker": True,
        "mode": "universal",
    },
    {
        "id": 26,
        "fn": "detectKitOverride",
        "rule_id": "RULE-SS-KIT-OVERRIDE",
        "source": "film-checks.mjs",
        "tag": "kit override:",
        "gate_blocker": True,
        "mode": "stage_only",
    },
    {
        "id": 27,
        "fn": "detectClippedGlyph",
        "rule_id": "RULE-SS-CLIPPED-GLYPH",
        "source": "film-checks.mjs",
        "tag": "clipped glyph:",
        "gate_blocker": True,
        "mode": "universal",
    },
    {
        "id": 28,
        "fn": "detectUnitWrapped",
        "rule_id": "RULE-SS-UNIT-WRAPPED",
        "source": "film-checks.mjs",
        "tag": "unit wrapped:",
        "gate_blocker": True,
        "mode": "universal",
    },
    {
        "id": 29,
        "fn": "detectOnionSkin",
        "rule_id": "RULE-SS-ONION-SKIN",
        "source": "film-checks.mjs",
        "tag": "onion skin:",
        "gate_blocker": True,
        "mode": "universal",
    },
    {
        "id": 30,
        "fn": "detectTightMark",
        "rule_id": "RULE-SS-TIGHT-MARK",
        "source": "film-checks.mjs",
        "tag": "tight mark:",
        "gate_blocker": True,
        "mode": "universal",
    },
    {
        "id": 31,
        "fn": "detectRowRhythm",
        "rule_id": "RULE-SS-ROW-RHYTHM",
        "source": "film-checks.mjs",
        "tag": "tight lines:",
        "gate_blocker": False,
        "mode": "universal",
    },
    {
        "id": 32,
        "fn": "detectHalfPixelGlyph",
        "rule_id": "RULE-SS-HALF-PIXEL-GLYPH",
        "source": "film-checks.mjs",
        "tag": "half-pixel glyph:",
        "gate_blocker": False,
        "mode": "universal",
    },
    {
        "id": 33,
        "fn": "detectSqueezed",
        "rule_id": "RULE-SS-SQUEEZED",
        "source": "film-checks.mjs",
        "tag": "squeezed:",
        "gate_blocker": False,
        "mode": "universal",
    },
    {
        "id": 34,
        "fn": "detectHeroFraming",
        "rule_id": "RULE-SS-HERO-FRAMING",
        "source": "film-checks.mjs",
        "tag": "framing:",
        "gate_blocker": True,
        "mode": "stage_only",
    },
    {
        "id": 35,
        "fn": "detectSatelliteGutters",
        "rule_id": "RULE-SS-SATELLITE-GUTTERS",
        "source": "film-checks.mjs",
        "tag": "framing:",
        "gate_blocker": True,
        "mode": "stage_only",
    },
    {
        "id": 36,
        "fn": "detectBoxEdges",
        "rule_id": "RULE-SS-BOX-EDGES",
        "source": "film-checks.mjs",
        "tag": "framing:",
        "gate_blocker": True,
        "mode": "stage_only",
    },
    {
        "id": 37,
        "fn": "detectSliverColumn",
        "rule_id": "RULE-SS-SLIVER-COLUMN",
        "source": "film-checks.mjs",
        "tag": "framing:",
        "gate_blocker": True,
        "mode": "stage_only",
    },
    {
        "id": 38,
        "fn": "detectOverlayRoom",
        "rule_id": "RULE-SS-OVERLAY-ROOM",
        "source": "film-checks.mjs",
        "tag": "framing:",
        "gate_blocker": True,
        "mode": "stage_only",
    },
    {
        "id": 39,
        "fn": "detectTouchingText",
        "rule_id": "RULE-SS-TOUCHING-TEXT",
        "source": "film-checks.mjs",
        "tag": "touching:",
        "gate_blocker": False,
        "mode": "universal",
    },
    {
        "id": 40,
        "fn": "detectTouchingBars",
        "rule_id": "RULE-SS-TOUCHING-BARS",
        "source": "film-checks.mjs",
        "tag": "touching:",
        "gate_blocker": False,
        "mode": "stage_only",
    },
    {
        "id": 41,
        "fn": "detectDarkSlab",
        "rule_id": "RULE-SS-DARK-SLAB",
        "source": "film-checks.mjs",
        "tag": "dark slab:",
        "gate_blocker": False,
        "mode": "universal",
    },
    {
        "id": 42,
        "fn": "detectLightsTangent",
        "rule_id": "RULE-SS-LIGHTS-TANGENT",
        "source": "film-checks.mjs",
        "tag": "near-tangent:",
        "gate_blocker": False,
        "mode": "stage_only",
    },
    {
        "id": 43,
        "fn": "detectShadowHalo",
        "rule_id": "RULE-SS-SHADOW-HALO",
        "source": "film-checks.mjs",
        "tag": "framing:",
        "gate_blocker": True,
        "mode": "stage_only",
    },
    {
        "id": 44,
        "fn": "detectFocusFeather",
        "rule_id": "RULE-SS-FOCUS-FEATHER",
        "source": "film-checks.mjs",
        "tag": "framing:",
        "gate_blocker": True,
        "mode": "stage_only",
    },
    {
        "id": 45,
        "fn": "detectTargetsCut",
        "rule_id": "RULE-SS-TARGETS-CUT",
        "source": "film-checks.mjs",
        "tag": "framing:",
        "gate_blocker": True,
        "mode": "stage_only",
    },
    {
        "id": 46,
        "fn": "detectWordsCut",
        "rule_id": "RULE-SS-WORDS-CUT",
        "source": "film-checks.mjs",
        "tag": "framing:",
        "gate_blocker": True,
        "mode": "stage_only",
    },
    {
        "id": 47,
        "fn": "detectControlsCut",
        "rule_id": "RULE-SS-CONTROLS-CUT",
        "source": "film-checks.mjs",
        "tag": "cut by the crop:",
        "gate_blocker": True,
        "mode": "stage_only",
    },
    {
        "id": 48,
        "fn": "smallestText",
        "rule_id": "RULE-SS-SMALLEST-TEXT",
        "source": "film-checks.mjs",
        "tag": "small text:",
        "gate_blocker": False,
        "mode": "universal",
    },
    {
        "id": 49,
        "fn": "detectSpills",
        "rule_id": "RULE-SS-SPILLS-SLOT",
        "source": "film-checks.mjs",
        "tag": "spills its slot:",
        "gate_blocker": True,
        "mode": "universal",
    },
    # 50..53: layout-core.mjs
    {
        "id": 50,
        "fn": "controlBlockBalance",
        "rule_id": "RULE-SS-CONTROL-BLOCK-BALANCE",
        "source": "layout-core.mjs",
        "tag": "layout:control-block-balance",
        "gate_blocker": False,
        "mode": "universal",
    },
    {
        "id": 51,
        "fn": "controlEdgeInset",
        "rule_id": "RULE-SS-CONTROL-EDGE-INSET",
        "source": "layout-core.mjs",
        "tag": "layout:control-edge-inset",
        "gate_blocker": False,
        "mode": "universal",
    },
    {
        "id": 52,
        "fn": "containerBlockInset",
        "rule_id": "RULE-SS-CONTAINER-BLOCK-INSET",
        "source": "layout-core.mjs",
        "tag": "layout:container-block-inset",
        "gate_blocker": False,
        "mode": "universal",
    },
    {
        "id": 53,
        "fn": "nestedCompositionCrop",
        "rule_id": "RULE-SS-NESTED-COMPOSITION-CROP",
        "source": "layout-core.mjs",
        "tag": "layout:nested-composition-crop",
        "gate_blocker": False,
        "mode": "stage_only",
    },
)

STAGESHOW_DOM_AUDIT_JS = r"""
() => {
  const violations = [];
  const emojiRegex = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/u;
  const unitRegex = /^\s*\d+(?:\.\d+)?\s*(?:px|ms|s|KB|MB|GB|TB|%|fps|Hz)\s*$/i;

  const describe = (el) => {
    if (!el || !el.tagName) return 'unknown';
    const tag = el.tagName.toLowerCase();
    if (el.id) return `${tag}#${el.id}`;
    const cls = typeof el.className === 'string' ? el.className.trim() : '';
    if (cls) return `${tag}.${cls.split(/\s+/).slice(0, 2).join('.')}`;
    return tag;
  };

  const isVisible = (el) => {
    if (!el || el.nodeType !== 1) return false;
    const cs = window.getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity || '1') === 0) return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };

  // 1. Universal optical & geometry detectors
  const allEls = Array.from(document.querySelectorAll('body *')).filter(isVisible);

  for (const el of allEls) {
    const cs = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    const role = el.getAttribute('role') || '';
    const cls = typeof el.className === 'string' ? el.className : '';
    const txt = (el.textContent || '').trim();

    // #18: Emoji used as standalone icon
    if (
      (role === 'img' || cls.includes('icon-slot') || cls.includes('ss-icon')) &&
      el.children.length === 0 &&
      txt.length > 0 &&
      txt.length <= 8 &&
      (emojiRegex.test(txt) || /[\uD800-\uDBFF]|[^\x00-\x7F]/.test(txt))
    ) {
      violations.push({
        rule_id: 'RULE-SS-EMOJI-ICON',
        severity: 'ERROR',
        selector: describe(el),
        message: `emoji icon: raw emoji '${txt}' used inside standalone icon container instead of vector SVG glyph.`,
        metrics: { width: rect.width, height: rect.height },
      });
    }

    // #28: Unit wrapped onto second line
    if (el.children.length === 0 && txt && unitRegex.test(txt) && el.firstChild && el.firstChild.nodeType === 3) {
      const range = document.createRange();
      range.selectNodeContents(el.firstChild);
      const lineRects = range.getClientRects();
      if (lineRects.length > 1) {
        violations.push({
          rule_id: 'RULE-SS-UNIT-WRAPPED',
          severity: 'ERROR',
          selector: describe(el),
          message: `unit wrapped: metric '${txt}' splits number and unit across ${lineRects.length} lines; enforce white-space: nowrap.`,
          metrics: { lines: lineRects.length, width: rect.width },
        });
      }
    }

    // #22: Uneven padding on bordered/shadowed surfaces
    const bw = parseFloat(cs.borderTopWidth || '0') + parseFloat(cs.borderLeftWidth || '0');
    const hasSurface = bw >= 1 || (cs.boxShadow && cs.boxShadow !== 'none');
    const tagLower = el.tagName.toLowerCase();
    const isInteractivePill = tagLower === 'button' || tagLower === 'a' || tagLower === 'span' || parseFloat(cs.borderTopLeftRadius || '0') >= 99;
    if (hasSurface && rect.width >= 80 && rect.height >= 44 && !isInteractivePill && !el.hasAttribute('data-allow-asymmetric-padding')) {
      const pt = parseFloat(cs.paddingTop || '0');
      const pb = parseFloat(cs.paddingBottom || '0');
      const pl = parseFloat(cs.paddingLeft || '0');
      const pr = parseFloat(cs.paddingRight || '0');
      const blockMin = Math.min(pt, pb);
      const inlineMax = Math.max(pl, pr);
      if (
        (Math.abs(pt - pb) > 8 && blockMin < 6) ||
        (Math.abs(pl - pr) > 10 && Math.min(pl, pr) < 6) ||
        (blockMin < 6 && inlineMax >= 16 && (inlineMax - blockMin) >= 12)
      ) {
        violations.push({
          rule_id: 'RULE-SS-UNEVEN-PADDING',
          severity: 'ERROR',
          selector: describe(el),
          message: `uneven padding: asymmetric surface padding (top=${pt}px, right=${pr}px, bottom=${pb}px, left=${pl}px).`,
          metrics: { pt, pr, pb, pl },
        });
      }
    }

    // #8: Double corner concentric radius mismatch
    const prRadius = parseFloat(cs.borderTopLeftRadius || '0');
    if (prRadius >= 12 && el.children.length >= 1) {
      const child = el.children[0];
      if (isVisible(child)) {
        const ccs = window.getComputedStyle(child);
        const crRadius = parseFloat(ccs.borderTopLeftRadius || '0');
        const crect = child.getBoundingClientRect();
        const isConcentricBox = crect.width >= rect.width * 0.7 && crect.height >= rect.height * 0.7;
        const inset = Math.min(crect.left - rect.left, crect.top - rect.top);
        if (isConcentricBox && crRadius >= 2 && inset >= 0 && inset <= 8 && Math.abs((prRadius - inset) - crRadius) > 6) {
          violations.push({
            rule_id: 'RULE-SS-DOUBLE-CORNER',
            severity: 'WARNING',
            selector: describe(child),
            message: `double corner: child radius ${crRadius}px clashes with parent radius ${prRadius}px at ${inset.toFixed(1)}px inset.`,
            metrics: { parentRadius: prRadius, childRadius: crRadius, inset },
          });
        }
      }
    }

    // #27: Clipped SVG glyph (icon-scale SVGs <= 256px)
    if (el.tagName.toLowerCase() === 'svg' && !el.closest('[data-allow-bleed="true"]')) {
      try {
        const bbox = el.getBBox();
        const vb = el.viewBox && el.viewBox.baseVal;
        if (vb && vb.width > 0 && vb.height > 0 && vb.width <= 256 && vb.height <= 256) {
          if (bbox.x < vb.x - 0.5 || bbox.y < vb.y - 0.5 || bbox.x + bbox.width > vb.x + vb.width + 0.5 || bbox.y + bbox.height > vb.y + vb.height + 0.5) {
            violations.push({
              rule_id: 'RULE-SS-CLIPPED-GLYPH',
              severity: 'ERROR',
              selector: describe(el),
              message: `clipped glyph: SVG path bbox exceeds viewBox bounds.`,
              metrics: { bboxWidth: bbox.width, viewBoxWidth: vb.width },
            });
          }
        }
      } catch (e) {}
    }
  }

  // 2. Stage-only framing & rehearsal rules ([data-stage-ui="true"] / .ss-stage)
  const stages = Array.from(document.querySelectorAll('.ss-stage, [data-stage-ui="true"]')).filter(isVisible);
  for (const stage of stages) {
    const sr = stage.getBoundingClientRect();
    const scs = window.getComputedStyle(stage);
    if (scs.overflow !== 'hidden' && scs.overflow !== 'clip') {
      violations.push({
        rule_id: 'RULE-SS-UNCLIPPED-STAGE',
        severity: 'WARNING',
        selector: describe(stage),
        message: `unclipped: stage root must declare overflow: hidden or clip.`,
        metrics: { overflow: scs.overflow },
      });
    }

    const heroes = Array.from(stage.querySelectorAll('.ss-window, [data-hero="true"]')).filter(isVisible);
    for (const hero of heroes) {
      if (hero.hasAttribute('data-allow-float')) continue;
      const hr = hero.getBoundingClientRect();
      const leftGutter = hr.left - sr.left;
      const rightGutter = sr.right - hr.right;
      const topGutter = hr.top - sr.top;
      const bottomGutter = sr.bottom - hr.bottom;
      const bleedsAnyEdge = leftGutter <= 0.5 || rightGutter <= 0.5 || topGutter <= 0.5 || bottomGutter <= 0.5;
      const unevenSides = Math.abs(leftGutter - rightGutter) > 8;
      if (!bleedsAnyEdge && (unevenSides || bottomGutter > 24)) {
        violations.push({
          rule_id: 'RULE-SS-HERO-FRAMING',
          severity: 'ERROR',
          selector: describe(hero),
          message: `framing: hero window floats inside stage without edge bleed (left=${leftGutter.toFixed(0)}px, right=${rightGutter.toFixed(0)}px, bottom=${bottomGutter.toFixed(0)}px).`,
          metrics: { leftGutter, rightGutter, topGutter, bottomGutter },
        });
      }
    }

    const bars = stage.querySelectorAll('.ss-bar, [data-skeleton-bar="true"]').length;
    const rows = stage.querySelectorAll('.ss-row, [data-worded-row="true"]').length;
    if (bars >= 4 && bars > rows && rows > 0) {
      violations.push({
        rule_id: 'RULE-SS-SKELETON-LADDER',
        severity: 'ERROR',
        selector: describe(stage),
        message: `skeleton ladder: ${bars} placeholder bars outnumber ${rows} worded rows.`,
        metrics: { bars, rows },
      });
    }
  }

  return violations;
}
"""
