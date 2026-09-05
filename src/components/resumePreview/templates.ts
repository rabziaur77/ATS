/**
 * Module: templates.ts
 * Created: 2026-09-05
 * Purpose: Client-side style specifications for the 10 built-in resume
 *          templates. Each spec transcribes the backend Jinja template's
 *          layout structure, CSS, accent, fonts, and section ordering so the
 *          editor's live preview can render any built-in template without a
 *          network request.
 */

export type SectionKey =
  | "summary"
  | "experience"
  | "education"
  | "skills"
  | "certifications"
  | "languages"
  | "projects";

export type Variant = "single" | "sidebar" | "header" | "stack";

export type SummaryMode = "section" | "headline" | "hidden";

/** Static description of a built-in template's look and structure. */
export interface TemplateStyleSpec {
  id: string;
  name: string;
  variant: Variant;
  accent: string;
  css: string;
  sectionOrder: SectionKey[];
  summaryMode?: SummaryMode;
  contact?: string[];
  labels?: Partial<Record<SectionKey, string>>;
  paragraphKeys?: SectionKey[];
  separator?: string;
  skillChipClass?: string;
  headDash?: boolean;
  expLocation?: boolean;
  eduGpa?: boolean;
  techStack?: boolean;
  projectItem?: boolean;
  sidebarKeys?: SectionKey[];
  rule?: boolean;
}

const CLASSIC_CSS = `
body{font-family:Georgia,'Times New Roman',serif;color:#1a202c;margin:0;padding:40px;font-size:11px;line-height:1.5;}
.name{font-size:24px;font-weight:bold;text-align:center;text-transform:uppercase;letter-spacing:1px;margin:0 0 2px;}
.contact{text-align:center;color:#4a5568;font-size:11px;margin:0 0 20px;}
.contact span + span::before{content:"  |  ";color:#cbd5e0;}
h2{font-size:12px;letter-spacing:1px;text-transform:uppercase;border-bottom:1px solid #1a202c;padding-bottom:4px;margin:22px 0 8px;}
.item{margin-bottom:10px;}
.item-head{display:flex;justify-content:space-between;font-size:12px;}
.item-title{font-weight:bold;}
.item-date{color:#718096;font-size:11px;font-style:italic;}
.item-sub{color:#4a5568;font-size:11px;}
.desc{font-size:11px;color:#2d3748;margin-top:2px;}
.skills-tags{padding-left:18px;}
.skills-tags li{font-size:11px;margin-bottom:2px;}
ul{margin:4px 0 0;padding-left:18px;}
li{font-size:11px;margin-bottom:2px;}
`;

const ATS_STANDARD_CSS = `
body{font-family:Arial,Helvetica,sans-serif;color:#111827;margin:0;padding:40px;font-size:11px;line-height:1.45;}
.name{font-size:22px;font-weight:bold;margin:0 0 2px;}
.contact{color:#374151;font-size:11px;margin:0 0 18px;}
.contact span + span::before{content:"  |  ";color:#9ca3af;}
h2{font-size:12px;font-weight:bold;text-transform:uppercase;letter-spacing:0.5px;border-bottom:1px solid #d1d5db;margin:16px 0 6px;padding-bottom:3px;}
.item{margin-bottom:8px;}
.item-head{display:block;font-size:11px;}
.item-title{font-weight:bold;}
.item-date{font-style:normal;color:#374151;}
.item-sub{color:#374151;}
.desc{margin:2px 0 0;}
.skills{display:block;}
p{margin:2px 0;}
`;

const ELEGANT_CSS = `
body{font-family:Georgia,serif;color:#1f2937;margin:0;padding:56px 64px;font-size:11px;line-height:1.55;}
.name{font-size:30px;font-weight:400;letter-spacing:3px;text-transform:uppercase;margin:0;color:#0f172a;}
.contact{color:#6b7280;font-size:10px;letter-spacing:0.5px;margin:8px 0 0;}
.contact span + span::before{content:"  \u00b7  ";}
.rule{border-bottom:1px solid #0f172a;margin:24px 0;}
h2{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#374151;margin:26px 0 10px;}
.item{margin-bottom:12px;}
.item-head{display:flex;justify-content:space-between;font-size:12px;}
.item-title{font-weight:700;}
.item-date{color:#9ca3af;font-size:10px;font-style:italic;}
.item-sub{color:#6b7280;font-size:11px;}
.desc{font-size:11px;color:#374151;margin-top:2px;font-weight:300;}
.skills{color:#374151;font-size:11px;}
ul{margin:4px 0 0;padding-left:16px;}
li{font-size:11px;margin-bottom:3px;}
`;

