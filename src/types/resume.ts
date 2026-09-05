/**
 * Module: resume.ts
 * Created: 2026-09-03
 * Purpose: TypeScript mirrors of the ATS backend Pydantic schemas.
 */

export interface PersonalInfo {
  name: string;
  email: string;
  phone: string;
  location: string;
  linkedin: string;
  website: string;
}

export interface ExperienceItem {
  company: string;
  title: string;
  location: string;
  start_date: string;
  end_date: string;
  description: string;
}

export interface EducationItem {
  institution: string;
  degree: string;
  start_date: string;
  end_date: string;
  gpa: string;
}

export interface ParsedResumeData {
  personal_info: PersonalInfo;
  summary: string;
  experience: ExperienceItem[];
  education: EducationItem[];
  skills: string[];
  certifications: string[];
  languages: string[];
  projects: Record<string, unknown>[];
}

export interface ResumeOut {
  id: number;
  session_id: string;
  filename: string;
  file_type: string;
  created_at: string;
  updated_at: string;
}

export interface ResumeDetailOut extends ResumeOut {
  parsed_data: ParsedResumeData;
}

export interface GenerateRequest {
  template_id: string;
  format: "pdf" | "docx" | "html";
  parsed_data?: ParsedResumeData;
}

export interface GenerateResponse {
  id: number;
  resume_id: number;
  template_id: string;
  format: string;
  file_path: string;
  created_at: string;
}

export interface TemplateOut {
  id: string;
  name: string;
  style?: string | null;
  layout?: string | null;
  is_custom: boolean;
}

export interface TemplateListOut {
  count: number;
  items: TemplateOut[];
}
