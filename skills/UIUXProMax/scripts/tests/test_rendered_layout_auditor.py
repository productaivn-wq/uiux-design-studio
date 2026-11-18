"""
Regression test suite for UIUXProMax Stage 2 Headless Playwright Rendered Geometry Auditor
(SPEC-TYPOGRAPHY-002 & SPEC-RESPONSIVE-REGRESSION-004 / v2.4.0).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANDIDATE_DIRS = [HERE, HERE.parent]
for candidate in CANDIDATE_DIRS:
    if (candidate / "rendered_layout_auditor.py").exists():
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
        AUDITOR_SCRIPT = candidate / "rendered_layout_auditor.py"
        break
else:
    raise RuntimeError("Could not locate rendered_layout_auditor.py")

from rendered_layout_auditor import (  # noqa: E402
    DEFAULT_VIEWPORTS,
    DESKTOP_VIEWPORTS,
    RESPONSIVE_VIEWPORTS,
    VIEWPORT_PROFILES,
    RenderedLayoutAuditor,
    parse_viewports,
)


ADVERSARIAL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: system-ui, sans-serif;
    background: #F9F8F6;
    color: #111921;
  }
  .app-shell {
    display: grid;
    grid-template-columns: 240px 1fr;
    min-height: 100vh;
  }
  aside {
    width: 240px;
    background: #111921;
    color: #FFFFFF;
    padding: 16px;
    overflow-y: auto;
  }
  /* Defect 1 & 2: BrandLogo wider than 240px sidebar and centered so left < 0 */
  .brand-wrap {
    display: flex;
    justify-content: center;
  }
  [data-testid="brand-logo"] {
    min-width: 280px;
    width: 280px;
    height: 44px;
    background: #1D2939;
    white-space: nowrap;
  }
  /* Defect 3: Truncated navigation & header eyebrow */
  aside nav a {
    display: block;
    width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 13px;
  }
  header {
    padding: 16px 24px;
    border-bottom: 1px solid #E2E8F0;
  }
  header .eyebrow {
    width: 90px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 11px;
    text-transform: uppercase;
  }
  /* Defect 4: Display serif KPI numeral without lining-nums */
  .font-display {
    font-family: Georgia, serif;
    font-size: 32px;
    font-variant-numeric: oldstyle-nums;
  }
  /* Defect 5: CSS Grid child without min-w-0 + wide table blowing out viewport */
  main {
    padding: 24px;
  }
  table.blowout {
    width: 1700px;
    border-collapse: collapse;
  }
</style>
</head>
<body>
  <div class="app-shell">
    <aside data-testid="app-sidebar">
      <div class="brand-wrap">
        <div data-testid="brand-logo">LUXURY MARITIME CONCIERGE</div>
      </div>
      <nav>
        <a href="#warranty">Warranty Claims &amp; Marine Survey</a>
      </nav>
    </aside>
    <main>
      <header>
        <div class="eyebrow">EXECUTIVE FLEET TELEMETRY OVERVIEW</div>
        <h1>Service Operations</h1>
      </header>
      <section data-testid="stat-card">
        <div class="font-display">148 Active Claims</div>
      </section>
      <table class="blowout" id="uncontained-table">
        <tr><td>Uncontained wide data grid cell causing horizontal blowout</td></tr>
      </table>
    </main>
  </div>
</body>
</html>
"""


CLEAN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: system-ui, sans-serif;
    background: #F9F8F6;
    color: #111921;
  }
  .app-shell {
    display: grid;
    grid-template-columns: 240px minmax(0, 1fr);
    min-height: 100vh;
  }
  aside {
    width: 240px;
    background: #111921;
    color: #FFFFFF;
    padding: 16px;
    overflow-x: hidden;
    overflow-y: auto;
  }
  [data-testid="brand-logo"] {
    max-width: 100%;
    width: 100%;
    padding: 8px 0;
    font-size: 15px;
    font-weight: 600;
  }
  aside nav a {
    display: block;
    padding: 6px 0;
    font-size: 13px;
    line-height: 1.35;
    white-space: normal;
    overflow-wrap: break-word;
    color: #F8FAFC;
  }
  main {
    min-width: 0;
    padding: 24px;
  }
  header {
    padding-bottom: 16px;
    border-bottom: 1px solid #E2E8F0;
  }
  header .eyebrow {
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }
  .font-display {
    font-family: Georgia, serif;
    font-size: 32px;
    font-variant-numeric: lining-nums tabular-nums;
  }
  .table-scroll-container {
    width: 100%;
    max-width: 100%;
    overflow-x: auto;
    border: 1px solid #CBD5E1;
  }
  .table-scroll-container table {
    width: 1600px;
    border-collapse: collapse;
  }
  /* Off-canvas mobile drawer should be ignored cleanly */
  .mobile-drawer-hidden {
    position: fixed;
    top: 0;
    left: 0;
    width: 260px;
    transform: translateX(-100%);
  }
