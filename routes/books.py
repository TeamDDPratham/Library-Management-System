"""
Book Management Blueprint.
Provides CRUD operations, multi-author associations, search, and filtering.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from db import execute_query, transaction
from mysql.connector import IntegrityError

books_bp = Blueprint('books', __name__)

@books_bp.route('/books')
@login_required
def index():
    """Lists books with search and filter controls."""
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '').strip()
    year_filter = request.args.get('year', '').strip()
    availability_filter = request.args.get('availability', '').strip()

    # Base query joining Publisher, Category, and aggregating Authors
    sql = """
        SELECT 
            b.Book_ID,
            b.ISBN,
            b.Title,
            b.Price,
            b.Total_Copies,
            b.Available_Copies,
            b.Publication_Year,
            p.Publisher_ID,
            p.Name AS Publisher_Name,
            c.Category_ID,
            c.Category_Name,
            COALESCE(GROUP_CONCAT(a.Name ORDER BY a.Name SEPARATOR ', '), 'None') AS Authors,
            GROUP_CONCAT(a.Author_ID) AS Author_IDs
        FROM BOOK b
        LEFT JOIN PUBLISHER p ON b.Publisher_ID = p.Publisher_ID
        LEFT JOIN CATEGORY c ON b.Category_ID = c.Category_ID
        LEFT JOIN BOOK_AUTHOR ba ON b.Book_ID = ba.Book_ID
        LEFT JOIN AUTHOR a ON ba.Author_ID = a.Author_ID
        WHERE 1=1
    """
    params = []

    if search_query:
        sql += """ AND (
            b.Title LIKE %s OR 
            b.ISBN LIKE %s OR 
            p.Name LIKE %s OR 
            c.Category_Name LIKE %s OR 
            a.Name LIKE %s
        )"""
        like_term = f"%{search_query}%"
        params.extend([like_term, like_term, like_term, like_term, like_term])

    if category_filter:
        sql += " AND b.Category_ID = %s"
        params.append(category_filter)

    if year_filter:
        sql += " AND b.Publication_Year = %s"
        params.append(year_filter)

    if availability_filter == 'available':
        sql += " AND b.Available_Copies > 0"
    elif availability_filter == 'unavailable':
        sql += " AND b.Available_Copies = 0"

    sql += """
        GROUP BY 
            b.Book_ID, b.ISBN, b.Title, b.Price, b.Total_Copies, 
            b.Available_Copies, b.Publication_Year, p.Publisher_ID, 
            p.Name, c.Category_ID, c.Category_Name
        ORDER BY b.Title ASC
    """

    books = execute_query(sql, params)
    categories = execute_query("SELECT Category_ID, Category_Name FROM CATEGORY ORDER BY Category_Name")
    publishers = execute_query("SELECT Publisher_ID, Name FROM PUBLISHER ORDER BY Name")
    authors = execute_query("SELECT Author_ID, Name FROM AUTHOR ORDER BY Name")
    
    # Distinct publication years for filter dropdown
    years = execute_query("SELECT DISTINCT Publication_Year FROM BOOK WHERE Publication_Year IS NOT NULL ORDER BY Publication_Year DESC")

    return render_template(
        'books.html',
        books=books,
        categories=categories,
        publishers=publishers,
        authors=authors,
        years=[y['Publication_Year'] for y in years],
        search_query=search_query,
        category_filter=category_filter,
        year_filter=year_filter,
        availability_filter=availability_filter
    )

@books_bp.route('/books/add', methods=['POST'])
@login_required
def add():
    """Adds a new book and associates its authors within a transaction."""
    isbn = request.form.get('isbn', '').strip()
    title = request.form.get('title', '').strip()
    publisher_id = request.form.get('publisher_id') or None
    category_id = request.form.get('category_id') or None
    price = request.form.get('price', '0.00').strip()
    total_copies = request.form.get('total_copies', '1').strip()
    available_copies = request.form.get('available_copies', total_copies).strip()
    publication_year = request.form.get('publication_year') or None
    selected_authors = request.form.getlist('author_ids')

    # Basic validations
    if not isbn or not title:
        flash('ISBN and Title are required fields.', 'danger')
        return redirect(url_for('books.index'))

    try:
        price_val = float(price)
        total_val = int(total_copies)
        avail_val = int(available_copies)

        if price_val < 0 or total_val < 0 or avail_val < 0:
            flash('Price, total copies, and available copies cannot be negative.', 'danger')
            return redirect(url_for('books.index'))

        if avail_val > total_val:
            flash('Available copies cannot exceed total copies.', 'danger')
            return redirect(url_for('books.index'))

        # Check duplicate ISBN
        existing_isbn = execute_query("SELECT Book_ID FROM BOOK WHERE ISBN = %s", (isbn,), fetchone=True)
        if existing_isbn:
            flash(f"A book with ISBN '{isbn}' already exists in the catalog.", 'danger')
            return redirect(url_for('books.index'))

        with transaction() as (cursor, conn):
            insert_sql = """
                INSERT INTO BOOK (ISBN, Title, Publisher_ID, Category_ID, Price, Total_Copies, Available_Copies, Publication_Year)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (isbn, title, publisher_id, category_id, price_val, total_val, avail_val, publication_year))
            book_id = cursor.lastrowid

            # Associate authors
            if selected_authors:
                ba_sql = "INSERT INTO BOOK_AUTHOR (Book_ID, Author_ID) VALUES (%s, %s)"
                for author_id in selected_authors:
                    cursor.execute(ba_sql, (book_id, int(author_id)))

        flash(f"Book '{title}' added successfully with {len(selected_authors)} author(s).", 'success')
    except IntegrityError as ie:
        flash(f"Database constraint error: {str(ie)}", 'danger')
    except Exception as e:
        flash(f"Error adding book: {str(e)}", 'danger')

    return redirect(url_for('books.index'))

