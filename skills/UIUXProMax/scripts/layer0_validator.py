"""
layer0_validator.py — Deterministic Code Engine (P=1) for Layer 0 Laws (v2.5.0).

Mechanical validation for:
1. Fitts's Law (interactive hit targets >= 44x44px).
2. 8pt Grid Token Linter (spacing/margins/paddings mod 8 == 0 or 4px micro-step).
3. Optical Color Contrast Engine (WCAG 2.1 AA >= 4.5:1).
4. Hick's Law Single Primary CTA Linter (max 1 primary CTA per screen/drawer).
5. Miller's Law Density Linter (max 7±2 groups, unless shielded by @shatter-request).
6. Skeleton Loader Latency Linter (async fetch > 400ms requires skeleton).
7. Reversibility / Undo Linter (destructive actions have escape/undo path).
8. Anti-Void Invariant (prohibit unconstrained space-between in flex column cards).
9. SVG Aspect Ratio Harmonization Invariant (delta AR <= 0.25 vs container).
10. Pixel Fill Factor Linter (cards achieve >= 85% active surface density).
11. Typography Governance Suite (SPEC-TYPOGRAPHY-001):
    - RULE-L0-MICRO-SUBMINIMUM-FONT (>= 11px web/app floor; >= 8.0pt deck floor)
    - RULE-L0-MICRO-ARBITRARY-TEXT-SIZE (forbid arbitrary Tailwind length text-[...])
    - RULE-L0-MICRO-MONO-OVERUSE (forbid font-mono on <button> / <Btn>)
    - RULE-L0-MICRO-TYPOGRAPHY-SPRAWL (<= 8 distinct resolved px scale steps)
    - RULE-L0-MICRO-FONT-FAMILY-SPRAWL (<= 3 distinct custom font families)
"""

from __future__ import annotations

import argparse
import io
import json
import math
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple
from urllib.parse import unquote

# Force UTF-8 for stdout/stderr to handle unicode characters on Windows cp1252
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


SUPPORTED_EXTENSIONS: Tuple[str, ...] = (
    ".css",
    ".scss",
    ".html",
    ".htm",
    ".jinja",
    ".jinja2",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
)

SKIP_SCAN_DIRS: Set[str] = {
    "node_modules",
    ".git",
    "dist",
    "build",
    ".output",
    ".astro",
    "__pycache__",
    ".venv",
    "venv",
    "test",
    "tests",
    "__tests__",
    "vendor",
    ".pytest_cache",
    ".ruff_cache",
    "coverage",
}

TAILWIND_TEXT_SIZE_PX: Dict[str, float] = {
    "text-micro": 11.0,
    "text-xs": 12.0,
    "text-sm": 14.0,
    "text-base": 16.0,
    "text-lg": 18.0,
    "text-xl": 20.0,
    "text-2xl": 24.0,
    "text-3xl": 30.0,
    "text-4xl": 36.0,
    "text-5xl": 48.0,
    "text-6xl": 60.0,
    "text-7xl": 72.0,
    "text-8xl": 96.0,
    "text-9xl": 128.0,
}

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
    "revert",
    "revert-layer",
    "none",
    "normal",
}

LAZY_PLACEHOLDER_PATTERNS: Tuple[str, ...] = (
    "// ... rest of code",
    "/* ... existing code ... */",
    "<!-- ... rest of",
    '"The future of',
)

_RE_TW_ARBITRARY_TEXT = re.compile(r"(?<![\w-])((?:[a-z0-9-]+:)*!?text-\[([^\]]+)\])")
_RE_DIMENSIONAL_LENGTH = re.compile(
    r"^(\d+(?:\.\d+)?)(px|rem|em|pt|vw|vh|vmin|vmax|cqw|cqh|ch|ex)$",
    re.IGNORECASE,
)
_RE_STATIC_LENGTH_PREFIX = re.compile(
    r"^(?:length:)?(\d+(?:\.\d+)?)(px|rem|pt)$",
    re.IGNORECASE,
)
_RE_TW_STANDARD_TEXT_SIZE = re.compile(
    r"(?<![\w-])(?:[a-z0-9-]+:)*!?(text-(?:micro|xs|sm|base|lg|xl|[2-9]xl))(?![\w-])"
)
_RE_CSS_FONT_SIZE = re.compile(
    r"(?<![\w-])font-size\s*:\s*([^;{}\"\'`]+)",
    re.IGNORECASE,
)
_RE_JSX_FONT_SIZE = re.compile(
    r"\bfontSize\s*:\s*(?:['\"]([^'\"]+)['\"]|(-?\d+(?:\.\d+)?)\b)"
)
_RE_STATIC_FONT_VALUE = re.compile(
    r"^\s*(\d+(?:\.\d+)?)\s*(px|rem|pt)?\s*(?:!important)?\s*$",
    re.IGNORECASE,
)
_RE_HTML_INLINE_STYLE = re.compile(
    r"""\bstyle\s*=\s*(?:"([^"]*)"|'([^']*)')""",
    re.IGNORECASE | re.DOTALL,
)
_RE_GFONTS_URL = re.compile(
    r"fonts\.googleapis\.com/css2?\?([^\"'\s)>]+)",
    re.IGNORECASE,
)


def check_lazy_placeholders(arg1: str | Path, arg2: str = "") -> list[dict]:
    """Detect Wave-3 AI lazy truncation placeholders (`RULE-SLOP-LAZY-PLACEHOLDER`).

    Accepts either `(content, file_path)` or `(file_path, content)` cleanly.
    """
    if isinstance(arg1, Path):
        file_path, content = str(arg1), str(arg2)
    else:
        s1, s2 = str(arg1), str(arg2)
        if (
            s2
            and "\n" not in s1
            and any(
                s1.lower().endswith(ext)
                for ext in SUPPORTED_EXTENSIONS + (".py", ".md", ".vue", ".svelte")
            )
            and (
                "\n" in s2
                or any(p.lower() in s2.lower() for p in LAZY_PLACEHOLDER_PATTERNS)
            )
        ):
            file_path, content = s1, s2
        else:
            content, file_path = s1, s2

    findings: list[dict] = []
    low_content = content.lower()
    for pat in LAZY_PLACEHOLDER_PATTERNS:
        idx = low_content.find(pat.lower())
        if idx != -1:
            line_no = content[:idx].count("\n") + 1
            findings.append(
                {
                    "rule_id": "RULE-SLOP-LAZY-PLACEHOLDER",
                    "layer": "Layer 0.3 (Micro / Output-Enforcement)",
                    "severity": "ERROR",
                    "line": line_no,
                    "match": pat,
                    "pattern": pat,
                    "file": file_path,
                    "message": f"Detected forbidden lazy placeholder or AI slop tell: {pat!r}",
                }
            )
    return findings


def is_arbitrary_font_size_value(raw_bracket_val: str) -> bool:
    """Return True strictly when `text-[...]` bracket content represents a font-size length."""
    inner = raw_bracket_val.strip()
    if not inner:
        return False
    low = inner.lower()
    if low.startswith(
        (
            "color:",
            "var(",
            "#",
            "rgb(",
            "rgba(",
            "hsl(",
            "hsla(",
            "oklch(",
            "oklab(",
            "lch(",
            "lab(",
        )
    ):
        return False
    if low in (
        "balance",
        "pretty",
        "nowrap",
        "wrap",
        "left",
        "center",
        "right",
        "justify",
        "ellipsis",
        "clip",
    ):
        return False
    if low.startswith(("length:", "clamp(", "calc(")):
        return True
    return bool(_RE_DIMENSIONAL_LENGTH.match(inner))


def resolve_static_length_to_px(raw_val: str) -> Optional[float]:
    """Convert static `px`, `rem` (16px base), or `pt` (96/72) length to rounded px, else None."""
    cleaned = raw_val.strip()
    if cleaned.lower().startswith("length:"):
        cleaned = cleaned[7:].strip()
    m = _RE_STATIC_FONT_VALUE.match(cleaned)
    if not m:
        return None
    num = float(m.group(1))
    unit = (m.group(2) or "").lower()
    if num == 0.0:
        return 0.0
    if unit == "px":
        return round(num, 2)
    if unit == "rem":
        return round(num * 16.0, 2)
    if unit == "pt":
        return round(num * (96.0 / 72.0), 2)
    return None


def _strip_comments_preserving_newlines(content: str, ext: str) -> str:
    """Strip CSS/JS/HTML comments while keeping line numbers identical."""

    def _blank(match: re.Match) -> str:
        txt = match.group(0)
        return "".join("\n" if ch == "\n" else " " for ch in txt)

    out = content
    if ext in (".html", ".htm", ".jinja", ".jinja2"):
        out = re.sub(r"<!--.*?-->", _blank, out, flags=re.DOTALL)
    if ext in (".css", ".scss", ".js", ".jsx", ".ts", ".tsx"):
        out = re.sub(r"/\*.*?\*/", _blank, out, flags=re.DOTALL)
    if ext in (".js", ".jsx", ".ts", ".tsx"):
        # Strip full-line or trailing // comments (avoiding https:// URLs)
        out = re.sub(r"(?<![:\w])//[^\n]*", _blank, out)
    return out


def _split_font_family_stack(raw_stack: str) -> List[str]:
    """Split a CSS font-family declaration on top-level commas, ignoring var(...)."""
    parts: List[str] = []
    buf: List[str] = []
    depth = 0
    quote_ch: Optional[str] = None
    for ch in raw_stack:
        if quote_ch:
            buf.append(ch)
            if ch == quote_ch:
                quote_ch = None
        else:
            if ch in ("'", '"'):
                quote_ch = ch
                buf.append(ch)
            elif ch == "(":
                depth += 1
                buf.append(ch)
            elif ch == ")":
                depth = max(0, depth - 1)
                buf.append(ch)
            elif ch == "," and depth == 0:
                parts.append("".join(buf).strip())
                buf = []
            else:
                buf.append(ch)
    if buf:
        parts.append("".join(buf).strip())
    return parts


def extract_custom_font_families_from_stack(raw_stack: str) -> Dict[str, str]:
    """Return `{lowercase_key: canonical_display_name}` for custom non-system font families."""
    found: Dict[str, str] = {}
    cleaned_stack = re.sub(r"!important\b", "", raw_stack, flags=re.IGNORECASE).strip()
    for token in _split_font_family_stack(cleaned_stack):
        tok = token.strip()
        if not tok:
            continue
        low_tok = tok.lower()
        if (
            low_tok.startswith(("var(", "--", "$", "{", "env(", "calc("))
            or "(" in tok
            or ")" in tok
            or "/" in tok
        ):
            continue
        unquoted = tok.strip("'\"` ").strip()
        unquoted = " ".join(unquoted.split())
        if not unquoted:
            continue
        norm_key = unquoted.lower()
        if norm_key in SYSTEM_AND_GENERIC_FONTS:
            continue
        # Ignore synthetic CSS keywords / template placeholders
        if norm_key.startswith(("{{", "${")) or not re.search(r"[a-zA-Z]", unquoted):
            continue
        found.setdefault(norm_key, unquoted)
    return found


def _iter_opening_tags(
    content: str, tag_names: Tuple[str, ...]
) -> Iterable[Tuple[int, str, str]]:
    """Yield `(start_offset, tag_name, opening_tag_text)` with JSX `{...}` and quote awareness."""
    tag_pattern = re.compile(
        r"<(" + "|".join(re.escape(t) for t in tag_names) + r")(?=$|[\s/>])"
    )
    n = len(content)
    for m in tag_pattern.finditer(content):
        start = m.start()
        t_name = m.group(1)
        idx = m.end()
        brace_depth = 0
        quote_ch: Optional[str] = None
        while idx < n:
            ch = content[idx]
            if quote_ch:
                if ch == "\\":
                    idx += 2
                    continue
                if ch == quote_ch:
                    quote_ch = None
            else:
                if ch in ("'", '"', "`"):
                    quote_ch = ch
                elif ch == "{":
                    brace_depth += 1
                elif ch == "}":
                    brace_depth = max(0, brace_depth - 1)
                elif ch == ">" and brace_depth == 0:
                    yield start, t_name, content[start : idx + 1]
                    break
            idx += 1


@dataclass
class Violation:
    rule_id: str
    law_layer: str
    severity: str  # "ERROR", "WARNING"
    file_path: str
    line_number: int
    element_or_token: str
    message: str
    suggested_fix: str


@dataclass
class ValidationReport:
    total_files_scanned: int = 0
    passed: bool = True
    violations: List[Violation] = field(default_factory=list)
    score: float = 1.0

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity.upper() == "ERROR")

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity.upper() == "WARNING")


