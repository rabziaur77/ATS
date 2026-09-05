/**
 * Module: App.tsx
 * Created: 2026-09-03
 * Purpose: Defines the app's routes and top-level layout.
 */

import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import UploadPage from "./pages/UploadPage";
import EditorPage from "./pages/EditorPage";
import TemplatePage from "./pages/TemplatePage";
import DonePage from "./pages/DonePage";

/** Route table for the ATS Resume Builder. */
export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<UploadPage />} />
        <Route path="/editor/:id" element={<EditorPage />} />
        <Route path="/template/:id" element={<TemplatePage />} />
        <Route path="/done" element={<DonePage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
