import { useNavigate } from 'react-router-dom';
import { Sparkles, Video, BrainCircuit, Wand2, ChevronRight, Github } from 'lucide-react';
import OrbWithCaptions from '../components/OrbWithCaptions';

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-obsidian text-white flex flex-col font-sans selection:bg-ai-indigo/30">

      {/* ── Navbar ── */}
      <nav className="w-full flex items-center justify-between px-6 sm:px-8 py-5 max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          {/* Logo — vibrant gradient */}
          <div className="p-1.5 bg-gradient-to-tr from-ai-indigo to-ai-cyan rounded-xl shadow-lg shadow-ai-indigo/20">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <span className="font-bold tracking-tight text-base font-display text-white">
            CaptionForge AI
          </span>
        </div>

        <div className="flex items-center gap-5">
          <a
            href="https://github.com/tanishkagupta00/amd-hackathon-track-2"
            target="_blank"
            rel="noreferrer"
            className="text-zinc-400 hover:text-white transition-colors duration-150
              flex items-center gap-2 text-sm font-medium
              focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ai-cyan/40 rounded-md px-1"
          >
            <Github className="h-4 w-4" />
            <span className="hidden sm:inline">GitHub</span>
          </a>
          <button
            onClick={() => navigate('/app')}
            className="px-4 py-2 rounded-full text-sm font-semibold
              bg-white hover:bg-zinc-200 text-obsidian
              transition-colors duration-150
              shadow-[0_0_16px_rgba(255,255,255,0.1)] hover:shadow-[0_0_24px_rgba(255,255,255,0.2)]
              focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-obsidian"
          >
            Launch App
          </button>
        </div>
      </nav>

      {/* ── Hero ── */}
      <main className="flex-1 flex flex-col items-center justify-center text-center px-4 relative overflow-hidden">

        {/* Ambient Orb — Interactive Background */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] opacity-70">
          <OrbWithCaptions hue={20} hoverIntensity={0.6} rotateOnHover={true} backgroundColor="#09090B" />
        </div>

        <div className="z-10 max-w-4xl space-y-8 mt-10 mb-20 pointer-events-none">

          {/* Live badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full
            glass border border-zinc-800 text-sm text-zinc-300">
            <span className="h-2 w-2 rounded-full bg-ai-cyan animate-pulse" />
            AMD Developer Hackathon · Track 2
          </div>

          {/* H1 */}
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight leading-[1.08] font-display">
            Intelligent Video Captions,{' '}
            <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-ai-indigo to-ai-cyan">
              Generated with Style.
            </span>
          </h1>

          <p className="text-base md:text-lg text-zinc-400 max-w-xl mx-auto leading-relaxed">
            Upload any video. Our multi-stage Extract → Reason → Style AI pipeline
            analyses visual content and renders captions in four bespoke tones — instantly.
          </p>

          {/* CTA */}
          <div className="flex items-center justify-center gap-4 pt-2 pointer-events-auto">
            <button
              onClick={() => navigate('/app')}
              className="group relative inline-flex items-center justify-center gap-2
                px-8 py-3.5 rounded-full overflow-hidden
                bg-gradient-to-r from-ai-indigo to-ai-cyan text-white font-bold text-base
                transition-all duration-200 hover:scale-[1.03]
                hover:shadow-[0_0_36px_rgba(99,102,241,0.4)]
                focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ai-indigo focus-visible:ring-offset-2 focus-visible:ring-offset-obsidian"
            >
              <span className="relative">Get Started</span>
              <ChevronRight className="relative h-4 w-4 group-hover:translate-x-0.5 transition-transform duration-150" />
            </button>
          </div>
        </div>

        {/* ── Feature cards ── */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 max-w-5xl w-full z-10 pb-20 px-2">
          {[
            {
              Icon: Video,
              title: 'Vision Extraction',
              body: 'Motion-aware keyframe sampling and semantic scene understanding — captures exactly what is happening.',
            },
            {
              Icon: BrainCircuit,
              title: 'Temporal Reasoning',
              body: 'LLM-powered scene graph analysis connects visual events across time into a coherent narrative.',
            },
            {
              Icon: Wand2,
              title: 'Style Matrix',
              body: 'Parallel style transformers output Formal, Sarcastic, Humorous-Tech, and Humorous-Non-Tech captions.',
            },
          ].map(({ Icon, title, body }) => (
            <div
              key={title}
              className="glass border border-zinc-800 p-7 rounded-2xl
                hover:border-zinc-700 hover:-translate-y-0.5 bg-zinc-900/50 hover:bg-zinc-900
                transition-all duration-200 shadow-2xl shadow-black/50
                focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ai-cyan/40"
              tabIndex={0}
            >
              <div className="h-10 w-10 rounded-xl flex items-center justify-center mb-5 border bg-zinc-950 border-zinc-800">
                <Icon className="h-5 w-5 text-ai-cyan" />
              </div>
              <h3 className="text-base font-bold text-white font-display mb-2">{title}</h3>
              <p className="text-sm text-zinc-400 leading-relaxed">{body}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
