/**
 * Module: Layout.tsx
 * Created: 2026-09-03
 * Purpose: Shared app shell: header with brand + session, and page outlet.
 */

import { Outlet } from "react-router-dom";

/** Renders the persistent header and the active page via Outlet. */
export default function Layout() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <h1 className="text-lg font-semibold text-gray-900">
            ATS Resume Builder
          </h1>
          <span className="text-xs text-gray-500">Secure session</span>
        </div>
      </header>
      <main className="flex-1 px-6 py-8">
        <div className="max-w-5xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
