import React, { useState } from 'react';
import {
  Copy, Download, RefreshCw, AlertTriangle, ShieldCheck, Check,
  Briefcase, Flame, Terminal, Laugh
} from 'lucide-react';

/* ── Interfaces/props unchanged ── */
interface CaptionData {
  formal: string;
  sarcastic: string;
  "humorous-tech": string;
  "humorous-non-tech": string;
}
interface EvalData {
  accuracy_score: number;
  style_score: number;
  hallucination_detected: boolean;
  hallucinated_words: string[];
}
interface MatrixProps {
  videoId: string;
  captions: CaptionData;
  evaluations: Record<string, EvalData>;
  onReset: () => void;
}

/*
 * Hyper-Modern AI Card Styles
 * We give them a subtle color hint on hover so they don't look completely uniform and dull,
 * but the base is still a sleek zinc-900.
 */
const STYLE_META = {
  formal: {
    title: 'Formal',
    desc: 'Objective, passive-voice corporate summary.',
    Icon: Briefcase,
    hoverRing: 'focus-visible:ring-blue-500/40 hover:border-blue-500/50',
    iconColor: 'text-blue-400',
  },
  sarcastic: {
    title: 'Sarcastic',
    desc: 'Dry observational irony and light mocking.',
    Icon: Flame,
    hoverRing: 'focus-visible:ring-orange-500/40 hover:border-orange-500/50',
    iconColor: 'text-orange-400',
  },
  "humorous-tech": {
    title: 'Humorous · Tech',
    desc: 'Coding, hardware, and workflow metaphors.',
    Icon: Terminal,
    hoverRing: 'focus-visible:ring-ai-cyan/40 hover:border-ai-cyan/50',
    iconColor: 'text-ai-cyan',
  },
  "humorous-non-tech": {
    title: 'Humorous · Non-Tech',
    desc: 'Everyday relatable situations and tropes.',
    Icon: Laugh,
    hoverRing: 'focus-visible:ring-emerald-500/40 hover:border-emerald-500/50',
    iconColor: 'text-emerald-400',
  },
} as const;

