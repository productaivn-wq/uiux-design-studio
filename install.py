#!/usr/bin/env python3
"""
Cross-IDE Skill Installer for UI/UX Design Studio (UIUXProMax + ProductArchitectureKit).
Installs the software UI/UX design skills into Claude Code, Cursor, Windsurf,
Google Antigravity, OpenAI Codex, or any local project workspace without modifying
this repository.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SKILLS_SRC = REPO_ROOT / "skills"
SKILL_NAMES = ["UIUXProMax", "ProductArchitectureKit"]

IDE_TARGETS = {
    "antigravity": {
        "description": "Google Antigravity (~/.gemini/config/skills/)",
        "global_path": Path.home() / ".gemini" / "config" / "skills",
        "project_rel": Path(".agent") / "skills",
    },
    "claude": {
        "description": "Claude Code (~/.claude/skills/ or ./.claude/skills/)",
        "global_path": Path.home() / ".claude" / "skills",
        "project_rel": Path(".claude") / "skills",
    },
    "cursor": {
        "description": "Cursor (~/.cursor/skills/ or ./.cursor/skills/)",
        "global_path": Path.home() / ".cursor" / "skills",
        "project_rel": Path(".cursor") / "skills",
    },
    "windsurf": {
        "description": "Windsurf (~/.codeium/windsurf/skills/ or ./.windsurf/skills/)",
        "global_path": Path.home() / ".codeium" / "windsurf" / "skills",
        "project_rel": Path(".windsurf") / "skills",
    },
    "codex": {
        "description": "OpenAI Codex (~/.codex/skills/ or ./.codex/skills/)",
        "global_path": Path.home() / ".codex" / "skills",
        "project_rel": Path(".codex") / "skills",
    },
    "agents": {
        "description": "Universal Agent Skills Standard (~/.agents/skills/ or ./.agents/skills/)",
        "global_path": Path.home() / ".agents" / "skills",
        "project_rel": Path(".agents") / "skills",
    },
}


def list_targets() -> None:
    print("Available AI IDE / Agent Targets:")
    print("-" * 72)
    for key, info in IDE_TARGETS.items():
        print(f"  {key:<14} : {info['description']}")
        print(f"                   Global : {info['global_path']}")
        print(f"                   Project: ./{info['project_rel'].as_posix()}")
    print("-" * 72)
    print("Examples:")
    print("  python install.py --ide claude --project /path/to/my-app")
    print("  python install.py --ide cursor --project /path/to/my-app --init-contracts")
    print("  python install.py --ide antigravity --global")


def install_to_destination(dest_skills_dir: Path, force: bool = False) -> list[Path]:
    installed: list[Path] = []
    dest_skills_dir.mkdir(parents=True, exist_ok=True)
    for skill_name in SKILL_NAMES:
        src = SKILLS_SRC / skill_name
        dst = dest_skills_dir / skill_name
        if dst.exists():
            if not force:
                print(f"[SKIP] {dst} already exists (pass --force to overwrite copy).")
                continue
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        installed.append(dst)
        print(f"[OK] Installed {skill_name} -> {dst}")
    return installed


def init_starter_contracts(project_dir: Path, force: bool = False) -> None:
    starter_dir = REPO_ROOT / "starter-templates"
    for fname in ["PRODUCT.md", "DESIGN.md"]:
        src = starter_dir / fname
        dst = project_dir / fname
        if dst.exists() and not force:
            print(f"[SKIP] {dst} already exists.")
            continue
        shutil.copy2(src, dst)
        print(f"[OK] Bootstrapped {dst}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install UIUXProMax & ProductArchitectureKit into your AI coding assistant or project."
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List supported AI IDEs and installation paths.",
    )
    parser.add_argument(
        "--ide",
        choices=[*IDE_TARGETS.keys(), "all"],
        default="agents",
        help="Target IDE/agent format (default: agents).",
    )
    parser.add_argument(
        "--project",
        type=Path,
        default=None,
        help="Install into a specific project directory (recommended for safe testing).",
    )
    parser.add_argument(
        "--global",
        dest="is_global",
        action="store_true",
        help="Install into the user's global home directory for the selected IDE.",
    )
    parser.add_argument(
        "--init-contracts",
        action="store_true",
        help="Also copy starter PRODUCT.md and DESIGN.md into --project root.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing target skill folders if present.",
    )

    args = parser.parse_args()

    if args.list:
        list_targets()
        return 0

    if not args.project and not args.is_global:
        list_targets()
        print("\nNote: Specify either --project <path> or --global to install.")
        return 0

    selected_ides = list(IDE_TARGETS.keys()) if args.ide == "all" else [args.ide]

    for ide_key in selected_ides:
        cfg = IDE_TARGETS[ide_key]
        if args.project:
            target_root = args.project.resolve() / cfg["project_rel"]
        else:
            target_root = cfg["global_path"]
        install_to_destination(target_root, force=args.force)

    if args.init_contracts and args.project:
        init_starter_contracts(args.project.resolve(), force=args.force)

    return 0


if __name__ == "__main__":
    sys.exit(main())
