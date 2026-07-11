import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Video, BrainCircuit, Wand2, ChevronRight, Github, Zap, Shield, Layers, Gauge, Code2, Target, CheckCircle2, Eye, Cpu, Clock } from 'lucide-react';
import TextGalaxy from '../components/TextGalaxy';
import Shuffle from '../components/Shuffle';

function FadeIn({ children, delay = 0, className = "" }: { children: React.ReactNode, delay?: number, className?: string }) {
  const [isVisible, setVisible] = useState(false);
  const domRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    
    if (domRef.current) observer.observe(domRef.current);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={domRef}
      className={className}
      style={{
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translateY(0)' : 'translateY(40px)',
        transition: `opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1) ${delay}s, transform 0.8s cubic-bezier(0.16, 1, 0.3, 1) ${delay}s`,
        willChange: 'opacity, transform'
      }}
    >
      {children}
    </div>
  );
}

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-obsidian text-white font-sans selection:bg-ai-gold/30">

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
            {/* Logo — gold gradient */}
            <div className="p-1.5 bg-gradient-to-tr from-ai-goldDark to-ai-gold rounded-xl shadow-[0_0_20px_rgba(212,175,55,0.18)]">
              <Sparkles className="h-5 w-5 text-obsidian" />
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
              className="text-zinc-400 hover:text-ai-goldLight transition-colors duration-150
                flex items-center gap-2 text-sm font-medium
                focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ai-gold/40 rounded-md px-1"
            >
              <Github className="h-4 w-4" />
              <span className="hidden sm:inline">GitHub</span>
            </a>

          </div>
        </nav>

        {/* ── Hero Section ── */}
        <section className="min-h-screen flex flex-col items-center justify-center text-center px-4 py-20">
          <FadeIn className="max-w-4xl space-y-8 mt-10 mb-20">

            {/* Live badge */}
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full
              bg-ai-gold/5 border border-ai-gold/25 text-sm text-ai-accent backdrop-blur-[10px]">
              <span className="h-2 w-2 rounded-full bg-ai-gold animate-pulse" />
              <span>AMD Developer Hackathon · Track 2</span>
            </div>

            {/* H1 */}
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight leading-[1.08] font-display">
              <Shuffle 
                tag="span"
                text="Intelligent Video Captions," 
                className="inline-block" 
                duration={1.2}
                stagger={0.06}
                ease="power3.out"
              />{' '}
              <br className="hidden md:block" />
              <Shuffle 
                tag="span"
                text="Generated with Style." 
                className="text-ai-gold inline-block" 
                duration={1.5}
                stagger={0.08}
                ease="power3.out"
              />
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
                  bg-gradient-to-br from-ai-goldDark via-ai-gold to-ai-goldLight text-obsidian font-bold text-base
                  transition-all duration-300
                  shadow-[0_8px_30px_rgba(212,175,55,0.25)]
                  hover:-translate-y-0.5 hover:shadow-[0_15px_45px_rgba(212,175,55,0.35)]
                  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ai-gold focus-visible:ring-offset-2 focus-visible:ring-offset-obsidian"
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
                <FadeIn key={i} delay={0.1 * (i + 1)} className="text-center">
                  <div className="text-2xl font-bold hero-title mb-1">
                    {stat.label}
                  </div>
                  <div className="text-xs text-zinc-500">{stat.value}</div>
                </FadeIn>
              ))}
            </div>
          </FadeIn>
        </section>

        {/* ── Core Features ── */}
        <section className="py-20 px-4">
          <div className="max-w-6xl mx-auto">
            <FadeIn className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-bold font-display mb-4">
                Powered by <span className="hero-title">Multi-Agent AI</span>
              </h2>
              <p className="text-zinc-400 max-w-2xl mx-auto">
                A modular pipeline that extracts visual semantics, reasons about temporal context, and transforms into styled captions.
              </p>
            </FadeIn>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
              ].map(({ Icon, title, body }, i) => (
                <FadeIn key={title} delay={0.1 * i}>
                  <div
                    className="card p-7 rounded-2xl group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ai-gold/40 h-full"
                    tabIndex={0}
                  >
                    <div className={`h-12 w-12 rounded-xl flex items-center justify-center mb-5 bg-gradient-to-br from-zinc-800 to-zinc-900 border border-zinc-700/50 shadow-lg`}>
                      <Icon className="h-6 w-6 text-ai-gold group-hover:text-ai-goldLight transition-colors" />
                    </div>
                    <h3 className="text-lg font-bold text-white font-display mb-3 group-hover:text-ai-goldLight transition-colors">{title}</h3>
                    <p className="text-sm text-zinc-400 leading-relaxed">{body}</p>
                  </div>
                </FadeIn>
              ))}
            </div>
          </div>
        </section>

        {/* ── How It Works ── */}
        <section className="py-20 px-4 bg-zinc-900/10">
          <div className="max-w-6xl mx-auto">
            <FadeIn className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-bold font-display mb-4">
                How It <span className="hero-title">Works</span>
              </h2>
              <p className="text-zinc-400 max-w-2xl mx-auto">
                A seamless multi-stage pipeline that transforms raw video into styled captions with pinpoint accuracy.
              </p>
            </FadeIn>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { step: '01', title: 'Upload Video', desc: 'Drop any video file into our platform', Icon: Video },
                { step: '02', title: 'Scene Analysis', desc: 'AI detects scenes and extracts key frames', Icon: Eye },
                { step: '03', title: 'Temporal Context', desc: 'Reasoning engine builds narrative flow', Icon: BrainCircuit },
                { step: '04', title: 'Style Generation', desc: 'Four parallel style transformations', Icon: Wand2 }
              ].map(({ step, title, desc, Icon }, i) => (
                <FadeIn key={step} delay={0.1 * i} className="relative">
                  <div className="card p-6 rounded-xl h-full group">
                    <div className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-br from-ai-gold/60 to-ai-goldLight/60 mb-4 group-hover:from-ai-gold group-hover:to-ai-goldLight transition-all">
                      {step}
                    </div>
                    <Icon className="h-8 w-8 text-ai-gold mb-4 group-hover:text-ai-goldLight transition-colors" />
                    <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
                    <p className="text-sm text-zinc-400">{desc}</p>
                  </div>
                </FadeIn>
              ))}
            </div>
          </div>
        </section>

        {/* ── Key Features ── */}
        <section className="py-20 px-4">
          <div className="max-w-6xl mx-auto">
            <FadeIn className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-bold font-display mb-4">
                Built for <span className="hero-title">Performance</span>
              </h2>
              <p className="text-zinc-400 max-w-2xl mx-auto">
                Production-ready architecture with enterprise-grade reliability and speed.
              </p>
            </FadeIn>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { Icon: Zap, title: 'Lightning Fast', desc: 'Optimized pipeline processes videos in real-time with minimal latency' },
                { Icon: Shield, title: 'Zero Hallucination', desc: 'Grounded vision models ensure factually accurate captions' },
                { Icon: Layers, title: 'Modular Design', desc: 'Each pipeline stage is independent, testable, and replaceable' },
                { Icon: Gauge, title: 'High Accuracy', desc: 'Multi-stage validation ensures caption quality and style adherence' },
                { Icon: Code2, title: 'Docker Ready', desc: 'One-command deployment with full containerization support' },
                { Icon: Target, title: 'Style Precision', desc: 'Fine-tuned transformers for each of the four required styles' }
              ].map(({ Icon, title, desc }, i) => (
                <FadeIn key={title} delay={0.05 * i}>
                  <div className="card p-6 rounded-xl group h-full">
                    <Icon className="h-8 w-8 text-ai-gold mb-4 group-hover:text-ai-goldLight transition-colors" />
                    <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
                    <p className="text-sm text-zinc-400 leading-relaxed">{desc}</p>
                  </div>
                </FadeIn>
              ))}
            </div>
          </div>
        </section>

        {/* ── Tech Stack ── */}
        <section className="py-20 px-4 bg-zinc-900/10">
          <div className="max-w-6xl mx-auto">
            <FadeIn className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-bold font-display mb-4">
                Powered by <span className="hero-title">Modern Stack</span>
              </h2>
              <p className="text-zinc-400 max-w-2xl mx-auto">
                Built with cutting-edge AI models and production-grade infrastructure.
              </p>
            </FadeIn>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {[
                { name: 'Gemini 2.5 Flash', category: 'Vision Engine' },
                { name: 'DeepSeek V4 Pro', category: 'Style Engine' },
                { name: 'FastAPI', category: 'Backend API' },
                { name: 'React & Vite', category: 'Frontend App' },
                { name: 'Gemini 2.0 Flash', category: 'Style Fallback' },
                { name: 'Vercel Serverless', category: 'Deployment' },
                { name: 'Fireworks AI', category: 'Inference API' },
                { name: 'SQLite', category: 'Database' }
              ].map(({ name, category }, i) => (
                <FadeIn key={name} delay={0.05 * i}>
                  <div className="card p-5 rounded-xl text-center h-full">
                    <div className="text-white font-semibold mb-1">{name}</div>
                    <div className="text-xs text-zinc-500">{category}</div>
                  </div>
                </FadeIn>
              ))}
            </div>
          </div>
        </section>

        {/* ── Why CaptionForge ── */}
        <section className="py-20 px-4">
          <div className="max-w-6xl mx-auto">
            <FadeIn className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-bold font-display mb-4">
                Why <span className="hero-title">CaptionForge</span>
              </h2>
            </FadeIn>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
              {[
                { title: 'Accuracy First', desc: 'Grounded vision models and multi-stage validation eliminate hallucinations and ensure factual correctness.' },
                { title: 'Style Mastery', desc: 'Four specialized transformers trained for distinct tones: Formal, Sarcastic, and two flavors of Humorous.' },
                { title: 'Temporal Understanding', desc: 'Unlike frame-by-frame captioning, we reason across scenes to build coherent narratives.' },
                { title: 'Production Ready', desc: 'Docker-native deployment, modular architecture, and comprehensive testing for real-world reliability.' }
              ].map(({ title, desc }, i) => (
                <FadeIn key={title} delay={0.1 * i} className="flex gap-4">
                  <div className="flex-shrink-0">
                    <CheckCircle2 className="h-6 w-6 text-ai-gold mt-1" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
                    <p className="text-sm text-zinc-400 leading-relaxed">{desc}</p>
                  </div>
                </FadeIn>
              ))}
            </div>
          </div>
        </section>

        {/* ── CTA Section ── */}
        <section className="py-20 px-4">
          <div className="max-w-4xl mx-auto text-center">
            <FadeIn className="p-12 rounded-3xl">
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
                  bg-gradient-to-br from-ai-goldDark via-ai-gold to-ai-goldLight text-obsidian font-bold text-lg
                  transition-all duration-300
                  shadow-[0_8px_30px_rgba(212,175,55,0.25)]
                  hover:-translate-y-0.5 hover:shadow-[0_15px_45px_rgba(212,175,55,0.35)]
                  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ai-gold focus-visible:ring-offset-2 focus-visible:ring-offset-obsidian"
              >
                <span className="relative">Start Captioning Now</span>
                <ChevronRight className="relative h-5 w-5 group-hover:translate-x-1 transition-transform duration-150" />
              </button>
            </FadeIn>
          </div>
        </section>

        {/* ── Footer ── */}
        <footer className="border-t border-white/10 py-8 px-4">
          <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-1.5 bg-gradient-to-tr from-ai-goldDark to-ai-gold rounded-xl">
                <Sparkles className="h-4 w-4 text-obsidian" />
              </div>
              <span className="text-sm text-zinc-400">
                © {new Date().getFullYear()} CaptionForge AI. Built for AMD Hackathon Track 2.
              </span>
            </div>
            <div className="flex items-center gap-6">
              <a
                href="https://github.com/tanishkagupta00/amd-hackathon-track-2"
                target="_blank"
                rel="noreferrer"
                className="text-zinc-400 hover:text-ai-goldLight transition-colors text-sm"
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
