/**
 * Module: session.ts
 * Created: 2026-09-03
 * Purpose: Create and retrieve the per-browser session id used for the
 *          X-Session-ID header, so backend session scoping works.
 *
 *          The session id is also persisted as a cookie so that browser-initiated
 *          requests (e.g. iframe navigations) carry the correct session context
 *          even though they cannot set custom headers.
 */

const STORAGE_KEY = "ats_session_id";
const COOKIE_NAME = "ats_session_id";

/** Return the existing session id, or create and persist a new one. */
export function getSessionId(): string {
  let id = localStorage.getItem(STORAGE_KEY);
  if (!id) {
    id = generateId();
    localStorage.setItem(STORAGE_KEY, id);
  }
  syncCookie(id);
  return id;
}

/** Generate a random session id string. */
function generateId(): string {
  return "sess_" + Math.random().toString(36).slice(2) + Date.now().toString(36);
}

/**
 * Sync the session id to a cookie so iframe browser requests pick it up.
 *
 * The cookie expires in 30 days and uses SameSite=Lax so it is sent on
 * top-level navigations and same-site iframe loads (Vite dev proxy is
 * same-origin).
 */
function syncCookie(id: string): void {
  if (document.cookie.includes(`${COOKIE_NAME}=`)) return;
  const expires = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toUTCString();
  document.cookie = `${COOKIE_NAME}=${id}; expires=${expires}; path=/; SameSite=Lax`;
}
