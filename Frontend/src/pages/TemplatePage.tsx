/**
 * Module: TemplatePage.tsx
 * Created: 2026-09-03
 * Purpose: Confirm the template chosen during editing, preview it, and
 *          generate a resume.
 */

import { useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import PreviewPane from "../components/PreviewPane";
import { useGenerateResume } from "../hooks/useResume";
import { errorMessage } from "../lib/api";

const DEFAULT_TEMPLATE = "classic";

/** Template page: preview the chosen template and generate the resume. */
export default function TemplatePage() {
  const { id } = useParams<{ id: string }>();
  const resumeId = Number(id);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const templateId = searchParams.get("template") ?? DEFAULT_TEMPLATE;

  const [error, setError] = useState<string | null>(null);

  const generate = useGenerateResume(resumeId);

  const handleGenerate = (format: "pdf" | "docx") => {
    setError(null);
    generate.mutate(
      { template_id: templateId, format },
      {
        onSuccess: (result) => {
          navigate("/done", {
            state: {
              generatedId: result.id,
              resumeId,
              format,
            },
          });
        },
        onError: (err) => setError(errorMessage(err)),
      }
    );
  };

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">
            Confirm your template
          </h2>
          <p className="text-sm text-gray-500">
            Review the preview for your selected template, then generate.
          </p>
        </div>
        <button
          type="button"
          onClick={() => navigate(`/editor/${resumeId}`)}
          className="text-sm text-blue-600 hover:underline"
        >
          ← Back to editor
        </button>
      </div>

      <div className="max-w-3xl mx-auto">
        <div className="flex flex-col gap-4">
          <div className="h-[520px]">
            <PreviewPane resumeId={resumeId} templateId={templateId} />
          </div>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => handleGenerate("pdf")}
              disabled={generate.isPending}
              className="flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              Generate PDF
            </button>
            <button
              type="button"
              onClick={() => handleGenerate("docx")}
              disabled={generate.isPending}
              className="flex-1 bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-900 disabled:opacity-50"
            >
              Generate DOCX
            </button>
          </div>
        </div>
        {generate.isPending && (
          <p className="text-sm text-blue-600 mt-3">Generating your resume…</p>
        )}
        <p className="text-sm text-red-600 mt-2">{error}</p>
      </div>
    </div>
  );
}
