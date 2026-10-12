"""
Book Loan Blueprint.
Implements ACID-compliant Issue and Return transactions with concurrency control,
row locking, fine calculation, and stock consistency guarantees.
"""

from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import login_required
from db import execute_query, transaction
from config import Config

loans_bp = Blueprint('loans', __name__)

@loans_bp.route('/loans')
@login_required
def index():
    """Lists current active loans, overdue loans, and loan history."""
    status_tab = request.args.get('tab', 'active')
    search_query = request.args.get('q', '').strip()

    sql = """
        SELECT 
            l.Loan_ID,
            l.Book_ID,
            b.Title AS Book_Title,
            b.ISBN,
            l.Member_ID,
            m.Name AS Member_Name,
            m.Email AS Member_Email,
            m.Phone AS Member_Phone,
            m.Status AS Member_Status,
            lib.Name AS Librarian_Name,
            l.Issue_Date,
            l.Due_Date,
            l.Return_Date,
            l.Fine_Amount,
            CASE 
                WHEN l.Return_Date IS NULL AND l.Due_Date < CURRENT_DATE 
                THEN DATEDIFF(CURRENT_DATE, l.Due_Date) 
                WHEN l.Return_Date IS NOT NULL AND l.Return_Date > l.Due_Date 
                THEN DATEDIFF(l.Return_Date, l.Due_Date)
                ELSE 0 
            END AS Overdue_Days,
            CASE 
                WHEN l.Return_Date IS NULL AND l.Due_Date < CURRENT_DATE 
                THEN ROUND(DATEDIFF(CURRENT_DATE, l.Due_Date) * %s, 2)
                ELSE 0.00 
            END AS Pending_Fine
        FROM BOOK_LOAN l
        JOIN BOOK b ON l.Book_ID = b.Book_ID
        JOIN MEMBER m ON l.Member_ID = m.Member_ID
        LEFT JOIN LIBRARIAN lib ON l.Issued_By = lib.Librarian_ID
        WHERE 1=1
    """
    params = [Config.FINE_PER_DAY]

    if search_query:
        sql += " AND (b.Title LIKE %s OR b.ISBN LIKE %s OR m.Name LIKE %s OR m.Email LIKE %s)"
        like_term = f"%{search_query}%"
        params.extend([like_term, like_term, like_term, like_term])

    if status_tab == 'active':
        sql += " AND l.Return_Date IS NULL"
    elif status_tab == 'overdue':
        sql += " AND l.Return_Date IS NULL AND l.Due_Date < CURRENT_DATE"
    elif status_tab == 'returned':
        sql += " AND l.Return_Date IS NOT NULL"

    sql += " ORDER BY l.Issue_Date DESC"

    loans = execute_query(sql, params)

    # For issue book form: available books and active members
    available_books = execute_query(
        """
        SELECT b.Book_ID, b.Title, b.ISBN, b.Price, b.Available_Copies, b.Total_Copies, c.Category_Name 
        FROM BOOK b 
        LEFT JOIN CATEGORY c ON b.Category_ID = c.Category_ID 
        WHERE b.Available_Copies > 0 
        ORDER BY b.Title
        """
    )
    active_members = execute_query(
        "SELECT Member_ID, Name, Email FROM MEMBER WHERE Status = 'Active' ORDER BY Name"
    )

    default_issue_date = date.today().isoformat()
    default_due_date = (date.today() + timedelta(days=Config.DEFAULT_LOAN_DAYS)).isoformat()

    return render_template(
        'loans.html',
        loans=loans,
        status_tab=status_tab,
        search_query=search_query,
        available_books=available_books,
        active_members=active_members,
        default_issue_date=default_issue_date,
        default_due_date=default_due_date,
        fine_rate=Config.FINE_PER_DAY,
        today=date.today().isoformat()
    )

