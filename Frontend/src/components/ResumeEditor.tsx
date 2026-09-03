/**
 * Module: ResumeEditor.tsx
 * Created: 2026-09-03
 * Purpose: Editable forms for all fields of the parsed resume data.
 */

import type { ParsedResumeData } from "../types/resume";

interface Props {
  parsed: ParsedResumeData;
  onChange: (parsed: ParsedResumeData) => void;
}

/** A reusable labeled text input bound to a string value. */
function TextField(props: {
  label: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <label className="block text-xs">
      <span className="text-gray-600">{props.label}</span>
      <input
        type="text"
        value={props.value}
        onChange={(e) => props.onChange(e.target.value)}
        className="mt-1 w-full border border-gray-300 rounded px-2 py-1 text-sm"
      />
    </label>
  );
}

/** Render editable forms for the parsed resume data. */
export default function ResumeEditor({ parsed, onChange }: Props) {
  const update = (patch: Partial<ParsedResumeData>) =>
    onChange({ ...parsed, ...patch });

  const updatePersonal = (patch: Partial<ParsedResumeData["personal_info"]>) =>
    update({ personal_info: { ...parsed.personal_info, ...patch } });

  return (
    <div className="space-y-6">
      <section>
        <h3 className="text-sm font-semibold text-gray-800 mb-2">Personal Info</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <TextField label="Name" value={parsed.personal_info.name} onChange={(v) => updatePersonal({ name: v })} />
          <TextField label="Email" value={parsed.personal_info.email} onChange={(v) => updatePersonal({ email: v })} />
          <TextField label="Phone" value={parsed.personal_info.phone} onChange={(v) => updatePersonal({ phone: v })} />
          <TextField label="Location" value={parsed.personal_info.location} onChange={(v) => updatePersonal({ location: v })} />
          <TextField label="LinkedIn" value={parsed.personal_info.linkedin} onChange={(v) => updatePersonal({ linkedin: v })} />
          <TextField label="Website" value={parsed.personal_info.website} onChange={(v) => updatePersonal({ website: v })} />
        </div>
      </section>

      <section>
        <h3 className="text-sm font-semibold text-gray-800 mb-2">Summary</h3>
        <textarea
          value={parsed.summary}
          onChange={(e) => update({ summary: e.target.value })}
          className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
          rows={3}
        />
      </section>

      <section>
        <h3 className="text-sm font-semibold text-gray-800 mb-2">Experience</h3>
        {parsed.experience.map((exp, i) => (
          <div key={i} className="border border-gray-200 rounded p-3 mb-3 grid grid-cols-2 gap-2">
            <TextField label="Title" value={exp.title} onChange={(v) => setExp(i, "title", v)} />
            <TextField label="Company" value={exp.company} onChange={(v) => setExp(i, "company", v)} />
            <TextField label="Location" value={exp.location} onChange={(v) => setExp(i, "location", v)} />
            <TextField label="Start" value={exp.start_date} onChange={(v) => setExp(i, "start_date", v)} />
            <TextField label="End" value={exp.end_date} onChange={(v) => setExp(i, "end_date", v)} />
            <div className="col-span-2">
              <label className="block text-xs">
                <span className="text-gray-600">Description</span>
                <textarea
                  value={exp.description}
                  onChange={(e) => setExp(i, "description", e.target.value)}
                  className="mt-1 w-full border border-gray-300 rounded px-2 py-1 text-sm"
                  rows={2}
                />
              </label>
            </div>
            <button
              type="button"
              onClick={() => removeExp(i)}
              className="text-xs text-red-500 hover:underline"
            >
              Remove
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={addExp}
          className="text-sm text-blue-600 hover:underline"
        >
          + Add experience
        </button>
      </section>

      <section>
        <h3 className="text-sm font-semibold text-gray-800 mb-2">Education</h3>
        {parsed.education.map((edu, i) => (
          <div key={i} className="border border-gray-200 rounded p-3 mb-3 grid grid-cols-2 gap-2">
            <TextField label="Institution" value={edu.institution} onChange={(v) => setEdu(i, "institution", v)} />
            <TextField label="Degree" value={edu.degree} onChange={(v) => setEdu(i, "degree", v)} />
            <TextField label="Start" value={edu.start_date} onChange={(v) => setEdu(i, "start_date", v)} />
            <TextField label="End" value={edu.end_date} onChange={(v) => setEdu(i, "end_date", v)} />
            <TextField label="GPA" value={edu.gpa} onChange={(v) => setEdu(i, "gpa", v)} />
            <button type="button" onClick={() => removeEdu(i)} className="text-xs text-red-500 hover:underline self-end">
              Remove
            </button>
          </div>
        ))}
        <button type="button" onClick={addEdu} className="text-sm text-blue-600 hover:underline">
          + Add education
        </button>
      </section>

      <section>
        <h3 className="text-sm font-semibold text-gray-800 mb-2">Skills</h3>
        <input
          type="text"
          value={parsed.skills.join(", ")}
          onChange={(e) => update({ skills: splitList(e.target.value) })}
          className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
          placeholder="Comma-separated skills"
        />
      </section>

      <section>
        <h3 className="text-sm font-semibold text-gray-800 mb-2">Languages</h3>
        <input
          type="text"
          value={parsed.languages.join(", ")}
          onChange={(e) => update({ languages: splitList(e.target.value) })}
          className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
          placeholder="Comma-separated languages"
        />
      </section>
    </div>
  );

  function splitList(text: string): string[] {
    return text
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
  }

  function setExp(i: number, key: keyof ParsedResumeData["experience"][number], v: string) {
    const experience = parsed.experience.map((e, idx) => (idx === i ? { ...e, [key]: v } : e));
    update({ experience });
  }
  function removeExp(i: number) {
    update({ experience: parsed.experience.filter((_, idx) => idx !== i) });
  }
  function addExp() {
    update({
      experience: [
        ...parsed.experience,
        { company: "", title: "", location: "", start_date: "", end_date: "", description: "" },
      ],
    });
  }

  function setEdu(i: number, key: keyof ParsedResumeData["education"][number], v: string) {
    const education = parsed.education.map((e, idx) => (idx === i ? { ...e, [key]: v } : e));
    update({ education });
  }
  function removeEdu(i: number) {
    update({ education: parsed.education.filter((_, idx) => idx !== i) });
  }
  function addEdu() {
    update({
      education: [
        ...parsed.education,
        { institution: "", degree: "", start_date: "", end_date: "", gpa: "" },
      ],
    });
  }
}
