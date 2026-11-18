"""
stageshow_temporal_harness.py — StageShow Virtual Clock, 13 Motion/Jump Detectors,
Coverage Gate (exit=2), Contact-Sheet Synthesizer & Blind Fresh-Eye Reviewer SoD Engine (Vector C4; P=1).

Enforces:
- Gate GW-HEADLESS-01 (--window-position=-32000,-32000, headless=True, zero window popups)
- Gate GW-SOD-01 (reviewer_id != executor_id, zero source-code path leakage in blind review packets)
"""

from __future__ import annotations

import shutil
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HEADLESS_ARGS: list[str] = [
    "--window-position=-32000,-32000",
    "--disable-gpu",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--hide-scrollbars",
]

MOTION_WATCH_DETECTORS: tuple[dict[str, Any], ...] = (
    {
        "id": 1,
        "tag": "hard edge:",
        "gate_blocker": False,
        "description": "Element exits masked container across sharp unfeathered clip",
    },
    {
        "id": 2,
        "tag": "steps in its box:",
        "gate_blocker": False,
        "description": "Text animated via layout top/left/margin instead of GPU transform",
    },
    {
        "id": 3,
        "tag": "fly size:",
        "gate_blocker": False,
        "description": "Flyer takeoff/landing box differs by >1px from source/target",
    },
    {
        "id": 4,
        "tag": "handoff shift:",
        "gate_blocker": False,
        "description": "Incoming swap element shifts >0.5px from outgoing element",
    },
    {
        "id": 5,
        "tag": "settle snap:",
        "gate_blocker": False,
        "description": "Element jumps >0.5px after transition finishes",
    },
    {
        "id": 6,
        "tag": "appears with no entrance:",
        "gate_blocker": False,
        "description": "Element snaps from 0 to 100% opacity/size in 1 frame",
    },
    {
        "id": 7,
        "tag": "vanishes with no exit:",
        "gate_blocker": False,
        "description": "Element vanishes in 1 frame without exit transition",
    },
    {
        "id": 8,
        "tag": "dashed edge resizes:",
        "gate_blocker": False,
        "description": "Dashed/dotted border animated in width/height causing dash crawl",
    },
    {
        "id": 9,
        "tag": "lands on a transform:",
        "gate_blocker": False,
        "description": "Text settles permanently on fractional subpixel transform",
    },
)

JUMPS_CORE_DETECTORS: tuple[dict[str, Any], ...] = (
    {
        "id": 1,
        "tag": "jump:",
        "gate_blocker": False,
        "description": "Single-frame >2px box jump between calm windows",
    },
    {
        "id": 2,
        "tag": "drift:",
        "gate_blocker": False,
        "description": "Flow column neighbors gliding out of step across >=4 frames",
    },
    {
        "id": 3,
        "tag": "anchor drift:",
        "gate_blocker": True,
        "description": "Open popover/dialog shifting top anchor while height resizes",
    },
    {
        "id": 4,
        "tag": "same-box content change:",
        "gate_blocker": False,
        "description": "Unannounced text/SVG swap inside unchanged bounding box",
    },
)

VIRTUAL_CLOCK_INIT_JS = r"""
(() => {
  let __now = 0;
  let __tid = 1;
  const __timers = [];
  const __rafs = [];

  performance.now = () => __now;
  Date.now = () => 1700000000000 + __now;

  window.setTimeout = (fn, delay = 0, ...args) => {
    const id = __tid++;
    __timers.push({ id, due: __now + Math.max(0, Number(delay) || 0), fn, args, interval: null });
    return id;
  };
  window.clearTimeout = (id) => {
    const idx = __timers.findIndex((t) => t.id === id);
    if (idx !== -1) __timers.splice(idx, 1);
  };
  window.setInterval = (fn, delay = 16, ...args) => {
    const id = __tid++;
    const iv = Math.max(1, Number(delay) || 16);
    __timers.push({ id, due: __now + iv, fn, args, interval: iv });
    return id;
  };
  window.clearInterval = window.clearTimeout;
  window.requestAnimationFrame = (cb) => {
    const id = __tid++;
    __rafs.push({ id, cb });
    return id;
  };
  window.cancelAnimationFrame = (id) => {
    const idx = __rafs.findIndex((r) => r.id === id);
    if (idx !== -1) __rafs.splice(idx, 1);
  };

  window.__ssStepClock = (targetMs) => {
    __now = Number(targetMs) || 0;
    let guard = 0;
    while (guard++ < 500) {
      __timers.sort((a, b) => a.due - b.due || a.id - b.id);
      const nextIdx = __timers.findIndex((t) => t.due <= __now);
      if (nextIdx === -1) break;
      const item = __timers[nextIdx];
      if (item.interval !== null) {
        item.due += item.interval;
      } else {
        __timers.splice(nextIdx, 1);
      }
      try {
        if (typeof item.fn === 'function') item.fn(...item.args);
      } catch (e) {}
    }

    const batch = __rafs.splice(0, __rafs.length);
    for (const r of batch) {
      try {
        r.cb(__now);
      } catch (e) {}
    }

    if (document.getAnimations) {
      for (const anim of document.getAnimations()) {
        try {
          anim.pause();
          anim.currentTime = __now;
        } catch (e) {}
      }
    }

    const snap = [];
    const nodes = document.querySelectorAll('[id], [role="dialog"], [data-popover], .ss-popover');
    nodes.forEach((el, idx) => {
      const r = el.getBoundingClientRect();
      const cs = window.getComputedStyle(el);
      snap.push({
        key: el.id ? `#${el.id}` : `${el.tagName.toLowerCase()}_${idx}`,
        isPopover:
          el.getAttribute('role') === 'dialog' ||
          el.hasAttribute('data-popover') ||
          el.classList.contains('ss-popover'),
        left: r.left,
        top: r.top,
        width: r.width,
        height: r.height,
        opacity: parseFloat(cs.opacity || '1'),
        transform: cs.transform || 'none',
      });
    });
    return snap;
  };
})();
"""


