import { useNavigate } from 'react-router-dom';
import { Sparkles, Video, BrainCircuit, Wand2, ChevronRight, Github, Zap, Shield, Layers, Gauge, Code2, Target, CheckCircle2, Eye, Cpu, Clock } from 'lucide-react';
import TextGalaxy from '../components/TextGalaxy';

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-obsidian text-white font-sans selection:bg-ai-indigo/30">

      {/* ── Fixed Background ── */}
      <div className="fixed top-0 left-0 w-full h-screen pointer-events-none z-0 overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <TextGalaxy density={160} speed={1.2} />
        </div>
      </div>

      {/* ── Scrollable Content ── */}
      <div className="relative z-10">

        {/* ── Navbar ── */}
        <nav className="w-full flex items-center justify-between px-6 sm:px-8 py-5 max-w-7xl mx-auto sticky top-0 z-50">
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

        {/* ── Hero Section ── */}
        <section className="min-h-screen flex flex-col items-center justify-center text-center px-4 py-20">
          <div className="max-w-4xl space-y-8 mt-10 mb-20">

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

            <p className="text-base md:text-lg text-zinc-400 max-w-2xl mx-auto leading-relaxed">
              Upload any video. Our multi-stage Extract → Reason → Style AI pipeline
              analyses visual content and renders captions in four bespoke tones — instantly.
            </p>

            {/* CTA */}
            <div className="flex items-center justify-center gap-4 pt-2">
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

            {/* Stats */}
            <div className="grid grid-cols-3 gap-8 pt-12 max-w-2xl mx-auto">
              {[
                { label: '4 Styles', value: 'Formal, Sarcastic, Humorous' },
                { label: 'Multi-Stage', value: 'AI Pipeline' },
                { label: 'High Accuracy', value: 'Zero Hallucination' }
              ].map((stat, i) => (
                <div key={i} className="text-center">
                  <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-ai-indigo to-ai-cyan mb-1">
                    {stat.label}
                  </div>
                  <div className="text-xs text-zinc-500">{stat.value}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Core Features ── */}
        <section className="py-20 px-4">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-bold font-display mb-4">
                Powered by <span className="text-transparent bg-clip-text bg-gradient-to-r from-ai-indigo to-ai-cyan">Multi-Agent AI</span>
              </h2>
              <p className="text-zinc-400 max-w-2xl mx-auto">
                A modular pipeline that extracts visual semantics, reasons about temporal context, and transforms into styled captions.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                {
                  Icon: Video,
                  title: 'Vision Extraction',
                  body: 'Motion-aware keyframe sampling and semantic scene understanding — captures exactly what is happening.',
                  gradient: 'from-purple-500 to-indigo-500'
                },
                {
                  Icon: BrainCircuit,
                  title: 'Temporal Reasoning',
                  body: 'LLM-powered scene graph analysis connects visual events across time into a coherent narrative.',
                  gradient: 'from-indigo-500 to-cyan-500'
                },
                {
                  Icon: Wand2,
                  title: 'Style Matrix',
                  body: 'Parallel style transformers output Formal, Sarcastic, Humorous-Tech, and Humorous-Non-Tech captions.',
                  gradient: 'from-cyan-500 to-blue-500'
                },
              ].map(({ Icon, title, body, gradient }) => (
                <div
                  key={title}
                  className="glass border border-zinc-800 p-7 rounded-2xl
                    hover:border-zinc-700 hover:-translate-y-1 bg-zinc-900/50 hover:bg-zinc-900
                    transition-all duration-300 shadow-2xl shadow-black/50
                    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ai-cyan/40 group"
                  tabIndex={0}
                >
                  <div className={`h-12 w-12 rounded-xl flex items-center justify-center mb-5 bg-gradient-to-br ${gradient} shadow-lg`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <h3 className="text-lg font-bold text-white font-display mb-3 group-hover:text-ai-cyan transition-colors">{title}</h3>
                  <p className="text-sm text-zinc-400 leading-relaxed">{body}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── How It Works ── */}
        <section className="py-20 px-4 bg-zinc-900/30">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-bold font-display mb-4">
                How It <span className="text-transparent bg-clip-text bg-gradient-to-r from-ai-indigo to-ai-cyan">Works</span>
              </h2>
              <p className="text-zinc-400 max-w-2xl mx-auto">
                A seamless multi-stage pipeline that transforms raw video into styled captions with pinpoint accuracy.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { step: '01', title: 'Upload Video', desc: 'Drop any video file into our platform', Icon: Video },
                { step: '02', title: 'Scene Analysis', desc: 'AI detects scenes and extracts key frames', Icon: Eye },
                { step: '03', title: 'Temporal Context', desc: 'Reasoning engine builds narrative flow', Icon: BrainCircuit },
                { step: '04', title: 'Style Generation', desc: 'Four parallel style transformations', Icon: Wand2 }
              ].map(({ step, title, desc, Icon }) => (
                <div key={step} className="relative">
                  <div className="glass border border-zinc-800 p-6 rounded-xl bg-zinc-900/50 hover:bg-zinc-900 transition-all duration-300 h-full">
                    <div className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-br from-ai-indigo/30 to-ai-cyan/30 mb-4">
                      {step}
                    </div>
                    <Icon className="h-8 w-8 text-ai-cyan mb-4" />
                    <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
                    <p className="text-sm text-zinc-400">{desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Key Features ── */}
        <section className="py-20 px-4">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-bold font-display mb-4">
                Built for <span className="text-transparent bg-clip-text bg-gradient-to-r from-ai-indigo to-ai-cyan">Performance</span>
              </h2>
              <p className="text-zinc-400 max-w-2xl mx-auto">
                Production-ready architecture with enterprise-grade reliability and speed.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { Icon: Zap, title: 'Lightning Fast', desc: 'Optimized pipeline processes videos in real-time with minimal latency' },
                { Icon: Shield, title: 'Zero Hallucination', desc: 'Grounded vision models ensure factually accurate captions' },
                { Icon: Layers, title: 'Modular Design', desc: 'Each pipeline stage is independent, testable, and replaceable' },
                { Icon: Gauge, title: 'High Accuracy', desc: 'Multi-stage validation ensures caption quality and style adherence' },
                { Icon: Code2, title: 'Docker Ready', desc: 'One-command deployment with full containerization support' },
                { Icon: Target, title: 'Style Precision', desc: 'Fine-tuned transformers for each of the four required styles' }
              ].map(({ Icon, title, desc }) => (
                <div key={title} className="glass border border-zinc-800 p-6 rounded-xl bg-zinc-900/30 hover:bg-zinc-900/50 transition-all duration-300">
                  <Icon className="h-8 w-8 text-ai-cyan mb-4" />
                  <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
                  <p className="text-sm text-zinc-400 leading-relaxed">{desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Tech Stack ── */}
        <section className="py-20 px-4 bg-zinc-900/30">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-bold font-display mb-4">
                Powered by <span className="text-transparent bg-clip-text bg-gradient-to-r from-ai-indigo to-ai-cyan">Modern Stack</span>
              </h2>
              <p className="text-zinc-400 max-w-2xl mx-auto">
                Built with cutting-edge AI models and production-grade infrastructure.
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {[
                { name: 'GPT-4 Vision', category: 'Vision Engine' },
                { name: 'LLaMA 3', category: 'Reasoning' },
                { name: 'FastAPI', category: 'Backend' },
                { name: 'React', category: 'Frontend' },
                { name: 'PyTorch', category: 'ML Framework' },
                { name: 'Docker', category: 'Deployment' },
                { name: 'OpenCV', category: 'Video Processing' },
                { name: 'Transformers', category: 'NLP' }
              ].map(({ name, category }) => (
                <div key={name} className="glass border border-zinc-800 p-5 rounded-xl bg-zinc-900/50 hover:bg-zinc-900 hover:border-ai-cyan/50 transition-all duration-300 text-center">
                  <div className="text-white font-semibold mb-1">{name}</div>
                  <div className="text-xs text-zinc-500">{category}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Why CaptionForge ── */}
        <section className="py-20 px-4">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-bold font-display mb-4">
                Why <span className="text-transparent bg-clip-text bg-gradient-to-r from-ai-indigo to-ai-cyan">CaptionForge</span>
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
              {[
                { title: 'Accuracy First', desc: 'Grounded vision models and multi-stage validation eliminate hallucinations and ensure factual correctness.' },
                { title: 'Style Mastery', desc: 'Four specialized transformers trained for distinct tones: Formal, Sarcastic, and two flavors of Humorous.' },
                { title: 'Temporal Understanding', desc: 'Unlike frame-by-frame captioning, we reason across scenes to build coherent narratives.' },
                { title: 'Production Ready', desc: 'Docker-native deployment, modular architecture, and comprehensive testing for real-world reliability.' }
              ].map(({ title, desc }) => (
                <div key={title} className="flex gap-4">
                  <div className="flex-shrink-0">
                    <CheckCircle2 className="h-6 w-6 text-ai-cyan mt-1" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
                    <p className="text-sm text-zinc-400 leading-relaxed">{desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── CTA Section ── */}
        <section className="py-20 px-4">
          <div className="max-w-4xl mx-auto text-center">
            <div className="glass border border-zinc-800 p-12 rounded-3xl bg-gradient-to-br from-zinc-900/80 to-zinc-900/40">
              <h2 className="text-4xl md:text-5xl font-bold font-display mb-6">
                Ready to Transform Your Videos?
              </h2>
              <p className="text-zinc-400 text-lg mb-8 max-w-2xl mx-auto">
                Experience the power of multi-agent AI captioning. Upload your first video and see the magic happen.
              </p>
              <button
                onClick={() => navigate('/app')}
                className="group relative inline-flex items-center justify-center gap-2
                  px-10 py-4 rounded-full overflow-hidden
                  bg-gradient-to-r from-ai-indigo to-ai-cyan text-white font-bold text-lg
                  transition-all duration-200 hover:scale-[1.03]
                  hover:shadow-[0_0_48px_rgba(99,102,241,0.5)]
                  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ai-indigo focus-visible:ring-offset-2 focus-visible:ring-offset-obsidian"
              >
                <span className="relative">Start Captioning Now</span>
                <ChevronRight className="relative h-5 w-5 group-hover:translate-x-1 transition-transform duration-150" />
              </button>
            </div>
          </div>
        </section>

        {/* ── Footer ── */}
        <footer className="border-t border-zinc-800 py-8 px-4">
          <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-1.5 bg-gradient-to-tr from-ai-indigo to-ai-cyan rounded-xl">
                <Sparkles className="h-4 w-4 text-white" />
              </div>
              <span className="text-sm text-zinc-400">
                © 2024 CaptionForge AI. Built for AMD Hackathon Track 2.
              </span>
            </div>
            <div className="flex items-center gap-6">
              <a
                href="https://github.com/tanishkagupta00/amd-hackathon-track-2"
                target="_blank"
                rel="noreferrer"
                className="text-zinc-400 hover:text-white transition-colors text-sm"
              >
                GitHub
              </a>
              <span className="text-zinc-600">•</span>
              <span className="text-zinc-400 text-sm">AMD Developer Hackathon</span>
            </div>
          </div>
        </footer>

      </div>
    </div>
  );
}
