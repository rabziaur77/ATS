# ATS Backend - Development Plan

## Vision

An API where users upload existing CVs and select a preferred resume format/template. Based on the selected format, the application processes and restructures the CV while preserving the original content, ultimately generating a professionally formatted resume.

---

## Scope - V1

**Core Flow:**
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

**V1 does NOT include:** Job description analysis, keyword optimization, ATS scoring. These will be added as a separate feature in a later version.

---

## Tech Stack

| Component        | Technology                          |
|------------------|-------------------------------------|
| Framework        | FastAPI (Python)                    |
| Database         | SQLite + SQLAlchemy (portable later)|
| CV Parsing       | pdfplumber (PDF), python-docx (DOCX)|
| PDF Generation   | reportlab                           |
| DOCX Generation  | python-docx                         |
| HTML Generation  | Jinja2 templates                    |
| AI Service       | OpenAI API (optional enhancement)   |
| File Storage     | Local filesystem (`uploads/`, `outputs/`) |

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
│   │   ├── ai_service.py          # AI-powered content enhancement (optional)
│   │   ├── resume_processor.py    # Restructure parsed data for templates
│   │   ├── template_service.py    # Template resolution & management
│   │   ├── pdf_generator.py       # Generate PDF output
│   │   ├── docx_generator.py      # Generate DOCX output
│   │   └── html_generator.py      # Generate HTML output
│   │
│   ├── templates/                 # Jinja2 template files
│   │   ├── classic/
│   │   ├── modern/
│   │   ├── minimal/
│   │   ├── executive/
│   │   ├── technical/
│   │   ├── professional/
│   │   ├── academic/
│   │   ├── simple/
│   │   ├── elegant/
│   │   └── ats_standard/
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

## API Endpoints

### Upload
| Method | Endpoint           | Description                              |
|--------|--------------------|------------------------------------------|
| POST   | `/api/upload/cv`   | Upload CV, returns parsed structured data|

### Resume
| Method | Endpoint                                      | Description                        |
|--------|-----------------------------------------------|------------------------------------|
| GET    | `/api/resume/{id}`                            | Get parsed resume data             |
| PUT    | `/api/resume/{id}`                            | Update/edit parsed resume data     |
| POST   | `/api/resume/{id}/generate`                   | Generate resume from parsed data   |
| GET    | `/api/resume/{id}/download/{format}`          | Download as PDF/DOCX               |
| GET    | `/api/resume/{id}/preview`                    | Preview as HTML                    |
| GET    | `/api/resumes`                                | List all user resumes              |
| DELETE | `/api/resume/{id}`                            | Delete a resume                    |

### Templates
| Method | Endpoint                     | Description                       |
|--------|------------------------------|-----------------------------------|
| GET    | `/api/templates`             | List all available templates      |
| GET    | `/api/templates/{id}`        | Get template details & preview    |
| POST   | `/api/templates/custom`      | Create a custom user template     |
| PUT    | `/api/templates/custom/{id}` | Update custom template            |
| DELETE | `/api/templates/custom/{id}` | Delete custom template            |

---

## Database Schema

### resumes
| Column         | Type     | Description                        |
|----------------|----------|------------------------------------|
| id             | INTEGER  | Primary key                        |
| filename       | TEXT     | Original uploaded filename         |
| file_path      | TEXT     | Path to uploaded file              |
| file_type      | TEXT     | pdf / docx / txt                   |
| parsed_data    | JSON     | Extracted structured content       |
| created_at     | DATETIME | Upload timestamp                   |
| updated_at     | DATETIME | Last modification timestamp        |

### generated_resumes
| Column         | Type     | Description                        |
|----------------|----------|------------------------------------|
| id             | INTEGER  | Primary key                        |
| resume_id      | INTEGER  | FK → resumes.id                    |
| template_id    | TEXT     | Template used for generation       |
| format         | TEXT     | pdf / docx / html                  |
| file_path      | TEXT     | Path to generated file             |
| created_at     | DATETIME | Generation timestamp               |

### templates (custom only)
| Column         | Type     | Description                        |
|----------------|----------|------------------------------------|
| id             | INTEGER  | Primary key                        |
| name           | TEXT     | Template display name              |
| config         | JSON     | Layout configuration               |
| html_template  | TEXT     | Custom Jinja2 HTML template content|
| is_custom      | BOOLEAN  | true for user-created templates    |
| created_at     | DATETIME | Creation timestamp                 |

---

## Parsed Data Structure

When a CV is uploaded, the parser extracts structured content:

