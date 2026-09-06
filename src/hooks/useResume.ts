/**
 * Module: useResume.ts
 * Created: 2026-09-03
 * Purpose: React Query query + mutation hooks for loading, saving, and
 *          generating a resume.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";
import type {
  GenerateRequest,
  GenerateResponse,
  ParsedResumeData,
  ResumeDetailOut,
} from "../types/resume";

function resumeKey(id: number) {
  return ["resume", id] as const;
}

/** Fetch a single resume with its parsed data. */
async function fetchResume(id: number): Promise<ResumeDetailOut> {
  const { data } = await api.get<ResumeDetailOut>(`/resume/${id}`);
  return data;
}

/** Query hook for loading a resume's parsed data. */
export function useResume(id: number) {
  return useQuery({
    queryKey: resumeKey(id),
    queryFn: () => fetchResume(id),
  });
}

/** Save (PUT) updated parsed data for a resume. */
async function saveResume(id: number, parsed: ParsedResumeData): Promise<ResumeDetailOut> {
  const { data } = await api.put<ResumeDetailOut>(`/resume/${id}`, {
    parsed_data: parsed,
  });
  return data;
}

/** Mutation hook for saving parsed resume data. */
export function useSaveResume(id: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (parsed: ParsedResumeData) => saveResume(id, parsed),
    onSuccess: () => qc.invalidateQueries({ queryKey: resumeKey(id) }),
  });
}

/** Generate a resume in a given format and template. */
async function generateResume(id: number, req: GenerateRequest): Promise<GenerateResponse> {
  const { data } = await api.post<GenerateResponse>(`/resume/${id}/generate`, req);
  return data;
}

/** Mutation hook for generating a resume. */
export function useGenerateResume(id: number) {
  return useMutation({
    mutationFn: (req: GenerateRequest) => generateResume(id, req),
  });
}

/**
 * Fetch the HTML preview for a resume and template via the shared axios
 * client so the real X-Session-ID header is attached (cross-origin iframe
 * loads cannot carry custom headers).
 */
async function fetchResumePreview(id: number, templateId: string): Promise<string> {
  const { data } = await api.get<string>(`/resume/${id}/preview`, {
    params: { template_id: templateId },
    responseType: "text",
  });
  return data;
}

/** Query hook for the backend-rendered HTML preview of a resume/template. */
export function useResumePreview(id: number, templateId: string) {
  return useQuery({
    queryKey: ["resume", id, "preview", templateId],
    queryFn: () => fetchResumePreview(id, templateId),
    enabled: id > 0 && templateId.length > 0,
  });
}

/**
 * Fetch a generated resume file as a Blob via the shared axios client so the
 * session header authenticates the download.
 */
async function downloadResume(id: number, generatedId: number): Promise<Blob> {
  const { data } = await api.get<Blob>(`/resume/${id}/download/${generatedId}`, {
    responseType: "blob",
  });
  return data;
}

/** Mutation hook for downloading a generated resume file. */
export function useDownloadResume(id: number, generatedId: number) {
  return useMutation({
    mutationFn: () => downloadResume(id, generatedId),
  });
}
