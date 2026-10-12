"""
Member Management Blueprint.
Provides member registration, status management (Active/Inactive),
and borrowing history inspection.
"""

from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.auth import login_required
from db import execute_query, execute_non_query
from config import Config

members_bp = Blueprint('members', __name__)

@members_bp.route('/members')
@login_required
def index():
    """Lists library members with borrowing statistics and status."""
    search_query = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()

    sql = """
        SELECT 
            m.Member_ID,
            m.Name,
            m.Email,
            m.Phone,
            m.Join_Date,
            m.Status,
            COUNT(l.Loan_ID) AS Total_Loans,
            SUM(CASE WHEN l.Return_Date IS NULL THEN 1 ELSE 0 END) AS Active_Loans,
            SUM(CASE WHEN l.Return_Date IS NULL AND l.Due_Date < CURRENT_DATE THEN 1 ELSE 0 END) AS Overdue_Loans,
            COALESCE(SUM(l.Fine_Amount), 0.00) AS Total_Fines_Recorded
        FROM MEMBER m
        LEFT JOIN BOOK_LOAN l ON m.Member_ID = l.Member_ID
        WHERE 1=1
    """
    params = []
    if search_query:
        sql += " AND (m.Name LIKE %s OR m.Email LIKE %s OR m.Phone LIKE %s)"
        like_term = f"%{search_query}%"
        params.extend([like_term, like_term, like_term])

    if status_filter:
        sql += " AND m.Status = %s"
        params.append(status_filter)

    sql += """
        GROUP BY m.Member_ID, m.Name, m.Email, m.Phone, m.Join_Date, m.Status
        ORDER BY m.Name ASC
    """
    members = execute_query(sql, params)
    return render_template(
        'members.html',
        members=members,
        search_query=search_query,
        status_filter=status_filter,
        today=date.today().isoformat()
    )

@members_bp.route('/members/add', methods=['POST'])
@login_required
def add():
    """Registers a new library member."""
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    join_date = request.form.get('join_date', '').strip() or date.today().isoformat()
    status = request.form.get('status', 'Active').strip()

    if not name or not email:
        flash('Member Name and Email are required.', 'danger')
        return redirect(url_for('members.index'))

    # Check duplicate email
    dup = execute_query("SELECT Member_ID FROM MEMBER WHERE Email = %s", (email,), fetchone=True)
    if dup:
        flash(f"A member with email '{email}' is already registered.", 'danger')
        return redirect(url_for('members.index'))

    try:
        execute_non_query(
            "INSERT INTO MEMBER (Name, Email, Phone, Join_Date, Status) VALUES (%s, %s, %s, %s, %s)",
            (name, email, phone or None, join_date, status)
        )
        flash(f"Member '{name}' registered successfully.", 'success')
    except Exception as e:
        flash(f"Error registering member: {str(e)}", 'danger')

    return redirect(url_for('members.index'))

@members_bp.route('/members/edit/<int:member_id>', methods=['POST'])
@login_required
def edit(member_id):
    """Updates member details."""
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    status = request.form.get('status', 'Active').strip()

    if not name or not email:
        flash('Member Name and Email are required.', 'danger')
        return redirect(url_for('members.index'))

    # Check email conflict
    dup = execute_query(
        "SELECT Member_ID FROM MEMBER WHERE Email = %s AND Member_ID <> %s",
        (email, member_id), fetchone=True
    )
    if dup:
        flash(f"Email '{email}' is already used by another member.", 'danger')
        return redirect(url_for('members.index'))

    try:
        execute_non_query(
            "UPDATE MEMBER SET Name = %s, Email = %s, Phone = %s, Status = %s WHERE Member_ID = %s",
            (name, email, phone or None, status, member_id)
        )
        flash(f"Member '{name}' updated successfully.", 'success')
    except Exception as e:
        flash(f"Error updating member: {str(e)}", 'danger')

    return redirect(url_for('members.index'))

@members_bp.route('/members/toggle-status/<int:member_id>', methods=['POST'])
@login_required
def toggle_status(member_id):
    """Toggles member between Active and Inactive (avoids deleting history)."""
    try:
        member = execute_query("SELECT Status, Name FROM MEMBER WHERE Member_ID = %s", (member_id,), fetchone=True)
        if not member:
            flash('Member not found.', 'danger')
            return redirect(url_for('members.index'))

        new_status = 'Inactive' if member['Status'] == 'Active' else 'Active'
        execute_non_query("UPDATE MEMBER SET Status = %s WHERE Member_ID = %s", (new_status, member_id))
        flash(f"Member '{member['Name']}' status changed to {new_status}.", 'info')
    except Exception as e:
        flash(f"Error toggling member status: {str(e)}", 'danger')

    return redirect(url_for('members.index'))

@members_bp.route('/members/<int:member_id>/history')
@login_required
def history(member_id):
    """Fetches borrowing history and active loans for a specific member."""
    member = execute_query("SELECT * FROM MEMBER WHERE Member_ID = %s", (member_id,), fetchone=True)
    if not member:
        flash('Member not found.', 'danger')
        return redirect(url_for('members.index'))

    loans = execute_query("""
        SELECT 
            l.Loan_ID,
            b.Title AS Book_Title,
            b.ISBN,
            l.Issue_Date,
            l.Due_Date,
            l.Return_Date,
            l.Fine_Amount,
            CASE 
                WHEN l.Return_Date IS NULL AND l.Due_Date < CURRENT_DATE 
                THEN DATEDIFF(CURRENT_DATE, l.Due_Date) 
                ELSE 0 
            END AS Days_Overdue,
            CASE 
                WHEN l.Return_Date IS NULL AND l.Due_Date < CURRENT_DATE 
                THEN ROUND(DATEDIFF(CURRENT_DATE, l.Due_Date) * %s, 2)
                ELSE 0.00 
            END AS Calculated_Pending_Fine
        FROM BOOK_LOAN l
        JOIN BOOK b ON l.Book_ID = b.Book_ID
        WHERE l.Member_ID = %s
        ORDER BY l.Issue_Date DESC
    """, (Config.FINE_PER_DAY, member_id))

    return render_template('member_history.html', member=member, loans=loans, fine_rate=Config.FINE_PER_DAY)
