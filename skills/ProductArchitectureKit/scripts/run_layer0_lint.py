"""
run_layer0_lint.py — Unified Layer 0 CLI & Programmatic Linter (ProductArchitectureKit v1.1.0).

Supports:
1. DesignState JSON files (`.json`) -> validates via `ProductArchitectureKit` `Layer0Validator`.
2. Directories or frontend source files (`.tsx`, `.jsx`, `.ts`, `.js`, `.css`, `.scss`, `.html`)
   -> delegates seamlessly to `UIUXProMax/scripts/layer0_validator.py` (`Layer0Validator`).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import asdict
from pathlib import Path

_SKILL_ROOT = Path(__file__).resolve().parent.parent
if str(_SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILL_ROOT))

from core.engine.layer0_validator import Layer0Validator  # noqa: E402
from core.schemas import DesignState, Layer0Rule  # noqa: E402


def _load_uiuxpromax_validator():
    candidates = [
        _SKILL_ROOT.parent / "UIUXProMax" / "scripts" / "layer0_validator.py",
        Path.home()
        / ".gemini"
        / "config"
        / "skills"
        / "UIUXProMax"
        / "scripts"
        / "layer0_validator.py",
        Path.home()
        / ".gemini"
        / "antigravity"
        / "skills"
        / "UIUXProMax"
        / "scripts"
        / "layer0_validator.py",
    ]
    for cand in candidates:
        if cand.exists():
            spec = importlib.util.spec_from_file_location(
                "uiuxpromax_layer0_validator", str(cand)
            )
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = mod
                spec.loader.exec_module(mod)
                return mod.Layer0Validator
    raise FileNotFoundError("Could not locate UIUXProMax/scripts/layer0_validator.py")


def _dump_model(obj) -> dict:
    return obj.model_dump() if hasattr(obj, "model_dump") else obj.dict()


def run_layer0_lint(target_or_state_path: str, rules_path: str | None = None) -> dict:
    target = Path(target_or_state_path)

    # Delegate directory or frontend code files directly to UIUXProMax Layer0Validator
    if target.is_dir() or target.suffix.lower() != ".json":
        UIUXLayer0Validator = _load_uiuxpromax_validator()
        code_validator = UIUXLayer0Validator(
            workspace_root=target if target.is_dir() else target.parent
        )
        report = code_validator.run_suite(target)
        return {
            "mode": "uiuxpromax_code_suite",
            "passed": report.passed,
            "total_files_scanned": report.total_files_scanned,
            "error_count": report.error_count,
            "warning_count": report.warning_count,
            "score": round(report.score, 4),
            "results": [asdict(v) for v in report.violations],
        }

    # Validate DesignState JSON
    with open(target, encoding="utf-8") as f:
        state = DesignState(**json.load(f))

    rules = []
    if rules_path:
        with open(rules_path, encoding="utf-8") as f:
            rules = [Layer0Rule(**rule) for rule in json.load(f)]

    validator = Layer0Validator(rules)
    if state.typography is not None or not rules_path:
        results = validator.validate_all(state)
    else:
        results = validator.validate(state)

    return {
        "passed": all(r.passed for r in results),
        "results": [_dump_model(r) for r in results],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run Layer0 Lint (DesignState JSON or UI Codebase)"
    )
    parser.add_argument(
        "state_path",
        type=str,
        help="Path to DesignState JSON, code file, or project directory",
    )
    parser.add_argument(
        "rules_path",
        nargs="?",
        default=None,
        type=str,
        help="Optional path to rules JSON",
    )
    parser.add_argument("--output", type=str, help="Output file path")
    args = parser.parse_args(argv)

    result = run_layer0_lint(args.state_path, args.rules_path)
    output = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0 if result.get("passed", False) else 1


if __name__ == "__main__":
    sys.exit(main())
