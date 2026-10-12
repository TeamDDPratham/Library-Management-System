-- =====================================================================
-- SQL SYLLABUS QUERIES & ANALYTICAL REPORTS FOR LIBRARY MANAGEMENT SYSTEM
-- Target RDBMS: MySQL 8.x
-- Database: LibraryDB
-- =====================================================================

USE LibraryDB;

-- =====================================================================
-- SECTION A: DATA DEFINITION LANGUAGE (DDL)
-- =====================================================================

-- A.1 CREATE DATABASE
-- Creates the logical schema container with utf8mb4 encoding.
-- CREATE DATABASE LibraryDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- A.2 CREATE TABLE (Example: core tables defined in schema.sql)
-- CREATE TABLE PUBLISHER (...);

-- A.3 ALTER TABLE: Add a new column safely
-- Example: Adding an optional note/bio column to AUTHOR
ALTER TABLE AUTHOR ADD COLUMN Bio TEXT NULL;

-- Example: Modifying column data type
ALTER TABLE AUTHOR MODIFY COLUMN Bio VARCHAR(500) NULL;

-- Example: Dropping the added column safely to maintain original schema
ALTER TABLE AUTHOR DROP COLUMN Bio;

-- A.4 DROP TABLE (Demonstrated safely using disposable temporary table)
CREATE TABLE TEMP_DROP_DEMO (
    Demo_ID INT PRIMARY KEY,
    Description VARCHAR(100)
);
-- Safely drop the temporary demonstration table
DROP TABLE IF EXISTS TEMP_DROP_DEMO;

-- A.5 TRUNCATE TABLE (Demonstrated safely using disposable temporary table)
CREATE TABLE TEMP_TRUNCATE_DEMO (
    Demo_ID INT PRIMARY KEY,
    Sample_Val VARCHAR(50)
);
INSERT INTO TEMP_TRUNCATE_DEMO VALUES (1, 'Test A'), (2, 'Test B');
-- Safely truncate table: deletes all rows and resets auto-increment without dropping structure
TRUNCATE TABLE TEMP_TRUNCATE_DEMO;
DROP TABLE IF EXISTS TEMP_TRUNCATE_DEMO;


-- =====================================================================
-- SECTION B: DATA MANIPULATION LANGUAGE (DML)
-- =====================================================================

-- B.1 INSERT: Add a new record
-- INSERT INTO CATEGORY (Category_Name) VALUES ('Cloud Computing');

-- B.2 UPDATE: Modify existing records
-- UPDATE BOOK SET Price = 49.99 WHERE Book_ID = 4;

-- B.3 DELETE: Remove a record with safety check
-- DELETE FROM CATEGORY WHERE Category_Name = 'Cloud Computing';


-- =====================================================================
-- SECTION C: SELECT AND FILTERING OPERATORS
-- =====================================================================

-- C.1 Basic SELECT with WHERE, DISTINCT, ORDER BY, LIMIT
SELECT DISTINCT Publication_Year 
FROM BOOK 
ORDER BY Publication_Year DESC;

-- C.2 Logical Operators: AND, OR, NOT
SELECT Title, Price, Available_Copies, Publication_Year 
FROM BOOK 
WHERE (Price > 50.00 AND Available_Copies > 0) 
   OR NOT (Publication_Year < 2015)
ORDER BY Price DESC;

-- C.3 Comparison Operators (=, <>, !=, >, <, >=, <=)
SELECT Title, Price, Total_Copies 
FROM BOOK 
WHERE Price >= 60.00 AND Total_Copies <> 3;

-- C.4 Range Operator: BETWEEN
SELECT Title, Price, Publication_Year 
FROM BOOK 
WHERE Publication_Year BETWEEN 2010 AND 2020
ORDER BY Publication_Year ASC;

-- C.5 Set Membership: IN
SELECT Title, Category_ID, Price 
FROM BOOK 
WHERE Category_ID IN (1, 2, 3);

-- C.6 Pattern Matching: LIKE
SELECT Title, ISBN 
FROM BOOK 
WHERE Title LIKE '%Data%' OR Title LIKE 'Clean%';

-- C.7 NULL Handling: IS NULL and IS NOT NULL
-- Identifies active loans (not yet returned)
SELECT Loan_ID, Book_ID, Member_ID, Issue_Date, Due_Date 
FROM BOOK_LOAN 
WHERE Return_Date IS NULL;

