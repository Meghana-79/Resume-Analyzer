from flask import Blueprint, render_template, request, redirect, url_for, current_app
from routes.auth import login_required
from utils import db as db_helper
import json

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')


@dashboard_bp.route('/')
@login_required
def dashboard():
    search = request.args.get('search', '').strip()
    min_score = request.args.get('min_score', '').strip()
    skill = request.args.get('skill', '').strip().lower()

    try:
        min_score_value = float(min_score) if min_score else 0.0
    except ValueError:
        min_score_value = 0.0

    resumes = db_helper.get_resumes(search=search, min_score=min_score_value, skill=skill or None)
    stats = db_helper.get_dashboard_stats()
    top_skill_labels = [item['skill'] for item in stats['top_skills']]
    top_skill_values = [item['count'] for item in stats['top_skills']]

    return render_template(
        'dashboard.html',
        resumes=resumes,
        stats=stats,
        search=search,
        min_score=min_score,
        skill=skill,
        skills=current_app.config.get('SKILL_KEYWORDS', []),
        top_skill_labels=json.dumps(top_skill_labels),
        top_skill_values=json.dumps(top_skill_values)
    )


@dashboard_bp.route('/history')
@login_required
def history():
    records = db_helper.get_history(100)
    return render_template('history.html', records=records)


@dashboard_bp.route('/resume/<int:resume_id>')
@login_required
def view_resume(resume_id):
    record = db_helper.get_resume_by_id(resume_id)
    if not record:
        return redirect(url_for('dashboard.dashboard'))
    return render_template('view_resume.html', record=record)
