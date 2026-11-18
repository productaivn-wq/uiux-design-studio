"""
slidewright_stage_embed.py — Vector C5 SlideWright Live Stage Embed Adapter (P=1).

Generates Vite+React `<StageSlideFrame>`, Zero-Build HTML `<section>`, and 1:1 Bento slide grids
respecting SlideWright's `.slide-surface` two-layer padding contract, projection `clamp()` typography
outside `.ss-stage`, Bento Iron Rules #12 & #14, off-slide IntersectionObserver pause, and presenter clicker sync.
"""

from __future__ import annotations

from typing import Any


def generate_react_stage_slide_component(
    slide_title: str,
    stage_width: int = 720,
    stage_height: int = 440,
) -> str:
    return f"""import React, {{ useEffect, useRef, useState }} from 'react';

export function StageSlideFrame({{ children }}: {{ children?: React.ReactNode }}) {{
  const stageRef = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState(false);
  const [beat, setBeat] = useState(0);

  useEffect(() => {{
    const node = stageRef.current;
    if (!node) return;
    const io = new IntersectionObserver(
      ([entry]) => setActive(entry.isIntersecting),
      {{ threshold: 0.5 }}
    );
    io.observe(node);
    return () => io.disconnect();
  }}, []);

  useEffect(() => {{
    if (!active) return;
    const onKey = (e: KeyboardEvent) => {{
      if (e.key === ' ' || e.key === 'ArrowRight') {{
        setBeat((b) => b + 1);
      }}
    }};
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }}, [active]);

  return (
    <div className="slide-surface" style={{{{ padding: 'clamp(24px, 2.5vw, 48px)' }}}}>
      <div style={{{{ fontSize: 'clamp(38px, 3.4vw, 60px)', fontWeight: 700, marginBottom: '0.6em' }}}}>
        {slide_title}
      </div>
      <div
        ref={{stageRef}}
        data-stage-ui="true"
        data-paused={{!active}}
        data-beat={{beat}}
        className="ss-stage"
        style={{{{
          position: 'relative',
          width: '{stage_width}px',
          height: '{stage_height}px',
          overflow: 'hidden',
          borderRadius: '12px',
        }}}}
      >
        {{children}}
      </div>
    </div>
  );
}}
"""


def generate_html_stage_slide_section(
    slide_id: str,
    slide_title: str,
    stage_width: int = 720,
    stage_height: int = 420,
) -> str:
    return f"""<section id="{slide_id}" class="slide" style="padding: clamp(40px, 5vh, 80px) clamp(48px, 5vw, 120px);">
  <style>
    @media (prefers-reduced-motion: reduce) {{
      #{slide_id} [data-stage-ui="true"] * {{
        transition: none !important;
        animation: none !important;
      }}
    }}
  </style>
  <div class="slide-surface" style="padding: clamp(24px, 2.5vw, 48px);">
    <div style="font-size: clamp(38px, 3.4vw, 60px); font-weight: 700; margin-bottom: 0.6em;">{slide_title}</div>
    <div
      class="ss-stage"
      data-stage-ui="true"
      data-paused="false"
      style="position: relative; width: {stage_width}px; height: {stage_height}px; overflow: hidden; border-radius: 12px;"
    ></div>
  </div>
  <script>
    (() => {{
      const root = document.querySelector('#{slide_id} [data-stage-ui="true"]');
      if (!root) return;
      const io = new IntersectionObserver(([entry]) => {{
        root.setAttribute('data-paused', String(!entry.isIntersecting));
      }}, {{ threshold: 0.5 }});
      io.observe(root);
    }})();
  </script>
</section>
"""


def generate_bento_slide_grid(tiles: list[dict[str, Any]]) -> str:
    """Enforces Bento Iron Rule #12 (1:1 Stage per tile) and #14 (white-space: nowrap on stat numerals)."""
    blocks: list[str] = []
    for tile in tiles:
        tid = tile.get("id", "tile")
        kind = tile.get("kind", "component")
        title = tile.get("title", "")
        unit = tile.get("unit", "")
        if kind == "stat" or unit:
            inner = (
                f'<div class="ss-bento-stat" style="white-space: nowrap; font-variant-numeric: tabular-nums lining-nums;">'
                f"{title} {unit}".strip()
                + "</div>"
            )
        else:
            inner = f'<div class="ss-bento-caption">{title}</div>'
        blocks.append(
            f'  <article class="slide-surface ss-bento-tile" data-tile-id="{tid}" data-tile-kind="{kind}" style="padding: clamp(24px, 2.5vw, 48px);">\n'
            f'    <div class="ss-stage" data-stage-ui="true" style="position: relative; overflow: hidden;">{inner}</div>\n'
            f"  </article>"
        )
    joined = "\n".join(blocks)
    return f'<div class="ss-bento-slide-grid" style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px;">\n{joined}\n</div>\n'
