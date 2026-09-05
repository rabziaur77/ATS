/**
 * Module: UploadDropzone.tsx
 * Created: 2026-09-03
 * Purpose: Drag-and-drop / file-picker widget for uploading a CV.
 */

import { useCallback, useRef, useState } from "react";

interface Props {
  /** Fired with the selected file when the user picks or drops one. */
  onFileSelected: (file: File) => void;
  /** Fired when the user cancels or clears a chosen file. */
  onClear?: () => void;
}

const ACCEPTED = ".pdf,.docx,.txt";

/** Render a dropzone that captures a CV file and forwards it upward. */
export default function UploadDropzone({ onFileSelected, onClear }: Props) {
  const [dragOver, setDragOver] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = useCallback(
    (files: FileList | null) => {
      const file = files?.[0];
      if (file) {
        setFileName(file.name);
        onFileSelected(file);
      }
    },
    [onFileSelected]
  );

  const clear = useCallback(() => {
    setFileName(null);
    if (inputRef.current) inputRef.current.value = "";
    onClear?.();
  }, [onClear]);

  return (
    <div>
      <div
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          handleFiles(e.dataTransfer.files);
        }}
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition ${
          dragOver
            ? "border-blue-500 bg-blue-50"
            : "border-gray-300 bg-white hover:border-blue-400"
        }`}
      >
        <p className="text-gray-700">
          Drag &amp; drop your CV here, or click to browse
        </p>
        <p className="text-xs text-gray-400 mt-1">
          Supports PDF, DOCX, TXT (max 10 MB)
        </p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
      {fileName && (
        <div className="mt-3 flex items-center justify-between text-sm">
          <span className="text-gray-700">Selected: {fileName}</span>
          <button onClick={clear} className="text-red-500 hover:underline">
            Clear
          </button>
        </div>
      )}
    </div>
  );
}
