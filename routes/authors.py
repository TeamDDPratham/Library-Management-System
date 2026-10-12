"""
Author Management Blueprint.
Provides CRUD operations for authors and displays their cataloged books.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from db import execute_query, execute_non_query

authors_bp = Blueprint('authors', __name__)

@authors_bp.route('/authors')
@login_required
def index():
    """Lists all authors with their book counts and country."""
    search_query = request.args.get('q', '').strip()
    sql = """
        SELECT 
            a.Author_ID,
            a.Name,
            a.Country,
            COUNT(ba.Book_ID) AS Book_Count,
            COALESCE(GROUP_CONCAT(b.Title SEPARATOR ' | '), 'None') AS Books_List
        FROM AUTHOR a
        LEFT JOIN BOOK_AUTHOR ba ON a.Author_ID = ba.Author_ID
        LEFT JOIN BOOK b ON ba.Book_ID = b.Book_ID
        WHERE 1=1
    """
    params = []
    if search_query:
        sql += " AND (a.Name LIKE %s OR a.Country LIKE %s)"
        like_term = f"%{search_query}%"
        params.extend([like_term, like_term])

    sql += """
        GROUP BY a.Author_ID, a.Name, a.Country
        ORDER BY a.Name ASC
    """
    authors = execute_query(sql, params)
    return render_template('authors.html', authors=authors, search_query=search_query)

@authors_bp.route('/authors/add', methods=['POST'])
@login_required
def add():
    """Adds a new author."""
    name = request.form.get('name', '').strip()
    country = request.form.get('country', '').strip()

    if not name:
        flash('Author name is required.', 'danger')
        return redirect(url_for('authors.index'))

    try:
        execute_non_query(
            "INSERT INTO AUTHOR (Name, Country) VALUES (%s, %s)",
            (name, country or None)
        )
        flash(f"Author '{name}' added successfully.", 'success')
    except Exception as e:
        flash(f"Error adding author: {str(e)}", 'danger')

    return redirect(url_for('authors.index'))

@authors_bp.route('/authors/edit/<int:author_id>', methods=['POST'])
@login_required
def edit(author_id):
    """Updates author details."""
    name = request.form.get('name', '').strip()
    country = request.form.get('country', '').strip()

    if not name:
        flash('Author name is required.', 'danger')
        return redirect(url_for('authors.index'))

    try:
        execute_non_query(
            "UPDATE AUTHOR SET Name = %s, Country = %s WHERE Author_ID = %s",
            (name, country or None, author_id)
        )
        flash(f"Author '{name}' updated successfully.", 'success')
    except Exception as e:
        flash(f"Error updating author: {str(e)}", 'danger')

    return redirect(url_for('authors.index'))

@authors_bp.route('/authors/delete/<int:author_id>', methods=['POST'])
@login_required
def delete(author_id):
    """Deletes an author if no books are associated."""
    try:
        # Check if author has associated books
        assoc = execute_query(
            "SELECT COUNT(*) AS cnt FROM BOOK_AUTHOR WHERE Author_ID = %s",
            (author_id,), fetchone=True
        )
        if assoc and assoc['cnt'] > 0:
            flash('Cannot delete author: This author is associated with cataloged books.', 'danger')
            return redirect(url_for('authors.index'))

        execute_non_query("DELETE FROM AUTHOR WHERE Author_ID = %s", (author_id,))
        flash('Author deleted successfully.', 'success')
    except Exception as e:
        flash(f"Error deleting author: {str(e)}", 'danger')

    return redirect(url_for('authors.index'))
