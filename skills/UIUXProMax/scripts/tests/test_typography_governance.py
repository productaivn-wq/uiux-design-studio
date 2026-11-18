#!/usr/bin/env python3
"""Unit tests for UIUXProMax v2.1.0 Deterministic Typography Governance (`SPEC-TYPOGRAPHY-001`)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
SKILL_ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from design_md_linter import validate_design_md  # noqa: E402
from layer0_validator import Layer0Validator, check_lazy_placeholders  # noqa: E402


def test_tsx_scanning_no_css_brace_false_positives(tmp_path: Path):
    tsx = tmp_path / "VesselCard.tsx"
    tsx.write_text(
        """
import React from 'react';

export function VesselCard({ title, status }: { title: string; status: string }) {
  const badgeColor = status === 'ACTIVE' ? 'text-[#8A6D3B]' : 'text-[var(--bronze)]';
  return (
    <div className="p-4 rounded bg-slate-900">
      <h2 className="text-lg font-semibold text-[oklch(95%_0.01_85)]">{title}</h2>
      <p className="text-sm text-[balance]">{status}</p>
      <span className={`text-xs font-mono ${badgeColor}`}>HIN-99201</span>
      <button onClick={() => console.log(title)} className="min-h-[44px] px-4 text-sm">
        Inspect Vessel
      </button>
    </div>
  );
}
""",
        encoding="utf-8",
    )
    validator = Layer0Validator(workspace_root=tmp_path)
    report = validator.run_suite(tmp_path)
    assert report.total_files_scanned == 1
    assert report.error_count == 0, f"Unexpected errors: {report.violations}"
    assert report.passed is True


def test_subminimum_font_size_detection_across_tsx_css_html(tmp_path: Path):
    tsx = tmp_path / "MicroText.tsx"
    tsx.write_text(
        """
export function MicroText() {
  return (
    <div>
      <span className="text-[9px]">Too small arbitrary Tailwind</span>
      <span style={{ fontSize: '10px' }}>Too small inline string</span>
      <span style={{ fontSize: 10 }}>Too small inline numeric</span>
      <span style={{ fontSize: '0.65rem' }}>Too small rem inline</span>
      <span className="sr-only" style={{ fontSize: 0 }}>Hidden accessible label</span>
    </div>
  );
}
""",
        encoding="utf-8",
    )
    css = tmp_path / "app.css"
    css.write_text(
        """
.micro-caption { font-size: 0.68rem; }
.ok-caption { font-size: 0.6875rem; }
.sr-only { font-size: 0; }
""",
        encoding="utf-8",
    )
    html = tmp_path / "fragment.html"
    html.write_text(
        '<div style="font-size: 9px;">Tiny HTML inline</div>\n',
        encoding="utf-8",
    )

    validator = Layer0Validator(workspace_root=tmp_path)
    report = validator.run_suite(tmp_path)
    submin = [
        v for v in report.violations if v.rule_id == "RULE-L0-MICRO-SUBMINIMUM-FONT"
    ]
    # 4 in TSX (9px, '10px', 10, '0.65rem') + 1 in CSS (0.68rem = 10.88px) + 1 in HTML (9px) = 6
    assert len(submin) == 6, f"Got {len(submin)}: {submin}"
    assert all(v.severity == "ERROR" for v in submin)


def test_slide_deck_keeps_8pt_floor(tmp_path: Path):
    slide_css = tmp_path / "deck.css"
    slide_css.write_text(
        """
@page { size: A4 landscape; }
.slide { width: 100%; }
.slide-note { font-size: 8.5pt; }
.slide-illegal { font-size: 7.5pt; }
""",
        encoding="utf-8",
    )
    validator = Layer0Validator(workspace_root=tmp_path)
    violations = validator.validate_file(slide_css)
    submin = [v for v in violations if v.rule_id == "RULE-L0-MICRO-SUBMINIMUM-FONT"]
    assert len(submin) == 1
    assert "7.5pt" in submin[0].element_or_token


def test_arbitrary_text_size_flags_lengths_only_never_colors(tmp_path: Path):
    tsx = tmp_path / "Tokens.tsx"
    tsx.write_text(
        """
