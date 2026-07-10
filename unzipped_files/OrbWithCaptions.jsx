import { useEffect, useRef, useState } from 'react';
import Orb from './Orb';
import './OrbWithCaptions.css';

// Placeholder captions spanning all 4 required styles — swap these for real
// generated captions once your Fireworks pipeline is wired up.
const DEFAULT_CAPTIONS = [
  'A golden retriever chasing waves at sunset',
  "Oh great, another 'life-changing' vacation video",
  'while(true) { admire_dog(); } // never breaks',
  'Dog goes brrr near water, humans lose it',
  'Urban traffic moves through a rain-soaked intersection',
  "Wow, cars. On a road. Groundbreaking stuff",
];

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
  chipCount = 6,
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
        const angle = angleStep * i + (Math.random() * 22 - 11); // jitter
        const distance = 95 + Math.random() * 55;
        const rad = (angle * Math.PI) / 180;
        return {
          id: `${Date.now()}-${i}`,
          text,
          dx: Math.cos(rad) * distance,
          dy: Math.sin(rad) * distance,
          delay: i * 70,
        };
      });
      setChips(next.map((c) => ({ ...c, phase: 'entering' })));
    } else if (chips.length) {
      setChips((prev) =>
        prev.map((c, i) => ({
          ...c,
          phase: 'exiting',
          delay: (prev.length - 1 - i) * 55,
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