```json
{
  "personal_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-0123",
    "location": "New York, NY",
    "linkedin": "linkedin.com/in/johndoe",
    "website": ""
  },
  "summary": "Experienced software engineer with 5+ years...",
  "experience": [
    {
      "company": "Tech Corp",
      "title": "Senior Developer",
      "location": "New York, NY",
      "start_date": "2021-01",
      "end_date": "Present",
      "description": "Led team of 5 developers..."
    }
  ],
  "education": [
    {
      "institution": "MIT",
      "degree": "B.S. Computer Science",
      "start_date": "2015",
      "end_date": "2019",
      "gpa": "3.8"
    }
  ],
  "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
  "certifications": [],
  "languages": [],
  "projects": []
}
```

---

## Resume Templates (10 Built-in)

| #  | Template       | Style                                          |
|----|----------------|------------------------------------------------|
| 1  | classic        | Traditional reverse-chronological, serif fonts |
| 2  | modern         | Clean lines, sans-serif, colored accents       |
| 3  | minimal        | Whitespace-focused, minimal decoration         |
| 4  | executive      | Formal, sophisticated, for senior roles        |
| 5  | technical      | Skills-forward, project-centric layout         |
| 6  | professional   | Balanced, corporate-friendly                   |
| 7  | academic       | Research/publications focus, detailed          |
| 8  | simple         | Bare-bones, maximum ATS readability            |
| 9  | elegant        | Subtle typography, refined spacing             |
| 10 | ats_standard   | Optimized for ATS parsing, clean sections      |

Each template has:
- A Jinja2 HTML template (for HTML output + PDF rendering)
- A layout config JSON (section order, spacing, fonts, colors)
- A reportlab rendering config (for direct PDF generation)
- A python-docx config (for DOCX generation)

---

## Core Services

### cv_parser.py
- Accepts file (PDF/DOCX/TXT)
- Uses `pdfplumber` for PDF text extraction
- Uses `python-docx` for DOCX text extraction
- Plain Python for TXT
- Detects sections (Contact, Summary, Experience, Education, Skills, etc.)
- Returns structured JSON matching the parsed data schema

### ai_service.py (Optional Enhancement)
- Uses OpenAI API to improve parsing accuracy
- Can restructure messy CV content into clean sections
- Can enhance bullet points and descriptions
- Falls back to rule-based parsing if AI is unavailable

### resume_processor.py
- Takes parsed data + selected template config
- Reorders sections based on template layout
- Adjusts content density (e.g., executive = concise, academic = detailed)
- Formats dates, contact info, etc. per template style
- Returns template-ready data structure

### template_service.py
- Lists available built-in templates from filesystem
- Lists custom templates from database
- Resolves template config + HTML template
- Validates custom template uploads

### pdf_generator.py
- Takes template-ready data + template config
- Renders PDF using reportlab
- Applies fonts, colors, spacing per template
- Returns PDF file path

### docx_generator.py
- Takes template-ready data + template config
- Creates DOCX using python-docx
- Applies formatting (fonts, headings, bullet styles)
- Returns DOCX file path

### html_generator.py
- Takes template-ready data + Jinja2 HTML template
- Renders final HTML with data injected
- Returns HTML string (for preview or download)

---

## Implementation Order

### Phase 1: Foundation
1. Initialize FastAPI app (`main.py`)
2. Setup config and database (`config.py`, `database.py`)
3. Define models and schemas
4. Create basic file upload endpoint

### Phase 2: CV Parsing
5. Build `cv_parser.py` - PDF extraction
6. Build `cv_parser.py` - DOCX extraction
7. Build `cv_parser.py` - TXT extraction
8. Build `content_restructurer.py` - Section detection
9. Build `utils/text_extractor.py` - Low-level helpers

### Phase 3: Template System
10. Create 10 Jinja2 HTML templates
11. Create template layout configs
12. Build `template_service.py`
13. Build template API endpoints

### Phase 4: Resume Generation
14. Build `html_generator.py`
15. Build `pdf_generator.py`
16. Build `docx_generator.py`
17. Build `resume_processor.py`
18. Build resume generation & download endpoints

### Phase 5: Polish
19. Build `ai_service.py` (optional AI enhancement)
20. Add error handling & validation
21. Add API documentation (FastAPI auto-docs)
22. Write README.md

---

## Future Features (V2+)

- [ ] Job description analysis & keyword matching
- [ ] ATS score calculation
- [ ] Multiple resume versions per user
- [ ] User authentication & accounts
- [ ] Cloud storage (S3/GCS)
- [ ] Batch processing (multiple CVs)
- [ ] Resume comparison & diff view
