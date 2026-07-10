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
        // ── NEW PALETTE (Hyper-Modern AI) ──
        obsidian: '#09090B',   // Deep, punchy dark background
        zinc: {
          950: '#09090B',
          900: '#18181B',      // Base card surface
          800: '#27272A',      // Elevated surface / border
          700: '#3F3F46',      // Stronger border
          400: '#A1A1AA',      // Secondary text
        },
        ai: {
          indigo: '#6366f1',   // Primary accent 1
          cyan: '#22d3ee',     // Primary accent 2
          emerald: '#10B981',  // Success
          rose: '#F43F5E',     // Error
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
