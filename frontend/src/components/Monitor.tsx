import React, { useEffect, useState, useRef } from 'react';
import { Terminal, Cpu, CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import axios from 'axios';
import ParticleOrb from './ParticleOrb';

interface MonitorProps {
  videoId: string;
  videoUrl?: string;   // tmpfiles.org direct URL — passed straight to /captions/generate
  onProcessingComplete: (videoId: string, captions?: any, evaluations?: any) => void;
}

const STAGES = [
  { id: 'uploading',  name: 'Upload',  desc: 'Transferring to Gemini AI' },
  { id: 'analyzing',  name: 'Analyze', desc: 'Watching entire video' },
  { id: 'generating', name: 'Style',   desc: 'Multi-head style transformers' },
  { id: 'completed',  name: 'Done',    desc: 'Pipeline successful' },
];

const STATUS_LABEL: Record<string, string> = {
  queued:       'Queued — waiting for worker slot',
  uploading:    'Uploading — transferring video context to Gemini AI',
  analyzing:    'Analyzing — watching entire video and extracting facts',
  generating:   'Styling — running parallel style transformers (Fireworks)',
  completed:    'Complete — all captions generated successfully',
  failed:       'Failed — check execution log for details',
};

/* Waveform bar — energetic gold when active */
function WaveformBar({ delay, active }: { delay: number; active: boolean }) {
  return (
    <span
      className={`inline-block w-[3px] rounded-full transition-colors duration-300 ${
        active ? 'bg-ai-gold' : 'bg-zinc-800'
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

export default function Monitor({ videoId, videoUrl, onProcessingComplete }: MonitorProps) {
  const [status, setStatus] = useState<string>('queued');
  const [logs,   setLogs]   = useState<string[]>([]);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Build the generate request body.
    // Always include video_url so /captions/generate can work self-contained on Vercel
    // (each serverless invocation gets a fresh /tmp — the DB record from upload is gone).
    const requestBody: Record<string, any> = { video_id: videoId };
    if (videoUrl) requestBody.video_url = videoUrl;

    axios.post('/api/v1/captions/generate', requestBody)
      .then((res) => {
        // Automatically jump to completed when the synchronous API returns
        setStatus('completed');
        setLogs(prev => [...prev, '[INFO] Caption generation finished successfully.']);
        
        // Pass the result directly to avoid the separate GET request which fails on Vercel's ephemeral FS
        if (res.data && res.data.captions && res.data.evaluations) {
          onProcessingComplete(videoId, res.data.captions, res.data.evaluations);
        } else {
          onProcessingComplete(videoId); // Fallback
        }
      })
      .catch(err => {
        const errData = err.response?.data;
        let detail: string | undefined;

        // FastAPI can return either a plain string detail or a ValidationError shape
        // for errors raised via HTTPException(500, detail=...).
        if (typeof errData?.detail === 'string') {
          detail = errData.detail;
        } else if (typeof errData?.detail === 'object' && errData?.detail?.errors) {
          // Fallback for nested validation error shapes
          detail = errData.detail.errors?.[0]?.msg || errData.detail.msg;
        } else if (typeof errData === 'string') {
          detail = errData;
        }

        const errorDetail = detail || err.message || 'Unknown error';
        setLogs(prev => [...prev, `[ERROR] Failed to start generation: ${errorDetail}`]);
      });

    // 2. Mock a log stream and status transitions since we can't reliably poll the ephemeral DB
    const mockInterval = setInterval(() => {
      setStatus(prev => {
        if (prev === 'queued') {
          setLogs(l => [...l, '[INFO] Uploading video context to Gemini...']);
          return 'uploading';
        }
        if (prev === 'uploading') {
          setLogs(l => [...l, '[INFO] Analyzing multimodal frames and audio...']);
          return 'analyzing';
        }
        if (prev === 'analyzing') {
          setLogs(l => [...l, '[INFO] Extracting factual scene graph...', '[INFO] Generating multi-head stylized text...']);
          return 'generating';
        }
        return prev;
      });
    }, 2000);

    return () => clearInterval(mockInterval);
  }, [videoId]);

  useEffect(() => { terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [logs]);

  const activeIndex = STAGES.findIndex(s => s.id === status);
  const isRunning   = status !== 'completed' && status !== 'failed';
  const isFailed    = status === 'failed';
  const isCompleted = status === 'completed';

  return (
    <div className="w-full space-y-5 animate-fade-in">

      {/* ── Pipeline Tracker ── */}
      <div className="glass border border-zinc-800 rounded-2xl p-7 space-y-6 shadow-2xl shadow-black/50">

        {/* Header */}
        <div className="flex items-start justify-between gap-4 border-b border-zinc-800/70 pb-5">
          <div>
            <h3 className="text-sm font-bold text-white font-display flex items-center gap-2">
              <Cpu className="h-4 w-4 text-ai-gold shrink-0" />
              AI Orchestration Pipeline
            </h3>
            {/* Real status text from API */}
            <p className={`text-xs mt-1.5 font-mono transition-colors duration-300 ${
              isFailed               ? 'text-rose-400' :
              status === 'completed' ? 'text-ai-emerald' :
              'text-ai-goldLight'
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
              const stageIsCompleted = idx < activeIndex || status === 'completed';
              const isActive         = idx === activeIndex && isRunning;
              const isStageFail      = isFailed && idx === activeIndex;

              return (
                <div key={stage.id} className="flex flex-col items-center gap-2.5 text-center">

                  {/* Connector fill — gradient fill! */}
                  {idx > 0 && stageIsCompleted && (
                    <div
                      className="absolute h-px bg-gradient-to-r from-ai-goldDark to-ai-goldLight connector-fill"
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
                    stageIsCompleted
                      ? 'bg-ai-gold border-ai-gold text-obsidian shadow-[0_0_14px_rgba(212,175,55,0.5)]'
                      : isActive
                      ? 'bg-obsidian border-ai-gold text-ai-gold shadow-[0_0_14px_rgba(212,175,55,0.35)] animate-pulse'
                      : isStageFail
                      ? 'bg-rose-950 border-rose-600 text-rose-400'
                      : 'bg-obsidian border-zinc-800 text-zinc-500',
                  ].join(' ')}>
                    {stageIsCompleted  ? <CheckCircle2 className="h-4 w-4 check-in text-obsidian" /> :
                     isStageFail       ? <XCircle className="h-4 w-4" /> :
                     idx + 1}
                  </div>

                  {/* Label */}
                  <div>
                    <p className={`text-[11px] font-bold font-display uppercase tracking-widest transition-colors duration-300 ${
                      isActive         ? 'text-ai-goldLight' :
                      stageIsCompleted ? 'text-white' :
                      isStageFail      ? 'text-rose-400' :
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

      {/* ── Visual Processing Display & Terminal Log ── */}
      <div className="bg-[#050505] rounded-2xl border border-zinc-800 flex h-[350px] overflow-hidden shadow-2xl shadow-black/50">
        
        {/* Left Side: Dynamic Visualization */}
        <div className="w-[40%] min-w-[280px] border-r border-zinc-800/80 bg-gradient-to-b from-zinc-900/40 to-transparent flex flex-col items-center justify-center p-6 relative">
          
          <div className="absolute top-5 left-5 flex items-center gap-2.5">
            <span className={`h-2.5 w-2.5 rounded-full ${isRunning ? 'bg-ai-gold animate-pulse' : isCompleted ? 'bg-ai-emerald' : 'bg-rose-500'}`} />
            <span className="text-[10px] font-mono text-zinc-400 font-bold uppercase tracking-widest">
              {isRunning ? 'Synthesizing...' : isCompleted ? 'System Idle' : 'Error'}
            </span>
          </div>
          
          <div className="h-44 w-44 relative mt-4">
            <ParticleOrb 
              hue={isRunning ? 45 : isCompleted ? 140 : 0} 
              hoverIntensity={0.5} 
              rotateOnHover={true} 
              forceHoverState={isRunning} 
              backgroundColor="transparent"
            />
            {isRunning && (
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <Loader2 className="h-8 w-8 text-ai-gold/50 animate-spin" />
              </div>
            )}
          </div>
          
          <p className="mt-8 text-center text-xs font-medium text-zinc-400 max-w-[200px] leading-relaxed">
            {STATUS_LABEL[status] ?? 'Processing request...'}
          </p>
        </div>

        {/* Right Side: Execution Stream */}
        <div className="flex-1 flex flex-col h-full bg-[#0a0a0c]">
          <div className="flex items-center gap-2 px-5 py-3 border-b border-zinc-800/80 bg-zinc-900/50 shrink-0">
            <div className="flex gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-rose-500/30" />
              <span className="h-2.5 w-2.5 rounded-full bg-yellow-500/30" />
              <span className="h-2.5 w-2.5 rounded-full bg-ai-emerald/30" />
            </div>
            <div className="flex items-center gap-2 ml-3 text-zinc-500 text-xs font-mono">
              <Terminal className="h-3.5 w-3.5 text-ai-gold" />
              <span>execution_log.sh &nbsp;·&nbsp; {videoId.substring(0,8)}</span>
            </div>
            {isRunning && (
              <span className="ml-auto flex items-center gap-1.5 text-[10px] font-mono text-ai-gold">
                <span className="h-1.5 w-1.5 rounded-full bg-ai-gold animate-pulse" />
                LIVE
              </span>
            )}
          </div>

          <div className="flex-1 overflow-y-auto px-5 py-4 space-y-1 font-mono text-[11.5px] leading-relaxed">
            {logs.length === 0 && (
              <span className="text-zinc-600 italic">Initializing compute stream...</span>
            )}
            {logs.map((log, i) => {
              const isError = log.includes('[ERROR]') || log.includes('CRITICAL');
              const isDone  = log.includes('finished') || log.includes('complete');
              const isInfo  = log.startsWith('[INFO]');
              const isWarn  = log.startsWith('[WARN]');
              return (
                <div key={i} className={
                  isError ? 'text-rose-400 font-medium' :
                  isDone  ? 'text-white font-semibold' :   
                  isWarn  ? 'text-yellow-400' :
                  isInfo  ? 'text-ai-goldLight/90' :   
                  'text-zinc-400'
                }>{log}</div>
              );
            })}
            <div ref={terminalEndRef} />
          </div>
        </div>
      </div>

      <style>{`@keyframes waveBar { from { height:4px; } to { height:20px; } }`}</style>
    </div>
  );
}
