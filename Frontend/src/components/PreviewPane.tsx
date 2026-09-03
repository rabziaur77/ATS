/**
 * Module: PreviewPane.tsx
 * Created: 2026-09-03
 * Purpose: Renders live HTML resume preview inside an iframe.
 */

/** Build the preview src URL for a resume and template. */
export function previewUrl(resumeId: number, templateId: string): string {
  const query = new URLSearchParams({ template_id: templateId });
  return `/api/resume/${resumeId}/preview?${query.toString()}`;
}

interface Props {
  resumeId: number;
  templateId: string;
}

/** Render the resume preview in a scrollable iframe. */
export default function PreviewPane({ resumeId, templateId }: Props) {
  return (
    <iframe
      title="Resume preview"
      src={previewUrl(resumeId, templateId)}
      className="w-full h-full border border-gray-200 rounded-lg bg-white"
    />
  );
}
