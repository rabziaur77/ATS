# AGENTS.md

Project context for working on the **ATS Backend**. This file summarizes the tech stack, structure, and conventions from the development plan so future sessions can work efficiently without re-reading the full plan.

> Full plan reference: `.opencode/plans/backend-plan.md` (at the repository root)

---

## Project Vision

An API where users upload existing CVs and select a preferred resume format/template. The application processes and restructures the CV while preserving the original content, generating a professionally formatted resume.

## V1 Scope

**Core flow:**
```
Upload CV (PDF/DOCX/TXT)
    ↓
Parse & Extract Structured Content
    ↓
Present Parsed Data (preview/edit)
    ↓
Select Resume Template (10 built-in + custom)
    ↓
Generate Resume (PDF / DOCX / HTML)
    ↓
Download
```

**Explicitly OUT of scope for V1:** Job description analysis, keyword optimization, ATS scoring. These are deferred as a separate future feature.

---

## Tech Stack

| Component        | Technology                           |
|------------------|--------------------------------------|
| Framework        | FastAPI (Python)                     |
| Database         | SQLite + SQLAlchemy (portable later) |
| CV Parsing       | pdfplumber (PDF), python-docx (DOCX) |
| PDF Generation   | Playwright (Chromium) -> print-to-PDF      |
| DOCX Generation  | python-docx                          |
| HTML Generation  | Jinja2 templates                     |
| AI Service       | OpenAI API (optional enhancement)    |
| File Storage     | Local filesystem (`uploads/`, `outputs/`) |

---

## Dev Commands

Run these from the `Backend/` directory.

### Install
```bash
# create & activate a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux

# install dependencies
pip install -r requirements.txt

# one-time: download the Chromium browser used for PDF rendering
python -m playwright install chromium
```

### Run (development server)
```bash
uvicorn app.main:app --reload
```

### Test
```bash
pytest                                # run all tests
pytest -q                             # quiet, minimal output
pytest tests/test_upload.py -k pdf    # filter by keyword/file
```
> If `pytest` is not yet set up, create `tests/` with fixtures and add a `pytest` config to `pyproject.toml` or `pytest.ini`.

### Diagnostics
- Interactive API docs (swagger): http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## Project Structure

```
Backend/
├── app/
│   ├── main.py                    # FastAPI app, CORS, lifespan
│   ├── config.py                  # Settings (env vars, paths)
│   ├── database.py                # SQLAlchemy engine & session
│   │
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── resume.py              # Uploaded resume record
│   │   └── template.py            # Template record (built-in + custom)
│   │
│   ├── schemas/                   # Pydantic request/response models
│   │   └── resume.py              # Request & response schemas
│   │
│   ├── routers/                   # API route handlers
│   │   ├── upload.py              # CV upload & parsing endpoint
│   │   ├── resume.py              # Resume generation & download
│   │   └── template.py            # Template listing & custom templates
│   │
│   ├── services/                  # Business logic
│   │   ├── cv_parser.py           # Extract structured data from CVs
│   │   ├── ai_service.py          # AI-powered enhancement (optional)
│   │   ├── resume_processor.py    # Restructure parsed data for templates
│   │   ├── template_service.py    # Template resolution & management
│   │   ├── pdf_generator.py       # Generate PDF output
│   │   ├── docx_generator.py      # Generate DOCX output
│   │   └── html_generator.py      # Generate HTML output
│   │
│   ├── templates/                 # Jinja2 template files
│   │   ├── classic/  modern/  minimal/  executive/  technical/
│   │   ├── professional/  academic/  simple/  elegant/  ats_standard/
│   │
│   └── utils/                     # Shared helpers
│       ├── text_extractor.py      # Low-level text extraction
│       └── content_restructurer.py # Section detection & normalization
│
├── uploads/                       # Temporary CV upload storage
├── outputs/                       # Generated resume files
├── requirements.txt
└── README.md
```

---

## Architecture Conventions

