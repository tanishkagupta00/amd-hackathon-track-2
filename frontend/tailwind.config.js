import plugin from 'tailwindcss/plugin';

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  safelist: [
    'check-in', 'morph-in', 'morph-out', 'drag-glow', 'scan-line',
    'border-ai-indigo', 'border-ai-cyan', 'border-zinc-800',
    'text-ai-indigo', 'text-ai-cyan', 'text-white', 'text-zinc-400',
    'bg-ai-indigo', 'bg-ai-cyan', 'bg-zinc-900', 'bg-zinc-800',
  ],

  theme: {
    extend: {
      colors: {
        // Legacy tokens — kept to avoid crashes during refactor
        brand: { primary: '#1E293B', accent: '#EA580C' },
        cinematic: { violet: '#7c3aed', cyan: '#06b6d4' },
        navy: { 950: '#0c0e14', 900: '#12151d', 800: '#1a1f2b', 700: '#232838' },
        steel: { 600: '#5a6478', 300: '#9aa3b5' },
        gold: { 400: '#D4AF6A', 300: '#E0C48A', 100: '#F0DFB5' },
        ivory: { 50: '#F7F3EA' },
        // ✨ NEW PALETTE (Premium Black/Gold/White) ✨
        obsidian: '#070707',   // Deep, punchy dark background
        zinc: {
          950: '#070707',
          900: '#111111',      // Base card surface (dark charcoal)
          800: '#1C1C1C',      // Elevated surface / border
          700: '#3F3F46',      // Stronger border
          400: '#9E9E9E',      // Muted text
        },
        ai: {
          gold: '#D4AF37',       // Primary gold
          goldLight: '#E6C75C',  // Hover / bright
          goldDark: '#B8860B',   // Deep gold
          accent: '#F5E6A1',     // Soft accent text
          emerald: '#3DDC84',    // Success
          warning: '#FFB547',    // Warning
          rose: '#FF5C5C',       // Error (danger)
        }
      },
      fontFamily: {
        display: ['Space Grotesk', 'system-ui', 'sans-serif'],
      },
    },
  },

  plugins: [
    plugin(function({ addUtilities }) {
      addUtilities({
        // Dark-mode glass — now using zinc-900 base
        '.glass': {
          'background': 'rgba(24, 24, 27, 0.65)',
          'backdrop-filter': 'blur(16px)',
          '-webkit-backdrop-filter': 'blur(16px)',
          'border': '1px solid rgba(39, 39, 42, 0.8)',
          'box-shadow': '0 4px 30px rgba(0, 0, 0, 0.3)',
        },
      });
    }),
  ],
}