def hex_to_relative_luminance(hex_str: str) -> float:
    """Computes WCAG relative luminance from hex string (#RRGGBB)."""
    hex_clean = hex_str.strip().lstrip("#")
    if len(hex_clean) == 3:
        hex_clean = "".join(c * 2 for c in hex_clean)
    if len(hex_clean) != 6:
        return 0.0

    try:
        r = int(hex_clean[0:2], 16) / 255.0
        g = int(hex_clean[2:4], 16) / 255.0
        b = int(hex_clean[4:6], 16) / 255.0
    except ValueError:
        return 0.0

    def transform(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else math.pow((c + 0.055) / 1.055, 2.4)

    r_lin = transform(r)
    g_lin = transform(g)
    b_lin = transform(b)

    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def compute_contrast_ratio(hex1: str, hex2: str) -> float:
    """Computes WCAG contrast ratio between two hex colors."""
    lum1 = hex_to_relative_luminance(hex1)
    lum2 = hex_to_relative_luminance(hex2)
    l_bright = max(lum1, lum2)
    l_dark = min(lum1, lum2)
    return (l_bright + 0.05) / (l_dark + 0.05)


def check_stefbuilds_vibe_slop(content: str, file_path: str) -> List[Violation]:
    """Detect StefBuilds' 12 Vibe-Coded Slop Tells and Signup Friction Budget violations."""
    violations: List[Violation] = []

    # 1. RULE-SLOP-PURPLE-DOMINANCE
    purple_classes = re.findall(
        r"\b(?:bg|text|ring|border|from|to|via)-(?:purple|violet|indigo)-\d+\b", content
    )
    if len(purple_classes) >= 2:
        violations.append(
            Violation(
                rule_id="RULE-SLOP-PURPLE-DOMINANCE",
                law_layer="LAYER-0",
                severity="ERROR",
                file_path=file_path,
                line_number=1,
                element_or_token=" ".join(purple_classes[:3]),
                message="Vibe-coded slop tell: Excessive purple/violet/indigo dominance across hero/body.",
                suggested_fix="Use brand-specific neutral or intentional thematic color palette.",
            )
        )

    # 2. RULE-SLOP-HERO-GLOW-BLOB
    if re.search(
        r'class="[^"]*(?:blur-3xl|blur-2xl)[^"]*rounded-full[^"]*"', content
    ) or re.search(
        r'class="[^"]*rounded-full[^"]*(?:blur-3xl|blur-2xl)[^"]*"', content
    ):
        violations.append(
            Violation(
                rule_id="RULE-SLOP-HERO-GLOW-BLOB",
                law_layer="LAYER-0",
                severity="ERROR",
                file_path=file_path,
                line_number=1,
                element_or_token="blur-3xl rounded-full",
                message="Vibe-coded slop tell: Generic hero glow blob detected (blur-3xl rounded-full).",
                suggested_fix="Replace generic glow blob with authentic structured content or crisp illustration.",
            )
        )

    # 3. RULE-SLOP-BETA-PILL-COPY
    if re.search(
        r"\b(?:now in beta|public beta|join (?:the )?waitlist)\b", content, re.I
    ):
        violations.append(
            Violation(
                rule_id="RULE-SLOP-BETA-PILL-COPY",
                law_layer="LAYER-0",
                severity="ERROR",
                file_path=file_path,
                line_number=1,
                element_or_token="Now in beta",
                message="Vibe-coded slop tell: Generic beta pill badge copy ('Now in beta' / 'Join waitlist').",
                suggested_fix="State concrete product capability or omit synthetic beta badge.",
            )
        )

    # 4. RULE-SLOP-VAGUE-HERO-HEADLINE
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.I | re.S)
    if h1_match:
        h1_text = h1_match.group(1).lower()
        if (
            "all-in-one" in h1_text and ("platform" in h1_text or "workflow" in h1_text)
        ) or "empower your workflow" in h1_text:
            violations.append(
                Violation(
                    rule_id="RULE-SLOP-VAGUE-HERO-HEADLINE",
                    law_layer="LAYER-0",
                    severity="ERROR",
                    file_path=file_path,
                    line_number=1,
                    element_or_token=h1_match.group(0)[:80],
                    message="Vibe-coded slop tell: Vague headline using all-in-one platform cliché.",
                    suggested_fix="Craft specific, verifiable headline focused on primary user outcome.",
                )
            )

    # 5. RULE-SLOP-UNVERIFIED-VANITY-METRIC
    if re.search(
        r"\b(?:trusted|loved|used)\s+by\s+\d+[\d,]*\+?\s*(?:users|teams|companies|creators|developers|worldwide)",
        content,
        re.I,
    ):
        violations.append(
            Violation(
                rule_id="RULE-SLOP-UNVERIFIED-VANITY-METRIC",
                law_layer="LAYER-0",
                severity="ERROR",
                file_path=file_path,
                line_number=1,
                element_or_token="Trusted by 10,000+ users worldwide",
                message="Vibe-coded slop tell: Unverified vanity metric banner.",
                suggested_fix="Display real verifiable customer proofs, case studies, or omit vanity counter.",
            )
        )

    # 6. RULE-SLOP-BUILDER-ARTIFACT-AND-LEGAL-LINK
    if re.search(r'href=["\x27][^"\x27]*vite\.svg["\x27]', content, re.I) or re.search(
        r"\b(?:built with|made with|built on)\s+(?:lovable|v0|bolt|framer|bubble)\b",
        content,
        re.I,
    ):
        violations.append(
            Violation(
                rule_id="RULE-SLOP-BUILDER-ARTIFACT-AND-LEGAL-LINK",
                law_layer="LAYER-0",
                severity="ERROR",
                file_path=file_path,
                line_number=1,
                element_or_token="Builder artifact or badge detected",
                message="Vibe-coded slop tell: Default scaffolding artifact or builder badge detected.",
                suggested_fix="Replace default vite favicon with custom brand icon and remove platform builder tags.",
            )
        )

    # 7. RULE-L0-MACRO-SIGNUP-FRICTION-BUDGET
    for form_match in re.finditer(r"<form\b([^>]*)>(.*?)</form>", content, re.I | re.S):
        form_attrs = form_match.group(1).lower()
        form_inner = form_match.group(2)
        if any(kw in form_attrs for kw in ("signup", "sign-up", "register", "join")):
            inputs = re.findall(r"<input\b([^>]*)>", form_inner, re.I)
            visible_inputs = []
            for inp_attrs in inputs:
                type_match = re.search(
                    r'type=["\x27]([^"\x27]+)["\x27]', inp_attrs, re.I
                )
                inp_type = type_match.group(1).lower() if type_match else "text"
                if inp_type not in ("hidden", "submit", "button"):
                    visible_inputs.append(inp_attrs)
            if len(visible_inputs) > 2:
                violations.append(
                    Violation(
                        rule_id="RULE-L0-MACRO-SIGNUP-FRICTION-BUDGET",
                        law_layer="LAYER-0",
                        severity="ERROR",
                        file_path=file_path,
                        line_number=1,
                        element_or_token=f"Form fields count: {len(visible_inputs)} (budget: <=2)",
                        message=f"Signup friction budget exceeded: {len(visible_inputs)} fields (max allowed is 2).",
                        suggested_fix="Reduce initial signup form to email only or email + password; collect rest progressively.",
                    )
                )

    return violations


