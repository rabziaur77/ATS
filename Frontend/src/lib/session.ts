/**
 * Module: session.ts
 * Created: 2026-09-03
 * Purpose: Create and retrieve the per-browser session id used for the
 *          X-Session-ID header, so backend session scoping works.
 */

const STORAGE_KEY = "ats_session_id";

/** Return the existing session id, or create and persist a new one. */
export function getSessionId(): string {
  let id = localStorage.getItem(STORAGE_KEY);
  if (!id) {
    id = generateId();
    localStorage.setItem(STORAGE_KEY, id);
  }
  return id;
}

/** Generate a random session id string. */
function generateId(): string {
  return "sess_" + Math.random().toString(36).slice(2) + Date.now().toString(36);
}