const EXECUTIVE_CSS = `
body{font-family:Palatino,Georgia,serif;color:#111827;margin:0;padding:48px 80px;font-size:11px;line-height:1.5;}
.name{font-size:26px;font-weight:700;text-align:center;letter-spacing:2px;margin:0;color:#7f1d1d;}
.headline{text-align:center;color:#374151;font-size:11px;font-style:italic;margin:6px 0 0;}
.contact{text-align:center;color:#6b7280;font-size:10px;margin:10px 0 20px;}
.contact span + span::before{content:"  |  ";}
h2{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:2px;text-align:center;color:#7f1d1d;margin:28px 0 10px;}
.item{margin-bottom:14px;}
.item-head{display:flex;justify-content:space-between;font-size:12px;}
.item-title{font-weight:700;}
.item-date{color:#6b7280;font-size:10px;}
.item-sub{color:#4b5563;font-size:11px;}
.desc{font-size:11px;color:#1f2937;margin-top:2px;}
.skills{font-size:11px;color:#374151;}
ul{margin:4px 0 0;padding-left:16px;}
li{font-size:11px;margin-bottom:3px;}
`;

const MINIMAL_CSS = `
body{font-family:Helvetica,Arial,sans-serif;color:#111827;margin:0 auto;max-width:700px;padding:72px 48px;font-size:11px;line-height:1.55;}
.name{font-size:28px;font-weight:300;letter-spacing:4px;text-transform:uppercase;margin:0 0 4px;color:#111827;}
.contact{color:#6b7280;font-size:11px;margin:0 0 32px;}
.contact span + span::before{content:"  \u00b7  ";color:#d1d5db;}
h2{font-size:10px;font-weight:400;text-transform:uppercase;letter-spacing:3px;color:#9ca3af;margin:32px 0 8px;}
.item{margin-bottom:14px;}
.item-head{display:flex;justify-content:space-between;font-size:12px;}
.item-title{font-weight:600;}
.item-date{color:#6b7280;font-size:10px;}
.item-sub{color:#4b5563;font-size:11px;}
.desc{font-size:11px;color:#374151;margin-top:2px;}
.skills{font-size:11px;color:#374151;}
ul{margin:4px 0 0;padding-left:16px;}
li{font-size:11px;margin-bottom:2px;}
`;

const SIMPLE_CSS = `
body{font-family:Arial,Helvetica,sans-serif;color:#000000;margin:0;padding:36px;font-size:11px;line-height:1.4;}
.name{font-size:20px;font-weight:bold;margin:0 0 2px;}
.contact{color:#000000;font-size:11px;margin:0 0 14px;}
.contact span + span::before{content:" | ";}
h2{font-size:12px;font-weight:bold;text-transform:uppercase;margin:14px 0 4px;}
.item{margin-bottom:8px;}
.item-head{font-size:11px;}
.item-title{font-weight:bold;}
.item-date{font-weight:normal;}
.item-sub{font-weight:normal;}
.desc{margin:1px 0 0;}
.skills{margin:0;}
ul{margin:2px 0 0;padding-left:16px;}
li{font-size:11px;margin-bottom:1px;}
`;

const ACADEMIC_CSS = `
body{font-family:Cambria,Georgia,serif;color:#1a202c;margin:0;padding:44px 56px;font-size:11px;line-height:1.5;}
.name{font-size:24px;font-weight:bold;text-transform:uppercase;letter-spacing:1px;margin:0 0 2px;color:#6b21a8;}
.contact{color:#4a5568;font-size:11px;margin:0 0 6px;}
.contact span + span::before{content:"  \u00b7  ";}
.affiliation{color:#718096;font-size:11px;font-style:italic;margin:0 0 18px;}
h2{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;border-bottom:1px solid #6b21a8;padding-bottom:3px;margin:22px 0 8px;}
.item{margin-bottom:12px;}
.item-head{display:flex;justify-content:space-between;font-size:12px;}
.item-title{font-weight:700;}
.item-date{color:#718096;font-size:10px;}
.item-sub{color:#4a5568;font-size:11px;font-style:italic;}
.desc{font-size:11px;color:#2d3748;margin-top:2px;}
.skills{font-size:11px;color:#374151;}
ul{margin:4px 0 0;padding-left:16px;}
li{font-size:11px;margin-bottom:3px;}
.publication{margin-bottom:6px;}
`;

