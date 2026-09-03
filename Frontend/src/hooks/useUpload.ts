/**
 * Module: useUpload.ts
 * Created: 2026-09-03
 * Purpose: React Query mutation that uploads a CV file to the backend and
 *          returns the parsed resume id.
 */

import { useMutation } from "@tanstack/react-query";
import { api } from "../lib/api";
import type { ResumeDetailOut } from "../types/resume";

/** Upload a CV file (PDF/DOCX/TXT) and return the parsed resume. */
async function uploadCv(file: File): Promise<ResumeDetailOut> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<ResumeDetailOut>("/upload/cv", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

/** Mutation hook exposing upload handler and state. */
export function useUpload() {
  return useMutation({
    mutationFn: uploadCv,
  });
}
