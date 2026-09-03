/**
 * Module: TemplatePicker.tsx
 * Created: 2026-09-03
 * Purpose: Grid of template cards with selection handling.
 */

import type { TemplateOut } from "../types/resume";
import TemplateCard from "./TemplateCard";

interface Props {
  templates: TemplateOut[];
  selectedId: string | null;
  onSelect: (t: TemplateOut) => void;
}

/** Render the template grid and manage selection. */
export default function TemplatePicker({
  templates,
  selectedId,
  onSelect,
}: Props) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {templates.map((t) => (
        <TemplateCard
          key={t.id}
          template={t}
          selected={selectedId === t.id}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}
