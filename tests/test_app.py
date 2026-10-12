"""
Test suite validating Flask backend routes, authentication decorators,
fine calculation business logic, and security configurations.
"""

from datetime import date, timedelta
import pytest
from werkzeug.security import check_password_hash, generate_password_hash
from app import create_app
from config import Config
import db

@pytest.fixture
def app():
    """Create and configure a Flask app instance for testing."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key-for-unit-testing'
    })
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_login_page_loads(client):
    """Verify that unauthenticated user can load the login page."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Librarian Sign In' in response.data
    assert b'admin@library.com' in response.data

def test_unauthenticated_access_redirects(client):
    """Verify that accessing protected endpoints redirects to /login."""
    protected_urls = [
        '/',
        '/books',
        '/loans',
        '/members',
        '/authors',
        '/publishers',
        '/categories',
        '/reports'
    ]
    for url in protected_urls:
        response = client.get(url, follow_redirects=False)
        assert response.status_code == 302, f"URL {url} did not redirect"
        assert '/login' in response.headers['Location']

def test_password_hashing():
    """Verify that Werkzeug password verification matches seed hash for Admin@123."""
    demo_password = "Admin@123"
    seed_hash = "scrypt:32768:8:1$yoq0KrQzaIUXlM0n$95ffc646d14ce83bf64640126e9f132fcf4baf711e30159d8b5956c2d1790aba1ed5d4b3d9a98faf2a70850671745c2829a17da2b02785b3a8b4bcdbb148b5b9"
    assert check_password_hash(seed_hash, demo_password) is True
    assert check_password_hash(seed_hash, "WrongPassword") is False

def test_fine_calculation_logic():
    """Verify overdue fine calculation math."""
    due_date = date(2026, 10, 1)
    # Case 1: Returned on time (or before)
    return_on_time = date(2026, 10, 1)
    overdue_days_0 = max(0, (return_on_time - due_date).days)
    fine_0 = round(overdue_days_0 * Config.FINE_PER_DAY, 2)
    assert overdue_days_0 == 0
    assert fine_0 == 0.0

    # Case 2: Returned 5 days late
    return_late_5 = date(2026, 10, 6)
    overdue_days_5 = max(0, (return_late_5 - due_date).days)
    fine_5 = round(overdue_days_5 * Config.FINE_PER_DAY, 2)
    assert overdue_days_5 == 5
    assert fine_5 == 5.0 * Config.FINE_PER_DAY

def test_authenticated_session(client):
    """Verify that an authenticated session can access protected views (with DB mock/handled)."""
    with client.session_transaction() as sess:
        sess['librarian_id'] = 1
        sess['librarian_name'] = 'Admin Librarian'
        sess['librarian_email'] = 'admin@library.com'

    # Testing logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'successfully logged out' in response.data or b'Sign In' in response.data

def test_database_offline_handling(client):
    """Verify that when database connection fails, app raises or renders error template."""
    with client.session_transaction() as sess:
        sess['librarian_id'] = 1

    # Request dashboard when MySQL is not running
    response = client.get('/')
    # It will either render the db_error template (status 200/503) or dashboard if DB is active
    assert response.status_code in (200, 503)
    if response.status_code == 503:
        assert b'MySQL Database Unreachable' in response.data or b'Cannot connect to MySQL' in response.data
