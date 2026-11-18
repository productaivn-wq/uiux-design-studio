"""
design_handoff_linter.py — Deterministic Design Handoff & WCAG 2.1 AA Linter ($P=1).
Implements: Gate GW-UIUX-01, Component Variant State Matrices, and Accessibility Verification.
Governed by: Layer 0 Architecture Standard.
"""

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Any, Dict, List, Optional


class AccessibilitySeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    VIOLATION = "VIOLATION"


@dataclass
class StateCoverageResult:
    component_name: str
    declared_states: List[str]
    missing_states: List[str]
    is_complete: bool


@dataclass
class AccessibilityFinding:
    severity: AccessibilitySeverity
    rule_id: str
    message: str
    target_element: Optional[str] = None


@dataclass
class DesignHandoffAuditReport:
    total_components_checked: int
    states_passed: bool
    wcag_passed: bool
    state_results: List[StateCoverageResult]
    accessibility_findings: List[AccessibilityFinding]
    is_gate_cleared: bool


class DesignHandoffLinter:
    """Linter for component variant states and WCAG 2.1 AA compliance under Gate GW-UIUX-01."""

    MANDATORY_STATES = [
        "default",
        "hover",
        "focus",
        "active",
        "disabled",
        "loading",
        "empty",
        "error",
    ]

    def audit_component_states(self, text: str) -> List[StateCoverageResult]:
        """Verifies that interactive components declare all mandatory variant states."""
        results = []
        # Find component sections (e.g. ### Button, ### Input, Component: XYZ)
        comp_matches = list(
            re.finditer(
                r"(?:###?\s*(?:Component:\s*)?([A-Za-z0-9_-]+)\s*(?:States|Variants)?|component:\s*([A-Za-z0-9_-]+))",
                text,
                re.IGNORECASE,
            )
        )

        if not comp_matches:
            # Fallback: scan whole text for state occurrences
            text_lower = text.lower()
            declared = [s for s in self.MANDATORY_STATES if s in text_lower]
            missing = [s for s in self.MANDATORY_STATES if s not in declared]
            results.append(
                StateCoverageResult(
                    component_name="Global Spec",
                    declared_states=declared,
                    missing_states=missing,
                    is_complete=len(missing) == 0,
                )
            )
            return results

        for i, match in enumerate(comp_matches):
            comp_name = match.group(1) or match.group(2)
            start_pos = match.end()
            end_pos = (
                comp_matches[i + 1].start() if i + 1 < len(comp_matches) else len(text)
            )
            comp_section = text[start_pos:end_pos].lower()

            declared = [
                s for s in self.MANDATORY_STATES if re.search(rf"\b{s}\b", comp_section)
            ]
            missing = [s for s in self.MANDATORY_STATES if s not in declared]
            results.append(
                StateCoverageResult(
                    component_name=comp_name,
                    declared_states=declared,
                    missing_states=missing,
                    is_complete=len(missing) == 0,
                )
            )

        return results

    def audit_wcag_accessibility(self, text: str) -> List[AccessibilityFinding]:
        """Audits WCAG 2.1 AA requirements (touch target size, outline removal, contrast, aria)."""
        findings = []

        # 1. Outline none without focus-visible
        if re.search(r"outline\s*:\s*none", text, re.IGNORECASE):
            if not re.search(
                r"\b(focus-visible|ring|focus:ring|focus-ring|border)\b",
                text,
                re.IGNORECASE,
            ):
                findings.append(
                    AccessibilityFinding(
                        severity=AccessibilitySeverity.VIOLATION,
                        rule_id="WCAG-FOCUS-OUTLINE",
                        message="Removed outline without declaring a visible focus replacement (WCAG 2.4.7 Focus Visible).",
                    )
                )

        # 2. Touch target size minimum 44px
        has_touch_target = bool(
            re.search(
                r"\b(44px|44\s*px|min-h-\[44px\]|h-11|py-3)\b", text, re.IGNORECASE
            )
        )
        if not has_touch_target and re.search(
            r"\b(button|link|clickable|touch\s*target)\b", text, re.IGNORECASE
        ):
            findings.append(
                AccessibilityFinding(
                    severity=AccessibilitySeverity.WARNING,
                    rule_id="WCAG-TARGET-SIZE",
                    message="Interactive elements should declare a minimum touch target size of 44x44px (WCAG 2.5.5).",
                )
            )

        # 3. Low contrast warning (e.g. gray on white without contrast audit)
        if re.search(r"#([a-fA-F0-9]{3}|[a-fA-F0-9]{6})", text):
            has_contrast_declaration = bool(
                re.search(
                    r"\b(contrast\s*ratio|4\.5:1|3:1|wcag\s*aa)\b", text, re.IGNORECASE
                )
            )
            if not has_contrast_declaration:
                findings.append(
                    AccessibilityFinding(
                        severity=AccessibilitySeverity.WARNING,
                        rule_id="WCAG-CONTRAST-AUDIT",
                        message="Colors declared without explicit contrast ratio certification (minimum 4.5:1 for text).",
                    )
                )

        # 4. ARIA label presence for icon-only elements
        if re.search(
            r"\bicon-only|only\s+icon|button\s+with\s+icon\b", text, re.IGNORECASE
        ):
            if not re.search(
                r"\b(aria-label|aria-labelledby|sr-only|screen-reader)\b",
                text,
                re.IGNORECASE,
            ):
                findings.append(
                    AccessibilityFinding(
                        severity=AccessibilitySeverity.VIOLATION,
                        rule_id="WCAG-ARIA-LABEL",
                        message="Icon-only interactive elements must declare an aria-label or sr-only text.",
                    )
                )

        return findings

    def run_gate(self, spec_text: str) -> DesignHandoffAuditReport:
        """Executes full Gate GW-UIUX-01 audit."""
        state_results = self.audit_component_states(spec_text)
        access_findings = self.audit_wcag_accessibility(spec_text)

        violations = [
            f for f in access_findings if f.severity == AccessibilitySeverity.VIOLATION
        ]
        states_ok = all(r.is_complete for r in state_results)
        wcag_ok = len(violations) == 0

        is_cleared = states_ok and wcag_ok

        return DesignHandoffAuditReport(
            total_components_checked=len(state_results),
            states_passed=states_ok,
            wcag_passed=wcag_ok,
            state_results=state_results,
            accessibility_findings=access_findings,
            is_gate_cleared=is_cleared,
        )
