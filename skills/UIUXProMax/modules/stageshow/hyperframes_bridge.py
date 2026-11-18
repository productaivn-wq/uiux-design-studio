"""
hyperframes_bridge.py — Vector C4 HyperFrames Seekable Composition Bridge (P=1).

Exports StageShow's 6 launch-film cubic-bezier curves (`ease.ts`) and renders seek-safe
HyperFrames HTML composition blocks quarantined under `data-stage-ui="true"`.
"""

from __future__ import annotations

STAGESHOW_EASE_CURVES: dict[str, tuple[float, float, float, float]] = {
    "house": (0.45, 0, 0.1, 1),
    "through": (0.38, 0, 0.85, 0.22),
    "settle": (0.16, 0.84, 0.26, 1),
    "enter": (0.25, 0.8, 0.25, 1),
    "trip": (0.34, 1.3, 0.64, 1),
    "camera": (0.4, 0, 0.2, 1),
}


def format_cubic_bezier(curve: tuple[float, float, float, float]) -> str:
    return f"cubic-bezier({curve[0]:g}, {curve[1]:g}, {curve[2]:g}, {curve[3]:g})"


def render_seekable_stage_snippet(
    scene_id: str,
    duration_sec: float = 12.0,
    ease: str = "house",
) -> str:
    """Renders a seek-safe HyperFrames HTML composition block with StageShow launch-film easing."""
    selected = STAGESHOW_EASE_CURVES.get(ease, STAGESHOW_EASE_CURVES["house"])
    active_css = format_cubic_bezier(selected)
    camera_css = format_cubic_bezier(STAGESHOW_EASE_CURVES["camera"])

    return f"""<!-- HyperFrames Seekable StageShow Composition: {scene_id} -->
<div class="hf-stageshow-clip" data-scene-id="{scene_id}" data-start="0" data-duration="{duration_sec}">
  <style>
    :root {{
      --ease-ss-house: {format_cubic_bezier(STAGESHOW_EASE_CURVES["house"])};
      --ease-ss-through: {format_cubic_bezier(STAGESHOW_EASE_CURVES["through"])};
      --ease-ss-settle: {format_cubic_bezier(STAGESHOW_EASE_CURVES["settle"])};
      --ease-ss-enter: {format_cubic_bezier(STAGESHOW_EASE_CURVES["enter"])};
      --ease-ss-trip: {format_cubic_bezier(STAGESHOW_EASE_CURVES["trip"])};
      --ease-ss-camera: {camera_css};
      --ease-ss-active: {active_css};
    }}
    @media (prefers-reduced-motion: reduce) {{
      .ss-stage[data-stage-ui="true"] * {{
        animation-duration: 0.001ms !important;
        transition-duration: 0.001ms !important;
      }}
    }}
  </style>
  <div class="ss-stage" data-stage-ui="true" data-crop="true" style="position: relative; overflow: hidden; transition-timing-function: var(--ease-ss-active);">
    <div class="ss-camera" style="transition: transform 800ms var(--ease-ss-camera);"></div>
  </div>
</div>
"""