class Layer0Validator:
    """Deterministic Mechanical Validator for Layer 0 Laws."""

    def __init__(
        self,
        workspace_root: Optional[Path] = None,
        max_type_scale_steps: int = 8,
        max_font_families: int = 3,
        min_font_size_px: float = 11.0,
    ):
        self.workspace_root = workspace_root or Path.cwd()
        self.max_type_scale_steps = max_type_scale_steps
        self.max_font_families = max_font_families
        self.min_font_size_px = min_font_size_px

    @staticmethod
    def _should_skip_filename(filename: str) -> bool:
        low = filename.lower()
        if low == "routetree.gen.ts" or low.endswith(".d.ts"):
            return True
        if ".test." in low or ".spec." in low:
            return True
        return False

    def validate_file(self, file_path: Path) -> List[Violation]:
        violations: List[Violation] = []
        if not file_path.exists():
            return violations

        ext = file_path.suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            return violations

        content = file_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.splitlines()

        if ext in (".css", ".scss"):
            violations.extend(self._validate_css(file_path, lines))
            violations.extend(
                self._validate_typography_utilities_and_inline(
                    file_path, content, ext, check_css_props=False
                )
            )
        elif ext in (".html", ".htm", ".jinja", ".jinja2"):
            violations.extend(self._validate_html(file_path, lines, content))
            violations.extend(
                self._validate_typography_utilities_and_inline(
                    file_path, content, ext, check_css_props=False
                )
            )
            violations.extend(self._validate_mono_buttons(file_path, content))
            violations.extend(
                self._validate_flex_wrap_minw0_collapse(file_path, content)
            )
            violations.extend(check_stefbuilds_vibe_slop(content, str(file_path)))
        elif ext in (".js", ".jsx", ".ts", ".tsx"):
            violations.extend(self._validate_js(file_path, lines, content))
            violations.extend(
                self._validate_typography_utilities_and_inline(
                    file_path, content, ext, check_css_props=False
                )
            )
            violations.extend(self._validate_mono_buttons(file_path, content))
            if ext in (".jsx", ".tsx"):
                violations.extend(
                    self._validate_flex_wrap_minw0_collapse(file_path, content)
                )

        for _lv in check_lazy_placeholders(content, str(file_path)):
            violations.append(
                Violation(
                    rule_id=_lv.get("rule_id", "RULE-SLOP-LAZY-PLACEHOLDER"),
                    law_layer=_lv.get(
                        "layer", "Layer 0.3 (Micro / Output-Enforcement)"
                    ),
                    severity=_lv.get("severity", "ERROR"),
                    file_path=str(file_path),
                    line_number=int(_lv.get("line", 1)),
                    element_or_token=_lv.get("match", "lazy-placeholder"),
                    message=_lv.get("message", "Lazy truncation placeholder detected."),
                    suggested_fix="Emit complete implementation without truncation comments.",
                )
            )

        violations.extend(
            self._validate_kinetic_gsap_and_overdrive(file_path, content, ext)
        )
        violations.extend(
            self._validate_stageshow_firewall_and_craft(file_path, content, ext)
        )
        return violations

    def _validate_stageshow_firewall_and_craft(
        self, file_path: Path, content: str, ext: str
    ) -> List[Violation]:
        """Enforce v2.6.0 GW-UIUX-STAGE-FIREWALL-01 & StageShow Universal Optical/Kinetic Craft Rules (P=1)."""
        violations: List[Violation] = []
        if "layer0-ignore-stageshow" in content.lower():
            return violations

        stripped = _strip_comments_preserving_newlines(content, ext)
        is_stage = bool(
            re.search(
                r'(?:data-stage-ui\s*=\s*["\']true["\']|\bss-stage\b|<Stage\b)',
                stripped,
            )
        )

        if not is_stage:
            for m in re.finditer(
                r"(?:<(?:Cursor|MacPointer)\b|(?<![\w-])ss-cursor(?![\w-]))", stripped
            ):
                line_no = stripped[: m.start()].count("\n") + 1
                violations.append(
                    Violation(
                        rule_id="RULE-L0-STAGE-FIREWALL-DOM-CURSOR",
                        law_layer="GW-UIUX-STAGE-FIREWALL-01 (Stage Firewall)",
                        severity="ERROR",
                        file_path=str(file_path),
                        line_number=line_no,
                        element_or_token=m.group(0).strip()[:50],
                        message="Simulated DOM cursor (<Cursor>, <MacPointer>, .ss-cursor) leaked outside [data-stage-ui='true'] / .ss-stage.",
                        suggested_fix="Remove fake DOM pointers from production UI, or confine showcase scenes inside a [data-stage-ui='true'] container.",
                    )
                )

            for m in re.finditer(r"<Bar(?:\s+|/>|>)", stripped):
                line_no = stripped[: m.start()].count("\n") + 1
                violations.append(
                    Violation(
                        rule_id="RULE-L0-STAGE-FIREWALL-SKELETON-BAR",
                        law_layer="GW-UIUX-STAGE-FIREWALL-01 (Stage Firewall)",
                        severity="ERROR",
                        file_path=str(file_path),
                        line_number=line_no,
                        element_or_token=m.group(0).strip()[:50],
                        message="StageShow skeleton filler (<Bar>) leaked into production interface outside [data-stage-ui='true'].",
                        suggested_fix="Bind semantic production data in shipped interfaces; reserve <Bar> placeholders strictly for [data-stage-ui='true'] showcase stages.",
                    )
                )
        else:
            for m in re.finditer(r"<h[1-6]\b", stripped, re.I):
                line_no = stripped[: m.start()].count("\n") + 1
                violations.append(
                    Violation(
                        rule_id="RULE-L0-STAGE-FIREWALL-HEADING-LEAK",
                        law_layer="GW-UIUX-STAGE-FIREWALL-01 (Stage Firewall)",
                        severity="ERROR",
                        file_path=str(file_path),
                        line_number=line_no,
                        element_or_token=m.group(0).strip()[:50],
                        message="Semantic heading (<h1-h6>) inside [data-stage-ui='true'] / .ss-stage pollutes host document outline and accessibility tree.",
                        suggested_fix="Author faux window/card titles inside StageShow scenes using styled <div> or <span> elements.",
                    )
                )

        # Universal Craft Rule 1: RULE-L0-ICON-ONION-SKIN (Specimen #47 style-onion)
        for m in re.finditer(
            r'<(?:svg|path|circle|rect|line|polyline|polygon|g)\b[^>]*?\bstroke\s*=\s*["\'](?:#[0-9a-fA-F]{6}(?!ff|FF)[0-9a-fA-F]{2}|rgba\([^)]*,\s*0?\.\d+\s*\))["\']',
            stripped,
        ):
            line_no = stripped[: m.start()].count("\n") + 1
            violations.append(
                Violation(
                    rule_id="RULE-L0-ICON-ONION-SKIN",
                    law_layer="Layer 0.3 (Micro / Optical Craft)",
                    severity="ERROR",
                    file_path=str(file_path),
                    line_number=line_no,
                    element_or_token=m.group(0).strip()[:60],
                    message="Translucent SVG stroke ink creates darker 'onion skin' artifacts where vector strokes intersect (Specimen #47 style-onion).",
                    suggested_fix="Color SVG strokes with 100% opaque ink tokens (e.g., #9a9a9a or var(--ss-icon)) instead of translucent hex/rgba.",
                )
            )

        # Universal Craft Rule 2: RULE-L0-KINETIC-DASHED-RESIZE
        for block_match in re.finditer(
            r"(?:\{[^{}]*?\b(?:dashed|dotted)\b[^{}]*?\}|style\s*=\s*\{\{[^{}]*?\b(?:dashed|dotted)\b[^{}]*?\}\}|style\s*=\s*[\x22\x27][^\x22\x27]*?\b(?:dashed|dotted)\b[^\x22\x27]*?[\x22\x27])",
            stripped,
            re.I | re.S,
        ):
            block_txt = block_match.group(0)
            if re.search(
                r"\btransition(?:-property)?\b[^;}\n]*?\b(?:width|height|inline-size|block-size|all)\b",
                block_txt,
                re.I,
            ):
                line_no = stripped[: block_match.start()].count("\n") + 1
                violations.append(
                    Violation(
                        rule_id="RULE-L0-KINETIC-DASHED-RESIZE",
                        law_layer="Layer 0.3 (Micro / Kinetic Physics)",
                        severity="ERROR",
                        file_path=str(file_path),
                        line_number=line_no,
                        element_or_token=block_txt.strip()[:60],
                        message="Resizing an element with a dashed/dotted border causes dashes to crawl and shimmer across frames.",
                        suggested_fix="Use a solid hairline border during width/height transitions, or animate opacity/transform on a fixed-size SVG stroke.",
                    )
                )

        return violations

    def _validate_kinetic_gsap_and_overdrive(
        self, file_path: Path, content: str, ext: str
    ) -> List[Violation]:
        """Enforce v2.5.0 Kinetic Physics (Emil Kowalski), GSAP 3.13+ Lifecycle, Scroll-World Scrubbing & Overdrive Surface Gates."""
        violations: List[Violation] = []
        if "layer0-ignore-kinetic" in content.lower():
            return violations

        stripped = _strip_comments_preserving_newlines(content, ext)

        # 1. RULE-L0-KINETIC-SCALE-FLOOR: Ban scale(0) on UI entry/popover/dropdown/modal
        for m in re.finditer(
            r"(?:transform\s*:\s*[^;{}\"\'`]*?\bscale\(\s*0(?:\.0+)?\s*\)|\bscale-0\b)",
            stripped,
        ):
            line_no = stripped[: m.start()].count("\n") + 1
            line_txt = (
                content.splitlines()[line_no - 1]
                if line_no - 1 < len(content.splitlines())
                else ""
            )
            if (
                "layer0-ignore-scale-floor" not in line_txt.lower()
                and "sr-only" not in line_txt.lower()
            ):
                violations.append(
                    Violation(
                        rule_id="RULE-L0-KINETIC-SCALE-FLOOR",
                        law_layer="Layer 0.3 (Micro / Kinetic Physics)",
                        severity="ERROR",
                        file_path=str(file_path),
                        line_number=line_no,
                        element_or_token=m.group(0).strip()[:50],
                        message="UI element scales from 0 (Emil Kowalski Scale Floor violation). Elements should never inflate from nothing.",
                        suggested_fix="Start entry animations from scale(0.95) or scale(0.96) paired with opacity: 0.",
                    )
                )

        # 2. RULE-L0-KINETIC-NO-EASE-IN-UI: Ban pure ease-in or power*.in on interactive UI transitions
        for m in re.finditer(
            r"(?:transition(?:-timing-function)?\s*:\s*[^;{}\"\'`]*?\bease-in\b(?!-out)|\bease\s*:\s*['\"](?:power[1-4]|expo|quart|cubic|circ)\.in['\"])",
            stripped,
        ):
            line_no = stripped[: m.start()].count("\n") + 1
            violations.append(
                Violation(
                    rule_id="RULE-L0-KINETIC-NO-EASE-IN-UI",
                    law_layer="Layer 0.3 (Micro / Kinetic Physics)",
                    severity="WARNING",
                    file_path=str(file_path),
                    line_number=line_no,
                    element_or_token=m.group(0).strip()[:50],
                    message="ease-in timing detected on UI transition. ease-in starts slow and makes interactive controls feel sluggish.",
                    suggested_fix="Use ease-out or cubic-bezier(0.16, 1, 0.3, 1) (or cubic-bezier(0.32, 0.72, 0, 1) for drawers/sheets).",
                )
            )

        # 3. RULE-L0-GSAP-REACT-CLEANUP: Ban raw gsap.to/from/fromTo/timeline inside React useEffect without useGSAP or gsap.context
        if ext in (".jsx", ".tsx") and "gsap." in stripped and "useEffect" in stripped:
            if "useGSAP" not in stripped and "gsap.context" not in stripped:
                for m in re.finditer(
                    r"useEffect\s*\(\s*\(\s*\)\s*=>\s*\{[^}]*?\bgsap\.(?:to|from|fromTo|timeline)\s*\(",
                    stripped,
                    re.DOTALL,
                ):
                    line_no = stripped[: m.start()].count("\n") + 1
                    violations.append(
                        Violation(
                            rule_id="RULE-L0-GSAP-REACT-CLEANUP",
                            law_layer="Layer 0.3 (Micro / GSAP Lifecycle)",
                            severity="ERROR",
                            file_path=str(file_path),
                            line_number=line_no,
                            element_or_token="useEffect + gsap.*",
                            message="Raw GSAP tween inside React useEffect without useGSAP() or gsap.context() revert causes detached DOM leaks.",
                            suggested_fix="Use useGSAP(() => { ... }, { scope: containerRef }) from '@gsap/react' or wrap in gsap.context() with ctx.revert().",
                        )
                    )

        # 4. RULE-L0-GSAP-SCROLLTRIGGER-CONFLICT: Ban simultaneous scrub and toggleActions in scrollTrigger config
        for m in re.finditer(
            r"scrollTrigger\s*:\s*\{([^}]+)\}",
            stripped,
            re.DOTALL,
        ):
            st_body = m.group(1)
            if re.search(r"\bscrub\s*:", st_body) and re.search(
                r"\btoggleActions\s*:", st_body
            ):
                line_no = stripped[: m.start()].count("\n") + 1
                violations.append(
                    Violation(
                        rule_id="RULE-L0-GSAP-SCROLLTRIGGER-CONFLICT",
                        law_layer="Layer 0.3 (Micro / GSAP ScrollTrigger)",
                        severity="ERROR",
                        file_path=str(file_path),
                        line_number=line_no,
                        element_or_token="scrollTrigger: { scrub, toggleActions }",
                        message="ScrollTrigger declares both 'scrub' and 'toggleActions', which are mutually exclusive in GSAP.",
                        suggested_fix="Remove 'toggleActions' when using 'scrub', or remove 'scrub' for discrete threshold triggers.",
                    )
                )

        # 5. RULE-L0-SCROLL-VIDEO-SCRUB-SAFE: Require reduced-motion or !seeking guard when scrubbing video.currentTime
        if ".currentTime" in stripped and re.search(
            r"(?:scroll|ScrollTrigger|requestAnimationFrame)", stripped
        ):
            if ".seeking" not in stripped and "prefers-reduced-motion" not in stripped:
                m = re.search(r"\.currentTime\s*=", stripped)
                if m:
                    line_no = stripped[: m.start()].count("\n") + 1
                    violations.append(
                        Violation(
                            rule_id="RULE-L0-SCROLL-VIDEO-SCRUB-SAFE",
                            law_layer="Layer 0.4 (Meta / Scroll-World Scrub Safety)",
                            severity="ERROR",
                            file_path=str(file_path),
                            line_number=line_no,
                            element_or_token="video.currentTime = ...",
                            message="Scroll-scrubbed video mutates currentTime without a !video.seeking canvas frame guard or prefers-reduced-motion fallback.",
                            suggested_fix="Guard canvas drawImage with (!video.seeking && video.readyState >= 2), encode with 'ffmpeg -g 8 -an -movflags +faststart', and provide a prefers-reduced-motion poster fallback.",
                        )
                    )

        # 6. RULE-L0-OVERDRIVE-SURFACE-GATE: Ban WebGL / WebGPU shaders inside Operate or Read surface modes
        if re.search(
            r"data-surface-mode\s*=\s*['\"](?:operate|read)['\"]",
            stripped,
            re.IGNORECASE,
        ):
            m = re.search(
                r"(?:getContext\s*\(\s*['\"]webgl2?['\"]|navigator\.gpu\b|THREE\.WebGLRenderer)",
                stripped,
            )
            if m:
                line_no = stripped[: m.start()].count("\n") + 1
                violations.append(
                    Violation(
                        rule_id="RULE-L0-OVERDRIVE-SURFACE-GATE",
                        law_layer="Layer 0.2 (Meso / Surface Mode Gate)",
                        severity="ERROR",
                        file_path=str(file_path),
                        line_number=line_no,
                        element_or_token=m.group(0).strip()[:50],
                        message="WebGL/WebGPU shader initialized inside an 'Operate' or 'Read' surface mode container.",
                        suggested_fix="Restrict WebGL shaders strictly to data-surface-mode='experience' (Overdrive verb).",
                    )
                )

        return violations

    @staticmethod
    def _has_subminimum_opt_out(line: str, context_window: str = "") -> bool:
        combined = f"{line}\n{context_window}".lower()
        return "layer0-ignore-subminimum" in combined

    @staticmethod
    def _has_zero_font_opt_out(line: str, context_window: str = "") -> bool:
        combined = f"{line}\n{context_window}".lower()
        return "layer0-ignore-subminimum" in combined or "sr-only" in combined

    def _validate_typography_utilities_and_inline(
        self,
        file_path: Path,
        content: str,
        ext: str,
        check_css_props: bool = False,
    ) -> List[Violation]:
        """Validate arbitrary Tailwind text-size utilities and JSX/HTML inline font sizes."""
        violations: List[Violation] = []
        raw_lines = content.splitlines()
        stripped = _strip_comments_preserving_newlines(content, ext)
        stripped_lines = stripped.splitlines()

        # 1. Arbitrary Tailwind text-[...] length classes
        for idx, s_line in enumerate(stripped_lines, start=1):
            orig_line = raw_lines[idx - 1] if idx - 1 < len(raw_lines) else s_line
            for m in _RE_TW_ARBITRARY_TEXT.finditer(s_line):
                full_cls = m.group(1)
                bracket_val = m.group(2).strip()
                if not is_arbitrary_font_size_value(bracket_val):
                    continue
                if "layer0-ignore-arbitrary-text" not in orig_line.lower():
                    violations.append(
                        Violation(
                            rule_id="RULE-L0-MICRO-ARBITRARY-TEXT-SIZE",
                            law_layer="Layer 0.3 (Micro / Typography)",
                            severity="ERROR",
                            file_path=str(file_path),
                            line_number=idx,
                            element_or_token=full_cls,
                            message=(
                                f"Arbitrary Tailwind font-size utility '{full_cls}' bypasses the governed typography scale."
                            ),
                            suggested_fix=(
                                "Replace with a canonical scale utility (text-xs, text-sm, text-base, text-lg, text-xl, text-2xl) or semantic typography token."
                            ),
                        )
                    )
                px_equiv = resolve_static_length_to_px(bracket_val)
                if px_equiv is not None:
                    if px_equiv == 0.0:
                        if not self._has_zero_font_opt_out(orig_line):
                            violations.append(
                                Violation(
                                    rule_id="RULE-L0-MICRO-SUBMINIMUM-FONT",
                                    law_layer="Layer 0.3 (Micro / Typography)",
                                    severity="ERROR",
                                    file_path=str(file_path),
                                    line_number=idx,
                                    element_or_token=full_cls,
                                    message=(
                                        f"Zero font-size utility '{full_cls}' without explicit sr-only or 'layer0-ignore-subminimum' annotation."
                                    ),
                                    suggested_fix="Use standard 'sr-only' accessibility utility or upgrade to >= 11px.",
                                )
                            )
                    elif (
                        px_equiv < self.min_font_size_px
                        and not self._has_subminimum_opt_out(orig_line)
                    ):
                        violations.append(
                            Violation(
                                rule_id="RULE-L0-MICRO-SUBMINIMUM-FONT",
                                law_layer="Layer 0.3 (Micro / Typography)",
                                severity="ERROR",
                                file_path=str(file_path),
                                line_number=idx,
                                element_or_token=full_cls,
                                message=(
                                    f"Arbitrary micro-class '{full_cls}' resolves to {px_equiv:.2f}px, violating the {self.min_font_size_px:.0f}px (0.6875rem) screen legibility floor."
                                ),
                                suggested_fix="Upgrade to >= 11px ('text-xs' 12px recommended for badges/captions).",
                            )
                        )

        # 2. Inline JSX style={{ fontSize: ... }} in JS/JSX/TS/TSX
        if ext in (".js", ".jsx", ".ts", ".tsx"):
            for m in _RE_JSX_FONT_SIZE.finditer(stripped):
                line_no = stripped[: m.start()].count("\n") + 1
                orig_line = (
                    raw_lines[line_no - 1] if line_no - 1 < len(raw_lines) else ""
                )
                str_val, num_val = m.group(1), m.group(2)
                px_equiv: Optional[float] = None
                token_repr = m.group(0).strip()
                if num_val is not None:
                    px_equiv = round(float(num_val), 2)
                elif str_val is not None:
                    s_clean = str_val.strip()
                    if re.fullmatch(r"\d+(?:\.\d+)?", s_clean):
                        px_equiv = round(float(s_clean), 2)
                    else:
                        px_equiv = resolve_static_length_to_px(s_clean)
                if px_equiv is not None:
                    if px_equiv == 0.0:
                        if not self._has_zero_font_opt_out(orig_line):
                            violations.append(
                                Violation(
                                    rule_id="RULE-L0-MICRO-SUBMINIMUM-FONT",
                                    law_layer="Layer 0.3 (Micro / Typography)",
                                    severity="ERROR",
                                    file_path=str(file_path),
                                    line_number=line_no,
                                    element_or_token=token_repr,
                                    message="Inline JSX fontSize: 0 requires explicit 'sr-only' or 'layer0-ignore-subminimum'.",
                                    suggested_fix="Use sr-only utility or set fontSize >= 11px.",
                                )
                            )
                    elif (
                        px_equiv < self.min_font_size_px
                        and not self._has_subminimum_opt_out(orig_line)
                    ):
                        violations.append(
                            Violation(
                                rule_id="RULE-L0-MICRO-SUBMINIMUM-FONT",
                                law_layer="Layer 0.3 (Micro / Typography)",
                                severity="ERROR",
                                file_path=str(file_path),
                                line_number=line_no,
                                element_or_token=token_repr,
                                message=(
                                    f"Inline JSX '{token_repr}' resolves to {px_equiv:.2f}px (< {self.min_font_size_px:.0f}px universal legibility minimum)."
                                ),
                                suggested_fix="Upgrade fontSize to >= 11px (0.6875rem) or use governed typography classes.",
                            )
                        )

        # 3. HTML inline style="... font-size: ... " in HTML/Jinja/JSX
        if ext in (".html", ".htm", ".jinja", ".jinja2", ".js", ".jsx", ".ts", ".tsx"):
            for sm in _RE_HTML_INLINE_STYLE.finditer(stripped):
                style_body = (
                    sm.group(1) if sm.group(1) is not None else (sm.group(2) or "")
                )
                base_line = stripped[: sm.start()].count("\n") + 1
                orig_line = (
                    raw_lines[base_line - 1] if base_line - 1 < len(raw_lines) else ""
                )
                for fm in _RE_CSS_FONT_SIZE.finditer(style_body):
                    raw_fval = fm.group(1).strip()
                    px_equiv = resolve_static_length_to_px(raw_fval)
                    if px_equiv is None:
                        continue
                    if px_equiv == 0.0:
                        if not self._has_zero_font_opt_out(orig_line, sm.group(0)):
                            violations.append(
                                Violation(
                                    rule_id="RULE-L0-MICRO-SUBMINIMUM-FONT",
                                    law_layer="Layer 0.3 (Micro / Typography)",
                                    severity="ERROR",
                                    file_path=str(file_path),
                                    line_number=base_line,
                                    element_or_token=f"font-size: {raw_fval}",
                                    message="Inline style 'font-size: 0' without sr-only or 'layer0-ignore-subminimum'.",
                                    suggested_fix="Add sr-only semantics or increase font-size to >= 11px.",
                                )
                            )
                    elif (
                        px_equiv < self.min_font_size_px
                        and not self._has_subminimum_opt_out(orig_line, sm.group(0))
                    ):
                        violations.append(
                            Violation(
                                rule_id="RULE-L0-MICRO-SUBMINIMUM-FONT",
                                law_layer="Layer 0.3 (Micro / Typography)",
                                severity="ERROR",
                                file_path=str(file_path),
                                line_number=base_line,
                                element_or_token=f"font-size: {raw_fval}",
                                message=(
                                    f"Inline style 'font-size: {raw_fval}' ({px_equiv:.2f}px) violates the {self.min_font_size_px:.0f}px minimum floor."
                                ),
                                suggested_fix="Upgrade font-size to >= 11px (0.6875rem / 8.25pt).",
                            )
                        )

        return violations

    def _validate_mono_buttons(self, file_path: Path, content: str) -> List[Violation]:
        """Flag `<button>` or `<Btn>` elements whose `class` or `className` includes `font-mono`."""
        violations: List[Violation] = []
        raw_lines = content.splitlines()
        ext = file_path.suffix.lower()
        stripped = _strip_comments_preserving_newlines(content, ext)

        class_attr_re = re.compile(
            r"""\b(?:class|className)\s*=\s*(?:"([^"]*)"|'([^']*)'|\{([^}]*)\})""",
            re.DOTALL,
        )
        mono_token_re = re.compile(r"(?<![\w-])(?:[a-z0-9-]+:)*!?font-mono(?![\w-])")

        for start_pos, tag_name, tag_text in _iter_opening_tags(
            stripped, ("button", "Btn")
        ):
            line_no = stripped[:start_pos].count("\n") + 1
            prev_line = (
                raw_lines[line_no - 2]
                if line_no >= 2 and (line_no - 2) < len(raw_lines)
                else ""
            )
            cur_line = raw_lines[line_no - 1] if (line_no - 1) < len(raw_lines) else ""
            raw_tag_slice = content[start_pos : start_pos + len(tag_text)]
            opt_out_ctx = f"{prev_line}\n{cur_line}\n{raw_tag_slice}".lower()
            if (
                "data-mono-allowed" in opt_out_ctx
                or "layer0-ignore-mono" in opt_out_ctx
            ):
                continue

            for cm in class_attr_re.finditer(tag_text):
                attr_body = cm.group(1) or cm.group(2) or cm.group(3) or ""
                if mono_token_re.search(attr_body):
                    violations.append(
                        Violation(
                            rule_id="RULE-L0-MICRO-MONO-OVERUSE",
                            law_layer="Layer 0.3 (Micro / Typography)",
                            severity="ERROR",
                            file_path=str(file_path),
                            line_number=line_no,
                            element_or_token=f"<{tag_name} ... font-mono>",
                            message=(
                                f"Interactive <{tag_name}> applies 'font-mono'. Monospace typography is reserved for tabular IDs, code, HINs, and timestamps—not action buttons."
                            ),
                            suggested_fix=(
                                "Remove 'font-mono' from <button>/<Btn> (use body sans-serif font) or add 'data-mono-allowed' if rendering a literal code token trigger."
                            ),
                        )
                    )
                    break

        return violations

    def _validate_flex_wrap_minw0_collapse(
        self, file_path: Path, content: str
    ) -> List[Violation]:
        """Flag single elements combining `flex-wrap`, `flex-1`, and `min-w-0` without an explicit width floor."""
        violations: List[Violation] = []
        raw_lines = content.splitlines()
        ext = file_path.suffix.lower()
        stripped = _strip_comments_preserving_newlines(content, ext)

        tag_open_re = re.compile(r"<([A-Za-z][A-Za-z0-9_.:-]*)(?=[\s/>])")
        class_attr_re = re.compile(
            r"""\b(?:class|className)\s*=\s*(?:"([^"]*)"|'([^']*)'|\{)""",
            re.DOTALL,
        )
        re_flex_wrap = re.compile(
            r"(?<![\w-])(?:[a-z0-9-]+:)*!?flex-wrap(?:-reverse)?(?![\w-])"
        )
        re_flex_1 = re.compile(r"(?<![\w-])(?:[a-z0-9-]+:)*!?flex-1(?![\w-])")
        re_min_w_0 = re.compile(r"(?<![\w-])(?:[a-z0-9-]+:)*!?min-w-0(?![\w-])")
        re_explicit_floor = re.compile(
            r"(?<![\w-])(?:[a-z0-9-]+:)*!?(?:"
            r"basis-(?!0(?![\w-]))[a-z0-9\[\]./%-]+|"
            r"min-w-\[(?!0(?:px|%|rem|em)?\])[^\]]+\]|"
            r"min-w-full(?![\w-])|"
            r"w-full(?![\w-])"
            r")"
        )

        n = len(stripped)
        for m in tag_open_re.finditer(stripped):
            start_pos = m.start()
            tag_name = m.group(1)
            idx = m.end()
            brace_depth = 0
            quote_ch: Optional[str] = None
            end_pos: Optional[int] = None
            while idx < n:
                ch = stripped[idx]
                if quote_ch:
                    if ch == "\\":
                        idx += 2
                        continue
                    if ch == quote_ch:
                        quote_ch = None
                else:
                    if ch in ("'", '"', "`"):
                        quote_ch = ch
                    elif ch == "{":
                        brace_depth += 1
                    elif ch == "}":
                        brace_depth = max(0, brace_depth - 1)
                    elif ch == ">" and brace_depth == 0:
                        end_pos = idx + 1
                        break
                idx += 1
            if end_pos is None:
                continue

            tag_text = stripped[start_pos:end_pos]
            if "class" not in tag_text:
                continue

            line_no = stripped[:start_pos].count("\n") + 1
            prev_line = (
                raw_lines[line_no - 2]
                if line_no >= 2 and (line_no - 2) < len(raw_lines)
                else ""
            )
            cur_line = raw_lines[line_no - 1] if (line_no - 1) < len(raw_lines) else ""
            raw_tag_slice = content[start_pos:end_pos]
            opt_out_ctx = f"{prev_line}\n{cur_line}\n{raw_tag_slice}".lower()
            if (
                "data-allow-flex-collapse" in opt_out_ctx
                or "layer0-ignore-flex-collapse" in opt_out_ctx
            ):
                continue

            for cm in class_attr_re.finditer(tag_text):
                if cm.group(1) is not None:
                    attr_body = cm.group(1)
                elif cm.group(2) is not None:
                    attr_body = cm.group(2)
                else:
                    b_idx = cm.end()
                    b_depth = 1
                    q_ch: Optional[str] = None
                    while b_idx < len(tag_text) and b_depth > 0:
                        c = tag_text[b_idx]
                        if q_ch:
                            if c == "\\":
                                b_idx += 2
                                continue
                            if c == q_ch:
                                q_ch = None
                        else:
                            if c in ("'", '"', "`"):
                                q_ch = c
                            elif c == "{":
                                b_depth += 1
                            elif c == "}":
                                b_depth -= 1
                        b_idx += 1
                    attr_body = tag_text[cm.end() : max(cm.end(), b_idx - 1)]

                if (
                    re_flex_wrap.search(attr_body)
                    and re_flex_1.search(attr_body)
                    and re_min_w_0.search(attr_body)
                    and not re_explicit_floor.search(attr_body)
                ):
                    violations.append(
                        Violation(
                            rule_id="RULE-L0-MICRO-FLEX-WRAP-MINW0-COLLAPSE",
                            law_layer="Layer 0.3 (Micro / Responsive Flexbox)",
                            severity="ERROR",
                            file_path=str(file_path),
                            line_number=line_no,
                            element_or_token=f"<{tag_name} ... flex-wrap flex-1 min-w-0>",
                            message=(
                                f"<{tag_name}> combines 'flex-wrap', 'flex-1', and 'min-w-0' without an explicit non-zero basis or width floor, collapsing sub-content width instead of wrapping sibling controls."
                            ),
                            suggested_fix=(
                                "Add an explicit floor ('min-w-[280px]', 'basis-full sm:basis-auto', 'min-w-full', or 'w-full') or remove 'min-w-0' so outer flex-wrap wraps cleanly."
                            ),
                        )
                    )
                    break

        return violations

    def _validate_css(self, file_path: Path, lines: List[str]) -> List[Violation]:
        violations: List[Violation] = []
        full_css = "\n".join(lines)
        is_deck_or_print = any(
            k in full_css for k in ("@page", ".slide", "canvas-frame")
        )
        stripped_css = _strip_comments_preserving_newlines(full_css, ".css")
        stripped_lines = stripped_css.splitlines()

        # Map line -> enclosing selector/comment context for sr-only / opt-out checks
        enclosing_context_by_line: Dict[int, str] = {}
        for bm in re.finditer(r"([^{}]+)\{([^{}]*)\}", full_css, re.DOTALL):
            b_start_line = full_css[: bm.start()].count("\n") + 1
            b_end_line = full_css[: bm.end()].count("\n") + 1
            ctx_txt = bm.group(0)
            for ln in range(b_start_line, b_end_line + 1):
                enclosing_context_by_line[ln] = ctx_txt

        for idx, line in enumerate(lines, start=1):
            s_line = stripped_lines[idx - 1] if idx - 1 < len(stripped_lines) else line
            block_ctx = enclosing_context_by_line.get(idx, "")

            # 1. Check Sub-pixel decimal values
            subpixel_match = re.search(r":\s*([0-9]+\.[0-9]+)px", s_line)
            if subpixel_match:
                val = subpixel_match.group(1)
                violations.append(
                    Violation(
                        rule_id="RULE-L0-MICRO-SUBPIXEL",
                        law_layer="Layer 0.3 (Micro)",
                        severity="WARNING",
                        file_path=str(file_path),
                        line_number=idx,
                        element_or_token=subpixel_match.group(0),
                        message=f"Sub-pixel value {val}px causes rendering blurriness.",
                        suggested_fix="Round to integer pixel multiple (4px or 8px).",
                    )
                )

            # 2. Check 8pt grid on fixed paddings/margins/gaps
            spacing_match = re.search(r"(?:padding|margin|gap):\s*([0-9]+)px", s_line)
            if spacing_match:
                px_val = int(spacing_match.group(1))
                if px_val > 0 and px_val not in (
                    4,
                    8,
                    12,
                    16,
                    20,
                    24,
                    32,
                    40,
                    48,
                    64,
                    80,
                    96,
                ):
                    if px_val % 8 != 0 and px_val % 4 != 0:
                        violations.append(
                            Violation(
                                rule_id="RULE-L0-MICRO-8PT-GRID",
                                law_layer="Layer 0.3 (Micro)",
                                severity="WARNING",
                                file_path=str(file_path),
                                line_number=idx,
                                element_or_token=f"{px_val}px",
                                message=f"Spacing value {px_val}px violates 8pt grid token rhythm.",
                                suggested_fix=f"Use standard token multiple: {round(px_val / 8) * 8}px or var(--tsy-space-*).",
                            )
                        )

            # 3. Check hardcoded button height < 44px
            height_match = re.search(
                r"(?:btn|button|touch)[^{;]*?(?:height|min-height):\s*([0-9]+)px",
                s_line,
                re.IGNORECASE,
            )
            if height_match:
                h_val = int(height_match.group(1))
                if h_val < 44:
                    violations.append(
                        Violation(
                            rule_id="RULE-L0-MICRO-FITTS-LAW",
                            law_layer="Layer 0.3 (Micro)",
                            severity="ERROR",
                            file_path=str(file_path),
                            line_number=idx,
                            element_or_token=f"{h_val}px",
                            message=f"Interactive target height {h_val}px violates Fitts's Law (< 44px).",
                            suggested_fix="Increase min-height to >= 44px or add padding.",
                        )
                    )

            # 4. Check Root Margin on Reusable Component Selectors (Component Layout Agnosticism)
            margin_match = re.search(
                r"^\s*\.(?:card|vcard|kcard|btn|chip|badge|table)\b[^{]*\{[^}]*?\bmargin(?:-top|-bottom|-left|-right)?:\s*([0-9]+px|[0-9]+%)\b",
                s_line,
                re.IGNORECASE,
            )
            if margin_match:
                val = margin_match.group(1)
                if val not in ("0px", "0"):
                    violations.append(
                        Violation(
                            rule_id="RULE-L0-MICRO-ZERO-ROOT-MARGIN",
                            law_layer="Layer 0.3 (Micro)",
                            severity="WARNING",
                            file_path=str(file_path),
                            line_number=idx,
                            element_or_token=margin_match.group(0),
                            message=f"Reusable component defines root margin {val}. Violates Component Layout Agnosticism.",
                            suggested_fix="Remove root margins; delegate spacing to parent layout primitives (Stack, Cluster, Grid).",
                        )
                    )

            # 5. RULE-L0-MICRO-SUBMINIMUM-FONT:
            #    - Presentation Decks / Print (@page / .slide / canvas-frame): < 8.0pt (10.67px)
            #    - Universal Web/App Screen CSS: < 11.0px (0.6875rem at 16px root, 8.25pt)
            for fm in _RE_CSS_FONT_SIZE.finditer(s_line):
                raw_fval = fm.group(1).strip()
                px_equiv = resolve_static_length_to_px(raw_fval)
                if px_equiv is None:
                    continue
                if px_equiv == 0.0:
                    if not self._has_zero_font_opt_out(line, block_ctx):
                        violations.append(
                            Violation(
                                rule_id="RULE-L0-MICRO-SUBMINIMUM-FONT",
                                law_layer="Layer 0.3 (Micro / Typography)",
                                severity="ERROR",
                                file_path=str(file_path),
                                line_number=idx,
                                element_or_token=f"font-size: {raw_fval}",
                                message="CSS 'font-size: 0' without explicit '.sr-only' or '/* layer0-ignore-subminimum */' opt-out.",
                                suggested_fix="Couple font-size: 0 with .sr-only / layer0-ignore-subminimum or set >= 11px.",
                            )
                        )
                    continue

                if self._has_subminimum_opt_out(line, block_ctx):
                    continue

                if is_deck_or_print:
                    pt_match = re.match(r"^([0-9.]+)\s*pt\b", raw_fval, re.IGNORECASE)
                    if pt_match and float(pt_match.group(1)) < 8.0:
                        pt_val = float(pt_match.group(1))
                        violations.append(
                            Violation(
                                rule_id="RULE-L0-MICRO-SUBMINIMUM-FONT",
                                law_layer="Layer 0.3 (Micro / Typography)",
                                severity="ERROR",
                                file_path=str(file_path),
                                line_number=idx,
                                element_or_token=f"{pt_val}pt",
                                message=f"Font size {pt_val}pt violates presentation deck floor (< 8.0pt). Creates unreadable micro-text.",
                                suggested_fix="Upgrade font-size to >= 8.5pt (body 9-10.5pt, titles 11-13pt, KPIs 20-32pt).",
                            )
                        )
                    elif not pt_match and px_equiv < 10.67:
                        violations.append(
                            Violation(
                                rule_id="RULE-L0-MICRO-SUBMINIMUM-FONT",
                                law_layer="Layer 0.3 (Micro / Typography)",
                                severity="ERROR",
                                file_path=str(file_path),
                                line_number=idx,
                                element_or_token=raw_fval,
                                message=f"Font size {raw_fval} ({px_equiv:.2f}px) violates presentation deck floor (< 10.67px / 8.0pt).",
                                suggested_fix="Upgrade font-size to >= 11px (body 12-14px, titles 15-18px, KPIs 28-44px).",
                            )
                        )
                else:
                    if px_equiv < self.min_font_size_px:
                        violations.append(
                            Violation(
                                rule_id="RULE-L0-MICRO-SUBMINIMUM-FONT",
                                law_layer="Layer 0.3 (Micro / Typography)",
                                severity="ERROR",
                                file_path=str(file_path),
                                line_number=idx,
                                element_or_token=f"font-size: {raw_fval}",
                                message=(
                                    f"Font size '{raw_fval}' ({px_equiv:.2f}px) violates the universal {self.min_font_size_px:.0f}px (0.6875rem / 8.25pt) web/app screen minimum."
                                ),
                                suggested_fix="Upgrade font-size to >= 11px (0.75rem / 12px recommended for compact metadata).",
                            )
                        )

        # 6. Check Layout Slot Anti-Blowout Invariant
        if ".tsy-slot" in full_css or ".tsy-split" in full_css:
            if not re.search(r"min-inline-size:\s*0|min-width:\s*0", full_css):
                violations.append(
                    Violation(
                        rule_id="RULE-L0-MICRO-ANTI-BLOWOUT",
                        law_layer="Layer 0.3 (Micro)",
                        severity="ERROR",
                        file_path=str(file_path),
                        line_number=1,
                        element_or_token="Layout Engine Slot",
                        message="Layout slot missing 'min-inline-size: 0' or 'min-width: 0'. Triggers content blowout bug in flex/grid.",
                        suggested_fix="Add 'min-inline-size: 0; min-width: 0;' to .tsy-slot and layout primitive children.",
                    )
                )

        # === ANTI-SLOP SUITE (ENGINE B - CSS) ===
        css_blocks = list(re.finditer(r"([^{]+)\{([^}]+)\}", stripped_css))

        # A1. Hairline Border + Wide Fuzzy Shadow (blur >= 24px)
        re_hairline = re.compile(
            r"(?:border|border-(?:top|right|bottom|left)):\s*(?:0\.[0-9]+|1)px\s+solid\b",
            re.IGNORECASE,
        )
        re_wide_shadow = re.compile(
            r"(?:box-shadow:\s*|,\s*)(?:inset\s+)?(?:-?[0-9]+(?:px)?\s+){2}([2-9][0-9]|[1-9][0-9]{2,})px\b",
            re.IGNORECASE,
        )
        shadow_matched = False
        for b in css_blocks:
            body = b.group(2)
            if re_hairline.search(body) and re_wide_shadow.search(body):
                line_no = stripped_css[: b.start()].count("\n") + 1
                violations.append(
                    Violation(
                        rule_id="RULE-SLOP-HAIRLINE-WIDE-SHADOW",
                        law_layer="Layer 0.3 (Micro / Anti-Slop)",
                        severity="WARNING",
                        file_path=str(file_path),
                        line_number=line_no,
                        element_or_token=b.group(1).strip()[:50],
                        message="Hairline border (<=1px) paired with wide diffuse shadow (blur >=24px). Universal AI design signature.",
                        suggested_fix="Commit to one: use a clean crisp border with zero shadow, or soft elevation with zero border.",
                    )
                )
                shadow_matched = True
        if (
            not shadow_matched
            and re_hairline.search(stripped_css)
            and re_wide_shadow.search(stripped_css)
        ):
            violations.append(
                Violation(
                    rule_id="RULE-SLOP-HAIRLINE-WIDE-SHADOW",
                    law_layer="Layer 0.3 (Micro / Anti-Slop)",
                    severity="WARNING",
                    file_path=str(file_path),
                    line_number=1,
                    element_or_token="Hairline border + wide shadow",
                    message="Hairline border (<=1px) paired with wide diffuse shadow (blur >=24px). Universal AI design signature.",
                    suggested_fix="Commit to one: use a clean crisp border with zero shadow, or soft elevation with zero border.",
                )
            )

        # A2. Side-Tab Accent Border on Rounded Elements (radius >= 4px)
        re_side_border = re.compile(
            r"(?:border-(?:left|right|top|bottom)):\s*([3-9]|1[0-2])px\s+solid\s+([^;{}]+)",
            re.IGNORECASE,
        )
        re_radius = re.compile(r"border-radius:\s*([4-9]|[1-9][0-9]+)px", re.IGNORECASE)
        for b in css_blocks:
            sel = b.group(1).strip()
            body = b.group(2)
            side_m = re_side_border.search(body)
            rad_m = re_radius.search(body)
            if side_m and rad_m:
                line_no = stripped_css[: b.start()].count("\n") + 1
                violations.append(
                    Violation(
                        rule_id="RULE-SLOP-SIDE-TAB",
                        law_layer="Layer 0.3 (Micro / Anti-Slop)",
                        severity="ERROR",
                        file_path=str(file_path),
                        line_number=line_no,
                        element_or_token=sel[:50],
                        message=f"Thick side-tab accent border ({side_m.group(1)}px) on rounded card container ({rad_m.group(1)}px). Prominent AI template tell.",
                        suggested_fix="Remove the side border or eliminate border-radius. Use background tinting or a subtle status icon instead.",
                    )
                )

        # A3. AI Beige / Warm Cream Surface Reflex
        re_cream = re.compile(
            r"(?:background|background-color):\s*(#(?:fcfbf9|fbf7ee|fdfcf7|f5f2eb|faf8f5|fbf8f1|f7f4ed))\b",
            re.IGNORECASE,
        )
        for b in css_blocks:
            sel = b.group(1).strip().lower()
            body = b.group(2)
            m = re_cream.search(body)
            if m and any(
                k in sel
                for k in (
                    "body",
                    "html",
                    ":root",
                    ".page",
                    "main",
                    "canvas",
                    "container",
                )
            ):
                line_no = stripped_css[: b.start()].count("\n") + 1
                violations.append(
                    Violation(
                        rule_id="RULE-SLOP-AI-BEIGE",
                        law_layer="Layer 0.3 (Micro / Anti-Slop)",
                        severity="WARNING",
                        file_path=str(file_path),
                        line_number=line_no,
                        element_or_token=m.group(1),
                        message=f"Warm cream/beige surface ({m.group(1)}) detected as root background. High-frequency AI fallback aesthetic.",
                        suggested_fix="Use deliberate project brand tokens or clean neutral canvas rather than default AI off-white.",
                    )
                )

        # A4. Canonical AI Violet/Purple Palette and Gradient Text
        purple_hexes = {
            "7c3aed",
            "8b5cf6",
            "a855f7",
            "9333ea",
            "7e22ce",
            "6d28d9",
            "6366f1",
        }
        re_purple = re.compile(r"#(?:" + "|".join(purple_hexes) + r")\b", re.IGNORECASE)
        re_bg_clip = re.compile(r"(?:-webkit-)?background-clip:\s*text", re.IGNORECASE)
        grad_text_matched = False
        for b in css_blocks:
            body = b.group(2)
            if re_bg_clip.search(body) and "linear-gradient" in body.lower():
                line_no = stripped_css[: b.start()].count("\n") + 1
                violations.append(
                    Violation(
                        rule_id="RULE-SLOP-GRADIENT-TEXT",
                        law_layer="Layer 0.3 (Micro / Anti-Slop)",
                        severity="ERROR",
                        file_path=str(file_path),
                        line_number=line_no,
                        element_or_token="background-clip: text + linear-gradient",
                        message="Gradient text detected on headings/metrics. High-frequency AI aesthetic crutch.",
                        suggested_fix="Use solid, high-contrast text color (WCAG AA >= 4.5:1).",
                    )
                )
                grad_text_matched = True
        if (
            not grad_text_matched
            and re_bg_clip.search(stripped_css)
            and "linear-gradient" in stripped_css.lower()
        ):
            violations.append(
                Violation(
                    rule_id="RULE-SLOP-GRADIENT-TEXT",
                    law_layer="Layer 0.3 (Micro / Anti-Slop)",
                    severity="ERROR",
                    file_path=str(file_path),
                    line_number=1,
                    element_or_token="background-clip: text + linear-gradient",
                    message="Gradient text detected on headings/metrics. High-frequency AI aesthetic crutch.",
                    suggested_fix="Use solid, high-contrast text color (WCAG AA >= 4.5:1).",
                )
            )
        for idx, s_line in enumerate(stripped_lines, start=1):
            m = re_purple.search(s_line)
            if m and "gradient" in s_line.lower():
                violations.append(
                    Violation(
                        rule_id="RULE-SLOP-AI-PALETTE",
                        law_layer="Layer 0.3 (Micro / Anti-Slop)",
                        severity="WARNING",
                        file_path=str(file_path),
                        line_number=idx,
                        element_or_token=m.group(0),
                        message=f"Canonical AI purple/violet gradient color {m.group(0)} detected.",
                        suggested_fix="Adopt deliberate project brand palette (e.g. obsidian slate or champagne bronze).",
                    )
                )

        # A5. Decorative Pulsing Dots & Bounce Easing
        re_pulse = re.compile(
            r"(?:animation|animation-name):\s*[^;{}]*\b(?:pulse|ping)\b", re.IGNORECASE
        )
        re_bounce = re.compile(
            r"(?:animation-timing-function|transition-timing-function):\s*[^;{}]*\b(?:bounce|elastic)\b|cubic-bezier\([^)]*,\s*(?:1\.[1-9]|[2-9]\.)",
            re.IGNORECASE,
        )
        for idx, s_line in enumerate(stripped_lines, start=1):
            if re_pulse.search(s_line):
                violations.append(
                    Violation(
                        rule_id="RULE-SLOP-PULSING-DOT",
                        law_layer="Layer 0.3 (Micro / Anti-Slop)",
                        severity="WARNING",
                        file_path=str(file_path),
                        line_number=idx,
                        element_or_token="pulse animation",
                        message="Decorative pulsing status dot detected without live telemetry binding.",
                        suggested_fix="Use a clean, static status indicator with clear descriptive text.",
                    )
                )
            if re_bounce.search(s_line):
                violations.append(
                    Violation(
                        rule_id="RULE-SLOP-BOUNCE-EASING",
                        law_layer="Layer 0.3 (Micro / Anti-Slop)",
                        severity="WARNING",
                        file_path=str(file_path),
                        line_number=idx,
                        element_or_token="bounce/elastic easing",
                        message="Bounce/elastic easing feels dated and gimmicky.",
                        suggested_fix="Use smooth exponential deceleration: cubic-bezier(0.16, 1, 0.3, 1).",
                    )
                )

        # A6. Hover Card Lift & Shadow Bloom
        for b in css_blocks:
            body = b.group(2)
            sel = b.group(1).strip()
            if (
                ":hover" in sel
                and ("translateY(-" in body or "scale(" in body)
                and "box-shadow:" in body
            ):
                line_no = stripped_css[: b.start()].count("\n") + 1
                violations.append(
                    Violation(
                        rule_id="RULE-SLOP-HOVER-CARD-LIFT",
                        law_layer="Layer 0.3 (Micro / Anti-Slop)",
                        severity="WARNING",
                        file_path=str(file_path),
                        line_number=line_no,
                        element_or_token=sel[:50],
                        message="Ubiquitous hover lift (translateY) paired with shadow bloom. Generic kinetic AI tell.",
                        suggested_fix="Reserve hover lift strictly for interactive drag-and-drop or clickable elements.",
                    )
                )

        # A7. Neon Cyberpunk Border Glow
        re_neon_glow = re.compile(
            r"box-shadow:\s*(?:inset\s+)?0\s+0\s+([1-9][0-9]+px)\s+(#(?:00f|0ff|f0f|06b6d4|a855f7|3b82f6|8b5cf6)|rgba?\(\s*(?:0|59|124|139|168)\b)",
            re.IGNORECASE,
        )
        for idx, s_line in enumerate(stripped_lines, start=1):
            m = re_neon_glow.search(s_line)
            if m:
                violations.append(
                    Violation(
                        rule_id="RULE-SLOP-NEON-BORDER-GLOW",
                        law_layer="Layer 0.3 (Micro / Anti-Slop)",
                        severity="WARNING",
                        file_path=str(file_path),
                        line_number=idx,
                        element_or_token=m.group(0)[:50],
                        message="Saturated neon glow shadow detected. Cyberpunk gimmick masking layout emptiness.",
                        suggested_fix="Use crisp 1px neutral border (rgba(255,255,255,0.08) or oklch border) with natural directional shadow.",
                    )
                )

        # A8. Excessive Glassmorphism Backdrop Blur (>= 20px)
        re_heavy_blur = re.compile(
            r"backdrop-filter:\s*blur\(\s*([2-9][0-9]|[1-9][0-9]{2,})px\s*\)",
            re.IGNORECASE,
        )
        for idx, s_line in enumerate(stripped_lines, start=1):
            m = re_heavy_blur.search(s_line)
            if m:
                violations.append(
                    Violation(
                        rule_id="RULE-SLOP-GLASSMORPHISM-BLUR-EXTREME",
                        law_layer="Layer 0.3 (Micro / Anti-Slop)",
                        severity="WARNING",
                        file_path=str(file_path),
                        line_number=idx,
                        element_or_token=f"{m.group(1)}px blur",
                        message=f"Excessive backdrop blur ({m.group(1)}px) creates GPU strain and illegible text.",
                        suggested_fix="Use opaque card background or subtle blur (<=12px) with crisp 1px border.",
                    )
                )

        # A9. Keyboard Focus Trapping (outline: none on :focus without custom ring)
        for b in css_blocks:
            sel = b.group(1).strip()
            body = b.group(2)
            if (
                ":focus" in sel
                and re.search(r"outline:\s*(?:none|0)\b", body, re.IGNORECASE)
                and "focus-visible" not in stripped_css
                and "box-shadow" not in body
            ):
                line_no = stripped_css[: b.start()].count("\n") + 1
                violations.append(
                    Violation(
                        rule_id="RULE-L0-META-FOCUS-VISIBLE",
                        law_layer="Layer 0.4 (Meta / Accessibility)",
                        severity="ERROR",
                        file_path=str(file_path),
                        line_number=line_no,
                        element_or_token=sel[:50],
                        message="outline:none on :focus without companion custom focus ring traps keyboard users (WCAG 2.4.7).",
                        suggested_fix="Declare custom :focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }.",
                    )
                )

        return violations

    def _validate_html(
        self, file_path: Path, lines: List[str], content: str
    ) -> List[Violation]:
        violations: List[Violation] = []

        # 0. Validate embedded <style> blocks
        style_matches = re.finditer(
            r"<style[^>]*>(.*?)</style>", content, re.DOTALL | re.IGNORECASE
        )
        for sm in style_matches:
            style_content = sm.group(1)
            style_lines = style_content.splitlines()
            css_violations = self._validate_css(file_path, style_lines)
            violations.extend(css_violations)

        # 1. Check Modals missing ARIA attributes (root containers only)
        modal_regex = re.finditer(
            r'<div[^>]*class=["\'][^"\']*\bmodal-(?:backdrop|dialog|overlay)\b[^"\']*["\'][^>]*>',
            content,
            re.IGNORECASE,
        )
        for m in modal_regex:
            tag = m.group(0)
            line_no = content[: m.start()].count("\n") + 1
            if 'role="dialog"' not in tag and "role='dialog'" not in tag:
                violations.append(
                    Violation(
                        rule_id="RULE-L0-META-ARIA-DIALOG",
                        law_layer="Layer 0.4 (Meta)",
                        severity="WARNING",
                        file_path=str(file_path),
                        line_number=line_no,
                        element_or_token=tag[:50],
                        message="Modal container missing role='dialog' accessibility attribute.",
                        suggested_fix="Add role='dialog' and aria-modal='true'.",
                    )
                )

        # 2. Check Pre-filled PII in input fields
        pii_regex = re.finditer(
            r'<input[^>]*value=["\'](?:Captain Minh|0908|thanberos)[^"\']*["\'][^>]*>',
            content,
            re.IGNORECASE,
        )
        for m in pii_regex:
            tag = m.group(0)
            line_no = content[: m.start()].count("\n") + 1
            violations.append(
                Violation(
                    rule_id="RULE-L0-META-DATA-MINIMIZATION",
                    law_layer="Layer 0.4 (Meta)",
                    severity="ERROR",
                    file_path=str(file_path),
                    line_number=line_no,
                    element_or_token=tag[:60],
                    message="Hardcoded personal PII found in input value. Violates Decree 13/GDPR privacy laws.",
                    suggested_fix="Remove hardcoded value; use placeholder instead.",
                )
            )

        # 3. Check Hick's Law: Multiple competing primary CTAs in the same card/drawer container
        for idx, line in enumerate(lines, start=1):
            if "tsy-drawer-footer" in line or "card-footer" in line:
                chunk = "\n".join(lines[idx - 1 : idx + 20])
                primary_count = len(
                    re.findall(
                        r'class=["\'][^"\']*(?:btn-primary|btn--primary)[^"\']*["\']',
                        chunk,
                    )
                )
                if primary_count > 1:
                    violations.append(
                        Violation(
                            rule_id="RULE-L0-MESO-HICKS-LAW",
                            law_layer="Layer 0.2 (Meso)",
                            severity="WARNING",
                            file_path=str(file_path),
                            line_number=idx,
                            element_or_token="footer actions",
                            message=f"Container has {primary_count} primary CTAs. Violates Hick's Law (max 1 primary CTA).",
                            suggested_fix="Demote secondary actions to outlined/ghost buttons or progressive disclosure menu.",
                        )
                    )

        # 4. Check Rule of 6 (Anti-Overwhelm Ceiling) on Form Containers
        form_chunks = re.finditer(
            r"<form\b[^>]*>(.*?)</form>", content, re.DOTALL | re.IGNORECASE
        )
        for form in form_chunks:
            form_content = form.group(1)
            if (
                'class="stepper"' not in form_content
                and "tsy-tabs" not in form_content
                and "stepper-step" not in form_content
            ):
                input_count = len(
                    re.findall(
                        r"<(?:input|select|textarea)\b", form_content, re.IGNORECASE
                    )
                )
                hidden_count = len(
                    re.findall(r'type=["\']hidden["\']', form_content, re.IGNORECASE)
                )
                visible_inputs = input_count - hidden_count
                if visible_inputs > 6:
                    line_no = content[: form.start()].count("\n") + 1
                    violations.append(
                        Violation(
                            rule_id="RULE-L0-MESO-RULE-OF-6",
                            law_layer="Layer 0.2 (Meso)",
                            severity="WARNING",
                            file_path=str(file_path),
                            line_number=line_no,
                            element_or_token=f"<form> ({visible_inputs} inputs)",
                            message=f"Form has {visible_inputs} visible inputs without stepper or tabs. Violates Rule of 6 Anti-Overwhelm Ceiling.",
                            suggested_fix="Partition form into a multi-step stepper (3-5 fields/step) or tabbed progressive disclosure.",
                        )
                    )

        # 5. Spatial & Flex Mechanics
        violations.extend(
            self._validate_spatial_and_flex_mechanics(file_path, content, lines)
        )

        return violations

    def _validate_spatial_and_flex_mechanics(
        self, file_path: Path, content: str, lines: List[str]
    ) -> List[Violation]:
        """Layer 0 deterministic spatial, flexbox, and SVG aspect-ratio rules."""
        violations: List[Violation] = []

        # 1. RULE-L0-MESO-EMPTY-VOID
        for idx, line in enumerate(lines, start=1):
            if (
                "flex-direction" in line
                or "justify-content" in line
                or "style=" in line
            ):
                if re.search(r"display:\s*flex", line, re.I) and re.search(
                    r"flex-direction:\s*column", line, re.I
                ):
                    if re.search(
                        r"justify-content:\s*space-(?:between|around|evenly)",
                        line,
                        re.I,
                    ):
                        violations.append(
                            Violation(
                                rule_id="RULE-L0-MESO-EMPTY-VOID",
                                law_layer="Layer 0.2 (Meso)",
                                severity="ERROR",
                                file_path=str(file_path),
                                line_number=idx,
                                element_or_token="flex-direction: column + justify-content: space-between",
                                message="Unconstrained 'space-between' in flex column card creates dead pixel voids and destroys proximity.",
                                suggested_fix="Use 'justify-content: flex-start; gap: 12px;'. Anchor footers with 'margin-top: auto;'.",
                            )
                        )

        # 2. RULE-L0-MICRO-ASPECT-FIT
        svg_matches = re.finditer(r"<svg\b([^>]*)>", content, re.IGNORECASE)
        for sm in svg_matches:
            tag_attrs = sm.group(1)
            vb = re.search(
                r'viewBox=["\']\s*([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)["\']',
                tag_attrs,
                re.I,
            )
            if vb:
                w, h = float(vb.group(3)), float(vb.group(4))
                if h > 0:
                    ar_svg = w / h
                    if (
                        'width="100%"' in tag_attrs
                        and 'height="100%"' in tag_attrs
                        and ar_svg >= 2.0
                    ):
                        line_no = content[: sm.start()].count("\n") + 1
                        violations.append(
                            Violation(
                                rule_id="RULE-L0-MICRO-ASPECT-FIT",
                                law_layer="Layer 0.3 (Micro)",
                                severity="ERROR",
                                file_path=str(file_path),
                                line_number=line_no,
                                element_or_token=f"<svg viewBox='0 0 {w} {h}'> (AR {ar_svg:.2f}:1)",
                                message=f"Panoramic SVG (AR {ar_svg:.2f}:1) with 100%/100% dimensions letterboxes in balanced containers, generating >50% dead space.",
                                suggested_fix="Redesign SVG viewBox to match container or assign parent full-width row span ('grid-column: 1 / -1').",
                            )
                        )

        # 3. RULE-L0-MICRO-PIXEL-FILL-FACTOR
        card_matches = re.finditer(
            r'<div[^>]*class=["\'][^"\']*\bcard\b[^"\']*["\'][^>]*>(.*?)</div>\s*(?=<div[^>]*class=["\']|\s*</div>|\s*<!--)',
            content,
            re.DOTALL | re.IGNORECASE,
        )
        for cm in card_matches:
            card_body = cm.group(1)
            line_no = content[: cm.start()].count("\n") + 1
            opening_tag = cm.group(0).split(">", 1)[0]
            if re.search(r"flex-direction:\s*column", opening_tag, re.I) and re.search(
                r"justify-content:\s*space-(?:between|around|evenly)", opening_tag, re.I
            ):
                table_rows = len(re.findall(r"<tr\b", card_body, re.I))
                p_count = len(re.findall(r"<(?:p|div|li)\b", card_body, re.I))
                if table_rows < 5 and p_count < 10:
                    violations.append(
                        Violation(
                            rule_id="RULE-L0-MICRO-PIXEL-FILL-FACTOR",
                            law_layer="Layer 0.3 (Micro)",
                            severity="WARNING",
                            file_path=str(file_path),
                            line_number=line_no,
                            element_or_token="Sparse Card Content",
                            message=f"Card has low information density ({table_rows} table rows, {p_count} blocks) inside stretched container; fill factor < 85%.",
                            suggested_fix="Collapse card height to content ('height: fit-content') or enrich content items to fill the layout.",
                        )
                    )

        # 4. RULE-L0-MESO-VERTICAL-BUDGET
        is_fixed_canvas = any(
            k in content
            for k in (
                "@page",
                ".page",
                "100vh",
                "height: 792px",
                "height: 1080px",
                "height: 210mm",
            )
        )
        if is_fixed_canvas:
            has_vertical_absorber = bool(
                re.search(
                    r"flex:\s*1\b|flex-grow:\s*1\b|grid-template-rows:[^;]*1fr",
                    content,
                    re.I,
                )
            )
            if not has_vertical_absorber:
                page_match = re.search(
                    r"(@page|\.page\b|height:\s*100vh)", content, re.I
                )
                line_no = (
                    content[: page_match.start()].count("\n") + 1 if page_match else 1
                )
                violations.append(
                    Violation(
                        rule_id="RULE-L0-MESO-VERTICAL-BUDGET",
                        law_layer="Layer 0.2 (Meso)",
                        severity="WARNING",
                        file_path=str(file_path),
                        line_number=line_no,
                        element_or_token="Fixed Canvas Layout",
                        message="Fixed canvas container lacks elastic vertical absorber ('flex: 1' or '1fr'). Risks uncontrolled dead bottom void or vertical overflow.",
                        suggested_fix="Allocate middle content arena using 'flex: 1 1 0; min-height: 0;' (absorbing 66-74% height) and anchor footer with 'margin-top: auto;'.",
                    )
                )

        # === ANTI-SLOP SUITE (ENGINE B - HTML) ===
        re_hero_eyebrow = re.compile(
            r'(<(?:span|div|p|badge)[^>]*class=["\'][^"\']*(?:pill|badge|chip|eyebrow|kicker)[^"\']*["\'][^>]*>.*?</(?:span|div|p|badge)>)\s*(<h1\b)',
            re.DOTALL | re.IGNORECASE,
        )
        for m in re_hero_eyebrow.finditer(content):
            line_no = content[: m.start()].count("\n") + 1
            violations.append(
                Violation(
                    rule_id="RULE-SLOP-HERO-EYEBROW-CHIP",
                    law_layer="Layer 0.2 (Meso / Anti-Slop)",
                    severity="WARNING",
                    file_path=str(file_path),
                    line_number=line_no,
                    element_or_token="pill chip above <h1>",
                    message="Hero eyebrow pill chip detected immediately above <h1>. Universal AI landing template tell.",
                    suggested_fix="Integrate context directly into the <h1> headline or demote to breadcrumb navigation.",
                )
            )

        re_serif_hero = re.compile(
            r'<h1[^>]*style=["\'][^"\']*(?:font-style:\s*italic|font-family:[^"\']*(?:fraunces|playfair|recoleta|newsreader|serif))[^"\']*["\']',
            re.IGNORECASE,
        )
        for m in re_serif_hero.finditer(content):
            tag = m.group(0)
            if "italic" in tag.lower():
                line_no = content[: m.start()].count("\n") + 1
                violations.append(
                    Violation(
                        rule_id="RULE-SLOP-ITALIC-SERIF-HERO",
                        law_layer="Layer 0.3 (Micro / Anti-Slop)",
                        severity="WARNING",
                        file_path=str(file_path),
                        line_number=line_no,
                        element_or_token=tag[:50],
                        message="Italic serif display hero headline on generic interface. Reflex AI-startup aesthetic.",
                        suggested_fix="Set display headline in clean roman typography or establish a comprehensive editorial serif system.",
                    )
                )

        re_icon_tile = re.compile(
            r'(<div[^>]*class=["\'][^"\']*(?:icon-box|icon-wrapper|icon-tile|feature-icon)[^"\']*["\'][^>]*>.*?</div>)\s*(<h[2-4]\b)',
            re.DOTALL | re.IGNORECASE,
        )
        for m in re_icon_tile.finditer(content):
            line_no = content[: m.start()].count("\n") + 1
            violations.append(
                Violation(
                    rule_id="RULE-SLOP-ICON-TILE-STACK",
                    law_layer="Layer 0.2 (Meso / Anti-Slop)",
                    severity="WARNING",
                    file_path=str(file_path),
                    line_number=line_no,
                    element_or_token="icon tile preceding heading",
                    message="Rounded icon tile container stacked vertically above heading. Universal AI feature-card template.",
                    suggested_fix="Place icon inline beside heading or allow icon to sit in natural flow without background tile.",
                )
            )

        tag_regex = re.compile(r"(<div\b[^>]*>|</div>)", re.IGNORECASE)
        card_class_re = re.compile(
            r'\bclass=["\'][^"\']*(?<![\w-])card(?![\w-])', re.IGNORECASE
        )
        div_stack: List[Tuple[str, bool, int]] = []
        for m in tag_regex.finditer(content):
            tag_str = m.group(0)
            line_no = content[: m.start()].count("\n") + 1
            if tag_str.lower().startswith("<div"):
                is_card = bool(card_class_re.search(tag_str))
                card_parents = [p for p in div_stack if p[1]]
                if is_card and card_parents:
                    parent_line = card_parents[-1][2]
                    violations.append(
                        Violation(
                            rule_id="RULE-SLOP-NESTED-CARDS",
                            law_layer="Layer 0.2 (Meso / Anti-Slop)",
                            severity="ERROR",
                            file_path=str(file_path),
                            line_number=line_no,
                            element_or_token=tag_str[:50],
                            message=f"Card nested inside another card at line {parent_line} (framing exhaustion). Destroys visual hierarchy and wastes density.",
                            suggested_fix="Flatten hierarchy: use typography, dividers, or subtle background tonal shifts instead of nested boxes.",
                        )
                    )
                div_stack.append((tag_str, is_card, line_no))
            else:
                if div_stack:
                    div_stack.pop()

        re_numbered = re.compile(
            r"<(?:span|div|p)[^>]*>\s*(?://\s*)?0[1-9]\s*</(?:span|div|p)>\s*<h[2-4]\b",
            re.IGNORECASE,
        )
        numbered_matches = list(re_numbered.finditer(content))
        if len(numbered_matches) >= 2:
            violations.append(
                Violation(
                    rule_id="RULE-SLOP-NUMBERED-SECTION-LABELS",
                    law_layer="Layer 0.2 (Meso / Anti-Slop)",
                    severity="WARNING",
                    file_path=str(file_path),
                    line_number=content[: numbered_matches[0].start()].count("\n") + 1,
                    element_or_token=f"{len(numbered_matches)} numbered section markers",
                    message="Artificial numbered section labels (01, 02...) detected beside headings. AI editorial scaffolding.",
                    suggested_fix="Remove numeric index markers. Let typographic scale, spacing, and narrative carry structure.",
                )
            )

        re_emoji_ui = re.compile(
            r'<(?:button|nav|tab|summary|h[1-6]|span\b[^>]*class=["\'][^"\']*(?:btn|badge|pill|chip|tab|nav)[^"\']*["\'])[^>]*>'
            r"[^<]*?([\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F900-\U0001F9FF\U00002600-\U000026FF\U00002700-\U000027BF\U0001FA70-\U0001FAFF])"
            r"[^<]*?</(?:button|nav|tab|summary|h[1-6]|span)>",
            re.DOTALL,
        )
        for m in re_emoji_ui.finditer(content):
            line_no = content[: m.start()].count("\n") + 1
            violations.append(
                Violation(
                    rule_id="RULE-SLOP-EMOJI-IN-UI",
                    law_layer="Layer 0.3 (Micro / Anti-Slop)",
                    severity="ERROR",
                    file_path=str(file_path),
                    line_number=line_no,
                    element_or_token=m.group(0)[:50],
                    message=f"Emoji '{m.group(1)}' used inside structural UI element. Causes cross-OS baseline and aesthetic breakage.",
                    suggested_fix="Replace emoji with a curated monochrome SVG vector icon (Lucide / Phosphor) and active imperative verb.",
                )
            )

        re_aphorisms = [
            (re.compile(r"\b[A-Z][a-z]+\.\s+No\s+[a-z\s]+\.", re.M), "X. No Y."),
            (
                re.compile(r"\bNo\s+[a-z\s]+\.\s+Just\s+[a-z\s]+\.", re.M),
                "No X. Just Y.",
            ),
            (
                re.compile(
                    r"\bNot\s+(?:a|just)\s+[a-z\s]+[.,;]\s+(?:A|The)\s+[a-z\s]+\.", re.M
                ),
                "Not a X. A Y.",
            ),
            (
                re.compile(
                    r"\bBuilt\s+for\s+[a-z\s]+[.,;]\s+(?:Designed|Engineered)\s+for\s+[a-z\s]+\.",
                    re.M,
                ),
                "Built for X. Designed for Y.",
            ),
        ]
        for pat, label in re_aphorisms:
            for m in pat.finditer(content):
                line_no = content[: m.start()].count("\n") + 1
                violations.append(
                    Violation(
                        rule_id="RULE-SLOP-APHORISTIC-CADENCE",
                        law_layer="Layer 0.2 (Meso / Anti-Slop)",
                        severity="WARNING",
                        file_path=str(file_path),
                        line_number=line_no,
                        element_or_token=m.group(0)[:50],
                        message=f"Aphoristic cadence copy detected ('{label}'). Hallmarked AI rhetorical filler.",
                        suggested_fix="Replace rhetorical contrast with concrete, factual system capabilities and SLA metrics.",
                    )
                )

        re_buzzwords = re.compile(
            r"\b(?:streamline[sd]?|empower(?:s|ed|ing)?|supercharge[sd]?|unleash(?:es|ed|ing)?|cutting-edge|seamless(?:ly)?|paradigm(?:s)?|effortless(?:ly)?|elevat(?:e|es|ed|ing)|revolutioniz(?:e|es|ed|ing)|game-changer|delv(?:e|es|ed|ing)|tapestry|next-generation|frictionless)\b",
            re.IGNORECASE,
        )
        buzzword_matches = list(re_buzzwords.finditer(content))
        if len(buzzword_matches) >= 3:
            violations.append(
                Violation(
                    rule_id="RULE-SLOP-BUZZWORD-DENSITY",
                    law_layer="Layer 0.3 (Micro / Anti-Slop)",
                    severity="WARNING",
                    file_path=str(file_path),
                    line_number=content[: buzzword_matches[0].start()].count("\n") + 1,
                    element_or_token=f"{len(buzzword_matches)} buzzwords ({', '.join(set(m.group(0).lower() for m in buzzword_matches[:4]))})",
                    message=f"High density of generic SaaS buzzwords ({len(buzzword_matches)} occurrences). Hallmarked AI marketing fluff.",
                    suggested_fix="Replace with Plain Language: concrete verbs and quantifiable product mechanisms.",
                )
            )

        re_emdash = re.compile(r"[\u2014—]|\s+--\s+")
        emdash_matches = list(re_emdash.finditer(content))
        char_count = max(1, len(content))
        emdash_density = (len(emdash_matches) / char_count) * 500
        if len(emdash_matches) >= 3 and emdash_density >= 1.0:
            violations.append(
                Violation(
                    rule_id="RULE-SLOP-EMDASH-DENSITY",
                    law_layer="Layer 0.3 (Micro / Anti-Slop)",
                    severity="WARNING",
                    file_path=str(file_path),
                    line_number=content[: emdash_matches[0].start()].count("\n") + 1,
                    element_or_token=f"{len(emdash_matches)} em-dashes",
                    message=f"Em-dash density ({emdash_density:.1f} per 500 chars) exceeds human copywriting threshold. AI punctuation tell.",
                    suggested_fix="Decompose compound parentheticals into distinct declarative sentences; eliminate dashes from UI labels.",
                )
            )

        re_sparkle = re.compile(
            r"<(?:button|a)\b[^>]*>(?=.*?(?:sparkle|magic|wand|✨|lucide-sparkles|fa-magic)).*?</(?:button|a)>",
            re.DOTALL | re.IGNORECASE,
        )
        for m in re_sparkle.finditer(content):
            line_no = content[: m.start()].count("\n") + 1
            violations.append(
                Violation(
                    rule_id="RULE-SLOP-SPARKLE-ICON-INFLATION",
                    law_layer="Layer 0.3 (Micro / Anti-Slop)",
                    severity="WARNING",
                    file_path=str(file_path),
                    line_number=line_no,
                    element_or_token=m.group(0)[:50],
                    message="Decorative sparkle/magic wand icon detected in action CTA. Superficial AI branding tell.",
                    suggested_fix="Remove magical iconography. Use plain imperative action verbs ('Generate report', 'Analyze dataset').",
                )
            )

        return violations

    def _validate_js(
        self, file_path: Path, lines: List[str], content: str
    ) -> List[Violation]:
        violations: List[Violation] = []
        ext = file_path.suffix.lower()
        stripped = _strip_comments_preserving_newlines(content, ext)
        stripped_lines = stripped.splitlines()

        # 1. Check Hardcoded white text color in JS templates
        for idx, line in enumerate(stripped_lines, start=1):
            if re.search(
                r'style=["\'][^"\']*color:\s*#(?:fff|ffffff)\b[^"\']*["\']',
                line,
                re.IGNORECASE,
            ):
                violations.append(
                    Violation(
                        rule_id="RULE-L0-MICRO-COLOR-INVARIANT",
                        law_layer="Layer 0.3 (Micro)",
                        severity="ERROR",
                        file_path=str(file_path),
                        line_number=idx,
                        element_or_token=line.strip()[:60],
                        message="Hardcoded white text color '#fff' in JS template renders invisible in Light Mode.",
                        suggested_fix="Use dynamic CSS variable: var(--text-primary).",
                    )
                )

        # 2. Check alert / prompt browser primitive usage
        for idx, line in enumerate(stripped_lines, start=1):
            if re.search(r"\b(?:window\.)?prompt\s*\(", line):
                violations.append(
                    Violation(
                        rule_id="RULE-L0-MACRO-BLOCKING-UI",
                        law_layer="Layer 0.1 (Macro)",
                        severity="WARNING",
                        file_path=str(file_path),
                        line_number=idx,
                        element_or_token="prompt()",
                        message="Primitive prompt() blocks thread and breaks luxury UI paradigm.",
                        suggested_fix="Use inline card creation or styled modal dialog.",
                    )
                )

        return violations

    def _collect_suite_typography_telemetry(
        self, files: List[Path]
    ) -> Tuple[Set[float], Dict[str, str], Optional[Path]]:
        """Aggregate distinct resolved `px` font-size steps and custom font families across scanned files."""
        distinct_px_steps: Set[float] = set()
        custom_families: Dict[str, str] = {}
        anchor_file: Optional[Path] = files[0] if files else None

        re_css_font_family = re.compile(
            r"(?<![\w-])font-family\s*:\s*([^;{}]+)",
            re.IGNORECASE,
        )
        re_jsx_font_family = re.compile(
            r"\bfontFamily\s*:\s*(?:\"([^\"]+)\"|'([^']+)')"
        )
        re_theme_block = re.compile(
            r"@theme\b[^{]*\{(.*?)\}",
            re.IGNORECASE | re.DOTALL,
        )
        re_theme_font_var = re.compile(r"--font-[a-zA-Z0-9_-]+\s*:\s*([^;{}]+)")

        for fp in files:
            if not fp.exists():
                continue
            ext = fp.suffix.lower()
            raw = fp.read_text(encoding="utf-8", errors="ignore")
            stripped = _strip_comments_preserving_newlines(raw, ext)

            # A. Standard Tailwind text-size classes
            for tm in _RE_TW_STANDARD_TEXT_SIZE.finditer(stripped):
                cls_key = tm.group(1)
                if cls_key in TAILWIND_TEXT_SIZE_PX:
                    distinct_px_steps.add(TAILWIND_TEXT_SIZE_PX[cls_key])

            # B. Arbitrary Tailwind length classes
            for am in _RE_TW_ARBITRARY_TEXT.finditer(stripped):
                b_val = am.group(2).strip()
                if is_arbitrary_font_size_value(b_val):
                    px_v = resolve_static_length_to_px(b_val)
                    if px_v is not None and px_v > 0.0:
                        distinct_px_steps.add(px_v)

            # C. Static CSS font-size declarations (CSS/SCSS, HTML <style> & inline style)
            css_segments: List[str] = []
            if ext in (".css", ".scss"):
                css_segments.append(stripped)
            elif ext in (".html", ".htm", ".jinja", ".jinja2"):
                for sm in re.finditer(
                    r"<style[^>]*>(.*?)</style>", stripped, re.DOTALL | re.IGNORECASE
                ):
                    css_segments.append(
                        _strip_comments_preserving_newlines(sm.group(1), ".css")
                    )
                for im in _RE_HTML_INLINE_STYLE.finditer(stripped):
                    css_segments.append(
                        im.group(1) if im.group(1) is not None else (im.group(2) or "")
                    )
            elif ext in (".js", ".jsx", ".ts", ".tsx"):
                for im in _RE_HTML_INLINE_STYLE.finditer(stripped):
                    css_segments.append(
                        im.group(1) if im.group(1) is not None else (im.group(2) or "")
                    )

            for seg in css_segments:
                for fm in _RE_CSS_FONT_SIZE.finditer(seg):
                    px_v = resolve_static_length_to_px(fm.group(1))
                    if px_v is not None and px_v > 0.0:
                        distinct_px_steps.add(px_v)

            # D. JSX inline style={{ fontSize: ... }}
            if ext in (".js", ".jsx", ".ts", ".tsx"):
                for jm in _RE_JSX_FONT_SIZE.finditer(stripped):
                    s_v, n_v = jm.group(1), jm.group(2)
                    px_v = None
                    if n_v is not None:
                        px_v = round(float(n_v), 2)
                    elif s_v is not None:
                        sc = s_v.strip()
                        if re.fullmatch(r"\d+(?:\.\d+)?", sc):
                            px_v = round(float(sc), 2)
                        else:
                            px_v = resolve_static_length_to_px(sc)
                    if px_v is not None and px_v > 0.0:
                        distinct_px_steps.add(px_v)

            # E. Custom Font Families:
            # E1. Google Fonts URLs (family=...)
            for gm in _RE_GFONTS_URL.finditer(stripped):
                qs = gm.group(1)
                for fam_param in re.finditer(r"(?:^|&)family=([^&\"'\s>]+)", qs):
                    decoded = unquote(fam_param.group(1).replace("+", " "))
                    for sub_fam in decoded.split("|"):
                        fam_name = " ".join(sub_fam.split(":", 1)[0].strip().split())
                        if (
                            fam_name
                            and fam_name.lower() not in SYSTEM_AND_GENERIC_FONTS
                        ):
                            custom_families.setdefault(fam_name.lower(), fam_name)

            # E2. CSS @font-face & font-family properties (excluding non-@theme custom vars like --tsy-font-fallback-sans:)
            for seg in css_segments:
                for ffm in re_css_font_family.finditer(seg):
                    for k, v in extract_custom_font_families_from_stack(
                        ffm.group(1)
                    ).items():
                        custom_families.setdefault(k, v)
                for tbm in re_theme_block.finditer(seg):
                    for tfm in re_theme_font_var.finditer(tbm.group(1)):
                        for k, v in extract_custom_font_families_from_stack(
                            tfm.group(1)
                        ).items():
                            custom_families.setdefault(k, v)

            # E3. JSX inline fontFamily
            if ext in (".js", ".jsx", ".ts", ".tsx"):
                for jff in re_jsx_font_family.finditer(stripped):
                    raw_jf = (
                        jff.group(1)
                        if jff.group(1) is not None
                        else (jff.group(2) or "")
                    )
                    for k, v in extract_custom_font_families_from_stack(raw_jf).items():
                        custom_families.setdefault(k, v)

        return distinct_px_steps, custom_families, anchor_file

    def run_suite(self, target_dir: Path) -> ValidationReport:
        report = ValidationReport()
        files: List[Path] = []

        if target_dir.is_file():
            if target_dir.suffix.lower() in SUPPORTED_EXTENSIONS:
                files = [target_dir]
        elif target_dir.exists():
            for root, dirnames, filenames in os.walk(target_dir):
                dirnames[:] = [d for d in sorted(dirnames) if d not in SKIP_SCAN_DIRS]
                for f in sorted(filenames):
                    if self._should_skip_filename(f):
                        continue
                    ext = Path(f).suffix.lower()
                    if ext in SUPPORTED_EXTENSIONS:
                        files.append(Path(root) / f)

        report.total_files_scanned = len(files)
        for f in files:
            v = self.validate_file(f)
            report.violations.extend(v)

        # Suite-level Typography Sprawl & Font-Family Sprawl Rules
        distinct_px_steps, custom_families, anchor = (
            self._collect_suite_typography_telemetry(files)
        )
        anchor_str = str(anchor or target_dir)

        if len(distinct_px_steps) > self.max_type_scale_steps:
            sorted_steps = ", ".join(f"{px:g}px" for px in sorted(distinct_px_steps))
            report.violations.append(
                Violation(
                    rule_id="RULE-L0-MICRO-TYPOGRAPHY-SPRAWL",
                    law_layer="Layer 0.3 (Micro / Typography)",
                    severity="ERROR",
                    file_path=anchor_str,
                    line_number=1,
                    element_or_token=f"{len(distinct_px_steps)} font-size steps ({sorted_steps})",
                    message=(
                        f"Typography scale sprawl: detected {len(distinct_px_steps)} distinct font-size steps ({sorted_steps}), exceeding the {self.max_type_scale_steps}-step ceiling."
                    ),
                    suggested_fix=(
                        f"Consolidate font sizes into a governed <= {self.max_type_scale_steps}-step modular scale (7-step recommended, floor >= 11px)."
                    ),
                )
            )

        if len(custom_families) > self.max_font_families:
            fam_names = ", ".join(sorted(custom_families.values()))
            report.violations.append(
                Violation(
                    rule_id="RULE-L0-MICRO-FONT-FAMILY-SPRAWL",
                    law_layer="Layer 0.3 (Micro / Typography)",
                    severity="ERROR",
                    file_path=anchor_str,
                    line_number=1,
                    element_or_token=f"{len(custom_families)} custom font families ({fam_names})",
                    message=(
                        f"Font family sprawl: detected {len(custom_families)} custom font families ({fam_names}), exceeding the {self.max_font_families}-family triad ceiling."
                    ),
                    suggested_fix=(
                        f"Consolidate custom typefaces to <= {self.max_font_families} families (Editorial Display, UI Body Sans, Tabular Technical Mono)."
                    ),
                )
            )

        report.passed = report.error_count == 0
        report.score = max(
            0.0, 1.0 - (report.error_count * 0.05) - (report.warning_count * 0.01)
        )
        return report


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="UIUXProMax Layer 0 Deterministic Governance Linter (v2.5.0)"
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target file or directory to scan",
    )
    parser.add_argument(
        "--max-scale-steps",
        type=int,
        default=8,
        help="Maximum distinct static px typography scale steps (default: 8)",
    )
    parser.add_argument(
        "--max-font-families",
        type=int,
        default=3,
        help="Maximum distinct custom font families (default: 3)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output",
    )
    args = parser.parse_args(argv)

    target = Path(args.target)
    validator = Layer0Validator(
        workspace_root=target if target.is_dir() else target.parent,
        max_type_scale_steps=args.max_scale_steps,
        max_font_families=args.max_font_families,
    )
    report = validator.run_suite(target)

    if args.json:
        payload = {
            "target": str(target),
            "total_files_scanned": report.total_files_scanned,
            "passed": report.passed,
            "error_count": report.error_count,
            "warning_count": report.warning_count,
            "score": round(report.score, 4),
            "violations": [asdict(v) for v in report.violations],
        }
        print(json.dumps(payload, indent=2))
        return 0 if report.passed else 1

    print(f"[UIUXProMax:Layer0Validator] Scanning target: {target}")
    print(f"Files Scanned: {report.total_files_scanned}")
    print(
        f"Violations: {len(report.violations)} (Errors: {report.error_count}, Warnings: {report.warning_count})"
    )
    print(f"Compliance Score: {report.score:.2f}")

    if report.violations:
        print("\nViolations Summary:")
        for v in report.violations:
            prefix = "[ERROR]" if v.severity.upper() == "ERROR" else "[WARN]"
            print(
                f"  {prefix} {v.rule_id} ({v.law_layer}) @ {Path(v.file_path).name}:{v.line_number}"
            )
            print(f"    Message: {v.message}")
            print(f"    Fix: {v.suggested_fix}")

    if report.passed:
        print("\n[SUCCESS] Layer 0 Governance Check Passed.")
        return 0
    print(
        f"\n[FAILURE] Layer 0 Governance Check Failed with {report.error_count} blocking errors."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
