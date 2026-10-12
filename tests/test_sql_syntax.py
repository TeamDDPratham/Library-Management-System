"""
Test suite validating SQL scripts structure, constraint completeness,
and syllabus coverage in LibraryDB.
"""

import os
import re
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')
SAMPLE_DATA_PATH = os.path.join(BASE_DIR, 'database', 'sample_data.sql')
REPORTS_PATH = os.path.join(BASE_DIR, 'database', 'reports.sql')

def test_sql_files_exist():
    """Verify that all three core database SQL scripts exist and are non-empty."""
    for path in (SCHEMA_PATH, SAMPLE_DATA_PATH, REPORTS_PATH):
        assert os.path.exists(path), f"File missing: {path}"
        assert os.path.getsize(path) > 0, f"File is empty: {path}"

def test_schema_contains_eight_core_tables():
    """Verify that schema.sql defines all 8 core tables mandated by specification."""
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        content = f.read().upper()

    required_tables = [
        'PUBLISHER',
        'CATEGORY',
        'AUTHOR',
        'BOOK',
        'BOOK_AUTHOR',
        'MEMBER',
        'LIBRARIAN',
        'BOOK_LOAN'
    ]

    for table in required_tables:
        pattern = rf'CREATE\s+TABLE\s+(IF\s+NOT\s+EXISTS\s+)?{table}\b'
        assert re.search(pattern, content), f"Table definition missing in schema.sql: {table}"

def test_schema_integrity_constraints():
    """Verify all domain, check, and relational integrity constraints in schema.sql."""
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        content = f.read().upper()

    # Check constraints
    assert 'CHECK (PRICE >= 0)' in content
    assert 'CHECK (TOTAL_COPIES >= 0)' in content
    assert 'CHECK (AVAILABLE_COPIES >= 0 AND AVAILABLE_COPIES <= TOTAL_COPIES)' in content
    assert "CHECK (STATUS IN ('ACTIVE', 'INACTIVE'))" in content
    assert 'CHECK (DUE_DATE >= ISSUE_DATE)' in content
    assert 'CHECK (FINE_AMOUNT >= 0)' in content

    # Unique constraints
    assert 'UNIQUE (ISBN)' in content
    assert 'UNIQUE (EMAIL)' in content

    # Bridge table composite key
    assert 'PRIMARY KEY (BOOK_ID, AUTHOR_ID)' in content

def test_sample_data_covers_all_tables():
    """Verify that sample_data.sql populates all 8 core tables."""
    with open(SAMPLE_DATA_PATH, 'r', encoding='utf-8') as f:
        content = f.read().upper()

    tables = ['PUBLISHER', 'CATEGORY', 'AUTHOR', 'BOOK', 'BOOK_AUTHOR', 'MEMBER', 'LIBRARIAN', 'BOOK_LOAN']
    for table in tables:
        assert f'INSERT INTO {table}' in content, f"Sample data missing inserts for table: {table}"

def test_reports_covers_sql_syllabus():
    """Verify that reports.sql demonstrates all required syllabus topics."""
    with open(REPORTS_PATH, 'r', encoding='utf-8') as f:
        content = f.read().upper()

    required_keywords = [
        'CREATE DATABASE',
        'ALTER TABLE',
        'DROP TABLE',
        'TRUNCATE TABLE',
        'INSERT INTO',
        'UPDATE',
        'DELETE',
        'DISTINCT',
        'ORDER BY',
        'BETWEEN',
        'LIKE',
        'IS NULL',
        'IS NOT NULL',
        'COUNT(',
        'SUM(',
        'AVG(',
        'MIN(',
        'MAX(',
        'GROUP BY',
        'HAVING',
        'INNER JOIN',
        'LEFT JOIN',
        'ANY (',
        'ALL (',
        'EXISTS',
        'NOT EXISTS',
        'DATEDIFF'
    ]

    for kw in required_keywords:
        assert kw in content, f"Syllabus SQL keyword missing in reports.sql: {kw}"