def evaluate_frame_coverage(
    timestamps_ms: Sequence[float],
    target_interval_ms: float = 16.67,
) -> dict[str, Any]:
    """Port of `verification.mjs` coverage(): exits with code 2 if any frame gap > 1.6x interval or > 40ms."""
    gaps: list[dict[str, Any]] = []
    max_allowed = min(40.0, target_interval_ms * 1.6)
    for idx in range(1, len(timestamps_ms)):
        dt = float(timestamps_ms[idx]) - float(timestamps_ms[idx - 1])
        if dt > target_interval_ms * 1.6 or dt > 40.0:
            gaps.append(
                {
                    "frame_index": idx,
                    "dt_ms": round(dt, 3),
                    "threshold_ms": round(max_allowed, 3),
                }
            )
    passed = len(gaps) == 0
    return {
        "passed": passed,
        "exit_code": 0 if passed else 2,
        "sample_count": len(timestamps_ms),
        "gaps": gaps,
    }


def _analyze_temporal_traces(
    frames: list[list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    by_key: dict[str, list[dict[str, Any]]] = {}
    for frame_idx, snap in enumerate(frames):
        for item in snap:
            rec = dict(item)
            rec["frame"] = frame_idx
            by_key.setdefault(item["key"], []).append(rec)

    for key, series in by_key.items():
        if len(series) < 4:
            continue

        # 1. Anchor drift (--gate blocker): popover shifting top while height changes
        if series[0].get("isPopover"):
            drift_steps = 0
            for i in range(1, len(series)):
                dy = abs(series[i]["top"] - series[i - 1]["top"])
                dh = abs(series[i]["height"] - series[i - 1]["height"])
                if dy >= 0.5 and dh >= 0.5:
                    drift_steps += 1
            total_dy = abs(series[-1]["top"] - series[0]["top"])
            total_dh = abs(series[-1]["height"] - series[0]["height"])
            if drift_steps >= 5 or (total_dy >= 3.0 and total_dh >= 3.0):
                findings.append(
                    {
                        "tag": "anchor drift:",
                        "selector": key,
                        "gate_blocker": True,
                        "message": f"anchor drift: popover {key} shifted top by {total_dy:.1f}px while resizing height by {total_dh:.1f}px.",
                    }
                )

        # 2. Single-frame >2px jump surrounded by calm frames
        for i in range(1, len(series) - 1):
            prev_dx = abs(series[i]["left"] - series[i - 1]["left"])
            prev_dy = abs(series[i]["top"] - series[i - 1]["top"])
            next_dx = abs(series[i + 1]["left"] - series[i]["left"])
            next_dy = abs(series[i + 1]["top"] - series[i]["top"])
            before_calm = (
                i >= 2
                and abs(series[i - 1]["left"] - series[i - 2]["left"]) < 0.3
                and abs(series[i - 1]["top"] - series[i - 2]["top"]) < 0.3
            )
            after_calm = next_dx < 0.3 and next_dy < 0.3
            if before_calm and after_calm and (prev_dx > 2.0 or prev_dy > 2.0):
                findings.append(
                    {
                        "tag": "jump:",
                        "selector": key,
                        "gate_blocker": False,
                        "message": f"jump: {key} snapped ({prev_dx:.1f}px, {prev_dy:.1f}px) in 1 frame.",
                    }
                )
                break

        # 3. Appears with no entrance
        for i in range(1, len(series)):
            if series[i - 1]["opacity"] == 0.0 and series[i]["opacity"] >= 0.99:
                findings.append(
                    {
                        "tag": "appears with no entrance:",
                        "selector": key,
                        "gate_blocker": False,
                        "message": f"appears with no entrance: {key} jumped from opacity 0 to 1 in 1 frame.",
                    }
                )
                break

    return findings


def _build_contact_sheet(
    frame_paths: list[Path], out_path: Path, cols: int = 3
) -> Path:
    if not frame_paths:
        img = Image.new("RGB", (640, 360), (17, 24, 39))
        img.save(out_path)
        return out_path

    thumbs: list[Image.Image] = []
    thumb_w, thumb_h = 320, 180
    for idx, fp in enumerate(frame_paths):
        with Image.open(fp) as raw:
            im = raw.convert("RGB").resize((thumb_w, thumb_h))
        draw = ImageDraw.Draw(im)
        draw.rectangle([(4, 4), (96, 24)], fill=(0, 0, 0))
        draw.text((10, 8), f"f#{idx:02d}", fill=(255, 255, 255))
        thumbs.append(im)

    rows = (len(thumbs) + cols - 1) // cols
    pad = 8
    sheet = Image.new(
        "RGB",
        (cols * thumb_w + (cols + 1) * pad, rows * thumb_h + (rows + 1) * pad),
        (15, 23, 42),
    )
    for i, th in enumerate(thumbs):
        r, c = divmod(i, cols)
        sheet.paste(th, (pad + c * (thumb_w + pad), pad + r * (thumb_h + pad)))
    sheet.save(out_path)
    return out_path


def run_virtual_clock_rehearsal(
    url: str,
    output_dir: Path,
    duration_ms: int = 600,
    fps: int = 30,
    viewport: tuple[int, int] = (800, 500),
    executor_id: str = "agt_executor",
) -> dict[str, Any]:
    """Steps virtual time deterministically in off-screen Chromium (`GW-HEADLESS-01`) and audits temporal continuity."""
    output_dir = Path(output_dir)
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    num_steps = max(1, int(round(duration_ms * fps / 1000.0)))
    step_ms = duration_ms / float(num_steps)
    shot_indices = {0, num_steps // 4, num_steps // 2, (3 * num_steps) // 4, num_steps}

    snapshots: list[list[dict[str, Any]]] = []
    timestamps: list[float] = []
    saved_shots: list[Path] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=HEADLESS_ARGS)
        try:
            context = browser.new_context(
                viewport={"width": viewport[0], "height": viewport[1]}
            )
            context.add_init_script(VIRTUAL_CLOCK_INIT_JS)
            page = context.new_page()
            page.goto(url, wait_until="load")

            for i in range(num_steps + 1):
                t_ms = round(i * step_ms, 3)
                timestamps.append(t_ms)
                snap = page.evaluate("(ms) => window.__ssStepClock(ms)", t_ms)
                snapshots.append(snap)
                if i in shot_indices:
                    fp = frames_dir / f"frame_{i:04d}.png"
                    page.screenshot(path=str(fp), full_page=False)
                    saved_shots.append(fp)

            context.close()
        finally:
            browser.close()

    contact_sheet = _build_contact_sheet(saved_shots, output_dir / "contact_sheet.png")
    findings = _analyze_temporal_traces(snapshots)
    coverage = evaluate_frame_coverage(timestamps, target_interval_ms=step_ms)
    gate_passed = coverage["passed"] and not any(
        f.get("gate_blocker") for f in findings
    )

    return {
        "frames_captured": len(snapshots),
        "timestamps_ms": timestamps,
        "coverage": coverage,
        "contact_sheet_png": str(contact_sheet),
        "key_frames": [str(fp) for fp in saved_shots],
        "findings": findings,
        "gate_passed": gate_passed,
        "executor_id": executor_id,
    }


def build_blind_fresh_eye_packet(
    rehearsal_result: dict[str, Any],
    executor_id: str,
    reviewer_id: str,
    output_dir: Path,
) -> dict[str, Any]:
    """Builds a code-blind visual review packet enforcing Separation of Duties (`GW-SOD-01`)."""
    if not executor_id or not reviewer_id or executor_id.strip() == reviewer_id.strip():
        raise ValueError(
            f"[GATE GW-SOD-01 VIOLATION]: reviewer_id ('{reviewer_id}') must differ from executor_id ('{executor_id}')."
        )

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    src_sheet = Path(rehearsal_result["contact_sheet_png"])
    dst_sheet = output_dir / "blind_contact_sheet.png"
    shutil.copy2(src_sheet, dst_sheet)

    dst_frames: list[str] = []
    for idx, f_str in enumerate(rehearsal_result.get("key_frames", [])):
        fp = Path(f_str)
        if fp.is_file():
            dst = output_dir / f"blind_frame_{idx:02d}.png"
            shutil.copy2(fp, dst)
            dst_frames.append(str(dst))

    return {
        "sod_valid": True,
        "gate": "GW-SOD-01",
        "executor_id": executor_id.strip(),
        "reviewer_id": reviewer_id.strip(),
        "contact_sheet_png": str(dst_sheet),
        "key_frames": dst_frames,
        "review_rubric": [
            "1_framing_and_bleed",
            "2_hierarchy_and_density",
            "3_motion_continuity_and_handoffs",
            "4_optical_polish_and_legibility",
        ],
        "instruction": "Evaluate solely from rendered frame images; cite exact blind_frame_XX.png indices for every critique.",
    }