</style>
</head>
<body>
  <aside class="mobile-drawer-hidden -translate-x-full" aria-hidden="true">
    Hidden off-canvas drawer
  </aside>
  <div class="app-shell">
    <aside data-testid="app-sidebar">
      <div data-testid="brand-logo">LUXURY MARITIME</div>
      <nav>
        <a href="#dashboard">Executive Overview</a>
        <a href="#warranty">Warranty Claims &amp; Marine Survey</a>
      </nav>
    </aside>
    <main>
      <header>
        <div class="eyebrow">EXECUTIVE FLEET TELEMETRY</div>
        <h1>Service Operations</h1>
      </header>
      <section data-testid="stat-card">
        <div class="font-display">148 Active Claims</div>
      </section>
      <div class="table-scroll-container">
        <table>
          <tr><td>Intentionally scrollable wide marine parts ledger inside min-w-0 main</td></tr>
        </table>
      </div>
    </main>
  </div>
</body>
</html>
"""


def test_adversarial_fixture_triggers_all_four_rendered_rules(tmp_path: Path) -> None:
    fixture_file = tmp_path / "adversarial.html"
    fixture_file.write_text(ADVERSARIAL_HTML, encoding="utf-8")
    shot_dir = tmp_path / "shots_bad"

    auditor = RenderedLayoutAuditor(wait_ms=50)
    report = auditor.audit_url(
        url=fixture_file.as_uri(),
        routes=["#warranty"],
        viewports=[(1280, 800)],
        screenshot_dir=shot_dir,
    )

    assert not report.passed
    assert report.error_count >= 4
    rule_ids = {v.rule_id for v in report.violations}
    assert "RULE-L0-RENDER-UNINTENDED-HSCROLL" in rule_ids
    assert "RULE-L0-RENDER-OUT-OF-VIEWPORT" in rule_ids
    assert "RULE-L0-RENDER-CRITICAL-TRUNCATION" in rule_ids
    assert "RULE-L0-RENDER-SERIF-LINING-NUMS" in rule_ids

    out_selectors = [
        v.selector
        for v in report.violations
        if v.rule_id == "RULE-L0-RENDER-OUT-OF-VIEWPORT"
    ]
    assert any("brand-logo" in s for s in out_selectors)
    assert any("uncontained-table" in s for s in out_selectors)
    assert len(report.screenshots) == 1
    assert Path(report.screenshots[0]).exists()


def test_clean_fixture_and_cli_pass_with_zero_errors(tmp_path: Path) -> None:
    fixture_file = tmp_path / "clean.html"
    fixture_file.write_text(CLEAN_HTML, encoding="utf-8")
    shot_dir = tmp_path / "shots_clean"

    proc = subprocess.run(
        [
            sys.executable,
            str(AUDITOR_SCRIPT),
            fixture_file.as_uri(),
            "--routes",
            "#dashboard,#warranty",
            "--viewports",
            "1280x800,1366x768",
            "--screenshot-dir",
            str(shot_dir),
            "--wait-ms",
            "50",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, f"Unexpected failure: {proc.stdout}\n{proc.stderr}"
    payload = json.loads(proc.stdout)
    assert payload["passed"] is True
    assert payload["error_count"] == 0
    assert payload["violations"] == []
    assert len(payload["screenshots"]) == 4
    for shot in payload["screenshots"]:
        assert Path(shot).is_file()


V230_ADVERSARIAL_SPLIT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, sans-serif; background: #F9F8F6; color: #111921; }
  .shell {
    display: grid;
    grid-template-columns: 240px minmax(0, 1fr);
    min-height: 100vh;
  }
  aside {
    width: 240px;
    background: #111921;
    color: #FFFFFF;
  }
  /* Defect 5: Faint alpha (0.06 < 0.14) and height 60px != external header 64px */
  .sidebar-brand {
    height: 60px;
    padding: 0 16px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  }
  /* Defect 6: Nav starts at top=60 with 8px top padding (firstNav top=68), main starts at top=64 with 28px top padding (first top=92) */
  aside nav {
    padding: 8px 16px;
  }
  aside nav a {
    display: block;
    padding: 8px 12px;
    color: #F8FAFC;
    text-decoration: none;
  }
  .right-col {
    min-width: 0;
    display: flex;
    flex-direction: column;
  }
  header.topbar {
    height: 64px;
    padding: 0 24px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid #E2E8F0;
    background: #FFFFFF;
  }
  main {
    min-width: 0;
    padding: 28px 24px;
  }
  /* Defect 8: Flex toolbar where role-lens-badge wraps onto second line at 1240x800 */
  .toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    width: 600px;
    margin-bottom: 20px;
  }
  .toolbar select {
    width: 480px;
    height: 36px;
  }
  .lens-badge {
    width: 180px;
    height: 28px;
    display: inline-flex;
    align-items: center;
    padding: 0 10px;
    background: #EFECE6;
  }
  /* Defect 7: Sibling stat cards with misaligned .font-display tops */
  .stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  .stat-card {
    padding: 16px;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
  }
  .font-display {
    font-family: Georgia, serif;
    font-size: 28px;
    font-variant-numeric: lining-nums tabular-nums;
  }
</style>
</head>
<body>
  <div class="shell">
    <aside data-testid="app-sidebar">
      <div class="sidebar-brand" data-testid="brand-logo">LUXURY MARITIME</div>
      <nav>
        <a href="#dashboard">Executive Overview</a>
      </nav>
    </aside>
    <div class="right-col">
      <header class="topbar">
        <div class="eyebrow">FLEET TELEMETRY</div>
      </header>
      <main>
        <div class="toolbar">
          <select aria-label="Vessel Filter"><option>All Vessels</option></select>
          <span class="lens-badge" data-testid="role-lens-badge">Concierge Lens</span>
        </div>
        <div class="stats-grid">
          <section class="stat-card" data-testid="stat-card">
            <div style="height: 18px; font-size: 12px;">Active Claims</div>
            <div class="font-display">148</div>
          </section>
          <section class="stat-card" data-testid="stat-card">
            <div style="height: 40px; font-size: 12px;">SLA On-Time Resolution Rate Across Regions</div>
            <div class="font-display">99.2%</div>
          </section>
        </div>
      </main>
    </div>
  </div>
</body>
</html>
"""


