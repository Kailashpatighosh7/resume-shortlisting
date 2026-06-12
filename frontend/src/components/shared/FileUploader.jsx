import { useCallback, useState } from 'react';
import { Upload, File, X } from 'lucide-react';

export default function FileUploader({
  accept,
  multiple = false,
  onFilesSelected,
  disabled = false,
  label = 'Drag & drop files here, or click to browse',
  hint,
}) {
  const [dragOver, setDragOver] = useState(false);
  const [files, setFiles] = useState([]);

  const handleFiles = useCallback(
    (fileList) => {
      const selected = Array.from(fileList);
      setFiles(selected);
      onFilesSelected?.(selected);
    },
    [onFilesSelected]
  );

  const removeFile = (index) => {
    const updated = files.filter((_, i) => i !== index);
    setFiles(updated);
    onFilesSelected?.(updated);
  };

  return (
    <div className="space-y-3">
      <label
        className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-10 transition-colors ${
          dragOver ? 'border-brand-500 bg-brand-50' : 'border-slate-300 bg-slate-50 hover:border-brand-400 hover:bg-brand-50/50'
        } ${disabled ? 'cursor-not-allowed opacity-50' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          if (!disabled) handleFiles(e.dataTransfer.files);
        }}
      >
        <Upload className="mb-3 h-10 w-10 text-slate-400" />
        <p className="text-sm font-medium text-slate-700">{label}</p>
        {hint && <p className="mt-1 text-xs text-slate-500">{hint}</p>}
        <input
          type="file"
          accept={accept}
          multiple={multiple}
          disabled={disabled}
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
      </label>

      {files.length > 0 && (
        <ul className="space-y-2">
          {files.map((file, i) => (
            <li key={`${file.name}-${i}`} className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-3 py-2">
              <div className="flex items-center gap-2 min-w-0">
                <File className="h-4 w-4 shrink-0 text-slate-400" />
                <span className="truncate text-sm text-slate-700">{file.name}</span>
                <span className="shrink-0 text-xs text-slate-400">
                  ({(file.size / 1024).toFixed(1)} KB)
                </span>
              </div>
              <button
                type="button"
                onClick={() => removeFile(i)}
                className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
              >
                <X className="h-4 w-4" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
