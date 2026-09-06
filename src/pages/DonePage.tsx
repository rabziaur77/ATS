/**
 * Module: DonePage.tsx
 * Created: 2026-09-03
 * Purpose: Shows generation success and provides download links.
 *
 * The download is fetched through the shared axios client as a Blob so the
 * session header authenticates the cross-origin request; the file is then
 * saved from an object URL (generic filename, backend content-disposition
 * is not exposed cross-origin).
 */

import { Link, useLocation } from "react-router-dom";
import { useDownloadResume } from "../hooks/useResume";
import { errorMessage, isScopingError } from "../lib/api";

interface LocationState {
  generatedId: number;
  resumeId: number;
  format: "pdf" | "docx";
}

/** Save a Blob as a file via a temporary anchor element. */
function saveBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/** Done page: confirm generation and allow downloading the result. */
export default function DonePage() {
  const location = useLocation();
  const state = (location.state ?? {}) as Partial<LocationState>;

  const resumeId = state.resumeId;
  const generatedId = state.generatedId;
  const format = state.format;

  const download = useDownloadResume(resumeId ?? 0, generatedId ?? 0);

  const formatLabel = format ? format.toUpperCase() : "resume";

  if (!resumeId || !generatedId) {
    return (
      <div>
        <p className="text-gray-500">No generated resume in this session.</p>
        <Link to="/" className="text-blue-600 hover:underline">
          Start over
        </Link>
      </div>
    );
  }

  const handleDownload = () => {
    download.mutate(undefined, {
      onSuccess: (blob) => saveBlob(blob, `resume.${format ?? "pdf"}`),
    });
  };

  const downloadError = download.isError
    ? isScopingError(download.error)
      ? "This resume belongs to a different session. Please upload the resume again."
      : errorMessage(download.error)
    : null;

  return (
    <div className="max-w-xl">
      <h2 className="text-2xl font-semibold text-gray-900">
        Your resume is ready!
      </h2>
      <p className="text-sm text-gray-500 mt-1">
        Generated as <span className="uppercase">{format}</span>. Download it
        below, or go back to choose a different template.
      </p>

      <button
        type="button"
        onClick={handleDownload}
        disabled={download.isPending}
        className="inline-block mt-6 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        {download.isPending ? "Preparing download…" : `Download ${formatLabel}`}
      </button>

      {downloadError && (
        <div className="mt-4 flex flex-col gap-3">
          <p className="text-sm text-red-600">{downloadError}</p>
          <Link
            to="/"
            className="inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 w-fit"
          >
            Upload Again
          </Link>
        </div>
      )}

      <div className="mt-4 flex gap-3">
        <Link
          to={`/editor/${resumeId}`}
          className="text-sm text-blue-600 hover:underline"
        >
          Choose a different template
        </Link>
        <Link
          to={`/`}
          className="text-sm text-blue-600 hover:underline"
        >
          Upload a new CV
        </Link>
      </div>
    </div>
  );
}