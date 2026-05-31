from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash

auth_bp = Blueprint('auth', __name__, template_folder='../templates')


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in to access the dashboard.', 'warning')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username == current_app.config['ADMIN_USERNAME'] and password == current_app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            flash('Login successful.', 'success')
            return redirect(url_for('dashboard.dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
