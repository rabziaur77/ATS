/**
 * Module: LiveResumePreview.tsx
 * Created: 2026-09-03
 * Purpose: Client-side, zero-API resume preview rendered instantly from the
 *          editing draft across any of the 10 built-in templates. No network
 *          request is made on edit or template changes.
 */

import { useMemo } from "react";
import type {
  EducationItem,
  ExperienceItem,
  ParsedResumeData,
} from "../types/resume";
import {
  getTemplateSpec,
  type SectionKey,
  type TemplateStyleSpec,
} from "./resumePreview/templates";

const DEFAULT_TITLES: Record<SectionKey, string> = {
  summary: "Professional Summary",
  experience: "Professional Experience",
  education: "Education",
  skills: "Skills",
  certifications: "Certifications",
  languages: "Languages",
  projects: "Projects",
};

/** Escape HTML-significant characters from user-provided resume content. */
function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/** Render a project/item record to its display name string. */
function projectName(project: Record<string, unknown>): string {
  const value = project["name"];
  if (typeof value === "string") return value;
  if (typeof value === "number") return String(value);
  return "";
}

/** Headline label for a section key, honoring per-template overrides. */
function labelOf(spec: TemplateStyleSpec, key: SectionKey): string {
  return spec.labels?.[key] ?? DEFAULT_TITLES[key];
}

/** Contact fields extracted from parsed personal info, in template order. */
function contactParts(
  parsed: ParsedResumeData,
  spec: TemplateStyleSpec
): string[] {
  const personal = parsed.personal_info;
  const fields: Record<string, string> = {
    email: personal.email,
    phone: personal.phone,
    location: personal.location,
    linkedin: personal.linkedin,
    website: personal.website,
  };
  const keys = spec.contact ?? [
    "email",
    "phone",
    "location",
    "linkedin",
    "website",
  ];
  return keys.map((key) => fields[key]).filter(Boolean);
}

/** Render one experience entry as markup honoring the template spec. */
function experienceItemHtml(
  exp: ExperienceItem,
  spec: TemplateStyleSpec
): string {
  const location =
    spec.expLocation === false
      ? ""
      : exp.location
      ? ` &middot; ${escapeHtml(exp.location)}`
      : "";
  const description = exp.description
    ? `<p class="desc">${escapeHtml(exp.description)}</p>`
    : "";
  const date = ` - ${escapeHtml(exp.end_date)}`;
  const head =
    spec.headDash === true
      ? `<div class="item-head"><span class="item-title">${escapeHtml(
          exp.company
        )}</span> <span class="item-date">${escapeHtml(
          exp.start_date
        )}${date}</span></div>`
      : `<div class="item-head"><span class="item-title">${escapeHtml(
          exp.company
        )}</span><span class="item-date">${escapeHtml(
          exp.start_date
        )}${date}</span></div>`;
  return (
    `<div class="item">${head}` +
    `<div class="item-sub">${escapeHtml(exp.title)}${location}</div>${description}</div>`
  );
}

/** Render one education entry as markup honoring the template spec. */
function educationItemHtml(
  edu: EducationItem,
  spec: TemplateStyleSpec
): string {
  const gpa =
    spec.eduGpa === false || !edu.gpa ? "" : ` &middot; GPA: ${escapeHtml(edu.gpa)}`;
  const date = ` - ${escapeHtml(edu.end_date)}`;
  const head =
    spec.headDash === true
      ? `<div class="item-head"><span class="item-title">${escapeHtml(
          edu.institution
        )}</span> <span class="item-date">${escapeHtml(
          edu.start_date
        )}${date}</span></div>`
      : `<div class="item-head"><span class="item-title">${escapeHtml(
          edu.institution
        )}</span><span class="item-date">${escapeHtml(
          edu.start_date
        )}${date}</span></div>`;
  return (
    `<div class="item">${head}` +
    `<div class="item-sub">${escapeHtml(edu.degree)}${gpa}</div></div>`
  );
}

