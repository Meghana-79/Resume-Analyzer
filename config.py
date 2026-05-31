import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'replace-with-a-secure-key')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resumes')
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'password')
    SKILL_KEYWORDS = [
        'Python', 'Java', 'SQL', 'Machine Learning', 'Deep Learning', 'Flask',
        'React', 'HTML', 'CSS', 'JavaScript', 'AWS', 'GitHub', 'Docker',
        'Kubernetes', 'TensorFlow', 'PyTorch', 'NLP', 'Azure', 'Google Cloud',
        'REST API', 'Data Science'
    ]