const MODERN_CSS = `
body{font-family:'Segoe UI',Helvetica,Arial,sans-serif;color:#1f2937;margin:0;padding:0;font-size:11px;}
.header{background:#2563EB;color:#fff;padding:24px 32px;}
.header .name{font-size:26px;font-weight:700;margin:0;}
.header .contact{color:#dbeafe;font-size:11px;margin-top:4px;}
.header .contact span + span::before{content:"  |  ";}
.layout{display:flex;}
.sidebar{width:30%;background:#f3f4f6;padding:20px 18px;border-right:1px solid #e5e7eb;}
.main{flex:1;padding:20px 24px;}
h2{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#2563EB;border-bottom:2px solid #2563EB;margin:14px 0 6px;padding-bottom:3px;}
.sidebar h2{color:#374151;border-color:#cbd5e1;}
.item{margin-bottom:10px;}
.item-head{display:flex;justify-content:space-between;font-size:11px;}
.item-title{font-weight:700;}
.item-date{color:#6b7280;font-size:10px;}
.item-sub{color:#4b5563;font-size:11px;}
.desc{margin:2px 0 0;font-size:11px;}
.sidebar ul{list-style:none;margin:0;padding:0;}
.sidebar li{font-size:11px;margin:3px 0;}
.chip{list-style:none;margin:2px 0;padding:2px 8px;background:#e5e7eb;border-radius:10px;display:inline-block;margin-right:4px;color:#1f2937;font-size:10px;}
.skills-tags{padding:0;margin:0;}
.skills-tags li{display:inline-block;}
`;

const PROFESSIONAL_CSS = `
body{font-family:Calibri,Arial,sans-serif;color:#111827;margin:0;padding:44px 52px;font-size:11px;line-height:1.45;}
.header{display:flex;justify-content:space-between;align-items:flex-start;border-bottom:3px solid #1d4ed8;padding-bottom:14px;margin-bottom:18px;}
.name{font-size:26px;font-weight:700;margin:0;}
.contact{text-align:right;color:#4b5563;font-size:10px;line-height:1.6;}
.contact span{display:block;}
h2{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#1d4ed8;margin:18px 0 8px;}
.item{margin-bottom:10px;}
.item-head{display:flex;justify-content:space-between;font-size:12px;}
.item-title{font-weight:700;}
.item-date{color:#4b5563;font-size:10px;}
.item-sub{color:#4b5563;font-size:11px;}
.desc{font-size:11px;color:#374151;margin-top:2px;}
.skills-tags{list-style:none;padding:0;margin:0;}
.skills-tags li{display:inline-block;background:#eef2ff;color:#1d4ed8;padding:2px 10px;border-radius:4px;margin:2px 4px 2px 0;font-size:10px;}
ul{margin:4px 0 0;padding-left:18px;}
li{font-size:11px;margin-bottom:2px;}
`;

const TECHNICAL_CSS = `
body{font-family:'Courier New',monospace;color:#111827;margin:0;padding:40px;font-size:11px;line-height:1.5;}
.name{font-size:24px;font-weight:bold;margin:0;color:#0f766e;}
.contact{color:#4b5563;font-size:11px;margin:2px 0 16px;}
.contact span + span::before{content:"  |  ";}
.stack{background:#0f766e;color:#fff;padding:10px 14px;margin:0 0 20px;font-size:11px;}
.stack strong{text-transform:uppercase;letter-spacing:1px;margin-right:8px;}
h2{font-size:12px;font-weight:bold;text-transform:uppercase;letter-spacing:1px;border-bottom:2px solid #0f766e;margin:20px 0 8px;padding-bottom:2px;}
.item{margin-bottom:10px;}
.item-head{display:flex;justify-content:space-between;font-size:11px;}
.item-title{font-weight:bold;}
.item-date{color:#4b5563;font-size:10px;}
.item-sub{color:#4b5563;}
.desc{margin:2px 0 0;}
ul{margin:4px 0 0;padding-left:18px;}
li{font-size:11px;margin-bottom:2px;}
.project{border-left:3px solid #0f766e;padding-left:10px;margin-bottom:10px;}
`;

const DEFAULT_ORDER: SectionKey[] = [
  "summary",
  "experience",
  "education",
  "skills",
  "certifications",
  "languages",
  "projects",
];

