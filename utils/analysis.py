import re
from utils.parser import extract_skills

SECTION_KEYWORDS = {
    'experience': ['experience', 'work history', 'professional experience', 'employment'],
    'education': ['education', 'qualifications', 'academic background', 'degrees'],
    'projects': ['project', 'projects', 'capstone', 'portfolio'],
    'skills': ['skills', 'technical skills', 'expertise', 'tools']
}

LABEL_KEYWORDS = {
    'linkedin': ['linkedin.com/in/', 'linkedin.com/pub/'],
    'github': ['github.com/']
}


def compute_score_breakdown(text, required_skills):
    """Compute a simple breakdown of skill, experience, education, and project scores."""
    lower = text.lower()
    skill_score = 0
    experience_score = 0
    education_score = 0
    project_score = 0

    for skill in required_skills:
        if skill.lower() in lower:
            skill_score += 1

    skill_score = min(100, round((skill_score / max(len(required_skills), 1)) * 100, 2))

    for keyword in SECTION_KEYWORDS['experience']:
        if keyword in lower:
            experience_score += 33
    experience_score = min(100, experience_score)

    for keyword in SECTION_KEYWORDS['education']:
        if keyword in lower:
            education_score += 50
    education_score = min(100, education_score)

    for keyword in SECTION_KEYWORDS['projects']:
        if keyword in lower:
            project_score += 50
    project_score = min(100, project_score)

    return {
        'skill_score': skill_score,
        'experience_score': experience_score,
        'education_score': education_score,
        'project_score': project_score
    }


def compute_recommendation(score, matched_skills, missing_skills):
    """Generate a recommendation based on score and skill coverage."""
    if score >= 85 and len(missing_skills) == 0:
        return 'Highly Recommended'
    if score >= 75:
        return 'Recommended'
    if score >= 60:
        return 'Needs Improvement'
    return 'Not Suitable'


def generate_feedback(missing_skills, score, found_skills):
    """Generate improvement suggestions for the candidate."""
    suggestions = []
    if missing_skills:
        suggestions.append(f"Add experience or projects using: {', '.join(missing_skills)}")
    if score < 70:
        suggestions.append('Improve resume keywords and include more measurable achievements.')
    if 'github' not in found_skills and 'github' not in missing_skills:
        suggestions.append('Add your GitHub profile and sample projects.')
    if not suggestions:
        suggestions.append('Resume looks strong. Keep showcasing relevant project experience.')
    return suggestions


def check_ats_compatibility(text, filename, score):
    """Heuristic ATS compatibility check based on formatting and keyword usage."""
    results = {
        'has_sections': False,
        'has_contact': False,
        'is_text_based': True,
        'keyword_optimized': False,
        'recommendation': ''
    }

    lower = text.lower() if text else ''
    if any(keyword in lower for keyword in SECTION_KEYWORDS['experience']):
        results['has_sections'] = True
    if 'linkedin.com/' in lower or 'github.com/' in lower or '@' in lower or 'phone' in lower:
        results['has_contact'] = True
    if len(text) < 150:
        results['is_text_based'] = False
    results['keyword_optimized'] = 'skills' in lower or 'experience' in lower

    recommendations = []
    if not results['has_sections']:
        recommendations.append('Add clear section headings like Experience, Education, and Projects.')
    if not results['has_contact']:
        recommendations.append('Include a contact section with email and phone number.')
    if not results['keyword_optimized']:
        recommendations.append('Use role-specific keywords and skills to improve ATS match.')
    if not results['is_text_based']:
        recommendations.append('Use a text-based resume format instead of an image-based file.')

    results['recommendation'] = ' '.join(recommendations)
    return results


def extract_profiles(text):
    """Extract LinkedIn and GitHub URLs from resume text."""
    profiles = {'linkedin': '', 'github': ''}
    if not text:
        return profiles

    lower = text.lower()
    linkedin_match = re.search(r'(https?://(www\.)?linkedin\.com/in/[\w\-_/]+)', text, re.I)
    github_match = re.search(r'(https?://(www\.)?github\.com/[\w\-_/]+)', text, re.I)
    if linkedin_match:
        profiles['linkedin'] = linkedin_match.group(1)
    if github_match:
        profiles['github'] = github_match.group(1)
    return profiles
