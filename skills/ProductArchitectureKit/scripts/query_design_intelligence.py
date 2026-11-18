"""
query_design_intelligence.py — Bridge to ui-ux-pro-max BM25 design intelligence.
Part of ProductArchitectureKit skill.

Enables agents to query 79 UI styles, 192 palettes, 74 typography pairings,
and 119 UX guidelines mapped to Domain 3 (Perception) and Domain 4 (Reality).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_skill_root = _here.parent
_vendor_search = (
    _skill_root
    / "vendor"
    / "ui_ux_pro_max"
    / "src"
    / "ui-ux-pro-max"
    / "scripts"
    / "search.py"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Query Design Intelligence (ProductArchitectureKit)"
    )
    parser.add_argument(
        "query",
        type=str,
        help="Search query (e.g. 'luxury dark nautical', 'dashboard density', 'saas fintech')",
    )
    parser.add_argument(
        "--domain",
        type=str,
        default="",
        help="Domain filter: style, color, typography, ux, icons, etc.",
    )
    parser.add_argument(
        "--stack",
        type=str,
        default="",
        help="Tech stack: html-tailwind, react, nextjs, vue, etc.",
    )
    parser.add_argument(
        "--design-system",
        action="store_true",
        help="Generate complete design system specification",
    )
    parser.add_argument(
        "--invariants",
        action="store_true",
        help="Print all codified governance invariants (GW-DATA-01, GW-HEADLESS-01, etc.)",
    )
    parser.add_argument(
        "--architecture",
        action="store_true",
        help="Print the 5 Domains of Product Architecture and Layer 0 Laws",
    )
    parser.add_argument(
        "--catalog",
        action="store_true",
        help="Output summary of extracted design intelligence catalog",
    )
    args = parser.parse_args()

    # Fast direct JSON lookups
    catalog_path = _skill_root / "resources" / "design_intelligence_catalog.json"
    invariants_path = _skill_root / "resources" / "governance_invariants.json"

    import json

    if args.invariants:
        if invariants_path.exists():
            with open(invariants_path, encoding="utf-8") as f:
                data = json.load(f)
            print("## Codified Governance Invariants\n")
            for gid, ginfo in data.items():
                print(f"### {gid}: {ginfo['name']}")
                print(f"{ginfo['rule']}\n")
            return 0

    if args.architecture or (
        args.query and args.query.lower() in ["architecture", "domains", "layer0"]
    ):
        if catalog_path.exists():
            with open(catalog_path, encoding="utf-8") as f:
                data = json.load(f)
            pa = data.get("prompt_architecture", {})
            print("## 5 Domains of Product Architecture\n")
            for dom, desc in pa.get("domains_of_product_architecture", {}).items():
                print(f"- **{dom}**: {desc}")
            print("\n## Layer 0 Architectural Laws\n")
            for lvl, laws in pa.get("layer_0_laws", {}).items():
                print(f"### {lvl.replace('_', ' ').title()}")
                for law_name, law_desc in laws.items():
                    print(f"- **{law_name.replace('_', ' ').title()}**: {law_desc}")
            return 0

    if args.catalog:
        if catalog_path.exists():
            with open(catalog_path, encoding="utf-8") as f:
                data = json.load(f)
            rc = data.get("repo_catalog", {})
            print("## Design Intelligence Catalog Summary\n")
            print(f"- Total Palettes: {rc.get('total_palettes')}")
            print(f"- Total UX Guidelines: {rc.get('total_ux_rules')}")
            print(f"- Version: {data.get('version')}")
            return 0

    if not _vendor_search.exists():
        print(f"[ERROR] Vendor search engine not found at: {_vendor_search}")
        return 1

    cmd = [sys.executable, "-u", str(_vendor_search), args.query]
    if args.domain:
        cmd.extend(["--domain", args.domain])
    if args.stack:
        cmd.extend(["--stack", args.stack])
    if args.design_system:
        cmd.append("--design-system")
    if args.max_results:
        cmd.extend(["--max-results", str(args.max_results)])

    proc = subprocess.run(
        cmd,
        cwd=str(_vendor_search.parent),
        capture_output=True,
        text=True,
        encoding="utf-8",
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