/** Render one section block (heading + body) for a section key, or "". */
function sectionHtml(
  parsed: ParsedResumeData,
  key: SectionKey,
  spec: TemplateStyleSpec
): string {
  const title = labelOf(spec, key);
  const separator = spec.separator ?? ", ";

  switch (key) {
    case "summary": {
      if (
        spec.summaryMode === "hidden" ||
        spec.summaryMode === "headline" ||
        spec.variant === "header"
      )
        return "";
      const text = parsed.summary.trim();
      return text ? `<h2>${title}</h2><p class="desc">${escapeHtml(text)}</p>` : "";
    }
    case "experience":
      return parsed.experience.length
        ? `<h2>${title}</h2>${parsed.experience
            .map((exp) => experienceItemHtml(exp, spec))
            .join("")}`
        : "";
    case "education":
      return parsed.education.length
        ? `<h2>${title}</h2>${parsed.education
            .map((edu) => educationItemHtml(edu, spec))
            .join("")}`
        : "";
    case "skills": {
      if (spec.techStack) return "";
      if (!parsed.skills.length) return "";
      if (spec.paragraphKeys?.includes("skills"))
        return `<h2>${title}</h2><p class="skills">${parsed.skills
          .map(escapeHtml)
          .join(separator)}</p>`;
      const items = parsed.skills
        .map(
          (sk) =>
            `<li${spec.skillChipClass ? ` class="${spec.skillChipClass}"` : ""}>${escapeHtml(
              sk
            )}</li>`
        )
        .join("");
      return `<h2>${title}</h2><ul class="skills-tags">${items}</ul>`;
    }
    case "certifications":
    case "languages": {
      const list = key === "certifications" ? parsed.certifications : parsed.languages;
      if (!list.length) return "";
      if (spec.paragraphKeys?.includes(key))
        return `<h2>${title}</h2><p class="skills">${list
          .map(escapeHtml)
          .join(separator)}</p>`;
      return `<h2>${title}</h2><ul>${list
        .map((item) => `<li>${escapeHtml(item)}</li>`)
        .join("")}</ul>`;
    }
    case "projects": {
      const names = parsed.projects.map(projectName).filter(Boolean);
      if (!names.length) return "";
      const items = names.map((name) => {
        if (spec.variant === "stack")
          return `<div class="project">${escapeHtml(name)}</div>`;
        if (spec.projectItem)
          return `<div class="item"><div class="item-title">${escapeHtml(
            name
          )}</div></div>`;
        return `<p class="desc">${escapeHtml(name)}</p>`;
      });
      return `<h2>${title}</h2>${items.join("")}`;
    }
    default:
      return "";
  }
}

/** Wrap specs in a full HTML document guarded by the given CSS. */
function documentHtml(
  name: string,
  body: string,
  spec: TemplateStyleSpec
): string {
  return (
    `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">` +
    `<title>${escapeHtml(name)}</title><style>${spec.css}</style></head><body>` +
    `<div class="name">${escapeHtml(name)}</div>${body}</body></html>`
  );
}

/** Assemble the classic single-column variants (incl. academic/executive). */
function singleHtml(parsed: ParsedResumeData, spec: TemplateStyleSpec): string {
  const name = parsed.personal_info.name.trim() || "Resume";
  const contact = contactParts(parsed, spec);
  const headline =
    spec.summaryMode === "headline" && parsed.summary.trim()
      ? `<div class="headline">${escapeHtml(parsed.summary)}</div>`
      : "";
  const contactHtml = contact.length
    ? `<div class="contact">${contact
        .map((part) => `<span>${escapeHtml(part)}</span>`)
        .join("")}</div>`
    : "";
  const rule = spec.rule === true ? `<div class="rule"></div>` : "";
  const sections = spec.sectionOrder
    .map((key) => sectionHtml(parsed, key, spec))
    .join("");
  return documentHtml(name, `${contactHtml}${headline}${rule}${sections}`, spec);
}

