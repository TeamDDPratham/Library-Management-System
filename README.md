# 📚 Library Management System

A full-stack **Library Management System** built using HTML, CSS, JavaScript, Python Flask, and MySQL. This project simplifies library operations through book inventory management, member registration, book issuing and returning, overdue tracking, and analytical reports.

It is developed as an academic **Relational Database Management System (RDBMS)** project to demonstrate practical SQL concepts and full-stack web development.

## ✨ Features

- **Dashboard:** View total books, available copies, registered members, active loans, and overdue books.
- **Book Management:** Add, update, search, filter, and manage book records.
- **Author Management:** Maintain author details and book associations.
- **Publisher & Category Management:** Organize books by publishers and categories.
- **Member Management:** Register members, update details, and view borrowing history.
- **Book Issue & Return:** Track issue dates, due dates, returns, and book availability.
- **Overdue Tracking:** Identify overdue books and calculate applicable fines.
- **Reports & Analytics:** Generate reports for popular books, borrowing activity, categories, and fines.
- **Authentication:** Secure librarian login and session management.
- **INR Support:** Display book prices and monetary values in Indian Rupees (₹).

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| HTML5 | Webpage structure |
| CSS3 | Styling and responsive design |
| JavaScript | Frontend interactivity |
| Python | Backend programming |
| Flask | Web framework |
| MySQL | Relational database |
| SQL | Data storage, retrieval, and analysis |
| Chart.js | Dashboard visualizations, if implemented |

## 🗄️ Database Design

The database is named `LibraryDB` and contains the following core tables:

- `BOOK` — Book details, prices, and inventory.
- `AUTHOR` — Author information.
- `BOOK_AUTHOR` — Many-to-many relationship between books and authors.
- `PUBLISHER` — Publisher information.
- `CATEGORY` — Book categories.
- `MEMBER` — Library member records.
- `BOOK_LOAN` — Issue, return, due-date, and fine records.
- `LIBRARIAN` — Librarian account information.

The database uses primary keys, foreign keys, unique constraints, and validation rules to maintain data integrity.

## 📖 RDBMS Concepts Implemented

This project demonstrates the following database concepts:

- Entity-Relationship (ER) diagrams and cardinalities
- ER-to-relational schema conversion
- Database normalization: 1NF, 2NF, and 3NF
- Primary keys, foreign keys, and integrity constraints
- DDL commands: `CREATE`, `ALTER`, `DROP`, `TRUNCATE`
- DML commands: `INSERT`, `UPDATE`, `DELETE`
- Data retrieval using `SELECT` and filtering operators
- Comparison, logical, and pattern-matching operators
- Aggregate functions: `COUNT()`, `SUM()`, `AVG()`, `MIN()`, `MAX()`
- `GROUP BY`, `HAVING`, and `ORDER BY`
- SQL joins: `INNER JOIN` and `LEFT JOIN`
- Single-row and multi-row subqueries
- `IN`, `ANY`, `ALL`, `EXISTS`, and `NOT EXISTS`
- Correlated subqueries and complex SQL queries
- Transactions using `COMMIT` and `ROLLBACK`

## 📁 Project Structure

```text
LibraryManagementSystem/
├── app.py
├── config.py
├── db.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── database/
│   ├── schema.sql
│   ├── sample_data.sql
│   └── reports.sql
│
├── routes/
│   ├── auth.py
│   ├── books.py
│   ├── authors.py
│   ├── publishers.py
│   ├── categories.py
│   ├── members.py
│   ├── loans.py
│   └── reports.py
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── books.html
│   ├── authors.html
│   ├── publishers.html
│   ├── categories.html
│   ├── members.html
│   ├── loans.html
│   └── reports.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── images/
│
└── docs/
    ├── ER_DIAGRAM.md
    └── RELATIONAL_SCHEMA.md
```

*Note: This is the intended structure. Update it to match the actual files generated in your repository.*

## ⚙️ Installation and Setup

### Prerequisites

Install the following:

- Python 3.10 or later
- MySQL Server 8.x
- MySQL Workbench (recommended)
- Git

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Library-Management-System.git
cd Library-Management-System
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the database

Open MySQL Workbench or the MySQL command-line client and execute:

```sql
CREATE DATABASE LibraryDB;
```

Import the schema and sample data using the project's SQL scripts:

```bash
mysql -u root -p LibraryDB < database/schema.sql
mysql -u root -p LibraryDB < database/sample_data.sql
```

Enter your MySQL password when prompted. If `schema.sql` already creates the database, follow the setup instructions provided in that file instead.

### 5. Configure environment variables

Copy `.env.example` to `.env` and configure your local database credentials and secret key.

Example configuration:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=LibraryDB
SECRET_KEY=replace_with_a_secure_random_value
```

Never commit your actual `.env` file or database password to GitHub.

### 6. Run the application

```bash
python app.py
```

Open the local URL printed by Flask, typically:

```text
http://127.0.0.1:5000
```

Create or configure a librarian account using the application's supported setup procedure. Do not assume a default login exists unless one has been configured.

## 🧪 SQL Demonstrations

The `database/reports.sql` file contains examples of SQL queries used for library operations and academic demonstrations.

Example: Find books priced above the average book price.

```sql
SELECT Title, Price
FROM BOOK
WHERE Price > (
    SELECT AVG(Price)
    FROM BOOK
);
```

Example: Find members with active loans.

```sql
SELECT M.Name
FROM MEMBER M
WHERE EXISTS (
    SELECT 1
    FROM BOOK_LOAN L
    WHERE L.Member_ID = M.Member_ID
      AND L.Return_Date IS NULL
);
```

Example: Display category-wise book counts.

```sql
SELECT C.Category_Name,
       COUNT(B.Book_ID) AS Total_Books
FROM CATEGORY C
LEFT JOIN BOOK B
    ON C.Category_ID = B.Category_ID
GROUP BY C.Category_ID, C.Category_Name;
```

## 🔐 Security and Data Integrity

The application is designed to use parameterized SQL queries, password hashing, session-based authentication, server-side validation, and database transactions.

Book issue and return operations should update loan records and available stock consistently. Database credentials must be kept outside the source code.

## 🚀 Future Enhancements

- Member-facing portal
- Book reservation and renewal
- Fine payment tracking
- Email reminders for due dates
- Exportable reports in CSV or PDF
- Advanced search and recommendation features
- Barcode-based book issue and return

## 🎓 Project Purpose

This project demonstrates how database design, SQL queries, and web technologies can be combined to solve a real-world library management problem. It provides practical experience with relational database design, backend development, frontend integration, and data integrity.

## 👨‍💻 Author

**Pratham Jain**

GitHub: [@TeamDDPratham](https://github.com/TeamDDPratham)

---

⭐ If you find this project useful, consider giving the repository a star!
