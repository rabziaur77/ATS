/**
 * Module: useTemplates.ts
 * Created: 2026-09-03
 * Purpose: React Query hook for listing available resume templates.
 */

import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import type { TemplateListOut } from "../types/resume";

/** Fetch the list of built-in and custom templates. */
async function fetchTemplates(): Promise<TemplateListOut> {
  const { data } = await api.get<TemplateListOut>("/templates");
  return data;
}

/** Query hook exposing available templates with loading/error state. */
export function useTemplates() {
  return useQuery({
    queryKey: ["templates"],
    queryFn: fetchTemplates,
  });
}
