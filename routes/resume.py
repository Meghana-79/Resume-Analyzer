import csv
import io
import json
import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, current_app, send_file, flash
from werkzeug.utils import secure_filename
from utils.parser import (
    extract_text,
    extract_email,
    extract_phone,
    extract_name
)
from utils.analysis import (
    compute_score_breakdown,
    compute_recommendation,
    generate_feedback,
    check_ats_compatibility,
    extract_profiles,
    extract_skills
)
from utils import db as db_helper
from routes.auth import login_required
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

resume_bp = Blueprint('resume', __name__, template_folder='../templates')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_uploaded_file(file_storage):
    filename = secure_filename(file_storage.filename)
    if not filename or not allowed_file(filename):
        return None, None
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
    file_storage.save(path)
    return unique_name, path


@resume_bp.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    if request.method == 'GET':
        return render_template('index.html', skills=current_app.config.get('SKILL_KEYWORDS', []))

    job_description = request.form.get('job_description', '').strip()
    if not job_description:
        flash('Job description is required.', 'warning')
        return redirect(url_for('resume.analyze'))

    uploaded_files = request.files.getlist('resumes')
    if not uploaded_files:
        flash('Upload at least one PDF or DOCX resume.', 'warning')
        return redirect(url_for('resume.analyze'))

    results = []
    required_skills = extract_skills(job_description, current_app.config.get('SKILL_KEYWORDS', []))

    for uploaded_file in uploaded_files:
        if uploaded_file.filename == '':
            continue

        filename, filepath = save_uploaded_file(uploaded_file)
        if not filepath:
            flash(f'Invalid file type: {uploaded_file.filename}', 'danger')
            continue

        text = extract_text(filepath)
        if not text.strip():
            flash(f'Unable to read text from {uploaded_file.filename} - make sure it is a valid PDF or DOCX.', 'danger')
            continue

        candidate_name = extract_name(text) or 'Unknown Candidate'
        email = extract_email(text)
        phone = extract_phone(text)
        profile_links = extract_profiles(text)

        candidate_id = db_helper.insert_or_get_candidate(candidate_name, email, phone)
        corpus = [job_description, text]
        tfidf = TfidfVectorizer()
        try:
            matrix = tfidf.fit_transform(corpus)
            similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        except Exception as exc:
            flash('Unable to analyze resume due to text processing error.', 'danger')
            continue

        score = round(float(similarity) * 100, 2)
        found_skills_list = extract_skills(text, current_app.config.get('SKILL_KEYWORDS', []))
        missing_skills = [skill for skill in extract_skills(job_description, current_app.config.get('SKILL_KEYWORDS', [])) if skill not in found_skills_list]

        recommendation = compute_recommendation(score, missing_skills, found_skills_list)
        feedback = generate_feedback(missing_skills, score, found_skills_list)
        breakdown = compute_score_breakdown(text, [s for s in current_app.config.get('SKILL_KEYWORDS', []) if s in job_description.lower()])
        ats = check_ats_compatibility(text, filename, score)

        resume_id = db_helper.insert_resume(candidate_id, filename, filepath, score, recommendation)
        for skill in found_skills_list:
            db_helper.insert_skill(resume_id, skill, 'found')
        for skill in missing_skills:
            db_helper.insert_skill(resume_id, skill, 'missing')
        db_helper.log_history(resume_id, 'analyzed')

        results.append({
            'id': resume_id,
            'candidate_name': candidate_name,
            'email': email,
            'phone': phone,
            'linkedin': profile_links.get('linkedin', ''),
            'github': profile_links.get('github', ''),
            'filename': filename,
            'score': score,
            'recommendation': recommendation,
            'feedback': feedback,
            'found_skills': found_skills_list,
            'missing_skills': missing_skills,
            'breakdown': breakdown,
            'ats': ats
        })

    results = sorted(results, key=lambda item: item['score'], reverse=True)
    labels = [item['candidate_name'] for item in results]
    scores = [item['score'] for item in results]

    return render_template(
        'result.html',
        results=results,
        labels=json.dumps(labels),
        scores=json.dumps(scores)
    )


@resume_bp.route('/export/csv')
@login_required
def export_csv():
    resumes = db_helper.get_resumes()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Candidate', 'Email', 'Phone', 'Filename', 'Score', 'Recommendation', 'Skills', 'Missing Skills', 'Created At'])
    for item in resumes:
        writer.writerow([
            item['candidate_name'],
            item['email'],
            item['phone'],
            item['filename'],
            item['score'],
            item['recommendation'],
            ', '.join(item['skills']),
            ', '.join(item['missing_skills']),
            item['created_at']
        ])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        download_name='top_candidates.csv',
        as_attachment=True
    )


@resume_bp.route('/export/pdf/<int:resume_id>')
@login_required
def export_pdf(resume_id):
    record = db_helper.get_resume_by_id(resume_id)
    if not record:
        flash('Resume record not found.', 'warning')
        return redirect(url_for('dashboard.dashboard'))

    buffer = io.BytesIO()
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    doc = canvas.Canvas(buffer, pagesize=letter)
    doc.setTitle(f"Resume Analysis - {record['candidate_name']}")
    doc.setFont('Helvetica-Bold', 16)
    doc.drawString(40, 750, 'Resume Analysis Report')
    doc.setFont('Helvetica', 11)
    doc.drawString(40, 730, f"Candidate: {record['candidate_name']}")
    doc.drawString(40, 715, f"Email: {record['email'] or 'Not found'}")
    doc.drawString(40, 700, f"Phone: {record['phone'] or 'Not found'}")
    doc.drawString(40, 685, f"Filename: {record['filename']}")
    doc.drawString(40, 670, f"Score: {record['score']}%")
    doc.drawString(40, 655, f"Recommendation: {record['recommendation']}")
    doc.drawString(40, 640, 'Skills Found: ' + (', '.join(record['skills']) or 'None'))
    doc.drawString(40, 625, 'Missing Skills: ' + (', '.join(record['missing_skills']) or 'None'))
    doc.save()
    buffer.seek(0)
    return send_file(buffer, mimetype='application/pdf', download_name=f'{record["candidate_name"]}_analysis.pdf', as_attachment=True)


@resume_bp.route('/delete/<int:resume_id>', methods=['POST'])
@login_required
def delete_resume(resume_id):
    record = db_helper.get_resume_by_id(resume_id)
    if record and os.path.exists(record['filepath']):
        os.remove(record['filepath'])
    db_helper.delete_resume(resume_id)
    flash('Resume deleted successfully.', 'success')
    return redirect(url_for('dashboard.dashboard'))
