"""
Flask Application Entry Point for Library Management System.
Configures app, registers blueprints, and implements the main dashboard.
"""

from datetime import date
from flask import Flask, render_template, redirect, url_for, session, flash, request
from config import Config
import db
from routes.auth import auth_bp, login_required
from routes.books import books_bp
from routes.authors import authors_bp
from routes.publishers import publishers_bp
from routes.categories import categories_bp
from routes.members import members_bp
from routes.loans import loans_bp
from routes.reports import reports_bp

def create_app():
    """Application factory initializing Flask app and registering routes."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register Route Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(authors_bp)
    app.register_blueprint(publishers_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(loans_bp)
    app.register_blueprint(reports_bp)

    @app.context_processor
    def inject_global_template_vars():
        """Makes librarian session info and system constants available to all Jinja templates."""
        overdue_badge = 0
        if 'librarian_id' in session:
            try:
                res = db.execute_query(
                    "SELECT COUNT(*) AS cnt FROM BOOK_LOAN WHERE Return_Date IS NULL AND Due_Date < CURRENT_DATE",
                    fetchone=True
                )
                if res:
                    overdue_badge = res.get('cnt', 0)
            except Exception:
                overdue_badge = 0

        return {
            'current_user_name': session.get('librarian_name'),
            'current_user_email': session.get('librarian_email'),
            'is_authenticated': 'librarian_id' in session,
            'system_today': date.today().isoformat(),
            'fine_per_day': Config.FINE_PER_DAY,
            'currency': Config.CURRENCY_SYMBOL,
            'overdue_badge_count': overdue_badge
        }

    @app.route('/')
    @login_required
    def dashboard():
        """Main administration dashboard featuring live SQL aggregations and charts."""
        try:
            # 1. Summary Statistics Aggregation
            stats_query = """
                SELECT 
                    (SELECT COUNT(*) FROM BOOK) AS total_titles,
                    (SELECT COALESCE(SUM(Total_Copies), 0) FROM BOOK) AS total_physical_copies,
                    (SELECT COALESCE(SUM(Available_Copies), 0) FROM BOOK) AS total_available_copies,
                    (SELECT COUNT(*) FROM MEMBER) AS total_members,
                    (SELECT COUNT(*) FROM MEMBER WHERE Status = 'Active') AS active_members,
                    (SELECT COUNT(*) FROM BOOK_LOAN WHERE Return_Date IS NULL) AS active_loans,
                    (SELECT COUNT(*) FROM BOOK_LOAN WHERE Return_Date IS NULL AND Due_Date < CURRENT_DATE) AS overdue_loans,
                    (SELECT COALESCE(SUM(Fine_Amount), 0.00) FROM BOOK_LOAN WHERE Return_Date IS NOT NULL) AS total_fines_collected,
                    (SELECT COALESCE(SUM(DATEDIFF(CURRENT_DATE, Due_Date) * %s), 0.00) 
                     FROM BOOK_LOAN 
                     WHERE Return_Date IS NULL AND Due_Date < CURRENT_DATE) AS total_pending_fines
            """
            stats = db.execute_query(stats_query, (Config.FINE_PER_DAY,), fetchone=True) or {}

            # 2. Category Distribution (for Chart.js)
            cat_query = """
                SELECT c.Category_Name, COUNT(b.Book_ID) AS book_count
                FROM CATEGORY c
                LEFT JOIN BOOK b ON c.Category_ID = b.Category_ID
                GROUP BY c.Category_ID, c.Category_Name
                HAVING book_count > 0
                ORDER BY book_count DESC
            """
            category_distribution = db.execute_query(cat_query)

            # 3. Overdue Loans Alert List
            overdue_query = """
                SELECT 
                    l.Loan_ID,
                    b.Title AS book_title,
                    m.Name AS member_name,
                    m.Phone AS member_phone,
                    l.Due_Date,
                    DATEDIFF(CURRENT_DATE, l.Due_Date) AS days_overdue,
                    ROUND(DATEDIFF(CURRENT_DATE, l.Due_Date) * %s, 2) AS calculated_fine
                FROM BOOK_LOAN l
                JOIN BOOK b ON l.Book_ID = b.Book_ID
                JOIN MEMBER m ON l.Member_ID = m.Member_ID
                WHERE l.Return_Date IS NULL AND l.Due_Date < CURRENT_DATE
                ORDER BY days_overdue DESC
                LIMIT 5
            """
            overdue_alerts = db.execute_query(overdue_query, (Config.FINE_PER_DAY,))

            # 4. Recently Issued Books
            recent_issued_query = """
                SELECT 
                    l.Loan_ID,
                    b.Title AS book_title,
                    m.Name AS member_name,
                    l.Issue_Date,
                    l.Due_Date
                FROM BOOK_LOAN l
                JOIN BOOK b ON l.Book_ID = b.Book_ID
                JOIN MEMBER m ON l.Member_ID = m.Member_ID
                ORDER BY l.Issue_Date DESC, l.Loan_ID DESC
                LIMIT 5
            """
            recent_issues = db.execute_query(recent_issued_query)

            # 5. Recently Returned Books
            recent_returned_query = """
                SELECT 
                    l.Loan_ID,
                    b.Title AS book_title,
                    m.Name AS member_name,
                    l.Return_Date,
                    l.Fine_Amount
                FROM BOOK_LOAN l
                JOIN BOOK b ON l.Book_ID = b.Book_ID
                JOIN MEMBER m ON l.Member_ID = m.Member_ID
                WHERE l.Return_Date IS NOT NULL
                ORDER BY l.Return_Date DESC, l.Loan_ID DESC
                LIMIT 5
            """
            recent_returns = db.execute_query(recent_returned_query)

            # 6. Top Most Borrowed Books
            most_borrowed_query = """
                SELECT 
                    b.Title AS book_title,
                    c.Category_Name AS category_name,
                    COUNT(l.Loan_ID) AS borrow_count
                FROM BOOK b
                JOIN CATEGORY c ON b.Category_ID = c.Category_ID
                JOIN BOOK_LOAN l ON b.Book_ID = l.Book_ID
                GROUP BY b.Book_ID, b.Title, c.Category_Name
                ORDER BY borrow_count DESC
                LIMIT 5
            """
            most_borrowed = db.execute_query(most_borrowed_query)

            return render_template(
                'dashboard.html',
                stats=stats,
                category_distribution=category_distribution,
                overdue_alerts=overdue_alerts,
                recent_issues=recent_issues,
                recent_returns=recent_returns,
                most_borrowed=most_borrowed
            )

        except RuntimeError as re:
            # Handles MySQL server offline / connection failure with informative screen
            return render_template('db_error.html', error_message=str(re), config=Config)

    @app.errorhandler(RuntimeError)
    def handle_database_runtime_error(err):
        """Catches unhandled database errors and presents a helpful setup guide."""
        return render_template('db_error.html', error_message=str(err), config=Config), 503

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', not_found=True), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', server_error=True), 500

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
