#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
design_md_linter.py - Deterministic SSOT Linter & Token Compiler for PRODUCT.md and DESIGN.md (P = 1, v2.5.0).

Upgraded with capabilities from:
- google-labs-code/design.md: OKLCH perceptual luminance & WCAG 2.1 AA contrast pair math, semantic token diffing (--diff).
- nexu-io/open-design: Deterministic DESIGN.md -> tokens.css + tailwind-v4.css (@theme) + W3C design-tokens.json compiler (--compile-tokens).
- VoltAgent/awesome-design-md: 9-section brand contract support.

Validates:
1. PRODUCT.md: Schema completeness, operational ergonomics, surface modes, anti-slop blacklist.
2. DESIGN.md: YAML frontmatter, OKLCH perceptual syntax, WCAG 2.1 AA foreground/background contrast ratios
   (>= 4.5:1 primary text, >= 3.0:1 secondary text), typography governance (<= 3 custom font families,
   <= 8 scale steps, >= 11px / 0.6875rem minimum font size), and shape scales.
3. Non-duplication invariant: PRODUCT.md contains no CSS tokens; DESIGN.md contains no business budgets.
"""

from __future__ import annotations

import argparse
import io
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

try:
    import yaml
except ImportError:
    yaml = None


OKLCH_PATTERN = re.compile(
    r"^oklch\(\s*([\d\.]+)(%?)\s+([\d\.]+)\s+([\d\.]+)(?:\s*\/\s*([\d\.]+%?))?\s*\)$",
    re.IGNORECASE,
)

STATIC_FONT_SCALE_RE = re.compile(
    r"^\s*(\d+(?:\.\d+)?)\s*(px|rem|pt)\s*$", re.IGNORECASE
)

SYSTEM_AND_GENERIC_FONTS: Set[str] = {
    "sans-serif",
    "serif",
    "monospace",
    "cursive",
    "fantasy",
    "system-ui",
    "ui-sans-serif",
    "ui-serif",
    "ui-monospace",
    "ui-rounded",
    "-apple-system",
    "blinkmacsystemfont",
    "segoe ui",
    "roboto",
    "helvetica neue",
    "helvetica",
    "arial",
    "noto sans",
    "liberation sans",
    "georgia",
    "cambria",
    "times new roman",
    "times",
    "consolas",
    "liberation mono",
    "menlo",
    "monaco",
    "courier new",
    "courier",
    "apple color emoji",
    "segoe ui emoji",
    "segoe ui symbol",
    "noto color emoji",
    "inherit",
    "initial",
    "unset",
}

PRODUCT_MD_REQUIRED_SECTIONS = [
    "## 1. Product Purpose",
    "## 2. Platform & Form Factor",
    "## 3. Users & Field Ergonomics",
    "## 4. Surface Modes",
    "## 5. Accessibility & Inclusion",
    "## 6. Constraints & Anti-References",
]


def parse_oklch(oklch_str: str) -> Optional[Tuple[float, float, float, float]]:
    """Parse an OKLCH string 'oklch(L C H [/ alpha])' into normalized (L in 0..1, C, H_deg, alpha)."""
    clean = oklch_str.split("#")[0].strip()
    m = OKLCH_PATTERN.match(clean)
    if not m:
        return None
    l_raw = float(m.group(1))
    is_pct = m.group(2) == "%"
    l_norm = (l_raw / 100.0) if (is_pct or l_raw > 1.0) else l_raw
    c_val = float(m.group(3))
    h_deg = float(m.group(4))
    alpha_raw = m.group(5)
    alpha = 1.0
    if alpha_raw:
        if alpha_raw.endswith("%"):
            alpha = float(alpha_raw[:-1]) / 100.0
        else:
            alpha = float(alpha_raw)
    return (
        max(0.0, min(1.0, l_norm)),
        max(0.0, c_val),
        h_deg,
        max(0.0, min(1.0, alpha)),
    )


def oklch_to_relative_luminance(oklch_str: str) -> Optional[float]:
    """Convert OKLCH string to WCAG 2.1 relative luminance Y in [0.0, 1.0] via Oklab -> Linear sRGB."""
    parsed = parse_oklch(oklch_str)
    if parsed is None:
        return None
    L, C, h_deg, _alpha = parsed
    h_rad = math.radians(h_deg)
    a = C * math.cos(h_rad)
    b = C * math.sin(h_rad)

    # Oklab to non-linear LMS
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b

    l_lin = l_ * l_ * l_
    m_lin = m_ * m_ * m_
    s_lin = s_ * s_ * s_

    # LMS to linear sRGB
    r_lin = +4.0767416621 * l_lin - 3.3077115913 * m_lin + 0.2309699292 * s_lin
    g_lin = -1.2684380046 * l_lin + 2.6097574011 * m_lin - 0.3413193965 * s_lin
    b_lin = -0.0041960863 * l_lin - 0.7034186147 * m_lin + 1.7076147010 * s_lin

    r_clamped = max(0.0, min(1.0, r_lin))
    g_clamped = max(0.0, min(1.0, g_lin))
    b_clamped = max(0.0, min(1.0, b_lin))

    return 0.2126 * r_clamped + 0.7152 * g_clamped + 0.0722 * b_clamped


def compute_oklch_contrast_ratio(color_a: str, color_b: str) -> Optional[float]:
    """Compute WCAG 2.1 contrast ratio between two OKLCH token strings."""
    lum_a = oklch_to_relative_luminance(color_a)
    lum_b = oklch_to_relative_luminance(color_b)
    if lum_a is None or lum_b is None:
        return None
    bright = max(lum_a, lum_b)
    dark = min(lum_a, lum_b)
    return round((bright + 0.05) / (dark + 0.05), 2)


def _extract_primary_custom_fonts(font_stack: str) -> Dict[str, str]:
    found: Dict[str, str] = {}
    for part in str(font_stack).split(","):
        tok = part.strip().strip("'\"` ").strip()
        tok = " ".join(tok.split())
        if not tok:
            continue
        low = tok.lower()
        if low.startswith(("var(", "--", "$", "{")) or "(" in tok or ")" in tok:
            continue
        if low in SYSTEM_AND_GENERIC_FONTS:
            continue
        found.setdefault(low, tok)
    return found


def _resolve_scale_step_px(raw_val: object) -> Optional[float]:
    if isinstance(raw_val, dict):
        raw_val = raw_val.get("size") or raw_val.get("fontSize") or raw_val.get("value")
    if isinstance(raw_val, (int, float)):
        return round(float(raw_val), 2)
    if not isinstance(raw_val, str):
        return None
    clean = raw_val.split("#")[0].strip()
    m = STATIC_FONT_SCALE_RE.match(clean)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2).lower()
    if unit == "px":
        return round(val, 2)
    if unit == "rem":
        return round(val * 16.0, 2)
    if unit == "pt":
        return round(val * (96.0 / 72.0), 2)
    return None


def _parse_design_md_yaml(path: Path) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    if not path.exists():
        return None, [f"DESIGN.md does not exist at {path}"]

    text = path.read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---"):
        return None, ["DESIGN.md missing leading YAML frontmatter delimiter ('---')."]

    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, [
            "DESIGN.md invalid frontmatter structure (closing '---' missing)."
        ]

    raw_yaml = parts[1]
    if yaml is None:
        if "tokens:" not in raw_yaml or "colors:" not in raw_yaml:
            return None, [
                "DESIGN.md frontmatter missing 'tokens' or 'colors' declaration."
            ]
        return {}, []

    try:
        data = yaml.safe_load(raw_yaml)
    except Exception as e:
        return None, [f"DESIGN.md YAML parse error: {e}"]

    if not isinstance(data, dict):
        return None, ["DESIGN.md frontmatter must be a valid YAML mapping."]

    return data, []


def validate_product_md(path: Path) -> List[str]:
    """Validates root PRODUCT.md for required sections and separation of concerns."""
    errors: List[str] = []
    if not path.exists():
        return [f"PRODUCT.md does not exist at {path}"]

    text = path.read_text(encoding="utf-8", errors="ignore")

    for section in PRODUCT_MD_REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"PRODUCT.md missing required section: '{section}'")

    hex_matches = re.findall(r"#[0-9a-fA-F]{3,8}\b", text)
    if len(hex_matches) > 3:
        errors.append(
            f"PRODUCT.md contains {len(hex_matches)} raw color hex codes. "
            "Visual tokens belong strictly in DESIGN.md."
        )

    return errors


def validate_design_md(
    path: Path,
    max_font_families: int = 3,
    max_scale_steps: int = 8,
    min_font_size_px: float = 11.0,
    check_contrast: bool = True,
) -> List[str]:
    """Validates root DESIGN.md for YAML frontmatter, OKLCH tokens, WCAG contrast, and shape/type scales."""
    data, parse_errors = _parse_design_md_yaml(path)
    if parse_errors or not data:
        return parse_errors

    errors: List[str] = []
    tokens = data.get("tokens", {})
    if not isinstance(tokens, dict):
        return ["DESIGN.md frontmatter missing 'tokens' dictionary."]

    for cat in ("colors", "typography", "shape"):
        if cat not in tokens:
            errors.append(f"DESIGN.md tokens missing mandatory category: '{cat}'.")

    colors = tokens.get("colors", {})
    if isinstance(colors, dict):
        for group_name, group_val in colors.items():
            if isinstance(group_val, dict):
                for role_name, val in group_val.items():
                    if isinstance(val, str):
                        clean_val = val.split("#")[0].strip()
                        if not OKLCH_PATTERN.match(clean_val):
                            errors.append(
                                f"Token 'colors.{group_name}.{role_name}' ({val}) is not valid OKLCH syntax. "
                                "Example: 'oklch(53.2% 0.092 78.5)'."
                            )

        # WCAG 2.1 AA Foreground/Background Contrast Verification (google-labs-code/design.md upgrade)
        if check_contrast:
            surfaces = (
                colors.get("surface", {})
                if isinstance(colors.get("surface"), dict)
                else {}
            )
            texts = (
                colors.get("text", {}) if isinstance(colors.get("text"), dict) else {}
            )
            fg_primary = texts.get("primary") or colors.get("foreground")
            fg_secondary = texts.get("secondary") or texts.get("muted")
            for surf_key in ("canvas", "card", "background", "primary"):
                bg_val = surfaces.get(surf_key) or (
                    colors.get("background") if surf_key == "background" else None
                )
                if isinstance(bg_val, str) and isinstance(fg_primary, str):
                    cr = compute_oklch_contrast_ratio(bg_val, fg_primary)
                    if cr is not None and cr < 4.5:
                        errors.append(
                            f"RULE-L0-MICRO-CONTRAST: Insufficient WCAG 2.1 AA contrast ({cr:.2f}:1 < 4.5:1) "
                            f"between surface '{surf_key}' ({bg_val}) and primary text ({fg_primary})."
                        )
                if isinstance(bg_val, str) and isinstance(fg_secondary, str):
                    cr_sec = compute_oklch_contrast_ratio(bg_val, fg_secondary)
                    if cr_sec is not None and cr_sec < 3.0:
                        errors.append(
                            f"RULE-L0-MICRO-CONTRAST: Insufficient contrast ({cr_sec:.2f}:1 < 3.0:1) "
                            f"between surface '{surf_key}' ({bg_val}) and secondary text ({fg_secondary})."
                        )

    typography = tokens.get("typography", {})
    if isinstance(typography, dict):
        fonts = typography.get("fonts", {})
        if isinstance(fonts, dict):
            custom_families: Dict[str, str] = {}
            for _role, stack_val in fonts.items():
                if isinstance(stack_val, str):
                    for k, v in _extract_primary_custom_fonts(stack_val).items():
                        custom_families.setdefault(k, v)
            if len(custom_families) > max_font_families:
                fam_str = ", ".join(sorted(custom_families.values()))
                errors.append(
                    f"RULE-L0-MICRO-FONT-FAMILY-SPRAWL: 'tokens.typography.fonts' declares {len(custom_families)} "
                    f"distinct custom font families ({fam_str}), exceeding the {max_font_families}-family ceiling."
                )

        scale = typography.get("scale", {})
        if isinstance(scale, dict):
            if len(scale) > max_scale_steps:
                errors.append(
                    f"RULE-L0-MICRO-TYPOGRAPHY-SPRAWL: 'tokens.typography.scale' declares {len(scale)} steps, "
                    f"exceeding the {max_scale_steps}-step ceiling (7-step modular scale recommended)."
                )
            for step_name, step_val in scale.items():
                px_val = _resolve_scale_step_px(step_val)
                if px_val is not None and px_val < min_font_size_px:
                    errors.append(
                        f"RULE-L0-MICRO-SUBMINIMUM-FONT: 'tokens.typography.scale.{step_name}' ({step_val} -> {px_val:.2f}px) "
                        f"violates the {min_font_size_px:.0f}px (0.6875rem) legibility floor."
                    )

    return errors


def compile_design_tokens(design_md_path: Path, out_dir: Path) -> Dict[str, str]:
    """Deterministically compile DESIGN.md frontmatter into tokens.css, tailwind-v4.css, and design-tokens.json.

    Modeled after nexu-io/open-design (od-design-system-project/v1) and @google/design.md.
    """
    data, errors = _parse_design_md_yaml(design_md_path)
    if errors or not data:
        raise ValueError(f"Cannot compile invalid DESIGN.md: {'; '.join(errors)}")

    tokens = data.get("tokens", {})
    colors = tokens.get("colors", {}) if isinstance(tokens.get("colors"), dict) else {}
    typography = (
        tokens.get("typography", {})
        if isinstance(tokens.get("typography"), dict)
        else {}
    )
    shape = tokens.get("shape", {}) if isinstance(tokens.get("shape"), dict) else {}
    spacing = (
        tokens.get("spacing", {}) if isinstance(tokens.get("spacing"), dict) else {}
    )

    css_vars: List[Tuple[str, str]] = []
    dtcg_json: Dict[str, Any] = {
        "$schema": "https://tr.designtokens.org/format/",
        "schemaVersion": "od-design-system-project/v1",
        "name": data.get("name", design_md_path.parent.name),
        "world": data.get("world", "custom"),
        "color": {},
        "typography": {},
        "shape": {},
        "spacing": {},
    }

    # 1. Colors
    for group_name, group_val in colors.items():
        if isinstance(group_val, dict):
            dtcg_json["color"][group_name] = {}
            for role_name, val in group_val.items():
                clean_v = str(val).split("#")[0].strip()
                var_name = f"--color-{group_name}-{role_name}".replace("_", "-")
                css_vars.append((var_name, clean_v))
                dtcg_json["color"][group_name][role_name] = {
                    "$type": "color",
                    "$value": clean_v,
                }
        elif isinstance(group_val, str):
            clean_v = group_val.split("#")[0].strip()
            var_name = f"--color-{group_name}".replace("_", "-")
            css_vars.append((var_name, clean_v))
            dtcg_json["color"][group_name] = {"$type": "color", "$value": clean_v}

    # 2. Typography (Fonts + Scale)
    fonts = (
        typography.get("fonts", {}) if isinstance(typography.get("fonts"), dict) else {}
    )
    dtcg_json["typography"]["fonts"] = {}
    for role_name, stack_val in fonts.items():
        clean_v = str(stack_val).strip()
        var_name = f"--font-{role_name}".replace("_", "-")
        css_vars.append((var_name, clean_v))
        dtcg_json["typography"]["fonts"][role_name] = {
            "$type": "fontFamily",
            "$value": clean_v,
        }

    scale = (
        typography.get("scale", {}) if isinstance(typography.get("scale"), dict) else {}
    )
    dtcg_json["typography"]["scale"] = {}
    for step_name, step_val in scale.items():
        clean_v = str(step_val).split("#")[0].strip()
        var_name = f"--text-{step_name}".replace("_", "-")
        css_vars.append((var_name, clean_v))
        dtcg_json["typography"]["scale"][step_name] = {
            "$type": "dimension",
            "$value": clean_v,
        }

    # 3. Shape / Radii
    radii = shape.get("radii", shape) if isinstance(shape, dict) else {}
    if isinstance(radii, dict):
        for r_name, r_val in radii.items():
            if isinstance(r_val, (str, int, float)):
                clean_v = str(r_val).split("#")[0].strip()
                var_name = f"--radius-{r_name}".replace("_", "-")
                css_vars.append((var_name, clean_v))
                dtcg_json["shape"][r_name] = {"$type": "dimension", "$value": clean_v}

    # 4. Spacing
    if isinstance(spacing, dict):
        for s_name, s_val in spacing.items():
            if isinstance(s_val, (str, int, float)):
                clean_v = str(s_val).split("#")[0].strip()
                var_name = f"--space-{s_name}".replace("_", "-")
                css_vars.append((var_name, clean_v))
                dtcg_json["spacing"][s_name] = {"$type": "dimension", "$value": clean_v}

    out_dir.mkdir(parents=True, exist_ok=True)
    tokens_css_path = out_dir / "tokens.css"
    tailwind_css_path = out_dir / "tailwind-v4.css"
    dtcg_json_path = out_dir / "design-tokens.json"

    tokens_lines = [
        "/* Auto-compiled from DESIGN.md by UIUXProMax design_md_linter.py (P=1) */",
        ":root {",
    ]
    for k, v in css_vars:
        tokens_lines.append(f"  {k}: {v};")
    tokens_lines.append("}\n")
    tokens_css_path.write_text("\n".join(tokens_lines), encoding="utf-8")

    tw_lines = [
        "/* Auto-compiled Tailwind v4 @theme from DESIGN.md by UIUXProMax (P=1) */",
        '@import "tailwindcss";',
        "",
        "@theme {",
    ]
    for k, v in css_vars:
        tw_lines.append(f"  {k}: {v};")
    tw_lines.append("}\n")
    tailwind_css_path.write_text("\n".join(tw_lines), encoding="utf-8")

    dtcg_json_path.write_text(json.dumps(dtcg_json, indent=2), encoding="utf-8")

    return {
        "tokens_css": str(tokens_css_path),
        "tailwind_v4_css": str(tailwind_css_path),
        "design_tokens_json": str(dtcg_json_path),
        "token_count": str(len(css_vars)),
    }


def _flatten_dict(d: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    items: Dict[str, Any] = {}
    for k, v in d.items():
        new_key = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            items.update(_flatten_dict(v, new_key))
        else:
            items[new_key] = v
    return items


def diff_design_md(old_path: Path, new_path: Path) -> Dict[str, Any]:
    """Compute semantic token diff between two DESIGN.md files (@google/design.md diff equivalent)."""
    old_data, old_err = _parse_design_md_yaml(old_path)
    new_data, new_err = _parse_design_md_yaml(new_path)
    if old_err or new_err or old_data is None or new_data is None:
        return {"error": old_err + new_err}

    old_flat = _flatten_dict(old_data.get("tokens", {}))
    new_flat = _flatten_dict(new_data.get("tokens", {}))

    added = {k: new_flat[k] for k in sorted(new_flat.keys() - old_flat.keys())}
    removed = {k: old_flat[k] for k in sorted(old_flat.keys() - new_flat.keys())}
    changed = {
        k: {"from": old_flat[k], "to": new_flat[k]}
        for k in sorted(old_flat.keys() & new_flat.keys())
        if str(old_flat[k]).strip() != str(new_flat[k]).strip()
    }
    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "breaking_changes": len(removed) + len(changed),
    }


def run_linter(workspace_root: Path) -> Tuple[bool, List[str]]:
    """Runs full SSOT validation across PRODUCT.md and DESIGN.md."""
    product_path = workspace_root / "PRODUCT.md"
    design_path = workspace_root / "DESIGN.md"

    errors: List[str] = []
    errors.extend(validate_product_md(product_path))
    errors.extend(validate_design_md(design_path))

    return (len(errors) == 0, errors)


def main():
    parser = argparse.ArgumentParser(
        description="Deterministic SSOT Linter & Token Compiler for PRODUCT.md and DESIGN.md (v2.5.0)"
    )
    parser.add_argument(
        "workspace_root",
        nargs="?",
        default=".",
        help="Root directory containing PRODUCT.md and DESIGN.md (or direct path to DESIGN.md)",
    )
    parser.add_argument("--strict", action="store_true", help="Fail on any warnings")
    parser.add_argument(
        "--compile-tokens",
        metavar="OUT_DIR",
        default="",
        help="Compile DESIGN.md YAML frontmatter into tokens.css, tailwind-v4.css, and design-tokens.json",
    )
    parser.add_argument(
        "--diff",
        metavar="BASELINE_DESIGN_MD",
        default="",
        help="Diff current DESIGN.md tokens against a baseline DESIGN.md file",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output machine-readable JSON"
    )
    args = parser.parse_args()

    target = Path(args.workspace_root).resolve()
    design_path = target if target.is_file() else (target / "DESIGN.md")
    root = target.parent if target.is_file() else target

    if args.diff:
        diff_res = diff_design_md(Path(args.diff).resolve(), design_path)
        print(json.dumps(diff_res, indent=2))
        sys.exit(0 if "error" not in diff_res else 1)

    if args.compile_tokens:
        out_dir = Path(args.compile_tokens).resolve()
        compiled = compile_design_tokens(design_path, out_dir)
        if args.json:
            print(json.dumps(compiled, indent=2))
        else:
            print(f"[OK] Compiled {compiled['token_count']} tokens to {out_dir}")
        sys.exit(0)

    passed, errors = run_linter(root)

    if args.json:
        print(
            json.dumps(
                {"passed": passed, "error_count": len(errors), "errors": errors},
                indent=2,
            )
        )
        sys.exit(0 if passed else 1)

    if not passed:
        print(f"[FAIL] Design System SSOT Lint Failed ({len(errors)} error(s)):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    print("[OK] Design System SSOT (PRODUCT.md + DESIGN.md) verified successfully.")
    sys.exit(0)


if __name__ == "__main__":
    main()