export const Tokens = () => (
  <div className="text-[#8A6D3B] text-[rgb(12,34,56)] text-[hsl(210,20%,90%)] text-[oklch(53%_0.09_78)] text-[var(--bronze)] text-[color:var(--ink)] text-[balance] text-[pretty] text-[nowrap]">
    <p className="text-[11px] md:text-[13px] text-[0.8rem] text-[clamp(0.75rem,2vw,1rem)] text-[length:15px]">
      Arbitrary lengths
    </p>
  </div>
);
""",
        encoding="utf-8",
    )
    validator = Layer0Validator(workspace_root=tmp_path)
    violations = validator.validate_file(tsx)
    arb = [v for v in violations if v.rule_id == "RULE-L0-MICRO-ARBITRARY-TEXT-SIZE"]
    assert len(arb) == 5, f"Got {arb}"
    flagged_tokens = {v.element_or_token for v in arb}
    assert flagged_tokens == {
        "text-[11px]",
        "md:text-[13px]",
        "text-[0.8rem]",
        "text-[clamp(0.75rem,2vw,1rem)]",
        "text-[length:15px]",
    }


def test_mono_overuse_flags_buttons_and_spares_data_elements(tmp_path: Path):
    tsx = tmp_path / "Actions.tsx"
    tsx.write_text(
        """
export function Actions({ onApprove }: { onApprove: () => void }) {
  return (
    <div>
      <span className="font-mono text-xs">CLM-2026-0041</span>
      <code className="font-mono text-xs">SHA256</code>
      <table><tbody><tr><td className="font-mono">12,500</td></tr></tbody></table>
      <button onClick={() => onApprove()} className="px-4 py-2 font-mono text-sm">
        Approve Claim
      </button>
      <Btn className="btn-secondary font-mono">Reject</Btn>
      <button data-mono-allowed className="font-mono text-xs">0xFA91</button>
    </div>
  );
}
""",
        encoding="utf-8",
    )
    validator = Layer0Validator(workspace_root=tmp_path)
    violations = validator.validate_file(tsx)
    mono = [v for v in violations if v.rule_id == "RULE-L0-MICRO-MONO-OVERUSE"]
    assert len(mono) == 2, f"Got {mono}"


def test_typography_scale_sprawl_and_non_size_class_immunity(tmp_path: Path):
    clean_tsx = tmp_path / "CleanScale.tsx"
    clean_tsx.write_text(
        """
export const CleanScale = () => (
  <div className="text-left text-center text-right text-justify text-wrap text-nowrap text-balance text-pretty text-ellipsis text-clip text-bronze text-navy text-white">
    <span className="text-micro">11</span>
    <span className="text-xs">12</span>
    <span className="text-sm">14</span>
    <span className="text-base">16</span>
    <span className="text-lg">18</span>
    <span className="text-xl">20</span>
    <span className="text-2xl">24</span>
    <span className="text-3xl">30</span>
  </div>
);
""",
        encoding="utf-8",
    )
    validator = Layer0Validator(workspace_root=tmp_path)
    clean_report = validator.run_suite(tmp_path)
    assert not any(
        v.rule_id == "RULE-L0-MICRO-TYPOGRAPHY-SPRAWL" for v in clean_report.violations
    )

    # Add 9th distinct step via CSS font-size -> triggers sprawl
    extra_css = tmp_path / "extra.css"
    extra_css.write_text(".hero-kpi { font-size: 42px; }\n", encoding="utf-8")
    sprawl_report = validator.run_suite(tmp_path)
    sprawl = [
        v
        for v in sprawl_report.violations
        if v.rule_id == "RULE-L0-MICRO-TYPOGRAPHY-SPRAWL"
    ]
    assert len(sprawl) == 1
    assert sprawl[0].severity == "ERROR"


def test_font_family_sprawl_and_custom_var_exclusion(tmp_path: Path):
    css = tmp_path / "tokens.css"
    css.write_text(
        """
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600&family=Plus+Jakarta+Sans:wght@400;600&family=JetBrains+Mono:wght@400&display=swap');

:root {
  --tsy-font-fallback-sans: 'Unused Legacy Sans', Arial, sans-serif;
}

@theme {
  --font-display: 'Cormorant Garamond', Georgia, serif;
  --font-sans: 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, Consolas, monospace;
}

