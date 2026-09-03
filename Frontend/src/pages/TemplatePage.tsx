/**
 * Module: TemplatePage.tsx
 * Created: 2026-09-03
 * Purpose: Template selection with live preview, then generate a resume.
 */

import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import PreviewPane from "../components/PreviewPane";
import TemplatePicker from "../components/TemplatePicker";
import { useGenerateResume } from "../hooks/useResume";
import { useTemplates } from "../hooks/useTemplates";
import { errorMessage } from "../lib/api";
import type { TemplateOut } from "../types/resume";

/** Template page: pick a template, preview it, and generate the resume. */
export default function TemplatePage() {
  const { id } = useParams<{ id: string }>();
  const resumeId = Number(id);
  const navigate = useNavigate();

  const templates = useTemplates();
  const generate = useGenerateResume(resumeId);

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSelect = (t: TemplateOut) => setSelectedId(t.id);

  const handleGenerate = (format: "pdf" | "docx") => {
    if (!selectedId) {
      setError("Please select a template first.");
      return;
    }
    setError(null);
    generate.mutate(
      { template_id: selectedId, format },
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
      <div className="mb-4">
        <Link
          to={`/editor/${resumeId}`}
          className="text-sm text-blue-600 hover:underline"
        >
          ← Back to editor
        </Link>
        <h2 className="text-2xl font-semibold text-gray-900 mt-1">
          Choose a template
        </h2>
        <p className="text-sm text-gray-500">
          Select from the formats below; the preview updates live.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <section>
          {templates.isPending ? (
            <p className="text-gray-500">Loading templates…</p>
          ) : (
            <TemplatePicker
              templates={templates.data?.items ?? []}
              selectedId={selectedId}
              onSelect={handleSelect}
            />
          )}
        </section>

        <section className="flex flex-col gap-4">
          {selectedId ? (
            <>
              <div className="h-[520px]">
                <PreviewPane resumeId={resumeId} templateId={selectedId} />
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
            </>
          ) : (
            <p className="text-gray-500">
              Select a template on the left to preview and generate.
            </p>
          )}
          {generate.isPending && (
            <p className="text-sm text-blue-600">Generating your resume…</p>
          )}
          {error && <p className="text-sm text-red-600">{error}</p>}
        </section>
      </div>
    </div>
  );
}