- **Layered separation:** routers → services → models/schemas. Routers stay thin; business logic lives in `services/`.
- **Parsing:** every uploaded CV (PDF/DOCX/TXT) is converted into the structured parsed-data schema below.
- **Rendering:** three independent output generators (PDF/DOCX/HTML) consume the same template-ready data produced by `resume_processor.py`.
- **Templates:** each of the 10 built-in templates ships with a Jinja2 HTML template, a layout config JSON, a reportlab config, and a python-docx config. Custom (user) templates are stored in the database.
- **AI is optional:** `ai_service.py` enhances parsing/restructuring, but rule-based parsing must always work as a fallback.
- **Storage:** uploaded CVs → `uploads/`; generated resumes → `outputs/`. Paths are stored in the DB, not the binaries.

---

## Coding Conventions

- **Async route handlers:** declare every route handler as `async def` and `await` all I/O. FastAPI runs coroutine handlers on the event loop, so no blocking calls may be made directly in them.
- **Type hints required:** all function signatures and Pydantic schemas must have full type annotations. No untyped parameters or return values. Use `Optional[X]`/`X | None` over bare `None` defaults where a value can be missing.
- **Blocking work off the event loop:** CV/PDF/DOCX parsing and reportlab/python-docx rendering are CPU/IO-bound and block the loop. Never call them synchronously in a route handler. Use one of:
  - `BackgroundTasks` when the work can complete after the HTTP response is returned (e.g., long parses/generations with a status/polling flow), or
  - `await run_in_executor(...)` / `asyncio.to_thread(...)` when the caller must wait on the result.
- **Principled async DB:** use SQLAlchemy sessions via async engine and `await` session operations (SQLite via `aiosqlite`). Avoid sync ORM calls inside handlers.
- **Small, focused modules:** keep services single-responsibility; routers thin; reuse `utils/` helpers instead of duplicating extraction logic.
- **Pydantic for boundaries:** all request/response payloads are Pydantic schemas in `app/schemas/`; internal parsed JSON follows the Parsed Data Structure schema.

### Comment & Docstring Convention

Every module file and every method/function must carry clear comments describing its purpose.

**File headers (every module):**
```python
"""
Module: cv_parser.py
Created: 2026-09-03
Purpose: Extracts structured content from uploaded CVs (PDF/DOCX/TXT)
         and returns normalized JSON matching the parsed-data schema.
"""
```
- Every file starts with a header comment containing: module name, creation date, and what the file is for.
- Use the file's original creation date (do not bump it on later edits).

**Method/function comments (every public & private function):**
```python
def parse_pdf(path: str) -> dict:
    """Extract text and detect sections from a PDF CV.

    Returns:
        dict: Structured parsed-data (see Parsed Data Structure).
    """
```
- Every method/function has a docstring stating what it does.
- Include `Returns:` and `Raises:` sections where the behavior is not obvious.
- Follow the existing style in the codebase; if a shared format exists, match it.

---

## Security & Scoping

- **SandboxedEnvironment for all custom templates:** user-supplied custom templates (Jinja2 HTML) MUST be rendered with `jinja2.sandbox.SandboxedEnvironment`, never the default `Environment`. This blocks access to dangerous attributes (`__class__`, `__globals__`, arbitrary imports) so untrusted templates cannot escape the sandbox. Built-in templates may use a non-sandboxed environment. Never enable `autoescape=False` while allowing user HTML.
- **Session-based scoping on every query:** even though V1 has no full auth, ALL resume and template queries/responses must be scoped to the caller's session/tenant id. No read/update/delete/generate may silently operate on records owned by another session. Derive the scope from the request (session header/id), and enforce it in every handler — never skip the filter for "convenience." Built-in templates are global/read-only; custom templates are scoped to their owner.
- **Path safety:** when resolving `file_path` from the DB for uploads/outputs/downloads, sanitize and confine reads to the allowed directories (`uploads/`, `outputs/`) to prevent path traversal.
- **No secrets in code:** config (db paths, OpenAI key, etc.) comes from environment variables / settings via `app/config.py`. Never hardcode or log secrets.

---

## Guardrails (scope discipline)

- **V2 features must NOT be built early.** Job description analysis, keyword matching, ATS scoring, user auth/accounts, cloud storage, batch processing, and resume comparison/diff are explicitly deferred. Do not implement, scaffold, or partially wire them in V1 "while you're at it."
- **V1 stays minimal:** the only flow is upload → parse → preview/edit → select template → generate → download. If a task drifts toward a V2 feature, stop and flag it rather than expanding scope.
- **Preserve-original-content rule:** restructuring must keep the parsed content intact — only structure/format changes are allowed, never content invention or loss. (AI enhancement may polish phrasing, but must not change meaning.)