@books_bp.route('/books/edit/<int:book_id>', methods=['POST'])
@login_required
def edit(book_id):
    """Updates an existing book and its author associations."""
    isbn = request.form.get('isbn', '').strip()
    title = request.form.get('title', '').strip()
    publisher_id = request.form.get('publisher_id') or None
    category_id = request.form.get('category_id') or None
    price = request.form.get('price', '0.00').strip()
    total_copies = request.form.get('total_copies', '1').strip()
    available_copies = request.form.get('available_copies', '1').strip()
    publication_year = request.form.get('publication_year') or None
    selected_authors = request.form.getlist('author_ids')

    if not isbn or not title:
        flash('ISBN and Title are required.', 'danger')
        return redirect(url_for('books.index'))

    try:
        price_val = float(price)
        total_val = int(total_copies)
        avail_val = int(available_copies)

        if price_val < 0 or total_val < 0 or avail_val < 0:
            flash('Price and copy counts cannot be negative.', 'danger')
            return redirect(url_for('books.index'))

        if avail_val > total_val:
            flash('Available copies cannot exceed total copies.', 'danger')
            return redirect(url_for('books.index'))

        # Check duplicate ISBN on different book
        dup = execute_query("SELECT Book_ID FROM BOOK WHERE ISBN = %s AND Book_ID <> %s", (isbn, book_id), fetchone=True)
        if dup:
            flash(f"Another book already uses ISBN '{isbn}'.", 'danger')
            return redirect(url_for('books.index'))

        with transaction() as (cursor, conn):
            update_sql = """
                UPDATE BOOK 
                SET ISBN = %s, Title = %s, Publisher_ID = %s, Category_ID = %s,
                    Price = %s, Total_Copies = %s, Available_Copies = %s, Publication_Year = %s
                WHERE Book_ID = %s
            """
            cursor.execute(update_sql, (isbn, title, publisher_id, category_id, price_val, total_val, avail_val, publication_year, book_id))

            # Replace author associations
            cursor.execute("DELETE FROM BOOK_AUTHOR WHERE Book_ID = %s", (book_id,))
            if selected_authors:
                ba_sql = "INSERT INTO BOOK_AUTHOR (Book_ID, Author_ID) VALUES (%s, %s)"
                for author_id in selected_authors:
                    cursor.execute(ba_sql, (book_id, int(author_id)))

        flash(f"Book '{title}' updated successfully.", 'success')
    except Exception as e:
        flash(f"Error updating book: {str(e)}", 'danger')

    return redirect(url_for('books.index'))

@books_bp.route('/books/delete/<int:book_id>', methods=['POST'])
@login_required
def delete(book_id):
    """Deletes a book if it has no active loans or loan history."""
    try:
        # Check active loans
        active_loans = execute_query(
            "SELECT COUNT(*) AS cnt FROM BOOK_LOAN WHERE Book_ID = %s AND Return_Date IS NULL", 
            (book_id,), fetchone=True
        )
        if active_loans and active_loans['cnt'] > 0:
            flash('Cannot delete book: There are currently active loans for this title.', 'danger')
            return redirect(url_for('books.index'))

        # Check completed loan history
        history_loans = execute_query(
            "SELECT COUNT(*) AS cnt FROM BOOK_LOAN WHERE Book_ID = %s",
            (book_id,), fetchone=True
        )
        if history_loans and history_loans['cnt'] > 0:
            flash('Cannot delete book: Historical borrowing records reference this book. Archive or adjust copies instead.', 'danger')
            return redirect(url_for('books.index'))

        with transaction() as (cursor, conn):
            cursor.execute("DELETE FROM BOOK_AUTHOR WHERE Book_ID = %s", (book_id,))
            cursor.execute("DELETE FROM BOOK WHERE Book_ID = %s", (book_id,))

        flash('Book deleted successfully.', 'success')
    except Exception as e:
        flash(f"Error deleting book: {str(e)}", 'danger')

    return redirect(url_for('books.index'))