/* Score bar — vibrant gradient fill for high scores */
function ScoreBar({ label, value, highlight }: { label: string; value: number; highlight?: boolean }) {
  return (
    <div className="flex flex-col gap-1 min-w-[64px]">
      <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">{label}</span>
      <div className="flex items-center gap-2">
        <div className="h-1 w-16 bg-zinc-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              highlight ? 'bg-gradient-to-r from-ai-indigo to-ai-cyan' : 'bg-zinc-600'
            }`}
            style={{ width: `${Math.round(value * 100)}%` }}
          />
        </div>
        <span className={`text-xs font-bold tabular-nums ${
          highlight ? 'text-white' : 'text-zinc-400'
        }`}>
          {Math.round(value * 100)}%
        </span>
      </div>
    </div>
  );
}

export default function Matrix({ videoId, captions, evaluations, onReset }: MatrixProps) {
  const [copiedStyle, setCopiedStyle] = useState<string | null>(null);

  /* Unchanged handlers */
  const handleCopy = (text: string, style: string) => {
    navigator.clipboard.writeText(text);
    setCopiedStyle(style);
    setTimeout(() => setCopiedStyle(null), 2000);
  };
  const handleDownloadJson = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(
      JSON.stringify({ task_id: videoId, captions, evaluations }, null, 2)
    );
    const a = document.createElement('a');
    a.setAttribute("href", dataStr);
    a.setAttribute("download", `captionforge_result_${videoId}.json`);
    document.body.appendChild(a); a.click(); a.remove();
  };

  const styleKeys = Object.keys(STYLE_META) as Array<keyof typeof STYLE_META>;

  return (
    <div className="w-full space-y-6 animate-fade-in">

      {/* Header bar */}
      <div className="glass border border-zinc-800 rounded-2xl px-6 py-5
        flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 shadow-2xl shadow-black/50">
        <div>
          <h3 className="text-base font-bold text-white font-display">Generated Style Matrix</h3>
          <p className="text-xs text-zinc-400 mt-0.5">4 styles · accuracy scores · side-by-side comparison</p>
        </div>
        <div className="flex gap-3 shrink-0">
          {/* Primary action — Vibrant Indigo->Cyan gradient */}
          <button
            onClick={handleDownloadJson}
            className="flex items-center gap-2 px-5 py-2.5 text-sm font-semibold rounded-xl
              bg-gradient-to-r from-ai-indigo to-ai-cyan text-white
              transition-all duration-200
              shadow-[0_0_18px_rgba(34,211,238,0.25)] hover:shadow-[0_0_24px_rgba(34,211,238,0.4)]
              focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ai-cyan focus-visible:ring-offset-2 focus-visible:ring-offset-obsidian"
          >
            <Download className="h-4 w-4" />
            Download JSON
          </button>
          {/* Secondary action — zinc-800, white text */}
          <button
            onClick={onReset}
            className="flex items-center gap-2 px-5 py-2.5 text-sm font-semibold rounded-xl
              bg-zinc-800 hover:bg-zinc-700 text-white
              border border-zinc-700 hover:border-zinc-500
              transition-all duration-200
              focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-500 focus-visible:ring-offset-2 focus-visible:ring-offset-obsidian"
          >
            <RefreshCw className="h-4 w-4" />
            New Video
          </button>
        </div>
      </div>

      {/* Caption Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {styleKeys.map((styleKey, idx) => {
          const meta     = STYLE_META[styleKey];
          const { Icon } = meta;
          const text     = captions[styleKey];
          const ev       = evaluations?.[styleKey];
          const hasScores = ev != null;

          return (
            <div
              key={styleKey}
              className={`flex flex-col bg-zinc-900/50 border border-zinc-800
                rounded-2xl p-6 transition-all duration-250 cursor-default
                hover:bg-zinc-900 hover:-translate-y-0.5
                hover:shadow-[0_8px_32px_rgba(0,0,0,0.5)]
                focus-visible:outline-none focus-visible:ring-2 ${meta.hoverRing}`}
              style={{ animationDelay: `${idx * 80}ms` }}
              tabIndex={0}
            >
              {/* Card header */}
              <div className="flex items-start justify-between mb-5 gap-3">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="shrink-0 h-9 w-9 rounded-xl flex items-center justify-center
                    bg-zinc-950 border border-zinc-800 shadow-inner">
                    <Icon className={`h-4 w-4 ${meta.iconColor}`} />
                  </div>
                  <div className="min-w-0">
                    <span className="inline-block text-[10px] font-bold uppercase tracking-widest
                      px-2 py-0.5 rounded border
                      bg-zinc-950 text-zinc-300 border-zinc-800">
                      {meta.title}
                    </span>
                    <p className="text-[11px] text-zinc-500 mt-0.5 truncate">{meta.desc}</p>
                  </div>
                </div>

                {/* Copy button */}
                <button
                  onClick={() => handleCopy(text, styleKey)}
                  title="Copy caption"
                  aria-label={`Copy ${meta.title} caption`}
                  className="shrink-0 p-2 rounded-lg
                    bg-zinc-800 hover:bg-zinc-700
                    border border-zinc-700 hover:border-zinc-500
                    text-zinc-400 hover:text-white
                    transition-all duration-150
                    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ai-cyan/40"
                >
                  {copiedStyle === styleKey
                    ? <Check className="h-4 w-4 text-ai-cyan check-in" />
                    : <Copy className="h-4 w-4" />
                  }
                </button>
              </div>

              {/* Caption bubble */}
              <div className="flex-1 bg-obsidian/60 border border-zinc-800/80 rounded-xl px-4 py-3.5 mb-5 shadow-inner">
                <p className="text-sm text-zinc-300 leading-relaxed italic">
                  "{text}"
                </p>
              </div>

              {/* Footer */}
              <div className="border-t border-zinc-800/80 pt-4 flex flex-wrap items-center justify-between gap-3">
                {hasScores ? (
                  <div className="flex gap-5">
                    <ScoreBar label="Accuracy"    value={ev.accuracy_score} highlight />
                    <ScoreBar label="Style Match" value={ev.style_score} />
                  </div>
                ) : (
                  <span className="text-[11px] text-zinc-600 italic">Scores pending…</span>
                )}

                {hasScores && (
                  ev.hallucination_detected ? (
                    <div className="flex items-center gap-1.5 text-[11px] font-semibold
                      text-rose-400 bg-rose-950/30 border border-rose-900/50
                      px-2.5 py-1 rounded-full">
                      <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
                      Hallucination Cleansed
                    </div>
                  ) : (
                    <div className="flex items-center gap-1.5 text-[11px] font-semibold
                      text-ai-emerald bg-emerald-950/20 border border-emerald-900/50
                      px-2.5 py-1 rounded-full">
                      <ShieldCheck className="h-3.5 w-3.5 shrink-0" />
                      Accurate
                    </div>
                  )
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