/** Assemble the Modern two-column sidebar layout. */
function sidebarHtml(parsed: ParsedResumeData, spec: TemplateStyleSpec): string {
  const name = parsed.personal_info.name.trim() || "Resume";
  const contact = contactParts(parsed, spec);
  const sidebarKeys = spec.sidebarKeys ?? [];
  const contactHtml =
    `<div class="header"><div class="name">${escapeHtml(name)}</div><div class="contact">` +
    contact.map((part) => `<span>${escapeHtml(part)}</span>`).join("") +
    `</div></div>`;
  const sidebar = sidebarKeys.map((key) => sectionHtml(parsed, key, spec)).join("");
  const main = spec.sectionOrder
    .filter((key) => !sidebarKeys.includes(key))
    .map((key) => sectionHtml(parsed, key, spec))
    .join("");
  const body =
    contactHtml +
    `<div class="layout"><div class="sidebar">${sidebar}</div><div class="main">${main}</div></div>`;
  return documentHtml(name, body, spec);
}

/** Assemble the Professional header-band layout. */
function headerHtml(parsed: ParsedResumeData, spec: TemplateStyleSpec): string {
  const name = parsed.personal_info.name.trim() || "Resume";
  const contact = contactParts(parsed, spec);
  const summary = parsed.summary.trim();
  const left =
    `<div><div class="name">${escapeHtml(name)}</div>` +
    (summary
      ? `<p class="desc" style="margin-top:4px; max-width:520px;">${escapeHtml(
          summary
        )}</p>`
      : "") +
    `</div>`;
  const right = `<div class="contact">${contact
    .map((part) => `<span>${escapeHtml(part)}</span>`)
    .join("")}</div>`;
  const sections = spec.sectionOrder
    .map((key) => sectionHtml(parsed, key, spec))
    .join("");
  return documentHtml(
    name,
    `<div class="header">${left}${right}</div>${sections}`,
    spec
  );
}

/** Assemble the Technical layout with a Tech Stack bar. */
function stackHtml(parsed: ParsedResumeData, spec: TemplateStyleSpec): string {
  const name = parsed.personal_info.name.trim() || "Resume";
  const contact = contactParts(parsed, spec);
  const contactHtml = contact.length
    ? `<div class="contact">${contact
        .map((part) => `<span>${escapeHtml(part)}</span>`)
        .join("")}</div>`
    : "";
  const stack = parsed.skills.length
    ? `<div class="stack"><strong>Tech Stack</strong> ${parsed.skills
        .map(escapeHtml)
        .join(", ")}</div>`
    : "";
  const sections = spec.sectionOrder
    .filter((key) => key !== "skills")
    .map((key) => sectionHtml(parsed, key, spec))
    .join("");
  return documentHtml(name, `${contactHtml}${stack}${sections}`, spec);
}

/** Build the full preview HTML for a parsed resume in a given template. */
export function buildPreviewHtml(
  parsed: ParsedResumeData,
  spec: TemplateStyleSpec
): string {
  switch (spec.variant) {
    case "sidebar":
      return sidebarHtml(parsed, spec);
    case "header":
      return headerHtml(parsed, spec);
    case "stack":
      return stackHtml(parsed, spec);
    default:
      return singleHtml(parsed, spec);
  }
}

interface Props {
  parsed: ParsedResumeData;
  templateId?: string;
}

/** Render the editing draft as a scrollable, instantly-updating preview. */
export default function LiveResumePreview({ parsed, templateId }: Props) {
  const spec = getTemplateSpec(templateId ?? "classic");
  const srcDoc = useMemo(() => buildPreviewHtml(parsed, spec), [parsed, spec]);
  return (
    <iframe
      title="Live resume preview"
      srcDoc={srcDoc}
      className="w-full h-full border border-gray-200 rounded-lg bg-white"
    />
  );
}