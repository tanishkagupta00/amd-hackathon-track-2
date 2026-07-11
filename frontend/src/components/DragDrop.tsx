import React, { useState, useRef, useEffect } from 'react';
import { AlertCircle } from 'lucide-react';
import axios from 'axios';

/* ── All logic/props/API calls unchanged ── */

interface DragDropProps {
  onUploadSuccess: (videoId: string, filename: string) => void;
}

function VideoStripIllustration({ active }: { active: boolean }) {
  // Colours mapped to new tokens: ai-indigo (#6366f1) active, zinc-700 (#3F3F46) inactive
  const accentFill  = active ? '#6366f1' : '#3F3F46';
  const frameFill   = active ? 'rgba(99,102,241,0.1)' : 'rgba(24,24,27,0.5)';
  const frameStroke = active ? '#6366f1' : '#27272A';
  const playFill    = active ? '#22d3ee' : '#A1A1AA'; // ai-cyan active, zinc-400 inactive

  return (
    <svg
      width="80" height="64"
      viewBox="0 0 80 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`transition-all duration-300 ${active ? 'opacity-100' : 'opacity-60'}`}
    >
      <rect x="2" y="10" width="76" height="44" rx="4"
        stroke={frameStroke} strokeWidth="1.5" fill={frameFill} />
      <rect x="6"  y="15" width="6" height="6" rx="1" fill={accentFill} />
      <rect x="6"  y="27" width="6" height="6" rx="1" fill={accentFill} />
      <rect x="6"  y="39" width="6" height="6" rx="1" fill={accentFill} />
      <rect x="68" y="15" width="6" height="6" rx="1" fill={accentFill} />
      <rect x="68" y="27" width="6" height="6" rx="1" fill={accentFill} />
      <rect x="68" y="39" width="6" height="6" rx="1" fill={accentFill} />
      <path d="M34 26 L34 38 L46 32 Z" fill={playFill} className="transition-colors duration-300" />
      {/* Waveform bars */}
      {[
        [17,52,6,'#6366f1'], [22,49,9,'#6366f1'], [27,51,7,'#22d3ee'],
        [32,48,10,'#22d3ee'],[37,50,8,'#6366f1'], [42,52,6,'#6366f1'],
        [47,49,9,'#22d3ee'], [52,51,7,'#6366f1'], [57,48,10,'#22d3ee'],
      ].map(([x, y, h, c], i) => (
        <rect key={i}
          x={x} y={y} width="3" height={h} rx="1"
          fill={active ? (c as string) : '#3F3F46'}
          opacity={active ? 0.9 : 0.5}
        />
      ))}
    </svg>
  );
}

function FilePreviewCard({ file, uploading }: { file: File; uploading: boolean }) {
  const [thumbUrl, setThumbUrl] = useState<string | null>(null);

  useEffect(() => {
    const url = URL.createObjectURL(file);
    const video = document.createElement('video');
    video.src = url;
    video.currentTime = 0.5;
    video.muted = true;
    video.playsInline = true;

    const handleSeeked = () => {
      const canvas = document.createElement('canvas');
      canvas.width = 320; canvas.height = 180;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0, 320, 180);
        setThumbUrl(canvas.toDataURL('image/jpeg', 0.8));
      }
      URL.revokeObjectURL(url);
    };

    video.addEventListener('seeked', handleSeeked, { once: true });
    video.load();
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const sizeMB = (file.size / (1024 * 1024)).toFixed(1);

  return (
    <div className="morph-in glass border border-zinc-800 rounded-2xl overflow-hidden shadow-2xl shadow-black/50">
      {/* Thumbnail */}
      <div className="relative h-44 bg-black flex items-center justify-center overflow-hidden">
        {thumbUrl
          ? <img src={thumbUrl} alt="preview" className="w-full h-full object-cover" />
          : <VideoStripIllustration active={false} />
        }
        <div className="absolute inset-0 bg-gradient-to-t from-zinc-950 via-transparent to-transparent" />
        {uploading && <div className="absolute inset-0 scan-line overflow-hidden rounded-none" />}

        {/* Status badge */}
        <div className="absolute bottom-3 left-4">
          {uploading ? (
            <span className="flex items-center gap-1.5 text-xs font-mono font-semibold
              text-ai-cyan bg-zinc-950/80 border border-ai-cyan/30
              px-2.5 py-1 rounded-full backdrop-blur-sm">
              <span className="h-1.5 w-1.5 rounded-full bg-ai-cyan animate-pulse" />
              Uploading…
            </span>
          ) : (
            <span className="flex items-center gap-1.5 text-xs font-mono font-semibold
              text-zinc-400 bg-zinc-950/80 border border-zinc-800
              px-2.5 py-1 rounded-full backdrop-blur-sm">
              <span className="h-1.5 w-1.5 rounded-full bg-zinc-400" />
              Ready
            </span>
          )}
        </div>
      </div>

      {/* Meta row */}
      <div className="px-5 py-3.5 flex items-center justify-between border-t border-zinc-800 bg-zinc-900/50">
        <div className="flex items-center gap-3 min-w-0">
          <div className="shrink-0 h-8 w-8 rounded-lg bg-zinc-800 border border-zinc-700 flex items-center justify-center">
            <VideoStripIllustration active={false} />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-white truncate max-w-[260px]">{file.name}</p>
            <p className="text-xs text-zinc-400 mt-0.5">{sizeMB} MB</p>
          </div>
        </div>
        {uploading && (
          <div className="shrink-0 h-5 w-5 rounded-full border-2 border-ai-cyan border-t-transparent animate-spin" />
        )}
      </div>
    </div>
  );
}