const FULL_CONTACT = ["email", "phone", "location", "linkedin", "website"];

/** All 10 built-in template style specifications. */
export const TEMPLATE_SPECS: TemplateStyleSpec[] = [
  {
    id: "classic",
    name: "Classic",
    variant: "single",
    accent: "#1a202c",
    css: CLASSIC_CSS,
    sectionOrder: DEFAULT_ORDER,
    contact: FULL_CONTACT,
  },
  {
    id: "ats_standard",
    name: "ATS Standard",
    variant: "single",
    accent: "#334155",
    css: ATS_STANDARD_CSS,
    sectionOrder: DEFAULT_ORDER,
    contact: FULL_CONTACT,
    paragraphKeys: ["skills", "certifications", "languages"],
    separator: ", ",
  },
  {
    id: "elegant",
    name: "Elegant",
    variant: "single",
    accent: "#0f172a",
    css: ELEGANT_CSS,
    sectionOrder: DEFAULT_ORDER,
    contact: FULL_CONTACT,
    paragraphKeys: ["skills", "certifications", "languages"],
    separator: " \u00b7 ",
    rule: true,
  },
  {
    id: "executive",
    name: "Executive",
    variant: "single",
    accent: "#7f1d1d",
    css: EXECUTIVE_CSS,
    sectionOrder: DEFAULT_ORDER,
    summaryMode: "headline",
    contact: ["email", "phone", "location", "linkedin"],
    paragraphKeys: ["skills", "certifications", "languages"],
    separator: ", ",
    labels: {
      experience: "Professional Experience",
      skills: "Core Competencies",
      projects: "Selected Projects",
    },
  },
  {
    id: "minimal",
    name: "Minimal",
    variant: "single",
    accent: "#111827",
    css: MINIMAL_CSS,
    sectionOrder: [
      "summary",
      "experience",
      "education",
      "skills",
      "languages",
      "certifications",
      "projects",
    ],
    contact: ["email", "phone", "location"],
    paragraphKeys: ["skills", "certifications", "languages"],
    separator: ", ",
    labels: { summary: "About" },
    expLocation: false,
    eduGpa: false,
  },
  {
    id: "simple",
    name: "Simple",
    variant: "single",
    accent: "#000000",
    css: SIMPLE_CSS,
    sectionOrder: DEFAULT_ORDER,
    contact: ["email", "phone", "location"],
    paragraphKeys: ["skills", "certifications", "languages"],
    separator: ", ",
    headDash: true,
  },
  {
    id: "academic",
    name: "Academic",
    variant: "single",
    accent: "#6b21a8",
    css: ACADEMIC_CSS,
    sectionOrder: [
      "summary",
      "education",
      "experience",
      "certifications",
      "languages",
      "skills",
      "projects",
    ],
    summaryMode: "hidden",
    contact: ["email", "phone", "location", "linkedin"],
    paragraphKeys: ["skills"],
    separator: ", ",
    labels: {
      experience: "Academic & Professional Experience",
      skills: "Research Skills",
    },
  },
  {
    id: "modern",
    name: "Modern",
    variant: "sidebar",
    accent: "#2563EB",
    css: MODERN_CSS,
    sectionOrder: [
      "summary",
      "experience",
      "skills",
      "education",
      "projects",
      "certifications",
      "languages",
    ],
    contact: ["email", "phone", "location"],
    sidebarKeys: ["skills", "certifications", "languages"],
    skillChipClass: "chip",
  },
  {
    id: "professional",
    name: "Professional",
    variant: "header",
    accent: "#1d4ed8",
    css: PROFESSIONAL_CSS,
    sectionOrder: [
      "summary",
      "experience",
      "skills",
      "education",
      "certifications",
      "languages",
      "projects",
    ],
    contact: ["email", "phone", "location", "linkedin"],
    projectItem: true,
  },
  {
    id: "technical",
    name: "Technical",
    variant: "stack",
    accent: "#0f766e",
    css: TECHNICAL_CSS,
    sectionOrder: [
      "skills",
      "summary",
      "experience",
      "projects",
      "education",
      "certifications",
      "languages",
    ],
    contact: FULL_CONTACT,
    techStack: true,
  },
];

/** Look up a built-in template spec, falling back to Classic. */
export function getTemplateSpec(templateId: string): TemplateStyleSpec {
  return (
    TEMPLATE_SPECS.find((spec) => spec.id === templateId) ?? TEMPLATE_SPECS[0]
  );
}