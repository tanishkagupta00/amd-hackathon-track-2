import { useEffect, useRef, useState } from 'react';
import Orb from './Orb';
import './OrbWithCaptions.css';

// Placeholder captions spanning all 4 required styles — swap these for real
// generated captions once your Fireworks pipeline is wired up.
// Emojis that fit the AI video generation theme
const DEFAULT_CAPTIONS = ['✨', '🔥', '🚀', '💡', '🎬', '🤖', '⚡', '🌟', '🎯', '🎨'];

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export default function OrbWithCaptions({
  captions = DEFAULT_CAPTIONS,
  chipCount = 7,
  hue = 0,
  ...orbProps
}) {
  const [hovered, setHovered] = useState(false);
  const [chips, setChips] = useState([]);
  const clearTimer = useRef(null);

  useEffect(() => {
    if (hovered) {
      clearTimeout(clearTimer.current);
      const pool = shuffle(captions).slice(0, chipCount);
      const angleStep = 360 / pool.length;

      const next = pool.map((text, i) => {
        const angle = angleStep * i + (Math.random() * 30 - 15); // jitter
        const rad = (angle * Math.PI) / 180;
        
        // Start slightly inside the visual circumference (~180px) so they pierce through
        const startRadius = 180;
        // Float far outwards to fill the rest of the screen
        const endRadius = startRadius + 150 + Math.random() * 250;

        return {
          id: `${Date.now()}-${i}`,
          text,
          start_dx: Math.cos(rad) * startRadius,
          start_dy: Math.sin(rad) * startRadius,
          dx: Math.cos(rad) * endRadius,
          dy: Math.sin(rad) * endRadius,
          delay: i * 60,
        };
      });
      setChips(next.map((c) => ({ ...c, phase: 'entering' })));
    } else if (chips.length) {
      setChips((prev) =>
        prev.map((c, i) => ({
          ...c,
          phase: 'exiting',
          delay: (prev.length - 1 - i) * 45,
        }))
      );
      clearTimer.current = setTimeout(() => setChips([]), 650);
    }
    return () => clearTimeout(clearTimer.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hovered]);

  return (
    <div
      className="orb-caption-wrapper"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <Orb hue={hue} {...orbProps} />

      <div className="caption-burst-layer">
        {chips.map((chip) => (
          <div
            key={chip.id}
            className={`caption-chip-outer ${chip.phase}`}
            style={{
              '--dx': `${chip.dx}px`,
              '--dy': `${chip.dy}px`,
              '--delay': `${chip.delay}ms`,
            }}
          >
            <div
              className="caption-chip-inner"
              style={{ '--hue': hue, '--delay': `${chip.delay}ms` }}
            >
              <span className="caption-chip-text">{chip.text}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
