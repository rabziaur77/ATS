# ATS Backend

An API where users upload existing CVs and select a preferred resume format/template. The application parses and restructures the CV while preserving the original content, ultimately generating a professionally formatted resume.

## Scope (V1)

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

> Job description analysis, keyword optimization, and ATS scoring are **out of scope** for V1 and reserved for a future feature.

## Tech Stack

- **FastAPI** (Python) — async REST framework
- **SQLite + SQLAlchemy 2.0** (async / aiosqlite) — storage (portable later)
- **pdfplumber** — PDF text extraction
- **python-docx** — DOCX handling & generation
- **reportlab** — PDF generation
- **Jinja2** (SandboxedEnvironment for custom templates) — HTML rendering

## Project Structure

```
Backend/
├── app/
│   ├── main.py                 # FastAPI app, CORS, lifespan, error handler
│   ├── config.py               # Settings (env vars, paths)
│   ├── database.py             # Async SQLAlchemy engine & session
│   ├── models/                 # resume.py, template.py
│   ├── schemas/                # Pydantic request/response models
│   ├── routers/                # upload.py, resume.py, template.py
│   ├── services/               # cv_parser, ai_service, resume_processor,
│   │                           # template_service, pdf/docx/html generators
│   ├── templates/              # _base.html + 10 built-in templates
│   └── utils/                  # text_extractor, content_restructurer, exceptions
├── uploads/                    # Stored uploaded CVs
├── outputs/                    # Generated resume files
├── tests/
├── requirements.txt
└── pytest.ini
```

## Getting Started

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the development server (from Backend/)
uvicorn app.main:app --reload
```

- Interactive API docs (Swagger): http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Testing

```bash
pytest                       # run all tests
pytest -q                    # quiet output
pytest tests/test_parser.py  # parser unit tests only
```

## Configuration

Copy `.env.example` to `.env` and adjust:

| Variable | Purpose |
|----------|---------|
| `DEBUG` | Enable detailed SQL/API logging |
| `OPENAI_API_KEY` | Optional AI enhancement (empty = disabled) |
| `OPENAI_MODEL` | Model used for AI enhancement |
| `MAX_UPLOAD_SIZE_MB` | Max CV upload size |

## API Overview

### Upload
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload/cv` | Upload CV → returns parsed structured data |

### Resumes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/resume/list` | List resumes for the session |
| GET | `/api/resume/{id}` | Get a resume with parsed data |
| PUT | `/api/resume/{id}` | Edit parsed resume data |
| DELETE | `/api/resume/{id}` | Delete a resume |
| POST | `/api/resume/{id}/generate` | Generate resume (pdf/docx/html) |
| GET | `/api/resume/{id}/preview?template_id=` | HTML preview |
| GET | `/api/resume/{id}/download/{generated_id}` | Download a generated file |

### Templates
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/templates` | List built-in + custom templates |
| GET | `/api/templates/{id}` | Template details & config |
| POST | `/api/templates/custom` | Create custom template |
| PUT | `/api/templates/custom/{id}` | Update custom template |
| DELETE | `/api/templates/custom/{id}` | Delete custom template |

All endpoints are **session-scoped**: pass `X-Session-ID` header (e.g. `X-Session-ID: my-session`). Built-in templates are read-only and shared; custom templates are scoped to their owning session.

## Built-in Templates (10)

classic · modern · minimal · executive · technical · professional · academic · simple · elegant · ats_standard

Each defines its own Jinja2 HTML layout + `config.json` (section order, accent color, fonts). Custom templates are validated and rendered in a sandboxed Jinja environment.

## Security Notes

- Custom templates are rendered with `SandboxedEnvironment` and rejected if they attempt unsafe attribute access.
- Generated-file downloads confine reads to the `outputs/` directory.
- No secrets are stored in code; config is read from environment / `.env`.
