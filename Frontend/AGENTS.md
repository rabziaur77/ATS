# AGENTS.md

Project context for working on the **ATS Frontend**. This file summarizes the tech stack, structure, and conventions from the frontend development plan so future sessions can work efficiently without re-reading the full plan.

> Full plan reference: `.opencode/plans/frontend-plan.md` (at the repository root)

---

## Project Vision

A web UI that lets users upload an existing CV, review and edit the parsed content, choose a resume template (10 built-in + custom), preview it live, and generate a professionally formatted resume for download. It is a client for the ATS FastAPI backend (`../Backend`).

## V1 Scope

**Core flow (mirrors the backend):**
```
Upload CV (PDF/DOCX/TXT)
    ↓
Edit Parsed Content (preview/edit)
    ↓
Select Template (10 built-in + custom)
    ↓
Live HTML Preview
    ↓
Generate Resume (PDF / DOCX / HTML)
    ↓
Download
```

**Explicitly OUT of scope for V1:** Job description analysis, keyword matching, ATS scoring, user accounts/authentication. These mirror the backend's deferred V2 features and must NOT be built early.

---

## Tech Stack

| Component       | Technology                               |
|-----------------|------------------------------------------|
| Framework       | React 18 + Vite + TypeScript             |
| Routing         | React Router                             |
| Styling         | TailwindCSS                              |
| Server state    | TanStack Query (React Query)             |
| HTTP client     | Axios (base URL + X-Session-ID header)   |
| Resume preview  | Backend HTML preview rendered in an iframe |

---

## Dev Commands

Run these from the `Frontend/` directory.

```bash
npm install          # install dependencies
npm run dev          # dev server (http://localhost:5173)
npm run build        # production build
npm run preview      # preview the production build
npm run lint         # lint (ESLint) if configured
npm run typecheck    # tsc --noEmit for type checking
```

The Vite dev server proxies `/api` → `http://127.0.0.1:8000` (the backend). Run the backend (`uvicorn app.main:app --reload` in `../Backend`) alongside `npm run dev`.

---

## Project Structure

```
Frontend/
├── index.html
├── package.json
├── vite.config.ts            # dev proxy /api → http://127.0.0.1:8000
├── tailwind.config.js
├── postcss.config.js
├── tsconfig.json
├── src/
│   ├── main.tsx              # app entry, providers (QueryClient, Router)
│   ├── App.tsx               # route definitions
│   ├── lib/
│   │   ├── api.ts            # axios instance (base URL + X-Session-ID)
│   │   └── session.ts        # session id create/retrieve (localStorage)
│   ├── types/
│   │   └── resume.ts         # TS mirrors of backend Pydantic schemas
│   ├── components/
│   │   ├── Layout.tsx
│   │   ├── UploadDropzone.tsx
│   │   ├── TemplateCard.tsx
│   │   ├── TemplatePicker.tsx
│   │   ├── ResumeEditor.tsx  # editable parsed-data forms
│   │   └── PreviewPane.tsx   # iframe of /preview HTML
│   ├── pages/
│   │   ├── UploadPage.tsx
│   │   ├── EditorPage.tsx
│   │   ├── TemplatePage.tsx
│   │   └── DonePage.tsx      # download results
│   └── hooks/
│       ├── useUpload.ts
│       ├── useResume.ts
│       └── useTemplates.ts
```

---

## Architecture Conventions

- **Pages orchestrate, components present:** route-level pages (`pages/`) wire data + navigation; presentational components (`components/`) render UI and emit events.
- **Server state via React Query:** query/mutation hooks live in `hooks/`; no manual fetch orchestration for CRUD. Pages consume hooks; components stay presentational.
- **Single HTTP client:** all requests go through `lib/api.ts`. Requests to the backend are never made directly with raw `fetch` or ad-hoc axios instances.
- **Session scoping:** every request carries `X-Session-ID` from `lib/session.ts` (a per-browser id in localStorage). Built-in templates are read-only/global; only custom templates are editable in the UI.
- **Preview via iframe:** the live resume preview is rendered by embedding the backend HTML preview endpoint, not re-rendered client-side.
- **The UI must follow the ACTUAL implemented backend contract** (see API mapping below), which differs slightly from the backend plan's tables: listing is `GET /api/resume/list`, and download targets a stored `generated_id`.

---

## Coding Conventions

- **TypeScript types required:** all components, functions, and API payloads must be fully typed. No `any` for domain models. Use the types in `types/resume.ts` rather than inline shapes.
- **Typed API responses:** cast axios responses to the mirror types in `types/`; validate against the backend Pydantic shapes.
- **Component style:** functional components with hooks; keep components small and single-responsibility.
- **Styling:** TailwindCSS utility classes; do not introduce a separate CSS-in-JS library without discussion.
- **Error handling:** surface backend errors via the normalized shape `{error:{code,message}}` (configured in `lib/api.ts`); use React Query error states and show user-friendly messages.

