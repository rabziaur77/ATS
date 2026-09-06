/**
 * Module: PreviewPane.tsx
 * Created: 2026-09-03
 * Purpose: Renders the backend HTML resume preview inside an iframe.
 *
 * The HTML is fetched through the shared axios client (so X-Session-ID is
 * attached even cross-origin) and injected via srcDoc, since a plain iframe
 * src load cannot carry the session header.
 */

import { Link } from "react-router-dom";
import { useResumePreview } from "../hooks/useResume";
import { errorMessage, isScopingError } from "../lib/api";

interface Props {
  resumeId: number;
  templateId: string;
}

/**
 * Render the resume preview in a scrollable iframe.
 *
 * Shows the HTML once fetched; on error shows an inline message with an
 * "Upload Again" action when the failure is a session-scoping rejection.
 */
export default function PreviewPane({ resumeId, templateId }: Props) {
  const preview = useResumePreview(resumeId, templateId);

  return (
    <div className="w-full h-full">
      {preview.isPending && (
        <div className="h-full flex items-center justify-center text-gray-500">
          Loading preview…
        </div>
      )}

      {preview.isError && (
        <div className="h-full flex flex-col items-center justify-center gap-3 text-center p-6">
          <p className="text-red-600">
            {isScopingError(preview.error)
              ? "This resume belongs to a different session. Please upload the resume again."
              : errorMessage(preview.error)}
          </p>
          <Link
            to="/"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Upload Again
          </Link>
        </div>
      )}

      {preview.data && (
        <iframe
          title="Resume preview"
          srcDoc={preview.data}
          className="w-full h-full border border-gray-200 rounded-lg bg-white"
        />
      )}
    </div>
  );
}