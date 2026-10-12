"""
Category Management Blueprint.
Provides CRUD operations for genres/categories with duplicate name validation.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from db import execute_query, execute_non_query

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories')
@login_required
def index():
    """Lists all categories along with total cataloged books in each."""
    sql = """
        SELECT 
            c.Category_ID,
            c.Category_Name,
            COUNT(b.Book_ID) AS Book_Count,
            COALESCE(SUM(b.Total_Copies), 0) AS Total_Physical_Copies
        FROM CATEGORY c
        LEFT JOIN BOOK b ON c.Category_ID = b.Category_ID
        GROUP BY c.Category_ID, c.Category_Name
        ORDER BY c.Category_Name ASC
    """
    categories = execute_query(sql)
    return render_template('categories.html', categories=categories)

@categories_bp.route('/categories/add', methods=['POST'])
@login_required
def add():
    """Adds a new book category with uniqueness validation."""
    name = request.form.get('name', '').strip()

    if not name:
        flash('Category name is required.', 'danger')
        return redirect(url_for('categories.index'))

    # Check for existing duplicate category
    existing = execute_query("SELECT Category_ID FROM CATEGORY WHERE Category_Name = %s", (name,), fetchone=True)
    if existing:
        flash(f"Category '{name}' already exists.", 'danger')
        return redirect(url_for('categories.index'))

    try:
        execute_non_query("INSERT INTO CATEGORY (Category_Name) VALUES (%s)", (name,))
        flash(f"Category '{name}' created successfully.", 'success')
    except Exception as e:
        flash(f"Error adding category: {str(e)}", 'danger')

    return redirect(url_for('categories.index'))

@categories_bp.route('/categories/edit/<int:category_id>', methods=['POST'])
@login_required
def edit(category_id):
    """Updates an existing category name."""
    name = request.form.get('name', '').strip()

    if not name:
        flash('Category name is required.', 'danger')
        return redirect(url_for('categories.index'))

    # Check duplicate on another category
    existing = execute_query(
        "SELECT Category_ID FROM CATEGORY WHERE Category_Name = %s AND Category_ID <> %s",
        (name, category_id), fetchone=True
    )
    if existing:
        flash(f"Category '{name}' is already used by another record.", 'danger')
        return redirect(url_for('categories.index'))

    try:
        execute_non_query("UPDATE CATEGORY SET Category_Name = %s WHERE Category_ID = %s", (name, category_id))
        flash(f"Category updated to '{name}'.", 'success')
    except Exception as e:
        flash(f"Error updating category: {str(e)}", 'danger')

    return redirect(url_for('categories.index'))

@categories_bp.route('/categories/delete/<int:category_id>', methods=['POST'])
@login_required
def delete(category_id):
    """Deletes a category if no books reference it."""
    try:
        books_count = execute_query(
            "SELECT COUNT(*) AS cnt FROM BOOK WHERE Category_ID = %s",
            (category_id,), fetchone=True
        )
        if books_count and books_count['cnt'] > 0:
            flash(f"Cannot delete category: {books_count['cnt']} book(s) belong to this category.", 'danger')
            return redirect(url_for('categories.index'))

        execute_non_query("DELETE FROM CATEGORY WHERE Category_ID = %s", (category_id,))
        flash('Category deleted successfully.', 'success')
    except Exception as e:
        flash(f"Error deleting category: {str(e)}", 'danger')

    return redirect(url_for('categories.index'))
