"""
test_design_handoff_linter.py — Unit test suite for DesignHandoffLinter ($P=1).
Governed by: Gate GW-UIUX-01, Sprint 72 Architecture.
"""

import pytest
import sys
import os

# Add parent directory of tests (scripts) to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from design_handoff_linter import (
    DesignHandoffLinter,
    AccessibilitySeverity,
    StateCoverageResult,
    AccessibilityFinding,
    DesignHandoffAuditReport,
)


def test_audit_component_states_complete():
    linter = DesignHandoffLinter()
    spec = """
    ### Component: Button
    - default: primary blue background
    - hover: darker blue background
    - focus: outline with ring 2px
    - active: pressed down effect
    - disabled: 50% opacity, cursor not-allowed
    - loading: spinner replaces label
    - empty: label fallback
    - error: red border highlight
    """
    results = linter.audit_component_states(spec)
    assert len(results) == 1
    res = results[0]
    assert res.component_name == "Button"
    assert res.is_complete is True
    assert len(res.missing_states) == 0
    assert set(res.declared_states) == set(DesignHandoffLinter.MANDATORY_STATES)


def test_audit_component_states_incomplete():
    linter = DesignHandoffLinter()
    spec = """
    ### Component: ModalCard
    - default: elevation-1
    - hover: elevation-2
    - focus: border-primary
    """
    results = linter.audit_component_states(spec)
    assert len(results) == 1
    res = results[0]
    assert res.component_name == "ModalCard"
    assert res.is_complete is False
    assert "disabled" in res.missing_states
    assert "loading" in res.missing_states
    assert "error" in res.missing_states


def test_audit_multiple_components():
    linter = DesignHandoffLinter()
    spec = """
    ### Component: Button States
    default, hover, focus, active, disabled, loading, empty, error

    ### Component: TextField States
    default, hover, focus, disabled
    """
    results = linter.audit_component_states(spec)
    assert len(results) == 2
    assert results[0].component_name == "Button"
    assert results[0].is_complete is True
    assert results[1].component_name == "TextField"
    assert results[1].is_complete is False
    assert "loading" in results[1].missing_states


def test_wcag_outline_violation():
    linter = DesignHandoffLinter()
    bad_spec = """
    button {
        outline: none;
    }
    """
    findings = linter.audit_wcag_accessibility(bad_spec)
    rule_ids = [f.rule_id for f in findings]
    assert "WCAG-FOCUS-OUTLINE" in rule_ids
    violation = next(f for f in findings if f.rule_id == "WCAG-FOCUS-OUTLINE")
    assert violation.severity == AccessibilitySeverity.VIOLATION


def test_wcag_outline_pass_with_ring():
    linter = DesignHandoffLinter()
    good_spec = """
    button {
        outline: none;
        focus-visible: ring-2 ring-blue-500;
    }
    """
    findings = linter.audit_wcag_accessibility(good_spec)
    rule_ids = [f.rule_id for f in findings]
    assert "WCAG-FOCUS-OUTLINE" not in rule_ids


def test_wcag_touch_target_size():
    linter = DesignHandoffLinter()
    # No min-h-44px mentioned for a button
    spec_no_target = "This is a primary button component with py-1 px-2."
    findings = linter.audit_wcag_accessibility(spec_no_target)
    rule_ids = [f.rule_id for f in findings]
    assert "WCAG-TARGET-SIZE" in rule_ids

    # Target explicitly declared
    spec_with_target = (
        "This is a primary button component with min-h-[44px] touch target."
    )
    findings_ok = linter.audit_wcag_accessibility(spec_with_target)
    rule_ids_ok = [f.rule_id for f in findings_ok]
    assert "WCAG-TARGET-SIZE" not in rule_ids_ok


def test_wcag_aria_label_icon_only():
    linter = DesignHandoffLinter()
    # Missing aria-label on icon-only
    bad_spec = "This is an icon-only button for search."
    findings = linter.audit_wcag_accessibility(bad_spec)
    rule_ids = [f.rule_id for f in findings]
    assert "WCAG-ARIA-LABEL" in rule_ids

    # With aria-label
    good_spec = (
        "This is an icon-only button for search with aria-label='Search database'."
    )
    findings_ok = linter.audit_wcag_accessibility(good_spec)
    rule_ids_ok = [f.rule_id for f in findings_ok]
    assert "WCAG-ARIA-LABEL" not in rule_ids_ok


def test_run_gate_cleared_and_rejected():
    linter = DesignHandoffLinter()

    good_spec = """
    ### Component: ActionButton
    default, hover, focus, active, disabled, loading, empty, error
    Touch target: min-h-[44px]
    Contrast ratio: 4.5:1 certified (WCAG AA)
    Focus: outline: none with focus-visible ring-2
    """
    report_good = linter.run_gate(good_spec)
    assert report_good.is_gate_cleared is True
    assert report_good.states_passed is True
    assert report_good.wcag_passed is True

    bad_spec = """
    ### Component: ActionButton
    default, hover
    button { outline: none; }
    icon-only search
    """
    report_bad = linter.run_gate(bad_spec)
    assert report_bad.is_gate_cleared is False
    assert report_bad.states_passed is False
    assert report_bad.wcag_passed is False