@loans_bp.route('/loans/issue', methods=['POST'])
@login_required
def issue_book():
    """
    Executes ACID transaction to issue a book:
    1. Validates input
    2. Checks member status == 'Active'
    3. Atomically decrements Available_Copies only if Available_Copies > 0
    4. Confirms exactly 1 row updated
    5. Inserts loan record
    6. Commits or rolls back
    """
    member_id = request.form.get('member_id')
    book_id = request.form.get('book_id')
    issue_date_str = request.form.get('issue_date', '').strip() or date.today().isoformat()
    due_date_str = request.form.get('due_date', '').strip()
    librarian_id = session.get('librarian_id')

    if not member_id or not book_id or not due_date_str:
        flash('Member, book, and due date are required.', 'danger')
        return redirect(url_for('loans.index', tab='issue'))

    try:
        issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()

        if due_date < issue_date:
            flash('Due date cannot be earlier than issue date.', 'danger')
            return redirect(url_for('loans.index', tab='issue'))

        with transaction() as (cursor, conn):
            # 1. Validate member is Active
            cursor.execute("SELECT Member_ID, Name, Status FROM MEMBER WHERE Member_ID = %s FOR UPDATE", (member_id,))
            member = cursor.fetchone()
            if not member:
                raise ValueError("Member not found.")
            if member['Status'] != 'Active':
                raise ValueError(f"Member '{member['Name']}' is Inactive and cannot be issued books.")

            # 2. Atomically decrement available stock if available copies > 0
            cursor.execute(
                "UPDATE BOOK SET Available_Copies = Available_Copies - 1 WHERE Book_ID = %s AND Available_Copies > 0",
                (book_id,)
            )
            if cursor.rowcount == 0:
                raise ValueError("The requested book is currently out of stock (0 copies available).")

            # 3. Insert Loan record
            insert_loan_sql = """
                INSERT INTO BOOK_LOAN (Book_ID, Member_ID, Issued_By, Issue_Date, Due_Date, Return_Date, Fine_Amount)
                VALUES (%s, %s, %s, %s, %s, NULL, 0.00)
            """
            cursor.execute(insert_loan_sql, (book_id, member_id, librarian_id, issue_date, due_date))

        flash(f"Book successfully issued to {member['Name']}.", 'success')
        return redirect(url_for('loans.index', tab='active'))

    except ValueError as ve:
        flash(str(ve), 'danger')
        return redirect(url_for('loans.index', tab='issue'))
    except Exception as e:
        flash(f"Transaction failed: {str(e)}", 'danger')
        return redirect(url_for('loans.index', tab='issue'))

@loans_bp.route('/loans/return/<int:loan_id>', methods=['POST'])
@login_required
def return_book(loan_id):
    """
    Executes ACID transaction to return a book:
    1. Locks loan row using SELECT ... FOR UPDATE
    2. Validates Return_Date IS NULL (prevents duplicate returns)
    3. Calculates overdue days & fine
    4. Sets Return_Date and Fine_Amount
    5. Increments Available_Copies in BOOK
    6. Commits or rolls back
    """
    return_date_str = request.form.get('return_date', '').strip() or date.today().isoformat()
    record_fine_input = request.form.get('fine_amount') # Optional override/waive

    try:
        return_date = datetime.strptime(return_date_str, '%Y-%m-%d').date()

        with transaction() as (cursor, conn):
            # 1. Row-lock loan record to prevent concurrent return race conditions
            cursor.execute("""
                SELECT l.Loan_ID, l.Book_ID, l.Member_ID, l.Due_Date, l.Return_Date, b.Title, m.Name AS Member_Name
                FROM BOOK_LOAN l
                JOIN BOOK b ON l.Book_ID = b.Book_ID
                JOIN MEMBER m ON l.Member_ID = m.Member_ID
                WHERE l.Loan_ID = %s 
                FOR UPDATE
            """, (loan_id,))
            loan = cursor.fetchone()

            if not loan:
                raise ValueError("Loan record not found.")

            if loan['Return_Date'] is not None:
                raise ValueError(f"This book was already returned on {loan['Return_Date']}.")

            # 2. Calculate overdue days and fine amount
            due_date = loan['Due_Date']
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()

            overdue_days = max(0, (return_date - due_date).days)
            auto_fine = round(overdue_days * Config.FINE_PER_DAY, 2)

            # Allow staff to confirm or record final fine
            final_fine = auto_fine
            if record_fine_input is not None and record_fine_input.strip() != '':
                try:
                    final_fine = max(0.0, float(record_fine_input))
                except ValueError:
                    final_fine = auto_fine

            # 3. Update BOOK_LOAN
            cursor.execute("""
                UPDATE BOOK_LOAN 
                SET Return_Date = %s, Fine_Amount = %s 
                WHERE Loan_ID = %s
            """, (return_date, final_fine, loan_id))

            # 4. Atomically restore available stock in BOOK
            cursor.execute("""
                UPDATE BOOK 
                SET Available_Copies = Available_Copies + 1 
                WHERE Book_ID = %s AND Available_Copies < Total_Copies
            """, (loan['Book_ID'],))

            if cursor.rowcount == 0:
                # Fallback safety if available copies was somehow equal to total
                cursor.execute("UPDATE BOOK SET Available_Copies = Total_Copies WHERE Book_ID = %s", (loan['Book_ID'],))

        flash(
            f"Successfully returned '{loan['Title']}' from {loan['Member_Name']}. "
            f"Overdue: {overdue_days} day(s). Fine recorded: {Config.CURRENCY_SYMBOL}{final_fine:.2f}.", 
            'success'
        )
    except ValueError as ve:
        flash(str(ve), 'danger')
    except Exception as e:
        flash(f"Return transaction failed: {str(e)}", 'danger')

    return redirect(url_for('loans.index', tab='active'))
