"""
Publisher Management Blueprint.
Provides CRUD operations for publishers and displays their published titles.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from db import execute_query, execute_non_query

publishers_bp = Blueprint('publishers', __name__)

@publishers_bp.route('/publishers')
@login_required
def index():
    """Lists all publishers with their book counts."""
    search_query = request.args.get('q', '').strip()
    sql = """
        SELECT 
            p.Publisher_ID,
            p.Name,
            p.Address,
            COUNT(b.Book_ID) AS Book_Count,
            COALESCE(GROUP_CONCAT(b.Title SEPARATOR ' | '), 'None') AS Books_List
        FROM PUBLISHER p
        LEFT JOIN BOOK b ON p.Publisher_ID = b.Publisher_ID
        WHERE 1=1
    """
    params = []
    if search_query:
        sql += " AND (p.Name LIKE %s OR p.Address LIKE %s)"
        like_term = f"%{search_query}%"
        params.extend([like_term, like_term])

    sql += """
        GROUP BY p.Publisher_ID, p.Name, p.Address
        ORDER BY p.Name ASC
    """
    publishers = execute_query(sql, params)
    return render_template('publishers.html', publishers=publishers, search_query=search_query)

@publishers_bp.route('/publishers/add', methods=['POST'])
@login_required
def add():
    """Adds a new publisher."""
    name = request.form.get('name', '').strip()
    address = request.form.get('address', '').strip()

    if not name:
        flash('Publisher name is required.', 'danger')
        return redirect(url_for('publishers.index'))

    try:
        execute_non_query(
            "INSERT INTO PUBLISHER (Name, Address) VALUES (%s, %s)",
            (name, address or None)
        )
        flash(f"Publisher '{name}' added successfully.", 'success')
    except Exception as e:
        flash(f"Error adding publisher: {str(e)}", 'danger')

    return redirect(url_for('publishers.index'))

@publishers_bp.route('/publishers/edit/<int:publisher_id>', methods=['POST'])
@login_required
def edit(publisher_id):
    """Updates publisher information."""
    name = request.form.get('name', '').strip()
    address = request.form.get('address', '').strip()

    if not name:
        flash('Publisher name is required.', 'danger')
        return redirect(url_for('publishers.index'))

    try:
        execute_non_query(
            "UPDATE PUBLISHER SET Name = %s, Address = %s WHERE Publisher_ID = %s",
            (name, address or None, publisher_id)
        )
        flash(f"Publisher '{name}' updated successfully.", 'success')
    except Exception as e:
        flash(f"Error updating publisher: {str(e)}", 'danger')

    return redirect(url_for('publishers.index'))

@publishers_bp.route('/publishers/delete/<int:publisher_id>', methods=['POST'])
@login_required
def delete(publisher_id):
    """Deletes a publisher if no books are associated."""
    try:
        books_count = execute_query(
            "SELECT COUNT(*) AS cnt FROM BOOK WHERE Publisher_ID = %s",
            (publisher_id,), fetchone=True
        )
        if books_count and books_count['cnt'] > 0:
            flash(f"Cannot delete publisher: Associated with {books_count['cnt']} book(s).", 'danger')
            return redirect(url_for('publishers.index'))

        execute_non_query("DELETE FROM PUBLISHER WHERE Publisher_ID = %s", (publisher_id,))
        flash('Publisher deleted successfully.', 'success')
    except Exception as e:
        flash(f"Error deleting publisher: {str(e)}", 'danger')

    return redirect(url_for('publishers.index'))
