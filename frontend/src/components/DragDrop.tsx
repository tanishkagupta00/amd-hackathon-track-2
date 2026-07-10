import React, { useState, useRef } from 'react';
import { Upload, Film, AlertCircle } from 'lucide-react';
import axios from 'axios';

interface DragDropProps {
  onUploadSuccess: (videoId: string, filename: string) => void;
}

export default function DragDrop({ onUploadSuccess }: DragDropProps) {
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const validateAndUpload = async (file: File) => {
    setError(null);
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!ext || !['mp4', 'mov', 'avi'].includes(ext)) {
      setError("Invalid file format. Please upload an MP4, MOV, or AVI video.");
      return;
    }

    // Size limit check: e.g. 50MB
    if (file.size > 50 * 1024 * 1024) {
      setError("File size exceeds 50MB limit.");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post('/api/v1/videos', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      onUploadSuccess(response.data.video_id, response.data.filename);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to upload video file.");
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndUpload(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndUpload(e.target.files[0]);
    }
  };

  const onButtonClick = () => {
    inputRef.current?.click();
  };

  return (
    <div className="w-full animate-fade-in">
      <div
        className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
          dragActive
            ? 'border-orange-500 bg-orange-50/30'
            : 'border-slate-300 hover:border-slate-400 bg-white'
        } shadow-sm`}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept=".mp4,.mov,.avi"
          onChange={handleChange}
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="p-4 bg-slate-100 rounded-full text-slate-600">
            <Film className="h-10 w-10 text-brand-primary" />
          </div>

          <div>
            <p className="text-lg font-semibold text-slate-700">
              Drag and drop your video file here
            </p>
            <p className="text-sm text-slate-500 mt-1">
              Supports MP4, MOV, or AVI format (Max 50MB)
            </p>
          </div>

          <button
            onClick={onButtonClick}
            disabled={loading}
            className="px-6 py-2.5 bg-brand-primary hover:bg-slate-700 text-white font-medium rounded-xl shadow-md transition disabled:opacity-50"
          >
            {loading ? 'Uploading...' : 'Browse Local Files'}
          </button>
        </div>
      </div>

      {error && (
        <div className="mt-4 flex items-center gap-2 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl animate-fade-in text-sm font-medium">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
