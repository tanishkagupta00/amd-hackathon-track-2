import React, { useEffect, useState, useRef } from 'react';
import { Terminal, Cpu, CheckCircle2, XCircle } from 'lucide-react';
import axios from 'axios';

/* ── All data-fetching, state, and props unchanged ── */

interface MonitorProps {
  videoId: string;
  onProcessingComplete: (videoId: string) => void;
}

const STAGES = [
  { id: 'preprocessor', name: 'Extract',   desc: 'Media validation & keyframe sampling' },
  { id: 'sampling',     name: 'Sample',    desc: 'Motion-aware visual extraction' },
  { id: 'reasoning',    name: 'Reason',    desc: 'Scene graph & semantic tagging' },
  { id: 'generating',   name: 'Style',     desc: 'Multi-head style transformers' },
];

const STATUS_LABEL: Record<string, string> = {
  queued:       'Queued — waiting for worker slot',
  preprocessor: 'Extracting — validating media container and tracks',
  sampling:     'Sampling — detecting motion-aware keyframes',
  reasoning:    'Reasoning — building visual scene graph',
  generating:   'Styling — running parallel style transformers',
  completed:    'Complete — all captions generated',
  failed:       'Failed — check execution log for details',
};

/* Waveform bar — energetic cyan/indigo when active */
function WaveformBar({ delay, active }: { delay: number; active: boolean }) {
  return (
    <span
      className={`inline-block w-[3px] rounded-full transition-colors duration-300 ${
        active ? 'bg-ai-cyan' : 'bg-zinc-800'
      }`}
      style={{
        height: active ? undefined : '8px',
        minHeight: '4px',
        maxHeight: '20px',
        animation: active ? `waveBar 0.9s ease-in-out ${delay}ms infinite alternate` : undefined,
      }}
    />
  );
}