-- Identifies completed loans
SELECT Loan_ID, Book_ID, Member_ID, Return_Date, Fine_Amount 
FROM BOOK_LOAN 
WHERE Return_Date IS NOT NULL;


-- =====================================================================
-- SECTION D: AGGREGATE FUNCTIONS & GROUPING
-- =====================================================================

-- D.1 Aggregate summaries: COUNT, SUM, AVG, MIN, MAX
SELECT 
    COUNT(*) AS Total_Titles,
    SUM(Total_Copies) AS Total_Physical_Books,
    SUM(Available_Copies) AS Total_Available_Books,
    ROUND(AVG(Price), 2) AS Average_Book_Price,
    MIN(Price) AS Cheapest_Book_Price,
    MAX(Price) AS Most_Expensive_Book_Price
FROM BOOK;

-- D.2 GROUP BY with HAVING
-- Lists categories with more than 1 book and computes average price
SELECT 
    c.Category_Name,
    COUNT(b.Book_ID) AS Book_Count,
    ROUND(AVG(b.Price), 2) AS Avg_Category_Price,
    SUM(b.Total_Copies) AS Total_Stock
FROM CATEGORY c
JOIN BOOK b ON c.Category_ID = b.Category_ID
GROUP BY c.Category_ID, c.Category_Name
HAVING COUNT(b.Book_ID) >= 2
ORDER BY Book_Count DESC;


-- =====================================================================
-- SECTION E: JOINS (INNER, LEFT, MULTI-TABLE)
-- =====================================================================

-- E.1 INNER JOIN: Books with Publisher and Category
SELECT 
    b.Book_ID,
    b.Title,
    b.ISBN,
    p.Name AS Publisher,
    c.Category_Name AS Category,
    b.Price,
    b.Available_Copies,
    b.Total_Copies
FROM BOOK b
INNER JOIN PUBLISHER p ON b.Publisher_ID = p.Publisher_ID
INNER JOIN CATEGORY c ON b.Category_ID = c.Category_ID
ORDER BY b.Title ASC;

-- E.2 LEFT JOIN: All categories including those with zero books
SELECT 
    c.Category_ID,
    c.Category_Name,
    COUNT(b.Book_ID) AS Number_Of_Books
FROM CATEGORY c
LEFT JOIN BOOK b ON c.Category_ID = b.Category_ID
GROUP BY c.Category_ID, c.Category_Name
ORDER BY Number_Of_Books DESC;

-- E.3 Multi-Table Join across 5 entities: Active Loans with Full Details
SELECT 
    l.Loan_ID,
    m.Name AS Member_Name,
    m.Email AS Member_Email,
    b.Title AS Book_Title,
    b.ISBN,
    c.Category_Name,
    lib.Name AS Issued_By_Librarian,
    l.Issue_Date,
    l.Due_Date,
    DATEDIFF(CURRENT_DATE, l.Due_Date) AS Days_Overdue
FROM BOOK_LOAN l
INNER JOIN MEMBER m ON l.Member_ID = m.Member_ID
INNER JOIN BOOK b ON l.Book_ID = b.Book_ID
INNER JOIN CATEGORY c ON b.Category_ID = c.Category_ID
LEFT JOIN LIBRARIAN lib ON l.Issued_By = lib.Librarian_ID
WHERE l.Return_Date IS NULL
ORDER BY l.Due_Date ASC;


-- =====================================================================
-- SECTION F: SINGLE-ROW SUBQUERIES
-- =====================================================================

-- F.1 Books priced above the overall average book price
SELECT Book_ID, Title, Price 
FROM BOOK 
WHERE Price > (SELECT AVG(Price) FROM BOOK)
ORDER BY Price DESC;

-- F.2 Book with the maximum price
SELECT Book_ID, Title, Price, Publication_Year 
FROM BOOK 
WHERE Price = (SELECT MAX(Price) FROM BOOK);


-- =====================================================================
-- SECTION G: MULTI-ROW SUBQUERIES (IN, ANY, ALL)
-- =====================================================================

-- G.1 Members who have borrowed at least one book using IN
SELECT Member_ID, Name, Email, Status 
FROM MEMBER 
WHERE Member_ID IN (SELECT DISTINCT Member_ID FROM BOOK_LOAN);

