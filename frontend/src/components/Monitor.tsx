import React, { useEffect, useState, useRef } from 'react';
import { Play, Terminal, Cpu, CheckCircle2, XCircle } from 'lucide-react';
import axios from 'axios';

interface MonitorProps {
  videoId: string;
  onProcessingComplete: (videoId: string) => void;
}

const STAGES = [
  { id: 'preprocessor', name: 'Preprocessing', desc: 'Validating media tracks' },
  { id: 'sampling', name: 'Sampling', desc: 'Motion-aware keyframe extraction' },
  { id: 'reasoning', name: 'Reasoning', desc: 'Scene object & action graph tagging' },
  { id: 'generating', name: 'Generating', desc: 'Multi-head style transformers' }
];

export default function Monitor({ videoId, onProcessingComplete }: MonitorProps) {
  const [status, setStatus] = useState<string>('queued');
  const [logs, setLogs] = useState<string[]>([]);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Start caption generation immediately
    axios.post('/api/v1/captions/generate', { video_id: videoId })
      .catch(err => {
        setLogs(prev => [...prev, `[ERROR] Failed to start generation: ${err.message}`]);
      });

    // Start polling status
    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`/api/v1/videos/${videoId}`);
        setStatus(res.data.status);
        setLogs(res.data.logs || []);

        if (res.data.status === 'completed') {
          clearInterval(interval);
          onProcessingComplete(videoId);
        } else if (res.data.status === 'failed') {
          clearInterval(interval);
        }
      } catch (err: any) {
        setLogs(prev => [...prev, `[ERROR] Connection issue: ${err.message}`]);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [videoId]);

  // Scroll to bottom of terminal log stream
  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const getStageIndex = () => {
    return STAGES.findIndex(s => s.id === status);
  };

  const activeIndex = getStageIndex();

  return (
    <div className="w-full space-y-8 animate-fade-in">
      {/* Dynamic Pipeline Stepper */}
      <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm space-y-6">
        <div className="flex items-center justify-between border-b pb-4">
          <div>
            <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
              <Cpu className="h-5 w-5 text-orange-600" />
              Active AI Orchestration Pipeline
            </h3>
            <p className="text-sm text-slate-500 mt-0.5">Tracking real-time visual-language processing</p>
          </div>
          <span className={`px-3 py-1 text-xs font-semibold rounded-full uppercase tracking-wider ${
            status === 'completed' ? 'bg-green-100 text-green-800' :
            status === 'failed' ? 'bg-red-100 text-red-800' :
            'bg-blue-100 text-blue-800 animate-pulse'
          }`}>
            {status}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 relative">
          {STAGES.map((stage, idx) => {
            const isCompleted = idx < activeIndex || status === 'completed';
            const isActive = idx === activeIndex && status !== 'completed' && status !== 'failed';
            const isFailed = status === 'failed' && idx === activeIndex;

            return (
              <div key={stage.id} className="relative flex flex-col items-center text-center space-y-2">
                <div className={`h-10 w-10 rounded-full flex items-center justify-center font-bold text-sm border-2 transition-all duration-300 ${
                  isCompleted ? 'bg-green-600 border-green-600 text-white shadow-md' :
                  isActive ? 'bg-orange-500 border-orange-500 text-white shadow-md animate-pulse' :
                  isFailed ? 'bg-red-600 border-red-600 text-white shadow-md' :
                  'bg-white border-slate-300 text-slate-400'
                }`}>
                  {isCompleted ? <CheckCircle2 className="h-5 w-5" /> :
                   isFailed ? <XCircle className="h-5 w-5" /> :
                   idx + 1}
                </div>
                <div>
                  <h4 className={`font-semibold text-sm ${isActive ? 'text-orange-600' : 'text-slate-700'}`}>{stage.name}</h4>
                  <p className="text-xs text-slate-400 mt-0.5">{stage.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Real-time Terminal Monitor logs */}
      <div className="bg-slate-950 text-slate-100 rounded-2xl p-6 border border-slate-800 shadow-2xl flex flex-col h-[350px]">
        <div className="flex items-center gap-2 border-b border-slate-800 pb-3 mb-3 text-slate-400 text-sm font-semibold">
          <Terminal className="h-4 w-4 text-orange-500" />
          <span>System Execution Log Monitor</span>
        </div>
        <div className="flex-1 overflow-y-auto space-y-1 font-mono text-xs text-slate-300 leading-relaxed pr-2">
          {logs.length === 0 && (
            <div className="text-slate-600 italic">Initializing console streaming...</div>
          )}
          {logs.map((log, index) => {
            const isError = log.includes("[ERROR]") || log.includes("CRITICAL");
            const isCompleted = log.includes("finished") || log.includes("complete");
            return (
              <div key={index} className={
                isError ? 'text-red-400 font-semibold' :
                isCompleted ? 'text-green-400 font-semibold' :
                'text-slate-300'
              }>
                {log}
              </div>
            );
          })}
          <div ref={terminalEndRef} />
        </div>
      </div>
    </div>
  );
}
