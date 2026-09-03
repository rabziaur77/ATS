/**
 * Module: EditorPage.tsx
 * Created: 2026-09-03
 * Purpose: Review and edit parsed resume data with a live preview, then
 *          proceed to template selection.
 */

import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import PreviewPane from "../components/PreviewPane";
import ResumeEditor from "../components/ResumeEditor";
import { useResume, useSaveResume } from "../hooks/useResume";
import { useTemplates } from "../hooks/useTemplates";
import { errorMessage } from "../lib/api";
import type { ParsedResumeData } from "../types/resume";

const DEFAULT_TEMPLATE = "classic";

/** Editor page: editable parsed-data fields alongside a live preview. */
export default function EditorPage() {
  const { id } = useParams<{ id: string }>();
  const resumeId = Number(id);
  const navigate = useNavigate();

  const resume = useResume(resumeId);
  const save = useSaveResume(resumeId);
  const templates = useTemplates();

  const [draft, setDraft] = useState<ParsedResumeData | null>(null);
  const [templateId, setTemplateId] = useState<string>(DEFAULT_TEMPLATE);
  const [error, setError] = useState<string | null>(null);

  if (resume.isPending || !resume.data) {
    return <p className="text-gray-500">Loading resume…</p>;
  }

  const parsed: ParsedResumeData = draft ?? resume.data.parsed_data;

  const handleSave = () => {
    setError(null);
    save.mutate(parsed, {
      onSuccess: () => navigate(`/template/${resumeId}`),
      onError: (err) => setError(errorMessage(err)),
    });
  };

  return (
    <div>
      <div className="mb-4">
        <Link to="/" className="text-sm text-blue-600 hover:underline">
          ← Upload another CV
        </Link>
        <h2 className="text-2xl font-semibold text-gray-900 mt-1">
          Review &amp; edit your parsed resume
        </h2>
        <p className="text-sm text-gray-500">
          {resume.data.filename} · {resume.data.file_type.toUpperCase()}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <section>
          <div className="mb-2">
            <label className="block text-xs text-gray-600 mb-1">
              Preview template
            </label>
            <select
              value={templateId}
              onChange={(e) => setTemplateId(e.target.value)}
              className="border border-gray-300 rounded px-2 py-1 text-sm"
            >
              {(templates.data?.items ?? []).map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>
          <div className="h-[600px]">
            <PreviewPane resumeId={resumeId} templateId={templateId} />
          </div>
        </section>

        <section className="bg-white border border-gray-200 rounded-xl p-4">
          <ResumeEditor parsed={parsed} onChange={setDraft} />
          <div className="mt-6 flex items-center gap-3">
            <button
              type="button"
              onClick={handleSave}
              disabled={save.isPending}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {save.isPending ? "Saving…" : "Save & Continue"}
            </button>
            {error && <span className="text-sm text-red-600">{error}</span>}
          </div>
        </section>
      </div>
    </div>
  );
}
