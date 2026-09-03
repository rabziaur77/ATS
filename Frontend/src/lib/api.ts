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
  baseURL: "/api",
  headers: {
    "X-Session-ID": getSessionId(),
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const data = error.response?.data?.error;
    const message: string = data?.message || error.message || "Request failed";
    const code: string = data?.code || "unknown_error";
    const status: number | undefined = error.response?.status;
    return Promise.reject(new ApiClientError(message, code, status));
  }
);

/** Extract a human-friendly message from an unknown thrown error. */
export function errorMessage(err: unknown): string {
  if (err instanceof ApiClientError) return err.message;
  if (err instanceof Error) return err.message;
  return String(err);
}
