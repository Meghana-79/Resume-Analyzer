import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resumes.db')


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        created_at TEXT
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER,
        filename TEXT,
        filepath TEXT,
        score REAL,
        recommendation TEXT,
        created_at TEXT,
        FOREIGN KEY(candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        skill_name TEXT,
        status TEXT,
        FOREIGN KEY(resume_id) REFERENCES resumes(id) ON DELETE CASCADE
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        action TEXT,
        created_at TEXT,
        FOREIGN KEY(resume_id) REFERENCES resumes(id) ON DELETE CASCADE
    )
    ''')

    # Migrate old schema if necessary
    cur.execute("PRAGMA table_info(resumes)")
    columns = [row['name'] for row in cur.fetchall()]
    has_candidate_id = 'candidate_id' in columns
    has_candidate_name = 'candidate_name' in columns

    if not has_candidate_id:
        cur.execute('ALTER TABLE resumes ADD COLUMN candidate_id INTEGER')
        has_candidate_id = True

    if 'filepath' not in columns:
        cur.execute('ALTER TABLE resumes ADD COLUMN filepath TEXT')
    if 'recommendation' not in columns:
        cur.execute('ALTER TABLE resumes ADD COLUMN recommendation TEXT')

    if has_candidate_name and has_candidate_id:
        cur.execute('SELECT id, candidate_name FROM resumes WHERE candidate_id IS NULL OR candidate_id = 0')
        rows = cur.fetchall()
        for resume_id, candidate_name in rows:
            if not candidate_name:
                continue
            cur.execute('SELECT id FROM candidates WHERE name = ?', (candidate_name,))
            candidate_row = cur.fetchone()
            if candidate_row:
                candidate_id = candidate_row['id']
            else:
                cur.execute('INSERT INTO candidates (name, email, phone, created_at) VALUES (?, ?, ?, ?)',
                            (candidate_name, '', '', datetime.utcnow().isoformat()))
                candidate_id = cur.lastrowid
            cur.execute('UPDATE resumes SET candidate_id = ? WHERE id = ?', (candidate_id, resume_id))

    conn.commit()
    conn.close()


def insert_or_get_candidate(name, email, phone):
    conn = connect_db()
    cur = conn.cursor()

    candidate_id = None
    if email:
        cur.execute('SELECT id FROM candidates WHERE email = ?', (email,))
        row = cur.fetchone()
        if row:
            candidate_id = row['id']

    if not candidate_id and name:
        cur.execute('SELECT id FROM candidates WHERE name = ?', (name,))
        row = cur.fetchone()
        if row:
            candidate_id = row['id']

    if candidate_id:
        conn.close()
        return candidate_id

    cur.execute('INSERT INTO candidates (name, email, phone, created_at) VALUES (?, ?, ?, ?)',
                (name, email, phone, datetime.utcnow().isoformat()))
    candidate_id = cur.lastrowid
    conn.commit()
    conn.close()
    return candidate_id


def insert_resume(candidate_id, filename, filepath, score, recommendation):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO resumes (candidate_id, filename, filepath, score, recommendation, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                (candidate_id, filename, filepath, score, recommendation, datetime.utcnow().isoformat()))
    resume_id = cur.lastrowid
    conn.commit()
    conn.close()
    return resume_id


def insert_skill(resume_id, skill_name, status):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO skills (resume_id, skill_name, status) VALUES (?, ?, ?)',
                (resume_id, skill_name, status))
    conn.commit()
    conn.close()


def log_history(resume_id, action):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO history (resume_id, action, created_at) VALUES (?, ?, ?)',
                (resume_id, action, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def get_resume_by_id(resume_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT r.id, COALESCE(c.name, r.candidate_name) AS name, c.email, c.phone, r.filename, r.filepath, r.score, r.recommendation, r.created_at'
                ' FROM resumes r LEFT JOIN candidates c ON r.candidate_id = c.id WHERE r.id = ?', (resume_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None

    cur.execute('SELECT skill_name, status FROM skills WHERE resume_id = ?', (resume_id,))
    skill_rows = cur.fetchall()
    conn.close()

    return {
        'id': row['id'],
        'candidate_name': row['name'],
        'email': row['email'],
        'phone': row['phone'],
        'filename': row['filename'],
        'filepath': row['filepath'],
        'score': row['score'],
        'recommendation': row['recommendation'],
        'created_at': row['created_at'],
        'skills': [s['skill_name'] for s in skill_rows if s['status'] == 'found'],
        'missing_skills': [s['skill_name'] for s in skill_rows if s['status'] == 'missing']
    }


def get_resumes(search='', min_score=0, skill=None):
    conn = connect_db()
    cur = conn.cursor()
    query = ('SELECT r.id, COALESCE(c.name, r.candidate_name) AS candidate_name, c.email, c.phone, r.filename, r.score, r.recommendation, r.created_at '
             'FROM resumes r LEFT JOIN candidates c ON r.candidate_id = c.id ')
    params = []
    conditions = []

    if search:
        conditions.append('(c.name LIKE ? OR c.email LIKE ? OR r.filename LIKE ? )')
        like_value = f'%{search}%'
        params.extend([like_value, like_value, like_value])
    if min_score:
        conditions.append('r.score >= ?')
        params.append(min_score)

    if conditions:
        query += 'WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY r.score DESC'

    cur.execute(query, tuple(params))
    rows = cur.fetchall()

    if not rows:
        conn.close()
        return []

    resume_ids = [row['id'] for row in rows]
    cur.execute('SELECT resume_id, skill_name, status FROM skills WHERE resume_id IN ({seq})'.format(seq=','.join(['?']*len(resume_ids))), tuple(resume_ids))
    skill_rows = cur.fetchall()
    conn.close()

    skills_by_resume = {}
    for skill_row in skill_rows:
        rid = skill_row['resume_id']
        skills_by_resume.setdefault(rid, []).append({'skill': skill_row['skill_name'], 'status': skill_row['status']})

    result = []
    for row in rows:
        found_skills = [s['skill'] for s in skills_by_resume.get(row['id'], []) if s['status'] == 'found']
        missing_skills = [s['skill'] for s in skills_by_resume.get(row['id'], []) if s['status'] == 'missing']
        if skill and skill not in found_skills:
            continue
        result.append({
            'id': row['id'],
            'candidate_name': row['candidate_name'],
            'email': row['email'],
            'phone': row['phone'],
            'filename': row['filename'],
            'score': row['score'],
            'recommendation': row['recommendation'],
            'created_at': row['created_at'],
            'skills': found_skills,
            'missing_skills': missing_skills
        })

    return result


def get_dashboard_stats():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute('SELECT COUNT(*) AS total_resumes, ROUND(AVG(score), 2) AS avg_score FROM resumes')
    row = cur.fetchone()
    total_resumes = row['total_resumes'] or 0
    avg_score = row['avg_score'] or 0.0

    cur.execute('SELECT COUNT(DISTINCT candidate_id) AS total_candidates FROM resumes')
    total_candidates = cur.fetchone()['total_candidates'] or 0

    cur.execute("SELECT skill_name, COUNT(*) AS count FROM skills WHERE status = 'found' GROUP BY skill_name ORDER BY count DESC LIMIT 8")
    top_skills = [{'skill': r['skill_name'], 'count': r['count']} for r in cur.fetchall()]

    cur.execute('SELECT COUNT(*) AS count FROM history')
    total_actions = cur.fetchone()['count'] or 0

    conn.close()
    return {
        'total_resumes': total_resumes,
        'avg_score': avg_score,
        'total_candidates': total_candidates,
        'top_skills': top_skills,
        'total_actions': total_actions
    }


def get_history(limit=50):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT h.id, h.action, h.created_at, r.id AS resume_id, COALESCE(c.name, r.candidate_name) AS candidate_name, r.filename, r.score
        FROM history h
        JOIN resumes r ON h.resume_id = r.id
        LEFT JOIN candidates c ON r.candidate_id = c.id
        ORDER BY h.created_at DESC
        LIMIT ?
    ''', (limit,))
    rows = cur.fetchall()
    conn.close()
    return [
        {
            'id': row['id'],
            'action': row['action'],
            'created_at': row['created_at'],
            'resume_id': row['resume_id'],
            'candidate_name': row['candidate_name'],
            'filename': row['filename'],
            'score': row['score']
        }
        for row in rows
    ]


def delete_resume(resume_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM resumes WHERE id = ?', (resume_id,))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return deleted
