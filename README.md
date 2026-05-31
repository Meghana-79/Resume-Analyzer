# AI Resume Analyzer

A professional, deployment-ready resume scoring and ranking application built with Python, Flask, NLP, TF-IDF, Cosine Similarity, and SQLite.

## Features

- Upload multiple resumes in PDF or DOCX formats
- Extract resume text and candidate details automatically
- Advanced skill extraction and missing skill detection
- Resume ranking with similarity score and candidate comparison
- Professional dashboard with stats, charts, filtering, and history
- SQLite database design with candidates, resumes, skills, and history
- CSV export and PDF report generation
- Responsive Bootstrap UI with dark mode support

## Folder Structure

```
ResumeAnalzer/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── Procfile
├── resumes/
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── history.html
│   ├── index.html
│   └── result.html
├── static/
│   └── style.css
└── utils/
    ├── __init__.py
    ├── db.py
    └── parser.py
```

## Quick Start

1. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python app.py
```

4. Open in browser:

```bash
http://127.0.0.1:5000
```

## Deployment

- Use Render, Railway, or PythonAnywhere with this repository.
- Ensure `requirements.txt` is installed.
- For Render or Railway, use `python app.py` or a Procfile with `web: gunicorn app:app`.
- Ensure the `resumes/` folder is writable.

## Key Concepts

### NLP
Natural Language Processing converts resume text and job descriptions into structured information used for matching, such as candidate details and technical skills.

### TF-IDF
Term Frequency-Inverse Document Frequency scores how important a word is in a document relative to the corpus. It is used to convert text into numeric vectors for similarity.

### Cosine Similarity
Cosine similarity measures the angle between two vectorized documents. A higher score means the resume and job description are more similar.

### Skill Extraction Logic
The project uses keyword matching against a curated technical skill list to identify candidate strengths and missing requirements.

### Flask Routing
Each URL route in `app.py` maps to a view function. For example, `/analyze` handles resume uploads and scoring, while `/` renders the dashboard.

### SQLite Integration
The app stores candidates, resume records, skills, and analysis history in a relational SQLite database for persistence and reporting.

## Debugging Tips

- Check the Flask console for debug output during upload and text extraction.
- Verify the `resumes/` directory exists and is writable.
- If a PDF has no extractable text, try converting it from a text-based version or use OCR.
- Use the `history` page to confirm resumes are recorded in the database.

## Professional Improvements

- Modern card layout, sidebar navigation, and responsive dashboard
- Filter and search candidates by name, skill, or score
- Export CSV and generate PDF candidate reports
- Clean database structure for interview-ready portfolio presentation

