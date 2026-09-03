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