---

## Database Schema (SQLite)

### resumes
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| filename | TEXT | Original uploaded filename |
| file_path | TEXT | Path to uploaded file |
| file_type | TEXT | pdf / docx / txt |
| parsed_data | JSON | Extracted structured content |
| created_at | DATETIME | Upload timestamp |
| updated_at | DATETIME | Last modification timestamp |

### generated_resumes
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| resume_id | INTEGER | FK → resumes.id |
| template_id | TEXT | Template used for generation |
| format | TEXT | pdf / docx / html |
| file_path | TEXT | Path to generated file |
| created_at | DATETIME | Generation timestamp |

### templates (custom only)
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Template display name |
| config | JSON | Layout configuration |
| html_template | TEXT | Custom Jinja2 HTML template content |
| is_custom | BOOLEAN | true for user-created templates |
| created_at | DATETIME | Creation timestamp |

---

## Parsed Data Structure (CV parsing output)

```json
{
  "personal_info": {
    "name": "John Doe", "email": "john@example.com",
    "phone": "+1-555-0123", "location": "New York, NY",
    "linkedin": "linkedin.com/in/johndoe", "website": ""
  },
  "summary": "Experienced software engineer with 5+ years...",
  "experience": [
    {
      "company": "Tech Corp", "title": "Senior Developer",
      "location": "New York, NY", "start_date": "2021-01",
      "end_date": "Present", "description": "Led team of 5 developers..."
    }
  ],
  "education": [
    {
      "institution": "MIT", "degree": "B.S. Computer Science",
      "start_date": "2015", "end_date": "2019", "gpa": "3.8"
    }
  ],
  "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
  "certifications": [], "languages": [], "projects": []
}
```

---

## Built-in Templates (10)

classic · modern · minimal · executive · technical · professional · academic · simple · elegant · ats_standard

---

## API Endpoints

### Upload
- `POST /api/upload/cv` — upload CV, returns parsed structured data

### Resume
- `GET /api/resume/{id}` — get parsed resume data
- `PUT /api/resume/{id}` — update/edit parsed resume data
- `POST /api/resume/{id}/generate` — generate resume from parsed data
- `GET /api/resume/{id}/download/{format}` — download as PDF/DOCX
- `GET /api/resume/{id}/preview` — preview as HTML
- `GET /api/resumes` — list all user resumes
- `DELETE /api/resume/{id}` — delete a resume

### Templates
- `GET /api/templates` — list all available templates
- `GET /api/templates/{id}` — get template details & preview
- `POST /api/templates/custom` — create a custom user template
- `PUT /api/templates/custom/{id}` — update custom template
- `DELETE /api/templates/custom/{id}` — delete custom template

---

## Service Responsibilities

| Service | Responsibility |
|---------|----------------|
| `cv_parser` | Extract text from PDF/DOCX/TXT; detect sections; return structured JSON |
| `ai_service` | Optional OpenAI enhancement with rule-based fallback |
| `resume_processor` | Reorder/normalize parsed data to match selected template |
| `template_service` | Resolve built-in (filesystem) vs custom (DB) templates |
| `pdf_generator` | Render PDF via reportlab per template config |
| `docx_generator` | Render DOCX via python-docx per template config |
| `html_generator` | Render HTML via Jinja2 template |

---

## Implementation Roadmap

- **Phase 1 — Foundation:** FastAPI app, config, database, models, schemas, upload endpoint
- **Phase 2 — CV Parsing:** PDF/DOCX/TXT extraction + section detection
- **Phase 3 — Template System:** 10 templates + `template_service` + template endpoints
- **Phase 4 — Resume Generation:** html/pdf/docx generators + `resume_processor` + generation/download endpoints
- **Phase 5 — Polish:** optional `ai_service`, error handling/validation, API docs, README

## Future Features (V2+ — do NOT build in V1)

Job description analysis & keyword matching · ATS score calculation · multiple resume versions per user · user authentication & accounts · cloud storage · batch processing · resume comparison/diff

> Refer to the **Guardrails** section above: none of these features may be implemented, scaffolded, or partially wired during V1. If work starts drifting toward a V2 feature, stop and flag it to the user instead of expanding scope.
