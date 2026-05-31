
import os
import re
import PyPDF2
from docx import Document

SKILL_KEYWORDS = [
    'python', 'java', 'sql', 'machine learning', 'deep learning', 'flask', 'react',
    'html', 'css', 'javascript', 'aws', 'github', 'docker', 'kubernetes', 'tensorflow',
    'pytorch', 'data science', 'nlp', 'azure', 'google cloud', 'rest api', 'sql server'
]

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'\+?\d[\d\s\-\(\)]{7,}\d')
NAME_LABEL_REGEX = re.compile(r'^(?:name|candidate name|applicant name)\s*[:\-]\s*(.+)$', re.I)
NAME_FALLBACK_REGEX = re.compile(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}$')


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file using PyPDF2."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages) if hasattr(reader, 'pages') else 0
            print(f"PDF reader opened, pages: {num_pages}")
            for i, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as pe:
                    print(f"Failed to extract text from page {i}:", pe)
    except Exception as e:
        print("PDF Read Error:", e)
    return text


def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file using python-docx."""
    text = ""
    try:
        doc = Document(docx_path)
        for para in doc.paragraphs:
            if para.text:
                text += para.text + "\n"
    except Exception as e:
        print("DOCX Read Error:", e)
    return text


def extract_text(path):
    """Dispatch to PDF or DOCX extractor based on file extension."""
    if not os.path.exists(path):
        print("File does not exist:", path)
        return ""

    ext = os.path.splitext(path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(path)
    elif ext == '.docx':
        return extract_text_from_docx(path)
    else:
        print("Unsupported file extension:", ext)
        return ""


def extract_email(text):
    if not text:
        return ''
    match = EMAIL_REGEX.search(text)
    return match.group(0).strip() if match else ''


def extract_phone(text):
    if not text:
        return ''
    match = PHONE_REGEX.search(text)
    if not match:
        return ''
    phone = re.sub(r'[^0-9+]', '', match.group(0))
    return phone


def extract_name(text):
    if not text:
        return ''

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:10]:
        label_match = NAME_LABEL_REGEX.match(line)
        if label_match:
            return label_match.group(1).strip()

    for line in lines[:20]:
        if '@' in line or 'http' in line or 'www' in line:
            continue
        if len(line.split()) in (2, 3) and NAME_FALLBACK_REGEX.match(line):
            return line.strip()

    return ''


def extract_skills(text, skill_list=None):
    if not text:
        return []
    if skill_list is None:
        skill_list = SKILL_KEYWORDS

    lower_text = text.lower()
    extracted = set()
    for skill in skill_list:
        pattern = re.compile(r'\b' + re.escape(skill.lower()) + r's?\b')
        if pattern.search(lower_text):
            extracted.add(skill)
    return sorted(extracted)

