# ATS Frontend - Development Plan

## Vision

A web UI that lets users upload an existing CV, review and edit the parsed content, choose a resume template (10 built-in + custom), preview it live, and generate a professionally formatted resume for download. It is a client for the ATS FastAPI backend.

---

## Scope - V1

**Core flow (mirrors the backend flow):**
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

**V1 does NOT include:** Job description analysis, keyword optimization, ATS scoring, user accounts/auth flows. These mirror the backend's deferred V2 features and must not be built early.

---

## Tech Stack

| Component       | Technology                                    |
|-----------------|-----------------------------------------------|
| Framework       | React 18 + Vite + TypeScript                  |
| Routing         | React Router                                  |
| Styling         | TailwindCSS                                   |
| Server state    | TanStack Query (React Query)                  |
| HTTP client     | Axios (base URL + X-Session-ID header)        |
| PDF/Resume preview | Backend HTML preview rendered in an iframe (no extra PDF lib) |

---

## Location

```
ATS/
├── Backend/      # existing FastAPI backend (unchanged)
└── Frontend/     # new React app (this plan)
```

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

## Page Flow & Responsibilities

### 1. UploadPage
- Drag & drop or file picker (PDF / DOCX / TXT, ≤ 10MB).
- Calls `POST /api/upload/cv` (multipart).
- Shows parsing state; on success navigates to `/editor/:id`.

### 2. EditorPage
- Loads parsed data via `GET /api/resume/{id}`.
- Editable forms for: `personal_info`, `summary`, `experience[]`, `education[]`, `skills`, `certifications`, `languages`, `projects`.
- Live HTML preview pane (`GET /api/resume/{id}/preview?template_id=`).
- "Save & Continue" calls `PUT /api/resume/{id}`.

### 3. TemplatePage
- Grid of template cards from `GET /api/templates`.
- Selecting a template refreshes the live preview.
- "Generate" calls `POST /api/resume/{id}/generate`.

### 4. DonePage
- Shows generation result.
- Download buttons (PDF / DOCX / HTML) via `GET /api/resume/{id}/download/{generated_id}`.

---

## API Contract Mapping (UI → Backend)

| UI action            | Backend endpoint                                    | Method |
|----------------------|-----------------------------------------------------|--------|
| Upload CV            | `/api/upload/cv`                                    | POST   |
| Load parsed data     | `/api/resume/{id}`                                  | GET    |
| Edit/save data       | `/api/resume/{id}`                                  | PUT    |
| HTML preview         | `/api/resume/{id}/preview?template_id=`             | GET    |
| List templates       | `/api/templates`                                    | GET    |
| Generate             | `/api/resume/{id}/generate`                         | POST   |
| Download             | `/api/resume/{id}/download/{generated_id}`          | GET    |

> NOTE: These reflect the ACTUAL implemented backend contract, which differs slightly from the backend plan's tables: listing is `GET /api/resume/list`, and download targets a stored `generated_id` (rather than a format token). The UI must follow the implemented contract.

**Session scoping:** every request carries `X-Session-ID` (a per-browser id stored in localStorage). Built-in templates are read-only/global; the UI lists them but only custom templates are editable.

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

## Key Files & Responsibility

- `lib/session.ts` — read/create a per-browser session id (localStorage) sent as `X-Session-ID`.
- `lib/api.ts` — axios instance: `baseURL: /api`, default header `X-Session-ID`, response interceptor normalizing the backend error shape `{error:{code,message}}`.
- `vite.config.ts` — dev proxy so the frontend runs on port 5173 and forwards `/api` to the backend on port 8000 (avoids CORS during development; backend already enables CORS).

---

## Conventions

- **TypeScript types required** on all components/functions and all API payloads (mirrors backend "type hints required").
- **File-header comment** at the top of every source file; **doc comment on every component/function** describing its purpose (mirrors backend AGENTS.md convention).
- **V1 scope discipline:** no JD analysis, ATS scoring, or user accounts in the UI. Do not scaffold them.
- **Server state via React Query** with caching and loading/error states; no manual fetch orchestration for CRUD.

---

## Implementation Order

1. Scaffold Vite React-TS app; add Tailwind, React Router, Axios, TanStack Query.
2. Build `lib/` (api, session) and `types/`.
3. Layout + Upload page (dropzone → upload → parse → navigate to editor).
4. Editor page (parsed-data forms + live preview iframe).
5. Template page (grid + preview refresh + generate).
6. Done page (download buttons for PDF/DOCX/HTML).
7. Wire dev proxy; verify the full flow against the running backend.

---

## Verification

- `npm run dev` → open http://localhost:5173.
- Upload `tests/fixtures/sample_cv.txt` from the backend; edit parsed data; select a template; preview; generate; download.
- Confirm session scoping and CORS work end-to-end against the running FastAPI server.

---

## Future (V2+ - do NOT build in V1)

Job description analysis · keyword matching · ATS scoring · custom template builder screen · user accounts/authentication · multiple resume versions · comparisons.
