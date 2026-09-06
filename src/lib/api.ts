/**
 * Module: api.ts
 * Created: 2026-09-03
 * Purpose: Shared axios instance for the ATS backend. Injects the session id
 *          header and normalizes backend error responses.
 */

import axios from "axios";
import { getSessionId } from "./session";

/** The normalized error shape produced by the backend. */
export interface ApiError {
  code: string;
  message: string;
}

/**
 * Base URL for backend requests. Defaults to the dev proxy ('/api'); override
 * for a hosted backend via VITE_API_BASE_URL (e.g. https://<host>/api).
 */
export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? "/api";

/** Standard response envelope for our API client functions. */
export class ApiClientError extends Error {
  code: string;
  status: number | undefined;

  constructor(message: string, code: string, status?: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "X-Session-ID": getSessionId(),
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // error.response.data can be a string when a call used responseType
    // "text" (e.g. the HTML preview fetch); parse it to surface the
    // backend's normalized {error: {code, message}} shape.
    let data: unknown = error.response?.data;
    if (typeof data === "string" && data.length > 0) {
      try {
        data = JSON.parse(data);
      } catch {
        // Not JSON (e.g. a plain text error); keep the raw message fallback.
      }
    }
    const parsed = data as { error?: { code?: string; message?: string } } | null;
    const message: string = parsed?.error?.message || error.message || "Request failed";
    const code: string = parsed?.error?.code || "unknown_error";
    const status: number | undefined = error.response?.status;
    return Promise.reject(new ApiClientError(message, code, status));
  }
);

/** True when the error is a backend session-scoping rejection. */
export function isScopingError(err: unknown): boolean {
  return err instanceof ApiClientError && err.code === "scoping_violation";
}

/** Extract a human-friendly message from an unknown thrown error. */
export function errorMessage(err: unknown): string {
  if (err instanceof ApiClientError) return err.message;
  if (err instanceof Error) return err.message;
  return String(err);
}
