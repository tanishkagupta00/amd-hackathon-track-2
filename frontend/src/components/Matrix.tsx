import React, { useState } from 'react';
import { Copy, Download, RefreshCw, AlertTriangle, ShieldCheck, ChevronRight } from 'lucide-react';

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

export default function Matrix({ videoId, captions, evaluations, onReset }: MatrixProps) {
  const [copiedStyle, setCopiedStyle] = useState<string | null>(null);

  const handleCopy = (text: string, style: string) => {
    navigator.clipboard.writeText(text);
    setCopiedStyle(style);
    setTimeout(() => setCopiedStyle(null), 2000);
  };

  const handleDownloadJson = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(
      JSON.stringify({
        task_id: videoId,
        captions: captions,
        evaluations: evaluations
      }, null, 2)
    );
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `captionforge_result_${videoId}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const styleDetails = {
    formal: { title: 'Formal Report', desc: 'Objective, passive-voice corporate summary.', color: 'border-slate-300 bg-slate-50/50' },
    sarcastic: { title: 'Sarcastic Tone', desc: 'Dry observational irony and light mocking.', color: 'border-amber-300 bg-amber-50/30' },
    "humorous-tech": { title: 'Humorous (Tech)', desc: 'Coding, hardware, and workflow metaphors.', color: 'border-blue-300 bg-blue-50/30' },
    "humorous-non-tech": { title: 'Humorous (Non-Tech)', desc: 'Everyday relatable situations and tropes.', color: 'border-green-300 bg-green-50/30' }
  };

  return (
    <div className="w-full space-y-8 animate-fade-in">
      {/* Header operations */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <h3 className="text-xl font-bold text-slate-800">Generated Style Matrix</h3>
          <p className="text-sm text-slate-500 mt-0.5">Compare accuracy scores and style outputs side-by-side</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleDownloadJson}
            className="flex items-center gap-2 px-5 py-2.5 bg-brand-primary hover:bg-slate-700 text-white font-medium rounded-xl transition shadow-md text-sm"
          >
            <Download className="h-4 w-4" />
            Download Submission JSON
          </button>
          <button
            onClick={onReset}
            className="flex items-center gap-2 px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-xl transition text-sm border border-slate-200"
          >
            <RefreshCw className="h-4 w-4" />
            Process Another Video
          </button>
        </div>
      </div>

      {/* Grid displays */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {(Object.keys(styleDetails) as Array<keyof typeof styleDetails>).map((styleKey) => {
          const detail = styleDetails[styleKey];
          const text = captions[styleKey];
          const ev = evaluations[styleKey];

          return (
            <div key={styleKey} className={`flex flex-col border rounded-2xl p-6 ${detail.color} transition-all duration-300 hover:shadow-md`}>
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h4 className="font-bold text-slate-800">{detail.title}</h4>
                  <p className="text-xs text-slate-400 mt-0.5">{detail.desc}</p>
                </div>
                <button
                  onClick={() => handleCopy(text, styleKey)}
                  className="p-2 bg-white rounded-lg hover:bg-slate-100 border border-slate-200 text-slate-600 transition"
                  title="Copy caption"
                >
                  <Copy className="h-4 w-4" />
                </button>
              </div>

              {/* Caption bubble */}
              <div className="flex-1 bg-white p-4 rounded-xl border border-slate-200 text-sm text-slate-700 leading-relaxed italic mb-4">
                "{text}"
              </div>

              {/* Grading panel */}
              <div className="border-t border-slate-200/60 pt-4 flex flex-wrap justify-between items-center gap-3">
                <div className="flex gap-4">
                  <div className="flex flex-col">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Accuracy</span>
                    <span className={`text-sm font-bold ${ev.accuracy_score >= 0.8 ? 'text-green-600' : 'text-amber-600'}`}>
                      {(ev.accuracy_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Style Match</span>
                    <span className="text-sm font-bold text-slate-700">
                      {(ev.style_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>

                {ev.hallucination_detected ? (
                  <div className="flex items-center gap-1 text-xs font-semibold text-red-600 bg-red-50 border border-red-200 px-2.5 py-1 rounded-full">
                    <AlertTriangle className="h-3.5 w-3.5" />
                    <span>Hallucination Cleansed</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-1 text-xs font-semibold text-green-700 bg-green-50 border border-green-200 px-2.5 py-1 rounded-full">
                    <ShieldCheck className="h-3.5 w-3.5" />
                    <span>Accurate Elements Only</span>
                  </div>
                )}
              </div>

              {copiedStyle === styleKey && (
                <div className="text-center text-xs font-semibold text-green-600 mt-2 animate-pulse">
                  Copied to clipboard!
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