-- G.2 Books with prices greater than ANY book in Category 2 (Database Systems)
SELECT Book_ID, Title, Price, Category_ID 
FROM BOOK 
WHERE Price > ANY (SELECT Price FROM BOOK WHERE Category_ID = 2)
  AND Category_ID <> 2
ORDER BY Price ASC;

-- G.3 Books with prices greater than ALL books in Category 4 (Software Engineering)
SELECT Book_ID, Title, Price, Category_ID 
FROM BOOK 
WHERE Price > ALL (SELECT Price FROM BOOK WHERE Category_ID = 4)
ORDER BY Price ASC;


-- =====================================================================
-- SECTION H: EXISTS AND NOT EXISTS
-- =====================================================================

-- H.1 Members with active (unreturned) loans using EXISTS
SELECT m.Member_ID, m.Name, m.Email 
FROM MEMBER m
WHERE EXISTS (
    SELECT 1 
    FROM BOOK_LOAN l 
    WHERE l.Member_ID = m.Member_ID 
      AND l.Return_Date IS NULL
);

-- H.2 Books that have NEVER been borrowed using NOT EXISTS
SELECT b.Book_ID, b.Title, b.ISBN, b.Total_Copies 
FROM BOOK b
WHERE NOT EXISTS (
    SELECT 1 
    FROM BOOK_LOAN l 
    WHERE l.Book_ID = b.Book_ID
);

-- H.3 Members who have NEVER borrowed any book using NOT EXISTS
SELECT m.Member_ID, m.Name, m.Email, m.Join_Date 
FROM MEMBER m
WHERE NOT EXISTS (
    SELECT 1 
    FROM BOOK_LOAN l 
    WHERE l.Member_ID = m.Member_ID
);


-- =====================================================================
-- SECTION I: CORRELATED SUBQUERIES
-- =====================================================================

-- I.1 Books priced higher than the average price of their own category
SELECT b1.Book_ID, b1.Title, b1.Price, b1.Category_ID
FROM BOOK b1
WHERE b1.Price > (
    SELECT AVG(b2.Price) 
    FROM BOOK b2 
    WHERE b2.Category_ID = b1.Category_ID
)
ORDER BY b1.Category_ID, b1.Price DESC;

-- I.2 Members whose total loan count exceeds the average loan count per borrowing member
SELECT m.Member_ID, m.Name, (
    SELECT COUNT(*) FROM BOOK_LOAN l WHERE l.Member_ID = m.Member_ID
) AS Member_Loan_Count
FROM MEMBER m
WHERE (
    SELECT COUNT(*) FROM BOOK_LOAN l WHERE l.Member_ID = m.Member_ID
) > (
    SELECT AVG(loan_counts.cnt) FROM (
        SELECT COUNT(*) AS cnt FROM BOOK_LOAN GROUP BY Member_ID
    ) AS loan_counts
)
ORDER BY Member_Loan_Count DESC;

-- I.3 Authors whose books have generated loans
SELECT a.Author_ID, a.Name, a.Country
FROM AUTHOR a
WHERE EXISTS (
    SELECT 1 
    FROM BOOK_AUTHOR ba
    JOIN BOOK_LOAN bl ON ba.Book_ID = bl.Book_ID
    WHERE ba.Author_ID = a.Author_ID
);


-- =====================================================================
-- SECTION J: COMPLEX APPLICATION & ANALYTICAL QUERIES
-- =====================================================================

-- J.1 Overdue Books with Member Details and Real-time Fine Calculation
-- Assuming fine rate = ₹5.00 per day overdue
SELECT 
    l.Loan_ID,
    b.Title AS Book_Title,
    b.ISBN,
    m.Name AS Member_Name,
    m.Email AS Member_Email,
    m.Phone,
    l.Issue_Date,
    l.Due_Date,
    DATEDIFF(CURRENT_DATE, l.Due_Date) AS Days_Overdue,
    ROUND(DATEDIFF(CURRENT_DATE, l.Due_Date) * 5.00, 2) AS Calculated_Fine_INR
FROM BOOK_LOAN l
JOIN BOOK b ON l.Book_ID = b.Book_ID
JOIN MEMBER m ON l.Member_ID = m.Member_ID
WHERE l.Return_Date IS NULL 
  AND l.Due_Date < CURRENT_DATE
ORDER BY Days_Overdue DESC;

