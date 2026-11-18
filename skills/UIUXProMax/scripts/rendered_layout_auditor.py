#!/usr/bin/env python3
"""
UIUXProMax Stage 2 Headless Playwright Rendered DOM Geometry & Visual Auditor (P=1)
===================================================================================
Spec Authority: SPEC-TYPOGRAPHY-002 (DoD-12), SPEC-RESPONSIVE-REGRESSION-004 | Skill Version: 2.5.0 | Gate: GW-UIUX-01, GW-HEADLESS-01

Executes an off-screen headless Chromium pass across viewports and routes to catch
rendered geometry defects that static AST/CSS linters cannot observe:
  1. RULE-L0-RENDER-UNINTENDED-HSCROLL (ERROR):
     Flags chrome landmarks (html, body, aside, header, nav, main,
     [data-testid*="sidebar"], [data-testid="brand-logo"]) where
     scrollWidth > clientWidth + 2.
  2. RULE-L0-RENDER-OUT-OF-VIEWPORT (ERROR):
     Flags visible elements (rect.width > 0 && rect.height > 0) where
     rect.left < -1 or rect.right > window.innerWidth + 1, unless inside an
     intentional horizontal scroll container (overflowX in {'auto', 'scroll'})
     whose own rect is within [-1, window.innerWidth + 1].
  3. RULE-L0-RENDER-CRITICAL-TRUNCATION (ERROR):
     Flags visible critical UX landmarks ([data-testid="brand-logo"] *,
     aside nav *, header .eyebrow, h1, h2, h3, .eyebrow,
     [data-testid="stat-card"] *, button) where computed textOverflow === 'ellipsis'
     AND scrollWidth > clientWidth + 2 (unless opted out via data-allow-truncate="true").
  4. RULE-L0-RENDER-SERIF-LINING-NUMS (ERROR):
     Flags visible .font-display elements containing digits (/\\d/) if
     computedStyle.fontVariantNumeric does not include 'lining-nums'
     (unless opted out via data-allow-oldstyle-nums="true").
  5. RULE-L0-RENDER-CHROME-DIVIDER-ALIGNMENT (ERROR):
     Verifies sidebar brand header bottom divider aligns with external top header border.
  6. RULE-L0-RENDER-TOP-RHYTHM-ALIGNMENT (ERROR):
     Verifies first sidebar nav item aligns horizontally with first main landmark/border.
  7. RULE-L0-RENDER-SIBLING-STAT-BASELINE (ERROR):
     Verifies sibling [data-testid="stat-card"] value baselines on the same row align within 2px.
  8. RULE-L0-RENDER-TOOLBAR-ORPHAN-WRAP (ERROR):
     Verifies [data-testid="role-lens-badge"] / [data-toolbar-inline="true"] stays inline at >= 1240px.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib.parse import urljoin


RESPONSIVE_VIEWPORTS: Tuple[Tuple[int, int], ...] = (
    (360, 800),
    (390, 844),
    (540, 800),
    (768, 1024),
    (1024, 768),
)

DESKTOP_VIEWPORTS: Tuple[Tuple[int, int], ...] = (
    (1240, 800),
    (1280, 800),
    (1366, 768),
    (1440, 900),
)

DEFAULT_VIEWPORTS: Tuple[Tuple[int, int], ...] = (
    RESPONSIVE_VIEWPORTS + DESKTOP_VIEWPORTS
)

VIEWPORT_PROFILES: Dict[str, Tuple[Tuple[int, int], ...]] = {
    "full": DEFAULT_VIEWPORTS,
    "responsive": RESPONSIVE_VIEWPORTS,
    "desktop": DESKTOP_VIEWPORTS,
}

HEADLESS_CHROMIUM_ARGS: List[str] = [
    "--window-position=-32000,-32000",
    "--disable-gpu",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--hide-scrollbars",
]


@dataclass
class RenderedViolation:
    rule_id: str
    severity: str
    viewport: str
    route: str
    selector: str
    message: str
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RenderedAuditReport:
    target_url: str
    routes_audited: List[str]
    viewports_audited: List[str]
    passed: bool
    error_count: int
    warning_count: int
    screenshots: List[str] = field(default_factory=list)
    violations: List[RenderedViolation] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_url": self.target_url,
            "routes_audited": self.routes_audited,
            "viewports_audited": self.viewports_audited,
            "passed": self.passed,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "screenshots": self.screenshots,
            "violations": [asdict(v) for v in self.violations],
        }


_DOM_GEOMETRY_AUDIT_JS = r"""
() => {
  const violations = [];
  const vw = window.innerWidth;
  const vh = window.innerHeight;

  const describeElement = (el) => {
    if (!el || !el.tagName) return 'unknown';
    const tag = el.tagName.toLowerCase();
    const testId = el.getAttribute && el.getAttribute('data-testid');
    if (testId) return `${tag}[data-testid="${testId}"]`;
    if (el.id) return `${tag}#${el.id}`;
    const cls = (typeof el.className === 'string' ? el.className.trim() : '');
    if (cls) {
      const tokens = cls.split(/\s+/).slice(0, 3).join('.');
      if (tokens) return `${tag}.${tokens}`;
    }
    return tag;
  };

  const isOffCanvasOrHidden = (el) => {
    let cur = el;
    while (cur && cur.nodeType === 1) {
      const style = window.getComputedStyle(cur);
      if (
        style.display === 'none' ||
        style.visibility === 'hidden' ||
        parseFloat(style.opacity || '1') === 0
      ) {
        return true;
      }
      if (cur.getAttribute('aria-hidden') === 'true') {
        return true;
      }
      if (cur.getAttribute('data-offcanvas') === 'true') {
        return true;
      }
      const cls = typeof cur.className === 'string' ? cur.className : '';
      if (
        cls.includes('-translate-x-full') ||
        cls.includes('translate-x-full') ||
        cls.split(/\s+/).includes('sr-only')
      ) {
        return true;
      }
      cur = cur.parentElement;
    }
    if (el !== document.documentElement && el !== document.body) {
      const rect = el.getBoundingClientRect();
      if (rect.width <= 0 || rect.height <= 0) return true;
      if (rect.right <= 0) return true;
    }
    return false;
  };

  const isChromeLandmark = (el) => {
    if (!el || !el.tagName) return false;
    const tag = el.tagName.toLowerCase();
    if (['html', 'body', 'aside', 'header', 'nav', 'main'].includes(tag)) {
      return true;
    }
    const testId = el.getAttribute('data-testid') || '';
    if (testId.includes('sidebar') || testId === 'brand-logo') {
      return true;
    }
    return false;
  };

  const hasContainedIntentionalHScrollAncestor = (el, elRect) => {
    let anc = el.parentElement;
    while (anc && anc !== document.body && anc !== document.documentElement) {
      const style = window.getComputedStyle(anc);
      const ox = style.overflowX;
      const explicitAllow = anc.getAttribute('data-allow-hscroll') === 'true';
      if ((ox === 'auto' || ox === 'scroll') && (!isChromeLandmark(anc) || explicitAllow)) {
        const ancRect = anc.getBoundingClientRect();
        if (
          ancRect.left >= -1 &&
          ancRect.right <= vw + 1 &&
          elRect.left >= ancRect.left - 1
        ) {
          return true;
        }
      }
      anc = anc.parentElement;
    }
    return false;
  };

  // 1. RULE-L0-RENDER-UNINTENDED-HSCROLL
  const hscrollSelector = [
    'html',
    'body',
    'aside',
    'header',
    'nav',
    'main',
    '[data-testid*="sidebar"]',
    '[data-testid="brand-logo"]',
  ].join(', ');

  const seenHscroll = new Set();
  for (const el of document.querySelectorAll(hscrollSelector)) {
    if (seenHscroll.has(el)) continue;
    seenHscroll.add(el);
    if (el.getAttribute('data-allow-hscroll') === 'true') continue;
    if (isOffCanvasOrHidden(el)) continue;
    const cw = el.clientWidth;
    const sw = el.scrollWidth;
    if (cw > 0 && sw > cw + 2) {
      violations.push({
        rule_id: 'RULE-L0-RENDER-UNINTENDED-HSCROLL',
        severity: 'ERROR',
        selector: describeElement(el),
        message: `Unintended horizontal overflow on chrome landmark (${describeElement(el)}): scrollWidth=${sw}px > clientWidth=${cw}px.`,
        metrics: { scrollWidth: sw, clientWidth: cw, viewportWidth: vw, viewportHeight: vh },
      });
    }
  }

  // 2. RULE-L0-RENDER-OUT-OF-VIEWPORT
  const flaggedOutAncestors = new Set();
  for (const el of document.querySelectorAll('body *')) {
    if (el.closest('[data-allow-bleed="true"]')) continue;
    if (isOffCanvasOrHidden(el)) continue;
    const rect = el.getBoundingClientRect();
    if (rect.width <= 0 || rect.height <= 0) continue;

    const outLeft = rect.left < -1;
    const outRight = rect.right > vw + 1;
    if (!outLeft && !outRight) continue;

    if (hasContainedIntentionalHScrollAncestor(el, rect)) continue;

    const hasIdentity = Boolean(
      (el.getAttribute && el.getAttribute('data-testid')) || el.id
    );
    let ancestorAlreadyFlagged = false;
    let p = el.parentElement;
    while (p) {
      if (flaggedOutAncestors.has(p)) {
        ancestorAlreadyFlagged = true;
        break;
      }
      p = p.parentElement;
    }
    if (ancestorAlreadyFlagged && !hasIdentity) {
      continue;
    }
    flaggedOutAncestors.add(el);

    violations.push({
      rule_id: 'RULE-L0-RENDER-OUT-OF-VIEWPORT',
      severity: 'ERROR',
      selector: describeElement(el),
      message: `Element ${describeElement(el)} bleeds outside viewport [0, ${vw}]: left=${rect.left.toFixed(1)}px, right=${rect.right.toFixed(1)}px.`,
      metrics: {
        left: Math.round(rect.left * 100) / 100,
        right: Math.round(rect.right * 100) / 100,
        width: Math.round(rect.width * 100) / 100,
        viewportWidth: vw,
      },
    });
  }

  // 3. RULE-L0-RENDER-CRITICAL-TRUNCATION
  const criticalTruncSelector = [
    '[data-testid="brand-logo"]',
    '[data-testid="brand-logo"] *',
    'aside nav *',
    'header .eyebrow',
    'h1',
    'h2',
    'h3',
    '.eyebrow',
    '[data-testid="stat-card"]',
    '[data-testid="stat-card"] *',
    'button',
  ].join(', ');

  const seenTrunc = new Set();
  for (const el of document.querySelectorAll(criticalTruncSelector)) {
    if (seenTrunc.has(el)) continue;
    seenTrunc.add(el);
    if (el.closest('[data-allow-truncate="true"]')) continue;
    if (isOffCanvasOrHidden(el)) continue;

    const style = window.getComputedStyle(el);
    const cw = el.clientWidth;
    const sw = el.scrollWidth;
    if (style.textOverflow === 'ellipsis' && cw > 0 && sw > cw + 2) {
      const sampleText = (el.innerText || el.textContent || '').trim().slice(0, 60);
      violations.push({
        rule_id: 'RULE-L0-RENDER-CRITICAL-TRUNCATION',
        severity: 'ERROR',
        selector: describeElement(el),
        message: `Critical UX landmark truncated with ellipsis (${describeElement(el)}, text="${sampleText}"): scrollWidth=${sw}px > clientWidth=${cw}px.`,
        metrics: {
          scrollWidth: sw,
          clientWidth: cw,
          textOverflow: style.textOverflow,
          sampleText,
        },
      });
    }
  }

  // 4. RULE-L0-RENDER-SERIF-LINING-NUMS
  for (const el of document.querySelectorAll('.font-display')) {
    if (el.closest('[data-allow-oldstyle-nums="true"]')) continue;
    if (isOffCanvasOrHidden(el)) continue;
    const txt = (el.innerText || el.textContent || '').trim();
    if (!/\d/.test(txt)) continue;

    const style = window.getComputedStyle(el);
    const fvn = String(style.fontVariantNumeric || '');
    if (!fvn.includes('lining-nums')) {
      violations.push({
        rule_id: 'RULE-L0-RENDER-SERIF-LINING-NUMS',
        severity: 'ERROR',
        selector: describeElement(el),
        message: `Display serif element (${describeElement(el)}, text="${txt.slice(0, 40)}") contains digits without lining-nums (computed fontVariantNumeric="${fvn}").`,
        metrics: {
          fontVariantNumeric: fvn,
          sampleText: txt.slice(0, 40),
        },
      });
    }
  }

  const parseCssColorAlpha = (rawColor) => {
    const c = String(rawColor || '').trim().toLowerCase();
    if (!c || c === 'transparent') return 0.0;
    const rgbaMatch = c.match(/^rgba\(\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*([0-9.]+)\s*\)$/);
    if (rgbaMatch) return parseFloat(rgbaMatch[1]);
    const slashMatch = c.match(/\/\s*([0-9.]+)(%?)\s*\)$/);
    if (slashMatch) {
      const val = parseFloat(slashMatch[1]);
      return slashMatch[2] === '%' ? val / 100.0 : val;
    }
    return 1.0;
  };

  // 5. RULE-L0-RENDER-CHROME-DIVIDER-ALIGNMENT
  for (const aside of Array.from(document.querySelectorAll('aside'))) {
    if (isOffCanvasOrHidden(aside)) continue;
    if (aside.closest('[data-allow-header-offset="true"]')) continue;
    const asideRect = aside.getBoundingClientRect();
    if (asideRect.width < 60 || asideRect.left > 4) continue;

    const navInAside = aside.querySelector('nav');
    if (!navInAside) continue;

    let asideHeader = null;
    for (const ch of Array.from(aside.children)) {
      if (ch === navInAside || ch.contains(navInAside)) break;
      if (isOffCanvasOrHidden(ch)) continue;
      if (ch.getBoundingClientRect().top <= 4) {
        asideHeader = ch;
        break;
      }
    }
    if (!asideHeader && navInAside.parentElement && navInAside.parentElement !== aside) {
      for (const ch of Array.from(navInAside.parentElement.children)) {
        if (ch === navInAside || ch.contains(navInAside)) break;
        if (isOffCanvasOrHidden(ch)) continue;
        if (ch.getBoundingClientRect().top <= 4) {
          asideHeader = ch;
          break;
        }
      }
    }
    if (!asideHeader || asideHeader.closest('[data-allow-header-offset="true"]')) continue;

    const extHeader = Array.from(document.querySelectorAll('header')).find((hdr) => {
      if (aside.contains(hdr) || hdr.closest('aside')) return false;
      if (hdr.closest('[data-allow-header-offset="true"]')) return false;
      if (isOffCanvasOrHidden(hdr)) return false;
      const r = hdr.getBoundingClientRect();
      if (r.top > 4) return false;
      const bw = parseFloat(window.getComputedStyle(hdr).borderBottomWidth || '0') || 0;
      return bw > 0;
    });
    if (!extHeader) continue;

    const asideHeaderRect = asideHeader.getBoundingClientRect();
    const headerRect = extHeader.getBoundingClientRect();
    const ahStyle = window.getComputedStyle(asideHeader);
    const ahBorderW = parseFloat(ahStyle.borderBottomWidth || '0') || 0;
    const ahAlpha = parseCssColorAlpha(ahStyle.borderBottomColor);
    const bottomDelta = Math.abs(asideHeaderRect.bottom - headerRect.bottom);

    if (ahBorderW < 0.5 || bottomDelta > 1.5 || ahAlpha < 0.14) {
      violations.push({
        rule_id: 'RULE-L0-RENDER-CHROME-DIVIDER-ALIGNMENT',
        severity: 'ERROR',
        selector: describeElement(asideHeader),
        message: `Sidebar header divider (${describeElement(asideHeader)}, bottom=${asideHeaderRect.bottom.toFixed(1)}px, borderBottomWidth=${ahBorderW}px, alpha=${ahAlpha.toFixed(2)}) misaligned or too faint against external header (${describeElement(extHeader)}, bottom=${headerRect.bottom.toFixed(1)}px).`,
        metrics: {
          asideHeaderBottom: Math.round(asideHeaderRect.bottom * 100) / 100,
          headerBottom: Math.round(headerRect.bottom * 100) / 100,
          bottomDelta: Math.round(bottomDelta * 100) / 100,
          asideBorderBottomWidth: ahBorderW,
          asideBorderAlpha: Math.round(ahAlpha * 1000) / 1000,
        },
      });
    }
  }

  // 6. RULE-L0-RENDER-TOP-RHYTHM-ALIGNMENT
  const mainEl = Array.from(document.querySelectorAll('main')).find(
    (m) => !isOffCanvasOrHidden(m)
  );
  if (mainEl && mainEl.scrollTop === 0 && !mainEl.closest('[data-allow-rhythm-offset="true"]')) {
    const mainRect = mainEl.getBoundingClientRect();
    for (const aside of Array.from(document.querySelectorAll('aside'))) {
      if (isOffCanvasOrHidden(aside)) continue;
      if (aside.closest('[data-allow-rhythm-offset="true"]')) continue;
      const asideRect = aside.getBoundingClientRect();
      if (asideRect.width < 180) continue;

      const asideNav = Array.from(aside.querySelectorAll('nav')).find(
        (n) => !isOffCanvasOrHidden(n) && !n.closest('[data-allow-rhythm-offset="true"]')
      );
      if (!asideNav) continue;

      const asideNavRect = asideNav.getBoundingClientRect();
      if (Math.abs(asideNavRect.top - mainRect.top) > 6.0) continue;

      const firstNav = Array.from(asideNav.children).find((c) => !isOffCanvasOrHidden(c));
      if (!firstNav) continue;

      let mainFirstTop = Infinity;
      for (const cand of Array.from(mainEl.querySelectorAll('*'))) {
        if (isOffCanvasOrHidden(cand)) continue;
        if (cand.closest('[data-allow-rhythm-offset="true"]')) continue;
        const cs = window.getComputedStyle(cand);
        const hasTopBorder = (parseFloat(cs.borderTopWidth || '0') || 0) > 0;
        const matchesLandmark = cand.matches('button, a, select, input, label, h1, h2, h3, .eyebrow');
        if (!matchesLandmark && !hasTopBorder) continue;
        const r = cand.getBoundingClientRect();
        if (r.top < mainFirstTop) {
          mainFirstTop = r.top;
        }
      }

      if (Number.isFinite(mainFirstTop)) {
        const firstNavTop = firstNav.getBoundingClientRect().top;
        const rhythmDelta = Math.abs(firstNavTop - mainFirstTop);
        if (rhythmDelta > 4.0) {
          violations.push({
            rule_id: 'RULE-L0-RENDER-TOP-RHYTHM-ALIGNMENT',
            severity: 'ERROR',
            selector: describeElement(mainEl),
            message: `Top rhythm mismatch between sidebar nav first item (${describeElement(firstNav)}, top=${firstNavTop.toFixed(1)}px) and main first content (${mainFirstTop.toFixed(1)}px): delta=${rhythmDelta.toFixed(1)}px > 4.0px.`,
            metrics: {
              firstNavTop: Math.round(firstNavTop * 100) / 100,
              mainFirstTop: Math.round(mainFirstTop * 100) / 100,
              deltaPx: Math.round(rhythmDelta * 100) / 100,
            },
          });
        }
      }
    }
  }

  // 7. RULE-L0-RENDER-SIBLING-STAT-BASELINE
  const statCards = Array.from(document.querySelectorAll('[data-testid="stat-card"]')).filter(
    (c) => !isOffCanvasOrHidden(c)
  );
  const statRows = [];
  for (const card of statCards) {
    const r = card.getBoundingClientRect();
    let rowGroup = statRows.find((row) => Math.abs(r.top - row.rowTop) <= 4.0);
    if (!rowGroup) {
      rowGroup = { rowTop: r.top, cards: [] };
      statRows.push(rowGroup);
    }
    rowGroup.cards.push(card);
  }
  for (const row of statRows) {
    if (row.cards.length < 2) continue;
    const tops = [];
    for (const card of row.cards) {
      const valNode = Array.from(
        card.querySelectorAll('[data-stat-value], .font-display')
      ).find((el) => !isOffCanvasOrHidden(el));
      if (valNode) {
        tops.push(valNode.getBoundingClientRect().top);
      }
    }
    if (tops.length >= 2) {
      const spread = Math.max(...tops) - Math.min(...tops);
      if (spread > 2.0) {
        violations.push({
          rule_id: 'RULE-L0-RENDER-SIBLING-STAT-BASELINE',
          severity: 'ERROR',
          selector: describeElement(row.cards[0]),
          message: `Sibling stat-card value baselines misaligned across row (${tops.length} cards): top spread=${spread.toFixed(1)}px > 2.0px.`,
          metrics: {
            spreadPx: Math.round(spread * 100) / 100,
            tops: tops.map((t) => Math.round(t * 100) / 100),
            cardCount: row.cards.length,
          },
        });
      }
    }
  }

  // 8. RULE-L0-RENDER-TOOLBAR-ORPHAN-WRAP
  if (vw >= 1240) {
    const seenBadges = new Set();
    for (const badge of Array.from(
      document.querySelectorAll('[data-testid="role-lens-badge"], [data-toolbar-inline="true"]')
    )) {
      if (seenBadges.has(badge)) continue;
      seenBadges.add(badge);
      if (isOffCanvasOrHidden(badge)) continue;

      let anc = badge.parentElement;
      let ctrl = null;
      while (anc && anc !== document.body && anc !== document.documentElement) {
        const disp = String(window.getComputedStyle(anc).display || '');
        if (disp.includes('flex')) {
          const foundCtrl = Array.from(anc.querySelectorAll('select, input, button')).find(
            (c) => c !== badge && !badge.contains(c) && !isOffCanvasOrHidden(c)
          );
          if (foundCtrl) {
            ctrl = foundCtrl;
            break;
          }
        }
        anc = anc.parentElement;
      }

      if (ctrl) {
        const badgeRect = badge.getBoundingClientRect();
        const ctrlRect = ctrl.getBoundingClientRect();
        const wrapGap = badgeRect.top - ctrlRect.bottom;
        if (wrapGap > -2.0) {
          violations.push({
            rule_id: 'RULE-L0-RENDER-TOOLBAR-ORPHAN-WRAP',
            severity: 'ERROR',
            selector: describeElement(badge),
            message: `Inline toolbar badge (${describeElement(badge)}, top=${badgeRect.top.toFixed(1)}px) wrapped onto orphan row below control (${describeElement(ctrl)}, bottom=${ctrlRect.bottom.toFixed(1)}px) at viewport width ${vw}px >= 1240px.`,
            metrics: {
              badgeTop: Math.round(badgeRect.top * 100) / 100,
              ctrlBottom: Math.round(ctrlRect.bottom * 100) / 100,
              wrapGap: Math.round(wrapGap * 100) / 100,
              viewportWidth: vw,
            },
          });
        }
      }
    }
  }

  // 9. RULE-L0-RENDER-INTERACTIVE-OVERLAP
  const getVisibleRect = (el) => {
    const r = el.getBoundingClientRect();
    let left = r.left, top = r.top, right = r.right, bottom = r.bottom;
    let anc = el.parentElement;
    while (anc && anc !== document.body && anc !== document.documentElement) {
      const cs = window.getComputedStyle(anc);
      const clipX = ['hidden', 'clip', 'auto', 'scroll'].includes(cs.overflowX);
      const clipY = ['hidden', 'clip', 'auto', 'scroll'].includes(cs.overflowY);
      if (clipX || clipY) {
        const ar = anc.getBoundingClientRect();
        if (clipX) { left = Math.max(left, ar.left); right = Math.min(right, ar.right); }
        if (clipY) { top = Math.max(top, ar.top); bottom = Math.min(bottom, ar.bottom); }
      }
      anc = anc.parentElement;
    }
    return { left, top, right, bottom, width: right - left, height: bottom - top };
  };

  const getOverlayStratum = (el) => {
    const ov = el.closest('[role="dialog"], [aria-modal="true"], [data-radix-popper-content-wrapper], [data-overlay="true"]');
    if (ov) return ov;
    let cur = el;
    while (cur && cur !== document.body && cur !== document.documentElement) {
      const pos = window.getComputedStyle(cur).position;
      if (pos === 'fixed' || pos === 'sticky') return cur;
      cur = cur.parentElement;
    }
    return document.body;
  };

  const interactiveSel = 'button, input, select, textarea, a[href], [role="tab"], [role="button"], [role="combobox"], [role="switch"]';
  const interactiveEntries = [];
  const seenInteractive = new Set();
  for (const el of document.querySelectorAll(interactiveSel)) {
    if (seenInteractive.has(el)) continue;
    seenInteractive.add(el);
    if (isOffCanvasOrHidden(el) || el.closest('[data-allow-overlap="true"]')) continue;
    if (el.tagName.toLowerCase() === 'input' && (el.getAttribute('type') || '').toLowerCase() === 'hidden') continue;
    if (window.getComputedStyle(el).pointerEvents === 'none') continue;
    const rawR = el.getBoundingClientRect();
    if (rawR.width < 2 || rawR.height < 2) continue;
    const visR = getVisibleRect(el);
    if (visR.width <= 1 || visR.height <= 1) continue;
    interactiveEntries.push({ el, rect: visR, stratum: getOverlayStratum(el) });
  }

  for (let i = 0; i < interactiveEntries.length; i += 1) {
    const a = interactiveEntries[i];
    for (let j = i + 1; j < interactiveEntries.length; j += 1) {
      const b = interactiveEntries[j];
      if (a.stratum !== b.stratum) continue;
      if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
      const overlapX = Math.min(a.rect.right, b.rect.right) - Math.max(a.rect.left, b.rect.left);
      const overlapY = Math.min(a.rect.bottom, b.rect.bottom) - Math.max(a.rect.top, b.rect.top);
      if (overlapX > 1.5 && overlapY > 1.5) {
        const selA = describeElement(a.el), selB = describeElement(b.el);
        violations.push({
          rule_id: 'RULE-L0-RENDER-INTERACTIVE-OVERLAP',
          severity: 'ERROR',
          selector: `${selA} <> ${selB}`,
          message: `Interactive controls collide (${selA} overlaps ${selB} by ${overlapX.toFixed(1)}px x ${overlapY.toFixed(1)}px at ${vw}px).`,
          metrics: {
            overlapX: Math.round(overlapX * 100) / 100,
            overlapY: Math.round(overlapY * 100) / 100,
            overlapArea: Math.round(overlapX * overlapY * 100) / 100,
            viewportWidth: vw,
          },
        });
      }
    }
  }

  // 10. RULE-L0-RENDER-FLEX-WRAP-COLLAPSE
  for (const container of document.querySelectorAll('body *')) {
    if (isOffCanvasOrHidden(container)) continue;
    const cStyle = window.getComputedStyle(container);
    if (!String(cStyle.display || '').includes('flex') || !String(cStyle.flexWrap || '').startsWith('wrap')) continue;
    const visibleItems = Array.from(container.children).filter((c) => {
      if (isOffCanvasOrHidden(c)) return false;
      const pos = window.getComputedStyle(c).position;
      return pos !== 'absolute' && pos !== 'fixed';
    });
    if (visibleItems.length < 2) continue;
    for (const item of visibleItems) {
      if (item.closest('[data-allow-flex-collapse="true"]')) continue;
      if (window.getComputedStyle(item).overflowX !== 'visible') continue;
      const itemRect = item.getBoundingClientRect();
      for (const ch of Array.from(item.children)) {
        if (isOffCanvasOrHidden(ch)) continue;
        const chPos = window.getComputedStyle(ch).position;
        if (chPos === 'absolute' || chPos === 'fixed') continue;
        const chRect = ch.getBoundingClientRect();
        if (chRect.right > itemRect.right + 2.0 || chRect.left < itemRect.left - 2.0) {
          violations.push({
            rule_id: 'RULE-L0-RENDER-FLEX-WRAP-COLLAPSE',
            severity: 'ERROR',
            selector: describeElement(item),
            message: `Flex-wrap item (${describeElement(item)}, w=${itemRect.width.toFixed(1)}px) collapsed narrower than child (${describeElement(ch)}, w=${chRect.width.toFixed(1)}px) at ${vw}px.`,
            metrics: {
              itemWidth: Math.round(itemRect.width * 100) / 100,
              childWidth: Math.round(chRect.width * 100) / 100,
              itemRight: Math.round(itemRect.right * 100) / 100,
              childRight: Math.round(chRect.right * 100) / 100,
              viewportWidth: vw,
            },
          });
          break;
        }
      }
    }
  }


  const isVisible = (el) => !isOffCanvasOrHidden(el);
  const getSelector = describeElement;

  // 11. Single-Line Tablist Invariant (RULE-L0-RENDER-TABLIST-MULTILINE-WRAP)
  // A horizontal [role="tablist"] must NOT wrap its [role="tab"] buttons onto multiple lines on desktop.
  if (vw >= 1024) {
    const tablists = Array.from(document.querySelectorAll('[role="tablist"]')).filter(isVisible);
    for (const tl of tablists) {
      if (tl.hasAttribute('data-allow-multiline-tabs') || tl.getAttribute('aria-orientation') === 'vertical') continue;
      const tabs = Array.from(tl.querySelectorAll('[role="tab"], button')).filter(isVisible);
      if (tabs.length >= 2) {
        const tops = tabs.map(t => Math.round(t.getBoundingClientRect().top));
        const minTop = Math.min(...tops);
        const maxTop = Math.max(...tops);
        if (maxTop - minTop > 12) {
          violations.push({
            rule_id: 'RULE-L0-RENDER-TABLIST-MULTILINE-WRAP',
            severity: 'ERROR',
            selector: getSelector(tl),
            message: `Horizontal tablist (${getSelector(tl)}) wraps onto multiple lines (topSpread=${maxTop - minTop}px across ${tabs.length} tabs). Use single-line nowrap or progressive disclosure.`,
            metrics: { topSpread: maxTop - minTop, tabCount: tabs.length }
          });
        }
      }
    }
  }

  // 12. Meso Cognitive Overload & Simultaneous Multi-Dock Stacking (RULE-L0-MESO-COGNITIVE-OVERLOAD)
  // Prevents >2 visible <aside> sidebars simultaneously open OR a single <aside> stacking both Transcript and Ask AI panels.
  if (vw >= 1024) {
    const visibleAsides = Array.from(document.querySelectorAll('aside')).filter(el => {
      if (!isVisible(el) || isOffCanvasOrHidden(el)) return false;
      const r = el.getBoundingClientRect();
      return r.width >= 180 && r.height >= 200;
    });
    if (visibleAsides.length > 2) {
      violations.push({
        rule_id: 'RULE-L0-MESO-COGNITIVE-OVERLOAD',
        severity: 'ERROR',
        selector: visibleAsides.map(getSelector).join(', '),
        message: `Cognitive Overload: ${visibleAsides.length} simultaneous <aside> columns visible at once (max 2 allowed: App Shell Sidebar + 1 Contextual Drawer). Move secondary sidebars into collapsible drawers/popovers.`,
        metrics: { visibleAsideCount: visibleAsides.length }
      });
    }
    for (const aside of visibleAsides) {
      const subPanels = Array.from(aside.querySelectorAll('[data-testid="kara-transcript-panel"], [data-testid="kara-ask-panel"], [data-cognitive-panel]')).filter(
        p => isVisible(p) && !isOffCanvasOrHidden(p)
      );
      if (subPanels.length > 1) {
        violations.push({
          rule_id: 'RULE-L0-MESO-COGNITIVE-OVERLOAD',
          severity: 'ERROR',
          selector: getSelector(aside),
          message: `Cognitive Overload inside ${getSelector(aside)}: ${subPanels.length} heavy panels (${subPanels.map(getSelector).join(' + ')}) are stacked simultaneously. Use a single-active-tab toggle.`,
          metrics: { stackedPanels: subPanels.length }
        });
      }
    }
  }

  // 13. Macro JTBD Navigation Friction Depth (RULE-L0-MACRO-JTBD-FRICTION-DEPTH)
  // Prevents stacking >2 horizontal navigation/tab-switching strata above the primary canvas.
  if (vw >= 1024) {
    const navStrata = Array.from(document.querySelectorAll('[role="tablist"], [data-testid="notes-subview-bar"], nav[aria-label*="sub"]')).filter(
      el => isVisible(el) && !isOffCanvasOrHidden(el) && el.getBoundingClientRect().width >= 300
    );
    if (navStrata.length > 2) {
      violations.push({
        rule_id: 'RULE-L0-MACRO-JTBD-FRICTION-DEPTH',
        severity: 'ERROR',
        selector: navStrata.map(getSelector).join(' -> '),
        message: `JTBD Friction Violation: ${navStrata.length} stacked horizontal navigation/tab bars visible simultaneously (max 2 allowed for <=3-step JTBD completion). Consolidate redundant sub-headers.`,
        metrics: { strataCount: navStrata.length }
      });
    }
  }

  return violations;
}
"""


def parse_viewports(raw: Optional[str], profile: str = "full") -> List[Tuple[int, int]]:
    if profile not in VIEWPORT_PROFILES:
        raise ValueError(f"Unknown profile '{profile}'.")
    fallback = list(VIEWPORT_PROFILES[profile])
    if not raw or not raw.strip():
        return fallback
    parsed: List[Tuple[int, int]] = []
    for token in raw.split(","):
        token = token.strip().lower()
        if not token:
            continue
        match = re.match(r"^(\d{3,5})x(\d{3,5})$", token)
        if not match:
            raise ValueError(
                f"Invalid viewport '{token}'. Expected WIDTHxHEIGHT (e.g. 1280x800)."
            )
        parsed.append((int(match.group(1)), int(match.group(2))))
    if not parsed:
        return fallback
    return parsed


def parse_routes(raw: Optional[str]) -> List[str]:
    if not raw or not raw.strip():
        return [""]
    routes = [r.strip() for r in raw.split(",") if r.strip()]
    return routes if routes else [""]


def _sanitize_slug(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", text.strip("#/"))
    return cleaned.strip("_") or "default"


def _build_route_url(base_url: str, route: str) -> str:
    if not route:
        return base_url
    if route.startswith("#"):
        root = base_url.split("#", 1)[0]
        return f"{root}{route}"
    if route.startswith(("http://", "https://", "file://", "data:")):
        return route
    return urljoin(base_url, route)


class RenderedLayoutAuditor:
    """Headless Playwright Stage 2 Rendered DOM Geometry & Visual Auditor."""

    def __init__(
        self,
        wait_ms: int = 250,
        timeout_ms: int = 15000,
        enable_stageshow_checks: bool = False,
    ) -> None:
        self.wait_ms = max(0, int(wait_ms))
        self.timeout_ms = max(1000, int(timeout_ms))
        self.enable_stageshow_checks = bool(enable_stageshow_checks)

    def audit_html(
        self,
        html_content: str,
        viewports: Sequence[Tuple[int, int]] = DEFAULT_VIEWPORTS,
        screenshot_dir: Optional[Path] = None,
    ) -> RenderedAuditReport:
        encoded = base64.b64encode(html_content.encode("utf-8")).decode("ascii")
        data_url = f"data:text/html;charset=utf-8;base64,{encoded}"
        return self.audit_url(
            url=data_url,
            routes=[""],
            viewports=viewports,
            screenshot_dir=screenshot_dir,
        )

    def audit_url(
        self,
        url: str,
        routes: Sequence[str] = (""),
        viewports: Sequence[Tuple[int, int]] = DEFAULT_VIEWPORTS,
        screenshot_dir: Optional[Path] = None,
    ) -> RenderedAuditReport:
        from playwright.sync_api import sync_playwright

        route_list = list(routes) if routes else [""]
        viewport_list = list(viewports) if viewports else list(DEFAULT_VIEWPORTS)
        if screenshot_dir is not None:
            screenshot_dir = Path(screenshot_dir)
            screenshot_dir.mkdir(parents=True, exist_ok=True)

        all_violations: List[RenderedViolation] = []
        screenshots: List[str] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=HEADLESS_CHROMIUM_ARGS,
            )
            try:
                for width, height in viewport_list:
                    vp_label = f"{width}x{height}"
                    context = browser.new_context(
                        viewport={"width": width, "height": height},
                        device_scale_factor=1,
                    )
                    page = context.new_page()
                    page.set_default_timeout(self.timeout_ms)
                    loaded_base: Optional[str] = None

                    try:
                        for route in route_list:
                            route_label = route if route else "default"
                            target_url = _build_route_url(url, route)
                            base_without_hash = target_url.split("#", 1)[0]

                            if (
                                route.startswith("#")
                                and loaded_base == base_without_hash
                            ):
                                page.evaluate(
                                    "(h) => { window.location.hash = h; }", route
                                )
                            else:
                                page.goto(target_url, wait_until="load")
                                loaded_base = base_without_hash
                                if route.startswith("#"):
                                    page.evaluate(
                                        "(h) => { if (window.location.hash !== h) window.location.hash = h; }",
                                        route,
                                    )

                            try:
                                page.evaluate(
                                    "() => document.fonts ? document.fonts.ready.then(() => true) : true"
                                )
                                # Auto-scroll hydration pass (from nextlevelbuilder design-audit.mjs)
                                # Triggers IntersectionObserver & ScrollTrigger reveals, then restores (0, 0).
                                page.evaluate(
                                    """() => {
                                      const step = Math.max(200, window.innerHeight || 600);
                                      const maxScroll = Math.min((document.body && document.body.scrollHeight) || 0, step * 8);
                                      for (let y = step; y <= maxScroll; y += step) {
                                        window.scrollTo(0, y);
                                      }
                                      window.scrollTo(0, 0);
                                      return true;
                                    }"""
                                )
                            except Exception:
                                pass

                            if self.wait_ms > 0:
                                page.wait_for_timeout(self.wait_ms)

                            raw_items: List[Dict[str, Any]] = page.evaluate(
                                _DOM_GEOMETRY_AUDIT_JS
                            )
                            if self.enable_stageshow_checks:
                                from stageshow_dom_checks import STAGESHOW_DOM_AUDIT_JS

                                ss_items: List[Dict[str, Any]] = page.evaluate(
                                    STAGESHOW_DOM_AUDIT_JS
                                )
                                raw_items = list(raw_items) + list(ss_items)
                            for item in raw_items:
                                all_violations.append(
                                    RenderedViolation(
                                        rule_id=str(item["rule_id"]),
                                        severity=str(item.get("severity", "ERROR")),
                                        viewport=vp_label,
                                        route=route_label,
                                        selector=str(item.get("selector", "unknown")),
                                        message=str(item.get("message", "")),
                                        metrics=dict(item.get("metrics") or {}),
                                    )
                                )

                            if screenshot_dir is not None:
                                shot_name = f"audit_{vp_label}_{_sanitize_slug(route_label)}.png"
                                shot_path = screenshot_dir / shot_name
                                page.screenshot(path=str(shot_path), full_page=False)
                                screenshots.append(str(shot_path))
                    finally:
                        context.close()
            finally:
                browser.close()

        errors = sum(1 for v in all_violations if v.severity == "ERROR")
        warnings = sum(1 for v in all_violations if v.severity == "WARNING")
        return RenderedAuditReport(
            target_url=url
            if not url.startswith("data:")
            else "data:text/html;base64,...",
            routes_audited=[r if r else "default" for r in route_list],
            viewports_audited=[f"{w}x{h}" for w, h in viewport_list],
            passed=(errors == 0),
            error_count=errors,
            warning_count=warnings,
            screenshots=screenshots,
            violations=all_violations,
        )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="UIUXProMax Stage 2 Headless Playwright Rendered DOM Geometry Auditor (P=1)."
    )
    parser.add_argument(
        "url",
        help="Target URL (http://127.0.0.1:4173, file:///..., or data:text/html...).",
    )
    parser.add_argument(
        "--routes",
        default="",
        help="Comma-separated hash or path routes (e.g. #dashboard,#fleet,#warranty).",
    )
    parser.add_argument(
        "--profile",
        choices=("full", "responsive", "desktop"),
        default="full",
        help="Viewport profile when --viewports is empty (default: full).",
    )
    parser.add_argument(
        "--viewports",
        default="",
        help="Comma-separated WIDTHxHEIGHT viewports overriding --profile.",
    )
    parser.add_argument(
        "--screenshot-dir",
        default="",
        help="Optional directory to save full-viewport PNG proofs per (viewport, route).",
    )
    parser.add_argument(
        "--wait-ms",
        type=int,
        default=250,
        help="Post-navigation settle wait in milliseconds (default: 250).",
    )
    parser.add_argument(
        "--stageshow-checks",
        action="store_true",
        help="Enable StageShow 53-detector spatial DOM & framing checks under GW-UIUX-STAGE-FIREWALL-01.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON audit report.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    viewports = parse_viewports(args.viewports, profile=args.profile)
    routes = parse_routes(args.routes)
    shot_dir = Path(args.screenshot_dir) if args.screenshot_dir else None

    auditor = RenderedLayoutAuditor(
        wait_ms=args.wait_ms,
        enable_stageshow_checks=args.stageshow_checks,
    )
    report = auditor.audit_url(
        url=args.url,
        routes=routes,
        viewports=viewports,
        screenshot_dir=shot_dir,
    )

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        status = "PASS" if report.passed else "FAIL"
        print(
            f"[GW-UIUX-01 Stage 2 Rendered Audit: {status}] "
            f"viewports={','.join(report.viewports_audited)} "
            f"routes={','.join(report.routes_audited)} "
            f"errors={report.error_count} warnings={report.warning_count}"
        )
        for v in report.violations:
            print(
                f"  - [{v.severity}] {v.rule_id} @ {v.viewport} ({v.route}) "
                f"{v.selector}: {v.message}"
            )
        if report.screenshots:
            print(f"  Screenshots saved: {len(report.screenshots)}")

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
