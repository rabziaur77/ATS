/**
 * Module: TemplateCard.tsx
 * Created: 2026-09-03
 * Purpose: Displays a single template option with a selection state.
 */

import type { TemplateOut } from "../types/resume";

interface Props {
  template: TemplateOut;
  selected: boolean;
  onSelect: (t: TemplateOut) => void;
}

/** Render a selectable template card. */
export default function TemplateCard({ template, selected, onSelect }: Props) {
  return (
    <button
      type="button"
      onClick={() => onSelect(template)}
      className={`text-left border rounded-xl p-4 transition ${
        selected
          ? "border-blue-500 bg-blue-50 ring-2 ring-blue-200"
          : "border-gray-200 bg-white hover:border-blue-300"
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="font-medium text-gray-900">{template.name}</span>
        {template.is_custom && (
          <span className="text-[10px] uppercase tracking-wide text-purple-600 bg-purple-50 px-2 py-0.5 rounded">
            Custom
          </span>
        )}
      </div>
      {template.style && (
        <p className="text-xs text-gray-500 mt-1">{template.style}</p>
      )}
    </button>
  );
}