-- J.2 Most Borrowed Books Ranking
SELECT 
    b.Book_ID,
    b.Title,
    b.ISBN,
    c.Category_Name,
    COUNT(l.Loan_ID) AS Times_Borrowed
FROM BOOK b
JOIN CATEGORY c ON b.Category_ID = c.Category_ID
LEFT JOIN BOOK_LOAN l ON b.Book_ID = l.Book_ID
GROUP BY b.Book_ID, b.Title, b.ISBN, c.Category_Name
ORDER BY Times_Borrowed DESC, b.Title ASC;

-- J.3 Least Borrowed Books (including zero borrowings)
SELECT 
    b.Book_ID,
    b.Title,
    b.ISBN,
    COUNT(l.Loan_ID) AS Times_Borrowed,
    b.Available_Copies,
    b.Total_Copies
FROM BOOK b
LEFT JOIN BOOK_LOAN l ON b.Book_ID = l.Book_ID
GROUP BY b.Book_ID, b.Title, b.ISBN, b.Available_Copies, b.Total_Copies
HAVING COUNT(l.Loan_ID) <= 1
ORDER BY Times_Borrowed ASC, b.Title ASC;

-- J.4 Category-wise Borrowing Statistics
SELECT 
    c.Category_ID,
    c.Category_Name,
    COUNT(DISTINCT b.Book_ID) AS Titles_Count,
    COUNT(l.Loan_ID) AS Total_Loans_Count,
    COALESCE(SUM(l.Fine_Amount), 0.00) AS Total_Fines_Collected
FROM CATEGORY c
LEFT JOIN BOOK b ON c.Category_ID = b.Category_ID
LEFT JOIN BOOK_LOAN l ON b.Book_ID = l.Book_ID
GROUP BY c.Category_ID, c.Category_Name
ORDER BY Total_Loans_Count DESC;

-- J.5 Author-wise Borrowing Statistics
SELECT 
    a.Author_ID,
    a.Name AS Author_Name,
    a.Country,
    COUNT(DISTINCT ba.Book_ID) AS Books_Written,
    COUNT(bl.Loan_ID) AS Total_Borrowings
FROM AUTHOR a
LEFT JOIN BOOK_AUTHOR ba ON a.Author_ID = ba.Author_ID
LEFT JOIN BOOK_LOAN bl ON ba.Book_ID = bl.Book_ID
GROUP BY a.Author_ID, a.Name, a.Country
ORDER BY Total_Borrowings DESC;

-- J.6 Books Never Borrowed but Currently Available in Stock
SELECT 
    b.Book_ID,
    b.Title,
    b.ISBN,
    p.Name AS Publisher,
    c.Category_Name,
    b.Available_Copies
FROM BOOK b
JOIN PUBLISHER p ON b.Publisher_ID = p.Publisher_ID
JOIN CATEGORY c ON b.Category_ID = c.Category_ID
WHERE b.Available_Copies > 0
  AND NOT EXISTS (
      SELECT 1 FROM BOOK_LOAN l WHERE l.Book_ID = b.Book_ID
  );

-- J.7 Members Who Have Borrowed More Than 1 Distinct Book
SELECT 
    m.Member_ID,
    m.Name,
    m.Email,
    COUNT(DISTINCT l.Book_ID) AS Distinct_Books_Borrowed
FROM MEMBER m
JOIN BOOK_LOAN l ON m.Member_ID = l.Member_ID
GROUP BY m.Member_ID, m.Name, m.Email
HAVING COUNT(DISTINCT l.Book_ID) > 1
ORDER BY Distinct_Books_Borrowed DESC;

-- J.8 Summary of All Fines (Paid Recorded Fines vs Pending Overdue Fines)
SELECT 
    (SELECT COALESCE(SUM(Fine_Amount), 0) FROM BOOK_LOAN WHERE Return_Date IS NOT NULL) AS Recorded_Fines_Collected,
    (SELECT COALESCE(SUM(DATEDIFF(CURRENT_DATE, Due_Date) * 5.00), 0) 
     FROM BOOK_LOAN 
     WHERE Return_Date IS NULL AND Due_Date < CURRENT_DATE) AS Pending_Uncollected_Fines,
    (SELECT COUNT(*) FROM BOOK_LOAN WHERE Return_Date IS NULL AND Due_Date < CURRENT_DATE) AS Active_Overdue_Loans_Count;
