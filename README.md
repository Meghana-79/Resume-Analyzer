# AI Resume Analyzer

A professional, modular, deployment-ready resume scoring and ranking web application built with Python and Flask. It extracts text from PDF/DOCX resumes, identifies skills, computes similarity against job descriptions using TF-IDF + cosine similarity, ranks candidates, and provides an admin dashboard for analytics and exports.

**Key features**
- Upload multiple resumes (PDF, DOCX) and analyze them against a job description
- Skill extraction and missing-skill detection from a curated keyword list
- TF-IDF + cosine-similarity resume-to-JD ranking with per-candidate score breakdown
- Dashboard with statistics, top-skill chart, filtering, and history
- Persisted data in SQLite (candidates, resumes, skills, history)
- CSV export and PDF report generation per candidate
- Modular codebase with Blueprints, config, and utility modules for easy extension

## Project layout

```
ResumeAnalzer/
├── app.py                  # Application factory and blueprint registration
├── config.py               # App configuration and skill keywords
├── requirements.txt
├── README.md
├── Procfile
├── resumes/                # Uploaded resume files (writable)
├── templates/              # Jinja2 templates (base, dashboard, index, result, login, view_resume)
├── static/                 # CSS and static assets
├── routes/                 # Flask Blueprints: auth.py, dashboard.py, resume.py
└── utils/                  # Helpers: db.py, parser.py, analysis.py
```

## Setup (local)

1. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # macOS / Linux
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Environment variables (recommended):

- `SECRET_KEY` — Flask secret key (overrides `config.Config.SECRET_KEY`)
- `ADMIN_USERNAME` — admin login username (default: `admin`)
- `ADMIN_PASSWORD` — admin login password (default: `password`)

You can set them in your shell or in a `.env` file (used by your deployment platform).

4. Run the application:

```bash
python app.py
```

Open http://127.0.0.1:5000 and sign in using the admin credentials (default username/password: `admin`/`password`). Change defaults before deploying.

## Routes / Usage

- `GET /login` — Admin login page
- `GET /` — Dashboard (requires login)
- `GET /analyze`, `POST /analyze` — Upload resumes and analyze against a job description
- `GET /history` — Analysis history
- `GET /export/csv` — Export all resumes as CSV (blueprint: `resume.export_csv`)
- `GET /export/pdf/<resume_id>` — Download PDF report for a resume (blueprint: `resume.export_pdf`)

Note: templates and URL endpoints use blueprint-qualified names (for example, `resume.export_pdf`).

## Database

- The app uses SQLite. Database file is created automatically as `resumes.db` in the project root when the app starts.
- Tables: `candidates`, `resumes`, `skills`, `history`.
- `utils/db.py` contains helper functions and lightweight migration logic to handle older resume schemas.

## Developer notes

- Modular structure: the app uses an application factory (`create_app` in `app.py`) and registers Blueprints from `routes/` for separation of concerns.
- `utils/parser.py` handles PDF/DOCX text extraction and basic contact/skill parsing.
- `utils/analysis.py` provides score breakdown, feedback, ATS checks, and profile extraction helpers.

## Deployment

- For production, run behind a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn "app:app" --bind 0.0.0.0:8000
```

- Add a `Procfile` for platforms like Heroku/Render:

```
web: gunicorn "app:app"
```

- Ensure `resumes/` is writable and `SECRET_KEY` + admin creds are set as environment variables.

## Testing the flow (quick)

1. Start the server: `python app.py`
2. Visit `/login` and authenticate using admin creds
3. Go to `Analyze Resumes` and upload 1-3 PDF/DOCX resumes with a job description
4. Review results, export CSV/PDF, and confirm entries appear on the Dashboard and History pages

## Troubleshooting

- If a PDF has no text, it's likely image-based. Convert it to a text-based PDF or use OCR before uploading.
- Check the server console for parsing errors (PDF/DOCX read messages are logged during analysis).
- If you see database schema issues, delete or back up `resumes.db` and restart — the app contains migration logic but a clean DB is simplest for local development.

## Security & next steps

- Replace the default admin credentials and `SECRET_KEY` for production.
- Consider adding HTTPS, session timeout, CSRF protection, and rate limits for file uploads.
- Add automated tests for upload → analyze → export flows and CI that runs `python -m py_compile` on commit.

If you want, I can add a `sample_resumes/` folder and an automated integration test that uploads one sample resume and validates the analysis flow.

