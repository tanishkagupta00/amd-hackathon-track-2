import { useState } from 'react';
import { Sparkles, Home as HomeIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

import DragDrop from '../components/DragDrop';
import Monitor from '../components/Monitor';
import Matrix from '../components/Matrix';

export default function Workspace() {
  const navigate = useNavigate();
  const [videoId, setVideoId] = useState<string | null>(null);
  const [filename, setFilename] = useState<string>('');
  const [stage, setStage] = useState<'upload' | 'processing' | 'completed'>('upload');
  const [captions, setCaptions] = useState<any>(null);
  const [evaluations, setEvaluations] = useState<any>(null);

  const handleUploadSuccess = (id: string, name: string) => {
    setVideoId(id);
    setFilename(name);
    setStage('processing');
  };

  const handleProcessingComplete = async (id: string, directCaptions?: any, directEvals?: any) => {
    // If the POST request returned the data directly, use it to avoid Vercel ephemeral DB read failure
    if (directCaptions && directEvals && Object.keys(directCaptions).length > 0) {
      setCaptions(directCaptions);
      setEvaluations(directEvals);
      setStage('completed');
      return;
    }
    
    // Fallback logic
    try {
      const res = await axios.get(`/api/v1/captions/${id}`);
      setCaptions(res.data.captions);
      setEvaluations(res.data.evaluations);
      setStage('completed');
    } catch (err) {
      console.error("Failed to load completed captions:", err);
    }
  };

  const handleReset = () => {
    setVideoId(null);
    setFilename('');
    setCaptions(null);
    setEvaluations(null);
    setStage('upload');
  };

  return (
    <div className="min-h-screen bg-obsidian flex flex-col selection:bg-ai-gold/30">
      {/* Premium Header */}
      <header className="sticky top-0 z-40 bg-obsidian/80 backdrop-blur-[18px] text-white border-b border-white/5">
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-1.5 bg-gradient-to-tr from-ai-goldDark to-ai-gold rounded-lg shadow-[0_0_20px_rgba(212,175,55,0.18)]">
              <Sparkles className="h-4 w-4 text-obsidian" />
            </div>
            <div>
              <span className="font-bold tracking-tight text-sm font-display text-white">CaptionForge AI</span>
              <span className="ml-2 px-2 py-0.5 text-[9px] font-bold bg-ai-gold/10 text-ai-goldLight rounded border border-ai-gold/20 uppercase tracking-widest">AMD Track 2</span>
            </div>
          </div>
          <div className="flex items-center gap-4 text-xs font-medium">
            <button 
              onClick={() => navigate('/')}
              className="flex items-center gap-1.5 text-zinc-400 hover:text-ai-goldLight transition-colors
                focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ai-gold/40 rounded px-1.5 py-1"
            >
              <HomeIcon className="h-3.5 w-3.5" />
              <span>Home</span>
            </button>
            <span className="text-zinc-600">|</span>
            <span className="text-zinc-500">Pipeline Agent</span>
          </div>
        </div>
      </header>

      {/* Main Workspace */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-10 space-y-8">
        {/* Intro */}
        {stage === 'upload' && (
          <div className="space-y-3 animate-fade-in">
            <h1 className="text-3xl font-bold tracking-tight font-display hero-title w-fit">
              Transform Videos with Style-Aware Captions
            </h1>
            <p className="text-zinc-400 max-w-xl text-sm leading-relaxed">
              CaptionForge AI analyzes your video content using a multi-stage semantic reasoning pipeline and renders accurate captions in four bespoke target styles.
            </p>
          </div>
        )}

        {stage !== 'upload' && filename && (
          <div className="flex items-center gap-2 text-xs font-semibold text-ai-accent uppercase tracking-wider bg-zinc-900 px-3 py-1.5 rounded-lg w-max border border-zinc-800 shadow-inner">
            <span>Active File:</span>
            <span className="text-white normal-case font-mono">{filename}</span>
          </div>
        )}

        {/* Workflow states */}
        {stage === 'upload' && (
          <DragDrop onUploadSuccess={handleUploadSuccess} />
        )}

        {stage === 'processing' && videoId && (
          <Monitor
            videoId={videoId}
            onProcessingComplete={handleProcessingComplete}
          />
        )}

        {stage === 'completed' && videoId && captions && evaluations && (
          <Matrix
            videoId={videoId}
            captions={captions}
            evaluations={evaluations}
            onReset={handleReset}
          />
        )}
      </main>

      {/* Sticky footer */}
      <footer className="border-t border-white/5 py-6 text-center text-xs text-zinc-500">
        <p>&copy; 2026 CaptionForge AI &nbsp;·&nbsp; AMD Developer Hackathon Track 2</p>
      </footer>
    </div>
  );
}
