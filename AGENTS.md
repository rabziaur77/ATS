# AGENTS.md

ATS resume builder: a monorepo where users upload a CV, review/edit the parsed content, pick one of 10 built-in templates, and download a generated resume (PDF/DOCX/HTML).

- `Backend/` — FastAPI app (Python 3.11, SQLAlchemy async + SQLite). See `Backend/AGENTS.md`.
- `Frontend/` — React 18 + Vite + TypeScript SPA. See `Frontend/AGENTS.md`.
- `.opencode/plans/` — original build plans (backend-plan.md, frontend-plan.md). **Aspirational**: where the code differs from the plans, trust the code / `Backend/README.md`.

## Commands

Run the backend first, then the frontend (its Vite dev server proxies `/api` → `http://127.0.0.1:8000`).

```bash
# Backend (shell from Backend/, venv active)
uvicorn app.main:app --reload          # dev server; swagger at /docs
pytest                                 # run all tests
python -m playwright install chromium  # one-time; required for PDF generation/tests

# Frontend (shell from Frontend/)
npm run dev          # http://localhost:5173
npm run typecheck    # tsc --noEmit — the only frontend check; no ESLint is configured
```

## Verified gotchas (high-signal, easy to get wrong)

- **API contract differs from the plan docs.** The implemented endpoints (from the routers/README):
  - list resumes: `GET /api/resume/list` (NOT `/api/resumes`)
  - download: `GET /api/resume/{id}/download/{generated_id}` (NOT `/{format}`)
  - preview: `GET /api/resume/{id}/preview?template_id=<id>` — `template_id` is required
  - custom templates: `POST /api/templates/custom`, `PUT`/`DELETE /api/templates/custom/{id}`
- **Session scoping.** Every backend request must carry `X-Session-ID`; the backend rejects read/update/delete/generate on records owned by another session (see `routers/resume.py`). The frontend injects the header automatically via the shared axios instance in `src/lib/api.ts` (id in localStorage). Do not add raw `fetch`/ad-hoc clients.
- **Two preview systems in the frontend** (don't conflate them):
  - Editor live preview is **client-side** — `src/components/LiveResumePreview.tsx` + `src/components/resumePreview/templates.ts`. `templates.ts` transcribes the backend Jinja templates' CSS/structure; it makes zero API calls per keystroke.
  - TemplatePage confirmation uses the **backend iframe** — `src/components/PreviewPane.tsx` → `GET /api/resume/{id}/preview?template_id=`.
  - If you change a backend built-in template (`Backend/app/templates/<name>/template.html` or `config.json`), also update the matching spec in `templates.ts` or the editor preview will diverge from the real output.
- **Async discipline (backend).** Handlers are `async def`; CV parsing and rendering are CPU/IO-bound and MUST be offloaded with `asyncio.to_thread(...)` (pattern in `routers/upload.py`, `routers/resume.py`). Never call them synchronously in a handler.
- **Custom templates** are user-supplied Jinja2 and MUST be rendered with `jinja2.sandbox.SandboxedEnvironment` (enforced in `services/html_generator.py`). Don't weaken this.
- **No migrations.** SQLite DB `Backend/ats.db` and its tables are auto-created on startup (`database.py:init_db`). Schema changes require editing the ORM models and deleting the db.
- **Built-in templates** live in `Backend/app/templates/<name>/` as `template.html` + `config.json` (`name`, `layout`, `accent_color`, `font_family`, `section_order`). There is no separate reportlab/docx config file — all three output formats render from the same Jinja2 HTML via `services/html_generator.py` (PDF via Playwright/Chromium).

## Conventions that apply repo-wide

- **File headers required.** Every source file starts with a header block — `Module: <file>` / `Created: <date>` / `Purpose: ...` (docstring for Python, JSDoc comment for TS/TSX). Every function/component needs a purpose docstring/comment. **Never bump the `Created` date on later edits** — it stays the file's original creation date.
- **V1 scope discipline.** Only the flow upload → edit → choose template → preview → generate → download exists. Do NOT build or scaffold V2: job-description analysis, keyword matching, ATS scoring, user accounts/auth, multi-version/compare, custom template builder. If work drifts there, stop and flag it.

## Tests

- Backend: `pytest` from `Backend/` (tests self-isolate to temp dirs via `tests/conftest.py`). PDF/DOCX/generation tests require the Playwright Chromium install.
- `tests/test_generation.py::test_generate_realistic_types` is documented in-code as **known-flaky** — don't chase a failure there without checking it actually regressed.