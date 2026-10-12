"""
Reports and SQL Syllabus Query Execution Blueprint.
Executes the syllabus analytical queries and presents results in print-friendly tables.
"""

from flask import Blueprint, render_template, request
from routes.auth import login_required
from db import execute_query
from config import Config

reports_bp = Blueprint('reports', __name__)

REPORTS_REGISTRY = {
    'all_books': {
        'title': 'All Books in Catalog',
        'description': 'Full inventory of cataloged titles with publisher, category, and pricing details.',
        'syllabus_concept': 'INNER JOIN, SELECT with ORDER BY',
        'sql': """
            SELECT 
                b.Book_ID,
                b.ISBN,
                b.Title,
                p.Name AS Publisher,
                c.Category_Name AS Category,
                b.Price,
                b.Available_Copies,
                b.Total_Copies,
                b.Publication_Year
            FROM BOOK b
            INNER JOIN PUBLISHER p ON b.Publisher_ID = p.Publisher_ID
            INNER JOIN CATEGORY c ON b.Category_ID = c.Category_ID
            ORDER BY b.Title ASC
        """
    },
    'available_books': {
        'title': 'Currently Available Books',
        'description': 'Titles currently in stock and ready to be issued to library members.',
        'syllabus_concept': 'Comparison Operator (>), WHERE Clause',
        'sql': """
            SELECT 
                b.Book_ID,
                b.ISBN,
                b.Title,
                c.Category_Name AS Category,
                b.Available_Copies,
                b.Total_Copies,
                b.Price
            FROM BOOK b
            JOIN CATEGORY c ON b.Category_ID = c.Category_ID
            WHERE b.Available_Copies > 0
            ORDER BY b.Available_Copies DESC, b.Title ASC
        """
    },
    'issued_books': {
        'title': 'Currently Issued (Active) Books',
        'description': 'Books currently checked out by members with due dates and issuing librarian.',
        'syllabus_concept': 'IS NULL Condition, Multi-table INNER & LEFT JOIN',
        'sql': """
            SELECT 
                l.Loan_ID,
                b.Title AS Book_Title,
                b.ISBN,
                m.Name AS Member_Name,
                m.Email AS Member_Email,
                l.Issue_Date,
                l.Due_Date,
                lib.Name AS Issued_By
            FROM BOOK_LOAN l
            INNER JOIN BOOK b ON l.Book_ID = b.Book_ID
            INNER JOIN MEMBER m ON l.Member_ID = m.Member_ID
            LEFT JOIN LIBRARIAN lib ON l.Issued_By = lib.Librarian_ID
            WHERE l.Return_Date IS NULL
            ORDER BY l.Due_Date ASC
        """
    },
    'overdue_books': {
        'title': 'Overdue Loans & Fine Calculation',
        'description': 'Loans where the due date has passed without return, showing computed penalty fines.',
        'syllabus_concept': 'DATEDIFF, Arithmetic Expressions, WHERE with CURRENT_DATE',
        'sql': """
            SELECT 
                l.Loan_ID,
                b.Title AS Book_Title,
                m.Name AS Member_Name,
                m.Phone,
                m.Email,
                l.Issue_Date,
                l.Due_Date,
                DATEDIFF(CURRENT_DATE, l.Due_Date) AS Days_Overdue,
                ROUND(DATEDIFF(CURRENT_DATE, l.Due_Date) * 5.00, 2) AS Calculated_Fine_INR
            FROM BOOK_LOAN l
            JOIN BOOK b ON l.Book_ID = b.Book_ID
            JOIN MEMBER m ON l.Member_ID = m.Member_ID
            WHERE l.Return_Date IS NULL 
              AND l.Due_Date < CURRENT_DATE
            ORDER BY Days_Overdue DESC
        """
    },
    'members_status': {
        'title': 'Active vs. Inactive Members Overview',
        'description': 'Summary of all registered members categorized by their status with borrowing activity.',
        'syllabus_concept': 'GROUP BY, Aggregate COUNT, CASE Expression',
        'sql': """
            SELECT 
                m.Status,
                COUNT(m.Member_ID) AS Total_Members,
                SUM(CASE WHEN l.Loan_ID IS NOT NULL THEN 1 ELSE 0 END) AS Total_Loans_History
            FROM MEMBER m
            LEFT JOIN BOOK_LOAN l ON m.Member_ID = l.Member_ID
            GROUP BY m.Status
        """
    },
    'most_borrowed': {
        'title': 'Most Borrowed Books',
        'description': 'Ranking of most frequently loaned books in library history.',
        'syllabus_concept': 'Aggregate COUNT, GROUP BY, ORDER BY DESC, LIMIT',
        'sql': """
            SELECT 
                b.Book_ID,
                b.Title,
                b.ISBN,
                c.Category_Name AS Category,
                COUNT(l.Loan_ID) AS Times_Borrowed
            FROM BOOK b
            JOIN CATEGORY c ON b.Category_ID = c.Category_ID
            LEFT JOIN BOOK_LOAN l ON b.Book_ID = l.Book_ID
            GROUP BY b.Book_ID, b.Title, b.ISBN, c.Category_Name
            ORDER BY Times_Borrowed DESC, b.Title ASC
            LIMIT 10
        """
    },
    'least_borrowed': {
        'title': 'Least Borrowed Books',
        'description': 'Books borrowed at most 1 time, indicating low-circulating titles.',
        'syllabus_concept': 'GROUP BY with HAVING Clause, Aggregate COUNT',
        'sql': """
            SELECT 
                b.Book_ID,
                b.Title,
                b.ISBN,
                c.Category_Name AS Category,
                COUNT(l.Loan_ID) AS Times_Borrowed,
                b.Available_Copies
            FROM BOOK b
            JOIN CATEGORY c ON b.Category_ID = c.Category_ID
            LEFT JOIN BOOK_LOAN l ON b.Book_ID = l.Book_ID
            GROUP BY b.Book_ID, b.Title, b.ISBN, c.Category_Name, b.Available_Copies
            HAVING COUNT(l.Loan_ID) <= 1
            ORDER BY Times_Borrowed ASC, b.Title ASC
        """
    },
    'category_stats': {
        'title': 'Category-wise Catalog & Circulation Statistics',
        'description': 'Book count, total copies, loan volume, and collected fines grouped by category.',
        'syllabus_concept': 'Multiple Aggregate Functions (COUNT, SUM, COALESCE), GROUP BY',
        'sql': """
            SELECT 
                c.Category_ID,
                c.Category_Name,
                COUNT(DISTINCT b.Book_ID) AS Titles_Count,
                COALESCE(SUM(b.Total_Copies), 0) AS Total_Physical_Copies,
                COUNT(l.Loan_ID) AS Total_Loans_Count,
                COALESCE(SUM(l.Fine_Amount), 0.00) AS Total_Fines_Collected
            FROM CATEGORY c
            LEFT JOIN BOOK b ON c.Category_ID = b.Category_ID
            LEFT JOIN BOOK_LOAN l ON b.Book_ID = l.Book_ID
            GROUP BY c.Category_ID, c.Category_Name
            ORDER BY Titles_Count DESC
        """
    },
    'author_stats': {
        'title': 'Author-wise Borrowing Statistics',
        'description': 'Total books authored and total loans generated across each author.',
        'syllabus_concept': '3-Table LEFT JOIN, Multi-level Aggregation',
        'sql': """
            SELECT 
                a.Author_ID,
                a.Name AS Author_Name,
                a.Country,
                COUNT(DISTINCT ba.Book_ID) AS Books_Authored,
                COUNT(bl.Loan_ID) AS Total_Times_Borrowed
            FROM AUTHOR a
            LEFT JOIN BOOK_AUTHOR ba ON a.Author_ID = ba.Author_ID
            LEFT JOIN BOOK_LOAN bl ON ba.Book_ID = bl.Book_ID
            GROUP BY a.Author_ID, a.Name, a.Country
            ORDER BY Total_Times_Borrowed DESC, Books_Authored DESC
        """
    },
    'fines_summary': {
        'title': 'Fine Collection & Outstanding Summary',
        'description': 'Breakdown of fines collected from completed returns versus outstanding uncollected fines.',
        'syllabus_concept': 'Scalar Aggregate Subqueries, COALESCE',
        'sql': """
            SELECT 
                (SELECT COALESCE(SUM(Fine_Amount), 0.00) FROM BOOK_LOAN WHERE Return_Date IS NOT NULL) AS Total_Recorded_Fines_Collected,
                (SELECT COALESCE(SUM(DATEDIFF(CURRENT_DATE, Due_Date) * 1.00), 0.00) 
                 FROM BOOK_LOAN 
                 WHERE Return_Date IS NULL AND Due_Date < CURRENT_DATE) AS Total_Pending_Uncollected_Fines,
                (SELECT COUNT(*) FROM BOOK_LOAN WHERE Return_Date IS NULL AND Due_Date < CURRENT_DATE) AS Active_Overdue_Loans_Count
        """
    },
    'never_borrowed_books': {
        'title': 'Books Never Borrowed',
        'description': 'Cataloged titles that have never had a loan transaction recorded.',
        'syllabus_concept': 'Correlated Subquery with NOT EXISTS',
        'sql': """
            SELECT 
                b.Book_ID,
                b.ISBN,
                b.Title,
                p.Name AS Publisher,
                c.Category_Name AS Category,
                b.Total_Copies,
                b.Available_Copies
            FROM BOOK b
            JOIN PUBLISHER p ON b.Publisher_ID = p.Publisher_ID
            JOIN CATEGORY c ON b.Category_ID = c.Category_ID
            WHERE NOT EXISTS (
                SELECT 1 
                FROM BOOK_LOAN l 
                WHERE l.Book_ID = b.Book_ID
            )
            ORDER BY b.Title ASC
        """
    },
    'members_never_borrowed': {
        'title': 'Members Who Never Borrowed Any Book',
        'description': 'Registered members who have zero circulation history in the system.',
        'syllabus_concept': 'Correlated Subquery with NOT EXISTS',
        'sql': """
            SELECT 
                m.Member_ID,
                m.Name,
                m.Email,
                m.Phone,
                m.Join_Date,
                m.Status
            FROM MEMBER m
            WHERE NOT EXISTS (
                SELECT 1 
                FROM BOOK_LOAN l 
                WHERE l.Member_ID = m.Member_ID
            )
            ORDER BY m.Join_Date DESC
        """
    },
    'above_category_avg': {
        'title': 'Books Priced Above Their Own Category Average',
        'description': 'Books whose price exceeds the average price of all books in that same category.',
        'syllabus_concept': 'Correlated Subquery with Category Matching',
        'sql': """
            SELECT 
                b1.Book_ID,
                b1.Title,
                c.Category_Name,
                b1.Price,
                ROUND((SELECT AVG(b2.Price) FROM BOOK b2 WHERE b2.Category_ID = b1.Category_ID), 2) AS Category_Avg_Price
            FROM BOOK b1
            JOIN CATEGORY c ON b1.Category_ID = c.Category_ID
            WHERE b1.Price > (
                SELECT AVG(b2.Price) 
                FROM BOOK b2 
                WHERE b2.Category_ID = b1.Category_ID
            )
            ORDER BY c.Category_Name, b1.Price DESC
        """
    }
}

@reports_bp.route('/reports')
@login_required
def index():
    """Renders the selected analytical report and displays the executed SQL."""
    report_key = request.args.get('report', 'all_books')
    if report_key not in REPORTS_REGISTRY:
        report_key = 'all_books'

    active_report = REPORTS_REGISTRY[report_key]
    data = []
    columns = []

    try:
        data = execute_query(active_report['sql'])
        if data and len(data) > 0:
            columns = list(data[0].keys())
    except Exception as e:
        data = []
        error_msg = str(e)
        return render_template(
            'reports.html',
            registry=REPORTS_REGISTRY,
            active_key=report_key,
            active_report=active_report,
            data=[],
            columns=[],
            error=error_msg
        )

    return render_template(
        'reports.html',
        registry=REPORTS_REGISTRY,
        active_key=report_key,
        active_report=active_report,
        data=data,
        columns=columns
    )