export default function Monitor({ videoId, onProcessingComplete }: MonitorProps) {
  const [status, setStatus] = useState<string>('queued');
  const [logs,   setLogs]   = useState<string[]>([]);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    axios.post('/api/v1/captions/generate', { video_id: videoId })
      .catch(err => setLogs(prev => [...prev, `[ERROR] Failed to start generation: ${err.message}`]));

    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`/api/v1/videos/${videoId}`);
        setStatus(res.data.status);
        setLogs(res.data.logs || []);
        if (res.data.status === 'completed') { clearInterval(interval); onProcessingComplete(videoId); }
        else if (res.data.status === 'failed') { clearInterval(interval); }
      } catch (err: any) {
        setLogs(prev => [...prev, `[ERROR] Connection issue: ${err.message}`]);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [videoId]);

  useEffect(() => { terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [logs]);

  const activeIndex = STAGES.findIndex(s => s.id === status);
  const isRunning   = status !== 'completed' && status !== 'failed';
  const isFailed    = status === 'failed';

  return (
    <div className="w-full space-y-5 animate-fade-in">

      {/* ── Pipeline Tracker ── */}
      <div className="glass border border-zinc-800 rounded-2xl p-7 space-y-6 shadow-2xl shadow-black/50">

        {/* Header */}
        <div className="flex items-start justify-between gap-4 border-b border-zinc-800/70 pb-5">
          <div>
            <h3 className="text-sm font-bold text-white font-display flex items-center gap-2">
              <Cpu className="h-4 w-4 text-ai-indigo shrink-0" />
              AI Orchestration Pipeline
            </h3>
            {/* Real status text from API */}
            <p className={`text-xs mt-1.5 font-mono transition-colors duration-300 ${
              isFailed               ? 'text-rose-400' :
              status === 'completed' ? 'text-ai-emerald' :
              'text-ai-cyan'
            }`}>
              {STATUS_LABEL[status] ?? status}
            </p>
          </div>

          {/* Waveform */}
          <div className="shrink-0 flex items-end gap-[3px] h-5 pr-1">
            {[0, 80, 160, 240, 80, 0].map((delay, i) => (
              <WaveformBar key={i} delay={delay} active={isRunning} />
            ))}
          </div>
        </div>

        {/* Horizontal step tracker */}
        <div className="relative">
          {/* Background rail — zinc-800 */}
          <div className="absolute top-[18px] left-[28px] right-[28px] h-px bg-zinc-800" />

          <div className="relative grid grid-cols-4 gap-2">
            {STAGES.map((stage, idx) => {
              const isCompleted = idx < activeIndex || status === 'completed';
              const isActive    = idx === activeIndex && isRunning;
              const isStageFail = isFailed && idx === activeIndex;

              return (
                <div key={stage.id} className="flex flex-col items-center gap-2.5 text-center">

                  {/* Connector fill — gradient fill! */}
                  {idx > 0 && isCompleted && (
                    <div
                      className="absolute h-px bg-gradient-to-r from-ai-indigo to-ai-cyan connector-fill"
                      style={{
                        top: '18px',
                        left:  `calc(${(idx - 1) * 25 + 12.5}% + 24px)`,
                        width: `calc(25% - 48px)`,
                      }}
                    />
                  )}

                  {/* Node */}
                  <div className={[
                    'relative z-10 h-9 w-9 rounded-full flex items-center justify-center',
                    'border-2 text-xs font-bold transition-all duration-300',
                    isCompleted
                      ? 'bg-ai-indigo border-ai-indigo text-white shadow-[0_0_14px_rgba(99,102,241,0.5)]'
                      : isActive
                      ? 'bg-obsidian border-ai-cyan text-ai-cyan shadow-[0_0_14px_rgba(34,211,238,0.35)] animate-pulse'
                      : isStageFail
                      ? 'bg-rose-950 border-rose-600 text-rose-400'
                      : 'bg-obsidian border-zinc-800 text-zinc-500',
                  ].join(' ')}>
                    {isCompleted  ? <CheckCircle2 className="h-4 w-4 check-in" /> :
                     isStageFail  ? <XCircle className="h-4 w-4" /> :
                     idx + 1}
                  </div>

                  {/* Label */}
                  <div>
                    <p className={`text-[11px] font-bold font-display uppercase tracking-widest transition-colors duration-300 ${
                      isActive    ? 'text-ai-cyan' :
                      isCompleted ? 'text-white' :
                      isStageFail ? 'text-rose-400' :
                      'text-zinc-500'
                    }`}>{stage.name}</p>
                    <p className="text-[10px] text-zinc-500 mt-0.5 leading-tight hidden sm:block">{stage.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* ── Terminal Log ── */}
      <div className="bg-obsidian rounded-2xl border border-zinc-800 flex flex-col h-[300px] overflow-hidden shadow-2xl shadow-black/50">
        {/* Chrome bar */}
        <div className="flex items-center gap-2 px-5 py-2.5 border-b border-zinc-800 bg-zinc-900/80 shrink-0">
          <div className="flex gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-rose-500/50" />
            <span className="h-2.5 w-2.5 rounded-full bg-yellow-500/50" />
            <span className="h-2.5 w-2.5 rounded-full bg-ai-emerald/50" />
          </div>
          <div className="flex items-center gap-2 ml-3 text-zinc-500 text-xs font-mono">
            <Terminal className="h-3 w-3 text-ai-cyan" />
            <span>captionforge — execution log &nbsp;·&nbsp; {videoId}</span>
          </div>
          {isRunning && (
            <span className="ml-auto flex items-center gap-1.5 text-[10px] font-mono text-ai-cyan">
              <span className="h-1.5 w-1.5 rounded-full bg-ai-cyan animate-pulse" />
              LIVE
            </span>
          )}
        </div>

        {/* Log stream */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-0.5 font-mono text-xs leading-5">
          {logs.length === 0 && (
            <span className="text-zinc-600 italic">Initializing console stream…</span>
          )}
          {logs.map((log, i) => {
            const isError = log.includes('[ERROR]') || log.includes('CRITICAL');
            const isDone  = log.includes('finished') || log.includes('complete');
            const isInfo  = log.startsWith('[INFO]');
            const isWarn  = log.startsWith('[WARN]');
            return (
              <div key={i} className={
                isError ? 'text-rose-400' :
                isDone  ? 'text-white font-semibold' :   
                isWarn  ? 'text-yellow-400' :
                isInfo  ? 'text-ai-cyan' :   
                'text-zinc-400'
              }>{log}</div>
            );
          })}
          <div ref={terminalEndRef} />
        </div>
      </div>

      <style>{`@keyframes waveBar { from { height:4px; } to { height:20px; } }`}</style>
    </div>
  );
}