V230_CLEAN_SPLIT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, sans-serif; background: #F9F8F6; color: #111921; }
  .shell {
    display: grid;
    grid-template-columns: 240px minmax(0, 1fr);
    min-height: 100vh;
  }
  aside {
    width: 240px;
    background: #111921;
    color: #FFFFFF;
  }
  .sidebar-brand {
    height: 64px;
    padding: 0 16px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.22);
    font-size: 15px;
    font-weight: 600;
  }
  aside nav {
    padding: 20px 16px;
  }
  aside nav a {
    display: block;
    padding: 8px 12px;
    color: #F8FAFC;
    text-decoration: none;
    font-size: 14px;
  }
  .right-col {
    min-width: 0;
    display: flex;
    flex-direction: column;
  }
  header.topbar {
    height: 64px;
    padding: 0 24px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid #E2E8F0;
    background: #FFFFFF;
  }
  main {
    min-width: 0;
    padding: 20px 24px;
  }
  .toolbar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
  }
  .toolbar select {
    width: 200px;
    max-width: 100%;
    height: 36px;
  }
  .lens-badge {
    height: 28px;
    display: inline-flex;
    align-items: center;
    padding: 0 12px;
    background: #EFECE6;
    font-size: 12px;
  }
  .stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  .stat-card {
    padding: 16px;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
  }
  .stat-label {
    height: 20px;
    font-size: 12px;
    margin-bottom: 8px;
  }
  .font-display {
    font-family: Georgia, serif;
    font-size: 28px;
    font-variant-numeric: lining-nums tabular-nums;
  }
  @media (max-width: 1023px) {
    aside { width: 200px; }
    .shell { grid-template-columns: 200px minmax(0, 1fr); }
  }
  @media (max-width: 767px) {
    .shell { grid-template-columns: minmax(0, 1fr); }
    aside { display: none; }
    .stats-grid { grid-template-columns: minmax(0, 1fr); }
  }
</style>
</head>
<body>
  <div class="shell">
    <aside data-testid="app-sidebar">
      <div class="sidebar-brand" data-testid="brand-logo">LUXURY MARITIME</div>
      <nav>
        <a href="#dashboard">Executive Overview</a>
      </nav>
    </aside>
    <div class="right-col">
      <header class="topbar">
        <div class="eyebrow" style="font-size: 12px;">FLEET TELEMETRY</div>
      </header>
      <main>
        <div class="toolbar">
          <select aria-label="Vessel Filter"><option>All Vessels</option></select>
          <span class="lens-badge" data-testid="role-lens-badge">Concierge Lens</span>
        </div>
        <div class="stats-grid">
          <section class="stat-card" data-testid="stat-card">
            <div class="stat-label">Active Claims</div>
            <div class="font-display">148</div>
          </section>
          <section class="stat-card" data-testid="stat-card">
            <div class="stat-label">SLA Resolution</div>
            <div class="font-display">99.2%</div>
          </section>
        </div>
      </main>
    </div>
  </div>
