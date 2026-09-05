/**
 * Module: UploadPage.tsx
 * Created: 2026-09-03
 * Purpose: CV upload entry point; uploads a file and navigates to the editor.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import UploadDropzone from "../components/UploadDropzone";
import { useUpload } from "../hooks/useUpload";
import { errorMessage } from "../lib/api";

/** Upload page: capture a CV file, parse it, then move to the editor. */
export default function UploadPage() {
  const navigate = useNavigate();
  const upload = useUpload();
  const [error, setError] = useState<string | null>(null);

  const handleFile = (file: File) => {
    setError(null);
    upload.mutate(file, {
      onSuccess: (resume) => {
        navigate(`/editor/${resume.id}`);
      },
      onError: (err) => setError(errorMessage(err)),
    });
  };

  return (
    <div>
      <h2 className="text-2xl font-semibold text-gray-900 mb-1">
        Upload your CV
      </h2>
      <p className="text-sm text-gray-500 mb-6">
        We'll parse it, let you review the content, and turn it into a polished
        resume.
      </p>

      <UploadDropzone onFileSelected={handleFile} onClear={() => setError(null)} />

      {upload.isPending && (
        <p className="mt-4 text-sm text-blue-600">Parsing your CV…</p>
      )}
      {error && (
        <p className="mt-4 text-sm text-red-600">Upload failed: {error}</p>
      )}
    </div>
  );
}
