"""
Authentication Blueprint for Librarian Login / Logout.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from db import execute_query

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    """Decorator ensuring that only authenticated librarians can access the route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'librarian_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles librarian authentication."""
    if 'librarian_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Both email and password are required.', 'danger')
            return render_template('login.html', email=email)

        try:
            # Parameterized query to fetch librarian by email
            query = "SELECT Librarian_ID, Name, Email, Password_Hash FROM LIBRARIAN WHERE Email = %s"
            librarian = execute_query(query, (email,), fetchone=True)

            if librarian and check_password_hash(librarian['Password_Hash'], password):
                # Setup session
                session.clear()
                session['librarian_id'] = librarian['Librarian_ID']
                session['librarian_name'] = librarian['Name']
                session['librarian_email'] = librarian['Email']
                flash(f'Welcome back, {librarian["Name"]}!', 'success')
                
                next_url = request.args.get('next')
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password. Please try again.', 'danger')
        except RuntimeError as e:
            flash(f'Database error: {str(e)}', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Clears the session and logs out the librarian."""
    session.clear()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('auth.login'))