</body>
</html>
"""


def test_v230_rhythm_and_alignment_rules() -> None:
    assert RESPONSIVE_VIEWPORTS == (
        (360, 800),
        (390, 844),
        (540, 800),
        (768, 1024),
        (1024, 768),
    )
    assert DESKTOP_VIEWPORTS == (
        (1240, 800),
        (1280, 800),
        (1366, 768),
        (1440, 900),
    )
    assert DEFAULT_VIEWPORTS == RESPONSIVE_VIEWPORTS + DESKTOP_VIEWPORTS
    assert len(DEFAULT_VIEWPORTS) == 9
    assert parse_viewports("", profile="responsive") == list(RESPONSIVE_VIEWPORTS)
    assert parse_viewports("", profile="desktop") == list(DESKTOP_VIEWPORTS)
    assert parse_viewports("", profile="full") == list(DEFAULT_VIEWPORTS)
    assert VIEWPORT_PROFILES["desktop"] == DESKTOP_VIEWPORTS

    auditor = RenderedLayoutAuditor(wait_ms=50)
    bad_report = auditor.audit_html(
        V230_ADVERSARIAL_SPLIT_HTML,
        viewports=[(1240, 800)],
    )
    assert not bad_report.passed
    rule_ids = {v.rule_id for v in bad_report.violations}
    assert "RULE-L0-RENDER-CHROME-DIVIDER-ALIGNMENT" in rule_ids
    assert "RULE-L0-RENDER-TOP-RHYTHM-ALIGNMENT" in rule_ids
    assert "RULE-L0-RENDER-SIBLING-STAT-BASELINE" in rule_ids
    assert "RULE-L0-RENDER-TOOLBAR-ORPHAN-WRAP" in rule_ids

    clean_report = auditor.audit_html(
        V230_CLEAN_SPLIT_HTML,
        viewports=DEFAULT_VIEWPORTS,
    )
    assert clean_report.passed, f"Unexpected violations: {clean_report.violations}"
    assert clean_report.error_count == 0
    assert clean_report.violations == []


V240_ADVERSARIAL_TOOLBAR_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, sans-serif; padding: 16px; background: #F9F8F6; }
  .toolbar-outer {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }
  .toolbar-left {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
    flex: 1 1 0%;
    min-width: 0;
  }
  .tablist { display: inline-flex; flex-shrink: 0; gap: 4px; }
  .tablist button { height: 36px; padding: 0 14px; }
  .search-label { display: inline-flex; align-items: center; min-width: 220px; width: 240px; height: 36px; }
  .search-label input { width: 100%; height: 36px; padding: 0 10px; }
  .cta-group { display: inline-flex; flex-shrink: 0; gap: 8px; }
  .cta-group button { height: 36px; padding: 0 16px; }
</style>
</head>
<body>
  <main>
    <div class="toolbar-outer">
      <div class="toolbar-left" data-testid="collapsed-flex-group">
        <div class="tablist" role="tablist">
          <button role="tab" type="button">All (24)</button>
          <button role="tab" type="button">Open (12)</button>
          <button role="tab" type="button">Warranty (8)</button>
        </div>
        <label class="search-label">
          <input type="search" placeholder="Search HIN or vessel..." />
        </label>
      </div>
      <div class="cta-group">
        <button type="button" data-testid="export-btn">Export CSV</button>
        <button type="button" data-testid="new-claim-btn">New Claim</button>
      </div>
    </div>
  </main>
</body>
</html>
"""


