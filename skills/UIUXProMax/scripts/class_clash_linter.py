"""
class_clash_linter.py — Cross-File Unscoped CSS Class Clash Detector (Vector C2; P=1).

Ported from `stageshow/scripts/class-clash.mjs`:
  - Strips CSS comments and @keyframes blocks.
  - Splits selector lists cleanly around nested parentheses (:where(), :is(), :not()).
  - Flags unscoped class selectors (e.g., `.row`) defined across >= 2 stylesheets while
    respecting module/demo ancestor scoping (e.g., `.scoped-a .title` vs `.scoped-b .title`).
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any


def split_selectors(selector_prelude: str) -> list[str]:
    """Split comma-separated CSS selectors without breaking inside :is()/:where()/:not()."""
    parts: list[str] = []
    depth = 0
    buf: list[str] = []
    for ch in selector_prelude:
        if ch == "(":
            depth += 1
            buf.append(ch)
        elif ch == ")":
            depth = max(0, depth - 1)
            buf.append(ch)
        elif ch == "," and depth == 0:
            s = "".join(buf).strip()
            if s:
                parts.append(s)
            buf = []
        else:
            buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def without_conditions(selector: str) -> str:
    """Strip pseudo-classes/elements and attribute conditions while preserving descendant combinators."""
    out = re.sub(r"\[[^\]]*\]", "", selector)
    out = re.sub(r"::?[a-zA-Z0-9_-]+(?:\([^()]*\))?", "", out)
    return re.sub(r"\s+", " ", out).strip()


def unwrap_attribute_where(selector: str) -> str:
    """Unwrap `:where(.scope)` prefixes so scoping tokens remain visible to clash analysis."""
    return re.sub(r":(?:where|is)\(([^()]+)\)", r"\1", selector)


def _extract_unscoped_classes_from_css(css_text: str) -> set[str]:
    cleaned = re.sub(r"/\*.*?\*/", "", css_text, flags=re.S)
    unscoped: set[str] = set()
    for match in re.finditer(r"([^{}@]+)\{[^{}]*\}", cleaned):
        prelude = match.group(1).strip()
        if not prelude or prelude.startswith("@"):
            continue
        for raw_sel in split_selectors(prelude):
            unwrapped = unwrap_attribute_where(raw_sel)
            bare = without_conditions(unwrapped)
            tokens = [t for t in re.split(r"[\s>+~]+", bare) if t]
            if not tokens:
                continue
            # If selector has >= 2 combinator segments starting with a scoping class/id/attr, it is scoped!
            if len(tokens) >= 2 and (
                tokens[0].startswith(".") or tokens[0].startswith("#")
            ):
                continue
            for cls_match in re.finditer(r"\.([a-zA-Z_][a-zA-Z0-9_-]*)", tokens[0]):
                unscoped.add(cls_match.group(1))
    return unscoped


def find_clashes(css_paths: Iterable[Path]) -> list[dict[str, Any]]:
    """Return all unscoped class names defined across >= 2 distinct CSS files."""
    by_class: dict[str, list[str]] = defaultdict(list)
    for raw_p in css_paths:
        p = Path(raw_p)
        if not p.is_file():
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore")
        for cls_name in sorted(_extract_unscoped_classes_from_css(txt)):
            by_class[cls_name].append(str(p))

    clashes: list[dict[str, Any]] = []
    for cls_name, files in sorted(by_class.items()):
        if len(files) >= 2:
            clashes.append(
                {
                    "class_name": cls_name,
                    "file_count": len(files),
                    "files": files,
                }
            )
    return clashes


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Detect unscoped cross-file CSS class clashes (P=1)."
    )
    parser.add_argument("paths", nargs="+", help="CSS files or directories to scan.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    css_files: list[Path] = []
    for item in args.paths:
        p = Path(item)
        if p.is_dir():
            css_files.extend(sorted(p.rglob("*.css")))
        elif p.is_file():
            css_files.append(p)

    clashes = find_clashes(css_files)
    if args.json:
        print(json.dumps({"passed": len(clashes) == 0, "clashes": clashes}, indent=2))
    else:
        for c in clashes:
            print(f"[CLASH] .{c['class_name']} in {', '.join(c['files'])}")
    return 1 if clashes else 0


if __name__ == "__main__":
    raise SystemExit(main())
