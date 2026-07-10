import { useState } from 'react';
import { Sparkles, Settings } from 'lucide-react';
import axios from 'axios';

import DragDrop from './components/DragDrop';
import Monitor from './components/Monitor';
import Matrix from './components/Matrix';

export default function App() {
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

  const handleProcessingComplete = async (id: string) => {
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
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Premium Header */}
      <header className="sticky top-0 z-50 bg-slate-900 text-white shadow-lg border-b border-slate-800">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-tr from-orange-600 to-amber-500 rounded-xl shadow-md">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <span className="font-extrabold tracking-tight text-lg">CaptionForge AI</span>
              <span className="ml-2 px-2 py-0.5 text-[10px] font-bold bg-orange-600/20 text-orange-400 rounded border border-orange-500/20 uppercase">AMD Hackathon</span>
            </div>
          </div>
          <div className="flex items-center gap-4 text-sm text-slate-400 font-medium">
            <span>Track 2 Agent</span>
            <div className="h-4 w-[1px] bg-slate-800" />
            <button className="hover:text-white transition flex items-center gap-1.5">
              <Settings className="h-4 w-4" />
              Settings
            </button>
          </div>
        </div>
      </header>

      {/* Main Workspace */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-10 space-y-8">
        {/* Intro */}
        {stage === 'upload' && (
          <div className="space-y-2 animate-fade-in">
            <h1 className="text-3xl font-extrabold tracking-tight text-slate-800">
              Transform Videos with Style-Aware Captions
            </h1>
            <p className="text-slate-500 max-w-xl">
              CaptionForge AI analyzes your video content using a multi-stage semantic reasoning pipeline and renders accurate captions in four bespoke target styles.
            </p>
          </div>
        )}

        {stage !== 'upload' && filename && (
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wider bg-slate-100 px-3 py-1.5 rounded-lg w-max border border-slate-200">
            <span>Active File:</span>
            <span className="text-slate-800 normal-case font-mono">{filename}</span>
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
      <footer className="bg-slate-900 border-t border-slate-800 py-6 text-center text-xs text-slate-500">
        <p>&copy; 2026 CaptionForge AI. Built for AMD Developer Hackathon Track 2.</p>
      </footer>
    </div>
  );
}
