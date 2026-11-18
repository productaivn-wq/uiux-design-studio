import React, { useEffect, useRef, useState } from 'react';

export interface SlideStageEmbedProps {
  slideTitle: string;
  stageWidth?: number;
  stageHeight?: number;
  children?: React.ReactNode;
}

export function SlideStageEmbed({
  slideTitle,
  stageWidth = 720,
  stageHeight = 440,
  children,
}: SlideStageEmbedProps) {
  const stageRef = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState(false);
  const [beat, setBeat] = useState(0);

  useEffect(() => {
    const el = stageRef.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([entry]) => setActive(entry.isIntersecting),
      { threshold: 0.5 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  useEffect(() => {
    if (!active) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === ' ' || e.key === 'ArrowRight') {
        setBeat((b) => b + 1);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [active]);

  return (
    <div className="slide-surface" style={{ padding: 'clamp(24px, 2.5vw, 48px)' }}>
      <div style={{ fontSize: 'clamp(38px, 3.4vw, 60px)', fontWeight: 700, marginBottom: '0.6em' }}>
        {slideTitle}
      </div>
      <div
        ref={stageRef}
        data-stage-ui="true"
        data-paused={!active}
        data-beat={beat}
        className="ss-stage"
        style={{
          position: 'relative',
          width: `${stageWidth}px`,
          height: `${stageHeight}px`,
          overflow: 'hidden',
          borderRadius: '12px',
        }}
      >
        {children}
      </div>
    </div>
  );
}