body {
  font-family: var(--font-sans);
}
""",
        encoding="utf-8",
    )
    validator = Layer0Validator(workspace_root=tmp_path)
    triad_report = validator.run_suite(tmp_path)
    assert not any(
        v.rule_id == "RULE-L0-MICRO-FONT-FAMILY-SPRAWL" for v in triad_report.violations
    ), f"Triad should pass: {triad_report.violations}"

    # Introduce a 4th custom font family -> triggers sprawl
    extra = tmp_path / "rogue.css"
    extra.write_text(
        """
@font-face {
  font-family: 'Space Grotesk';
  src: local('Space Grotesk');
}
.rogue { font-family: 'Space Grotesk', sans-serif; }
""",
        encoding="utf-8",
    )
    sprawl_report = validator.run_suite(tmp_path)
    fam_sprawl = [
        v
        for v in sprawl_report.violations
        if v.rule_id == "RULE-L0-MICRO-FONT-FAMILY-SPRAWL"
    ]
    assert len(fam_sprawl) == 1
    assert fam_sprawl[0].severity == "ERROR"


def test_run_suite_skips_non_production_dirs_and_test_files(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "App.tsx").write_text(
        "export const App = () => <div className='text-sm'>Clean</div>;\n",
        encoding="utf-8",
    )
    # Ignored files/directories containing violations that MUST NOT be scanned
    (tmp_path / "src" / "App.test.tsx").write_text(
        "export const T = () => <button className='font-mono text-[8px]'>Test</button>;\n",
        encoding="utf-8",
    )
    (tmp_path / "src" / "App.spec.tsx").write_text(
        "export const S = () => <button className='font-mono text-[8px]'>Spec</button>;\n",
        encoding="utf-8",
    )
    (tmp_path / "src" / "types.d.ts").write_text(
        "// ... rest of code\n", encoding="utf-8"
    )
    (tmp_path / "src" / "routeTree.gen.ts").write_text(
        "// ... rest of code\n", encoding="utf-8"
    )
    nm = tmp_path / "node_modules" / "pkg"
    nm.mkdir(parents=True)
    (nm / "bad.js").write_text("// ... rest of code\n", encoding="utf-8")

    validator = Layer0Validator(workspace_root=tmp_path)
    report = validator.run_suite(tmp_path)
    assert report.total_files_scanned == 1
    assert report.passed is True


def test_cli_execution_succeeds_without_name_error(tmp_path: Path):
    (tmp_path / "index.tsx").write_text(
        "export const Home = () => <main className='text-base'>Ready</main>;\n",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "layer0_validator.py"), str(tmp_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert proc.returncode == 0, f"stderr={proc.stderr}\nstdout={proc.stdout}"
    assert "NameError" not in proc.stderr
    assert "[SUCCESS] Layer 0 Governance Check Passed." in proc.stdout

    # Also verify check_lazy_placeholders supports both (content, path) and (path, content)
    assert len(check_lazy_placeholders("// ... rest of code", "demo.tsx")) == 1
    assert len(check_lazy_placeholders("demo.tsx", "// ... rest of code")) == 1


def test_design_md_linter_typography_contracts_and_template_pass(tmp_path: Path):
    template_path = SKILL_ROOT / "templates" / "base" / "DESIGN_template.md"
    assert template_path.exists()
    assert validate_design_md(template_path) == []

    bad_design = tmp_path / "DESIGN.md"
    bad_design.write_text(
        """---
version: "1.0.0"
tokens:
  colors:
    surface:
      canvas: "oklch(16% 0.015 250)"
  typography:
    fonts:
      display: "'Cormorant Garamond', serif"
      heading: "'Fraunces', serif"
      body: "'Plus Jakarta Sans', sans-serif"
      mono: "'JetBrains Mono', monospace"
    scale:
      micro: "0.625rem"
      xs: "0.75rem"
      sm: "0.875rem"
      base: "1.0rem"
      lg: "1.125rem"
      xl: "1.25rem"
      2xl: "1.5rem"
      3xl: "1.875rem"
      4xl: "2.25rem"
  shape:
    radii:
      sm: "4px"
---
# Bad Design
""",
        encoding="utf-8",
    )
    errs = validate_design_md(bad_design)
    joined = "\n".join(errs)
    assert "RULE-L0-MICRO-FONT-FAMILY-SPRAWL" in joined
    assert "RULE-L0-MICRO-TYPOGRAPHY-SPRAWL" in joined
    assert "RULE-L0-MICRO-SUBMINIMUM-FONT" in joined