### Comment & Docstring Convention

Every source file must carry clear comments describing its purpose.

**File headers (every module):**
```tsx
/**
 * Module: UploadDropzone.tsx
 * Created: 2026-09-03
 * Purpose: Drag-and-drop / file-picker widget for uploading a CV.
 */
```
- Every file starts with a header comment containing: module name, creation date, and what the file is for.
- Use the file's original creation date (do not bump it on later edits).

**Component/function comments:**
```tsx
/** Renders the upload dropzone and fires onFileSelected with the chosen file. */
export function UploadDropzone({ onFileSelected }: Props) { ... }
```
- Every component/function has a doc comment stating what it does.
- Include `@param`/`@returns` comments where behavior is not obvious.
- Follow the existing style in the codebase.

---

## API Contract Mapping (UI → Backend)

| UI action            | Backend endpoint                                   | Method |
|----------------------|----------------------------------------------------|--------|
| Upload CV            | `/api/upload/cv`                                   | POST   |
| Load parsed data     | `/api/resume/{id}`                                 | GET    |
| Edit/save data       | `/api/resume/{id}`                                 | PUT    |
| HTML preview         | `/api/resume/{id}/preview?template_id=`            | GET    |
| List templates       | `/api/templates`                                   | GET    |
| Generate             | `/api/resume/{id}/generate`                        | POST   |
| Download             | `/api/resume/{id}/download/{generated_id}`         | GET    |
| List user resumes    | `/api/resume/list`                                 | GET    |

**Session scoping:** every request carries `X-Session-ID`. Backend rejects access to resources owned by other sessions.

---

## Data Types (TS mirrors)

`types/resume.ts` mirrors the backend Pydantic schemas:

```ts
interface PersonalInfo { name: string; email: string; phone: string; location: string; linkedin: string; website: string }
interface ExperienceItem { company: string; title: string; location: string; start_date: string; end_date: string; description: string }
interface EducationItem { institution: string; degree: string; start_date: string; end_date: string; gpa: string }
interface ParsedResumeData {
  personal_info: PersonalInfo; summary: string;
  experience: ExperienceItem[]; education: EducationItem[];
  skills: string[]; certifications: string[]; languages: string[]; projects: Record<string, unknown>[];
}
interface ResumeOut { id: number; session_id: string; filename: string; file_type: string; created_at: string; updated_at: string }
interface ResumeDetailOut extends ResumeOut { parsed_data: ParsedResumeData }
interface GenerateRequest { template_id: string; format: "pdf" | "docx" | "html"; parsed_data?: ParsedResumeData }
interface GenerateResponse { id: number; resume_id: number; template_id: string; format: string; file_path: string; created_at: string }
interface TemplateOut { id: string; name: string; style?: string | null; is_custom: boolean }
interface TemplateListOut { count: number; items: TemplateOut[] }
```

---

## Page Flow

- **UploadPage** — upload CV (`POST /api/upload/cv`), parsing state, navigate to `/editor/:id` on success.
- **EditorPage** — load/resume data; editable forms for all parsed sections; live preview; "Save & Continue" (`PUT /api/resume/{id}`).
- **TemplatePage** — template grid (`GET /api/templates`); selecting refreshes preview; "Generate" (`POST .../generate`).
- **DonePage** — show result; download buttons (PDF/DOCX/HTML) via `GET .../download/{generated_id}`.

---

## Guardrails (scope discipline)

- **V2 features must NOT be built early.** Job description analysis, keyword matching, ATS scoring, user accounts/authentication, custom template builder, multiple versions, comparisons — all deferred. Do not implement, scaffold, or partially wire them in V1.
- **V1 stays minimal:** upload → edit → select template → preview → generate → download only. If a task drifts toward a V2 feature, stop and flag it.
- **Match the backend contract exactly:** use the implemented endpoints and payload shapes above; do not invent endpoints or change payload shapes to "simplify."
- **Preserve-original-content rule:** the UI edits and submits parsed content; it must not silently drop or invent resume data on save.

---

## Implementation Order

1. Scaffold Vite React-TS app; add Tailwind, React Router, Axios, TanStack Query.
2. Build `lib/` (api, session) and `types/`.
3. Layout + Upload page.
4. Editor page (parsed-data forms + live preview iframe).
5. Template page (grid + preview refresh + generate).
6. Done page (download buttons).
7. Wire dev proxy; verify the full flow against the running backend.

## Verification

- `npm run dev` → open http://localhost:5173.
- Upload `../Backend/tests/fixtures/sample_cv.txt`; edit parsed data; select a template; preview; generate; download.
- Confirm session scoping and CORS work end-to-end against the running FastAPI server.

## Future Features (V2+ — do NOT build in V1)

Job description analysis · keyword matching · ATS scoring · custom template builder screen · user accounts/authentication · multiple resume versions · comparisons.
