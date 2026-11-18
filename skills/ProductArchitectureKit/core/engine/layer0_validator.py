"""
layer0_validator.py — ProductArchitectureKit Layer 0 & Typography Governance Engine (v1.1.0).
"""

from __future__ import annotations

import re

from core.schemas import (
    DesignState,
    Layer0Rule,
    Layer0ValidationResult,
    TypographyGovernanceContract,
)

_TAILWIND_SCALE_PX: dict[str, float] = {
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

_SYSTEM_FONTS: set[str] = {
    "sans-serif",
    "serif",
    "monospace",
    "cursive",
    "fantasy",
    "system-ui",
    "ui-sans-serif",
    "ui-serif",
    "ui-monospace",
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

_ARBITRARY_TEXT_RE = re.compile(r"^(?:[a-z0-9-]+:)*!?text-\[([^\]]+)\]$")
_DIMENSIONAL_LEN_RE = re.compile(
    r"^(\d+(?:\.\d+)?)(px|rem|em|pt|vw|vh|vmin|vmax|cqw|cqh|ch|ex)$",
    re.IGNORECASE,
)


def _is_arbitrary_length_class(cls_token: str) -> str | None:
    m = _ARBITRARY_TEXT_RE.match(cls_token.strip())
    if not m:
        return None
    inner = m.group(1).strip()
    low = inner.lower()
    if low.startswith(
        ("color:", "var(", "#", "rgb(", "rgba(", "hsl(", "hsla(", "oklch(")
    ):
        return None
    if low in (
        "balance",
        "pretty",
        "nowrap",
        "wrap",
        "left",
        "center",
        "right",
        "justify",
    ):
        return None
    if low.startswith(("length:", "clamp(", "calc(")) or _DIMENSIONAL_LEN_RE.match(
        inner
    ):
        return inner
    return None


def _parse_px_value(raw: object) -> float | None:
    if isinstance(raw, (int, float)):
        return round(float(raw), 2)
    if not isinstance(raw, str):
        return None
    s = raw.strip()
    if s.lower().startswith("length:"):
        s = s[7:].strip()
    if re.fullmatch(r"\d+(?:\.\d+)?", s):
        return round(float(s), 2)
    m = re.match(r"^(\d+(?:\.\d+)?)\s*(px|rem|pt)$", s, re.IGNORECASE)
    if not m:
        return None
    v = float(m.group(1))
    u = m.group(2).lower()
    if u == "px":
        return round(v, 2)
    if u == "rem":
        return round(v * 16.0, 2)
    if u == "pt":
        return round(v * (96.0 / 72.0), 2)
    return None


def _extract_custom_fonts(raw_family: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in str(raw_family).split(","):
        tok = " ".join(part.strip().strip("'\"` ").split())
        if not tok:
            continue
        low = tok.lower()
        if low.startswith(("var(", "--")) or low in _SYSTEM_FONTS:
            continue
        out.setdefault(low, tok)
    return out


class Layer0Validator:
    def __init__(self, rules: list[Layer0Rule] | None = None):
        self.rules: list[Layer0Rule] = list(rules or [])

    def validate(self, state: DesignState) -> list[Layer0ValidationResult]:
        results: list[Layer0ValidationResult] = []
        for rule in self.rules:
            try:
                passed = bool(
                    eval(
                        rule.condition,
                        {
                            "state": state,
                            "len": len,
                            "any": any,
                            "all": all,
                            "min": min,
                            "max": max,
                        },
                    )
                )
            except Exception as e:
                passed = False
                message = f"Error evaluating rule {rule.id}: {str(e)}"
            else:
                message = rule.description if passed else f"Failed: {rule.description}"

            results.append(
                Layer0ValidationResult(
                    rule_id=rule.id,
                    passed=passed,
                    message=message,
                    severity=rule.severity,
                )
            )
        return results

    def validate_typography(self, state: DesignState) -> list[Layer0ValidationResult]:
        """Evaluate the 5 deterministic typography governance rules on `DesignState`."""
        contract = state.typography or TypographyGovernanceContract()
        min_px = contract.min_font_size_px
        max_steps = contract.max_scale_steps
        max_families = contract.max_font_families

        submin_items: list[str] = []
        arbitrary_items: list[str] = list(contract.arbitrary_size_classes)
        mono_button_items: list[str] = list(contract.mono_button_violations)
        scale_steps: set[float] = {
            round(float(s), 2) for s in contract.scale_steps_px if float(s) > 0.0
        }
        for s in contract.scale_steps_px:
            if float(s) < min_px:
                submin_items.append(f"contract:{s}px")

        custom_fonts: dict[str, str] = {}
        for fam in contract.font_families:
            for k, v in _extract_custom_fonts(fam).items():
                custom_fonts.setdefault(k, v)

        # Inspect DesignElements
        for eid, elem in state.elements.items():
            # 1. Explicit element font_size_px or styles.fontSize / font-size
            elem_sizes: list[float | None] = [
                _parse_px_value(elem.font_size_px),
                _parse_px_value(elem.styles.get("fontSize")),
                _parse_px_value(elem.styles.get("font-size")),
                _parse_px_value(elem.props.get("fontSize")),
            ]
            is_sr_only = "sr-only" in elem.classes or bool(elem.props.get("sr_only"))
            for sz in elem_sizes:
                if sz is None:
                    continue
                if sz == 0.0 and is_sr_only:
                    continue
                if sz > 0.0:
                    scale_steps.add(sz)
                if sz < min_px:
                    submin_items.append(f"{eid}:{sz:g}px")

            # 2. Element font_family / styles.fontFamily
            for raw_fam in (
                elem.font_family,
                elem.styles.get("fontFamily"),
                elem.styles.get("font-family"),
            ):
                if isinstance(raw_fam, str) and raw_fam.strip():
                    for k, v in _extract_custom_fonts(raw_fam).items():
                        custom_fonts.setdefault(k, v)

            # 3. Element utility classes
            is_button = elem.type in ("button", "Btn")
            allow_mono = (
                elem.allow_mono
                or bool(elem.props.get("data-mono-allowed"))
                or bool(elem.props.get("allow_mono"))
            )
            for cls_tok in elem.classes:
                base_cls = cls_tok.split(":")[-1].lstrip("!")
                if base_cls in _TAILWIND_SCALE_PX:
                    scale_steps.add(_TAILWIND_SCALE_PX[base_cls])
                arb_inner = _is_arbitrary_length_class(cls_tok)
                if arb_inner is not None:
                    arbitrary_items.append(f"{eid}:{cls_tok}")
                    arb_px = _parse_px_value(arb_inner)
                    if arb_px is not None:
                        if arb_px > 0.0:
                            scale_steps.add(arb_px)
                        if arb_px < min_px and not (arb_px == 0.0 and is_sr_only):
                            submin_items.append(f"{eid}:{cls_tok}({arb_px:g}px)")
                if is_button and not allow_mono and base_cls == "font-mono":
                    mono_button_items.append(f"{eid}:{cls_tok}")

        results: list[Layer0ValidationResult] = [
            Layer0ValidationResult(
                rule_id="RULE-L0-MICRO-SUBMINIMUM-FONT",
                passed=len(submin_items) == 0,
                message=(
                    f"All font sizes satisfy >= {min_px:g}px floor."
                    if not submin_items
                    else f"Subminimum font sizes (< {min_px:g}px) detected: {', '.join(submin_items)}"
                ),
            ),
            Layer0ValidationResult(
                rule_id="RULE-L0-MICRO-ARBITRARY-TEXT-SIZE",
                passed=len(arbitrary_items) == 0,
                message=(
                    "Zero arbitrary Tailwind font-size length utilities."
                    if not arbitrary_items
                    else f"Arbitrary font-size utilities detected: {', '.join(arbitrary_items)}"
                ),
            ),
            Layer0ValidationResult(
                rule_id="RULE-L0-MICRO-MONO-OVERUSE",
                passed=len(mono_button_items) == 0,
                message=(
                    "Zero monospace button violations."
                    if not mono_button_items
                    else f"Monospace font-mono prohibited on interactive buttons: {', '.join(mono_button_items)}"
                ),
            ),
            Layer0ValidationResult(
                rule_id="RULE-L0-MICRO-TYPOGRAPHY-SPRAWL",
                passed=len(scale_steps) <= max_steps,
                message=(
                    f"Typography scale within ceiling ({len(scale_steps)}/{max_steps} steps)."
                    if len(scale_steps) <= max_steps
                    else f"Typography scale sprawl: {len(scale_steps)} distinct px steps exceeds {max_steps}-step ceiling ({sorted(scale_steps)})."
                ),
            ),
            Layer0ValidationResult(
                rule_id="RULE-L0-MICRO-FONT-FAMILY-SPRAWL",
                passed=len(custom_fonts) <= max_families,
                message=(
                    f"Custom font families within ceiling ({len(custom_fonts)}/{max_families})."
                    if len(custom_fonts) <= max_families
                    else f"Font family sprawl: {len(custom_fonts)} custom families ({', '.join(sorted(custom_fonts.values()))}) exceeds {max_families}-family ceiling."
                ),
            ),
        ]
        return results

    def validate_all(self, state: DesignState) -> list[Layer0ValidationResult]:
        """Run both declarative `Layer0Rule` checks and deterministic typography governance checks."""
        return self.validate(state) + self.validate_typography(state)
