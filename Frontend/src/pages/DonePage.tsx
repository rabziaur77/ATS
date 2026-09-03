/**
 * Module: DonePage.tsx
 * Created: 2026-09-03
 * Purpose: Shows generation success and provides download links.
 */

import { Link, useLocation, useNavigate } from "react-router-dom";

interface LocationState {
  generatedId: number;
  resumeId: number;
  format: "pdf" | "docx";
}

/** Build the download URL for a generated resume file. */
function downloadUrl(resumeId: number, generatedId: number): string {
  return `/api/resume/${resumeId}/download/${generatedId}`;
}

/** Done page: confirm generation and allow downloading the result. */
export default function DonePage() {
  const location = useLocation();
  const navigate = useNavigate();
  const state = (location.state ?? {}) as Partial<LocationState>;

  const resumeId = state.resumeId;
  const generatedId = state.generatedId;
  const format = state.format;

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

  const formatLabel = format ? format.toUpperCase() : "resume";

  return (
    <div className="max-w-xl">
      <h2 className="text-2xl font-semibold text-gray-900">
        Your resume is ready!
      </h2>
      <p className="text-sm text-gray-500 mt-1">
        Generated as <span className="uppercase">{format}</span>. Download it
        below, or go back to try another template.
      </p>

      <a
        href={downloadUrl(resumeId, generatedId)}
        className="inline-block mt-6 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
      >
        Download {formatLabel}
      </a>

      <div className="mt-4 flex gap-3">
        <Link
          to={`/template/${resumeId}`}
          className="text-sm text-blue-600 hover:underline"
        >
          Try another template
        </Link>
        <button
          type="button"
          onClick={() => navigate("/")}
          className="text-sm text-gray-500 hover:underline"
        >
          Upload a new CV
        </button>
      </div>
    </div>
  );
}