V240_CLEAN_MODAL_AND_TOOLBAR_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, sans-serif; padding: 16px; background: #F9F8F6; }
  .toolbar-outer { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px; }
  .toolbar-left { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; flex: 1 1 280px; min-width: min(100%, 280px); }
  .tablist { display: inline-flex; flex-wrap: wrap; gap: 6px; }
  .tablist button { height: 36px; padding: 0 12px; }
  .search-label { display: inline-flex; align-items: center; flex: 1 1 180px; max-width: 100%; height: 36px; }
  .search-label input { width: 100%; height: 36px; padding: 0 10px; }
  .cta-group { display: inline-flex; flex-wrap: wrap; gap: 8px; }
  .cta-group button { height: 36px; padding: 0 14px; }
  .modal-backdrop { position: fixed; inset: 0; display: flex; align-items: flex-start; justify-content: center; padding: 16px; background: rgba(17, 25, 33, 0.45); }
  .modal-card { width: min(100%, 320px); padding: 20px; background: #FFFFFF; border: 1px solid #CBD5E1; }
  .modal-actions { display: flex; gap: 8px; margin-top: 12px; }
  .modal-actions button { height: 36px; padding: 0 14px; }
</style>
</head>
<body>
  <main>
    <div class="toolbar-outer">
      <div class="toolbar-left">
        <div class="tablist" role="tablist">
          <button role="tab" type="button">All</button>
          <button role="tab" type="button">Open</button>
        </div>
        <label class="search-label" role="button">
          <input type="search" placeholder="Search claims" />
        </label>
      </div>
      <div class="cta-group">
        <button type="button">New Claim</button>
      </div>
    </div>
  </main>
  <div class="modal-backdrop">
    <div class="modal-card" role="dialog" aria-modal="true">
      <h2>Approve Claim</h2>
      <div class="modal-actions">
        <button type="button">Cancel</button>
        <button type="button">Confirm</button>
      </div>
    </div>
  </div>
</body>
</html>
"""


def test_v240_adversarial_toolbar_profiles_and_rules(tmp_path: Path) -> None:
    fixture = tmp_path / "v240_bad_toolbar.html"
    fixture.write_text(V240_ADVERSARIAL_TOOLBAR_HTML, encoding="utf-8")

    desktop_proc = subprocess.run(
        [
            sys.executable,
            str(AUDITOR_SCRIPT),
            fixture.as_uri(),
            "--profile",
            "desktop",
            "--wait-ms",
            "30",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert desktop_proc.returncode == 0, desktop_proc.stdout
    assert json.loads(desktop_proc.stdout)["passed"] is True

    for profile in ("responsive", "full"):
        proc = subprocess.run(
            [
                sys.executable,
                str(AUDITOR_SCRIPT),
                fixture.as_uri(),
                "--profile",
                profile,
                "--wait-ms",
                "30",
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 1
        payload = json.loads(proc.stdout)
        assert payload["passed"] is False
        narrow_rules = {
            v["rule_id"]
            for v in payload["violations"]
            if v["viewport"] in ("390x844", "540x800")
        }
        assert "RULE-L0-RENDER-INTERACTIVE-OVERLAP" in narrow_rules
        assert "RULE-L0-RENDER-FLEX-WRAP-COLLAPSE" in narrow_rules


def test_v240_clean_responsive_modal_and_static_layer0_rule(tmp_path: Path) -> None:
    auditor = RenderedLayoutAuditor(wait_ms=30)
    clean_report = auditor.audit_html(
        V240_CLEAN_MODAL_AND_TOOLBAR_HTML, viewports=DEFAULT_VIEWPORTS
    )
    assert clean_report.passed, f"Unexpected violations: {clean_report.violations}"
    assert clean_report.violations == []

    from layer0_validator import Layer0Validator

    bad_tsx = tmp_path / "BadToolbar.tsx"
    bad_tsx.write_text(
        "export const Bad = () => (\n"
        '  <div className="flex flex-wrap items-center justify-between gap-3">\n'
        '    <div className="flex flex-wrap items-center gap-3 flex-1 min-w-0">\n'
        '      <button className="min-h-[44px] px-4 text-sm">Filter</button>\n'
        "    </div>\n"
        "  </div>\n"
        ");\n",
        encoding="utf-8",
    )
    validator = Layer0Validator(workspace_root=tmp_path)
    bad_v = validator.validate_file(bad_tsx)
    assert any(
        v.rule_id == "RULE-L0-MICRO-FLEX-WRAP-MINW0-COLLAPSE" and v.severity == "ERROR"
        for v in bad_v
    )

    good_tsx = tmp_path / "GoodToolbar.tsx"
    good_tsx.write_text(
        "export const Good = () => (\n"
        '  <div className="flex flex-wrap items-center justify-between gap-3">\n'
        '    <div className="flex flex-wrap items-center gap-3 flex-1 min-w-[280px]">\n'
        '      <button className="min-h-[44px] px-4 text-sm">Filter</button>\n'
        "    </div>\n"
        "  </div>\n"
        ");\n",
        encoding="utf-8",
    )
    good_v = validator.validate_file(good_tsx)
    assert not any(
        v.rule_id == "RULE-L0-MICRO-FLEX-WRAP-MINW0-COLLAPSE" for v in good_v
    )