export default function DragDrop({ onUploadSuccess }: DragDropProps) {
  const [dragActive,   setDragActive]   = useState(false);
  const [loading,      setLoading]      = useState(false);
  const [error,        setError]        = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [morphing,     setMorphing]     = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault(); e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };

  const validateAndUpload = async (file: File) => {
    setError(null);
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!ext || !['mp4', 'mov', 'avi'].includes(ext)) {
      setError('Invalid file format. Please upload an MP4, MOV, or AVI video.');
      return;
    }
    if (file.size > 4.5 * 1024 * 1024) { 
      setError('File size exceeds Vercel 4.5MB Serverless limit. Please use a smaller video for this demo.'); 
      return; 
    }

    setMorphing(true);
    await new Promise(r => setTimeout(r, 200));
    setSelectedFile(file);
    setMorphing(false);

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await axios.post('/api/v1/videos', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      onUploadSuccess(response.data.video_id, response.data.filename);
    } catch (err: any) {
      if (err.response?.status === 413) {
        setError("Vercel Error: Payload Too Large. The file exceeded the 4.5MB serverless limit.");
      } else if (err.response?.status === 504) {
        setError("Vercel Error: Gateway Timeout. Upload took too long (limit is 10s).");
      } else {
        setError(err.response?.data?.detail || 'Failed to upload video file.');
      }
      setSelectedFile(null);
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault(); e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) validateAndUpload(e.dataTransfer.files[0]);
  };
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files?.[0]) validateAndUpload(e.target.files[0]);
  };
  const onButtonClick = () => inputRef.current?.click();

  return (
    <div className="w-full animate-fade-in">
      <input ref={inputRef} type="file" className="hidden" accept=".mp4,.mov,.avi" onChange={handleChange} />

      {selectedFile ? (
        <FilePreviewCard file={selectedFile} uploading={loading} />
      ) : (
        <div
          className={[
            'relative border border-dashed rounded-2xl p-14 text-center transition-all duration-200 glass cursor-pointer select-none',
            dragActive
              ? 'border-ai-indigo/70 bg-ai-indigo/10 drag-glow'         // indigo glow on drag
              : 'border-zinc-800 hover:border-zinc-600 bg-zinc-900/40',
            morphing ? 'morph-out' : 'morph-in',
          ].join(' ')}
          onDragEnter={handleDrag} onDragOver={handleDrag}
          onDragLeave={handleDrag} onDrop={handleDrop}
          onClick={onButtonClick}
        >
          <div className="flex flex-col items-center justify-center gap-5 pointer-events-none">
            <VideoStripIllustration active={dragActive} />

            <div className="space-y-1.5">
              <p className={`text-base font-semibold font-display transition-colors duration-200 ${
                dragActive ? 'text-white' : 'text-zinc-300'
              }`}>
                {dragActive ? 'Release to analyse' : 'Drop a video file to begin analysis'}
              </p>
              <p className="text-sm text-zinc-500">
                MP4 &nbsp;·&nbsp; MOV &nbsp;·&nbsp; AVI &nbsp;·&nbsp; max 4.5 MB (Vercel Limit)
              </p>
            </div>

            {/* Secondary button — zinc-800 base */}
            <button
              type="button"
              className="pointer-events-auto mt-2 px-6 py-2.5 rounded-xl text-sm font-semibold
                bg-zinc-800 hover:bg-zinc-700 text-white
                border border-zinc-700 hover:border-zinc-500
                transition-all duration-200
                focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ai-indigo/50"
              onClick={(e) => { e.stopPropagation(); onButtonClick(); }}
            >
              Browse local files
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-4 flex items-center gap-2.5 p-4
          bg-rose-950/40 border border-rose-900/50 text-rose-400
          rounded-xl animate-fade-in text-sm font-medium">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
