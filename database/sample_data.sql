-- =====================================================================
-- REALISTIC SAMPLE DATA FOR LIBRARY MANAGEMENT SYSTEM
-- Target Database: LibraryDB (MySQL 8.x)
-- Context: Indian Academic & Engineering College Library Catalogue
-- Currency Standard: Indian Rupees (₹)
-- =====================================================================

USE LibraryDB;

-- ---------------------------------------------------------------------
-- 1. Insert PUBLISHER Records (10 Publishers)
-- Prominent Indian publishing houses and academic branches
-- ---------------------------------------------------------------------
INSERT INTO PUBLISHER (Publisher_ID, Name, Address) VALUES
(1, 'Tata McGraw-Hill Education', '12/48, Malcha Marg, Chanakyapuri, New Delhi, Delhi 110021'),
(2, 'Oxford University Press India', 'YMCA Library Building, 1 Jai Singh Road, New Delhi, Delhi 110001'),
(3, 'Pearson India Education Services', '15th Floor, Tower B, World Trade Tower, Sector 16, Noida, UP 201301'),
(4, 'PHI Learning (Prentice Hall India)', 'Rimjhim House, 111, Patparganj Industrial Estate, Delhi 110092'),
(5, 'S. Chand Publishing', 'Ravindra Mansion, 7361, Ram Nagar, Qutab Road, New Delhi, Delhi 110055'),
(6, 'Cambridge University Press India', 'Cambridge House, 4381/4 Ansari Road, Daryaganj, New Delhi, Delhi 110002'),
(7, 'Rupa Publications India', '1/16, Ansari Road, Daryaganj, New Delhi, Delhi 110002'),
(8, 'Jaico Publishing House', 'A-2, Jash Chambers, Sir Phirozshah Mehta Road, Fort, Mumbai, Maharashtra 400001'),
(9, 'Penguin Random House India', '7th Floor, Infinity Tower C, DLF Cyber City, Gurugram, Haryana 122002'),
(10, 'Wiley India Pvt. Ltd.', '4436/7, Ansari Road, Daryaganj, New Delhi, Delhi 110002');

-- ---------------------------------------------------------------------
-- 2. Insert CATEGORY Records (10 Categories)
-- Broad academic and engineering syllabus classifications
-- ---------------------------------------------------------------------
INSERT INTO CATEGORY (Category_ID, Category_Name) VALUES
(1, 'Computer Science & Engineering'),
(2, 'Database Management Systems'),
(3, 'Artificial Intelligence & Machine Learning'),
(4, 'Software Engineering & Architecture'),
(5, 'Mathematics & Discrete Structures'),
(6, 'Data Structures & Algorithms'),
(7, 'Cybersecurity & Cryptography'),
(8, 'Operating Systems & Networking'),
(9, 'Indian Literature & Humanities'),
(10, 'Business & Economics');

-- ---------------------------------------------------------------------
-- 3. Insert AUTHOR Records (16 Authors)
-- Prominent Indian academicians, authors, and global computer scientists
-- ---------------------------------------------------------------------
INSERT INTO AUTHOR (Author_ID, Name, Country) VALUES
(1, 'Dr. A.P.J. Abdul Kalam', 'India'),
(2, 'S. Sudarshan', 'India'),
(3, 'Abraham Silberschatz', 'United States'),
(4, 'Henry F. Korth', 'United States'),
(5, 'E. Balagurusamy', 'India'),
(6, 'Seymour Lipschutz', 'United States'),
(7, 'B.S. Grewal', 'India'),
(8, 'Amartya Sen', 'India'),
(9, 'Arundhati Roy', 'India'),
(10, 'R.K. Narayan', 'India'),
(11, 'Stuart Russell', 'United Kingdom'),
(12, 'Peter Norvig', 'United States'),
(13, 'Thomas H. Cormen', 'United States'),
(14, 'Narasimha Karumanchi', 'India'),
(15, 'Andrew S. Tanenbaum', 'Netherlands'),
(16, 'Behrouz A. Forouzan', 'United States');

-- ---------------------------------------------------------------------
-- 4. Insert BOOK Records (26 Books)
-- Varied prices in INR (₹250 - ₹1499), publication years, and total copies.
-- Integrity Constraint Note:
-- Available_Copies = Total_Copies - Active_Loans_Count.
-- Active Loans:
-- Book 1 has 1 active loan -> (6 total - 1 active = 5 available)
-- Book 2 has 2 active loans -> (8 total - 2 active = 6 available)
-- Book 3 has 2 active loans -> (7 total - 2 active = 5 available)
-- Book 4 has 1 active loan -> (6 total - 1 active = 5 available)
-- Book 5 has 1 active loan -> (5 total - 1 active = 4 available)
-- Book 6 has 1 active loan -> (6 total - 1 active = 5 available)
-- Book 7 has 1 active loan -> (5 total - 1 active = 4 available)
-- Book 8 has 1 active loan -> (4 total - 1 active = 3 available)
-- Book 9 has 1 active loan -> (5 total - 1 active = 4 available)
-- Book 10 has 1 active loan -> (4 total - 1 active = 3 available)
-- Books 11-26 have 0 active loans -> Available_Copies = Total_Copies.
-- ---------------------------------------------------------------------
INSERT INTO BOOK (Book_ID, ISBN, Title, Publisher_ID, Category_ID, Price, Total_Copies, Available_Copies, Publication_Year) VALUES
(1, '978-8173711466', 'Wings of Fire: An Autobiography', 9, 9, 350.00, 6, 5, 1999),
(2, '978-9353166304', 'Database System Concepts (Indian Edition)', 1, 2, 895.00, 8, 6, 2020),
(3, '978-9389588545', 'Data Structures and Algorithms Made Easy', 4, 6, 650.00, 7, 5, 2021),
(4, '978-9352837335', 'Higher Engineering Mathematics', 5, 5, 750.00, 6, 5, 2018),
(5, '978-0136042594', 'Artificial Intelligence: A Modern Approach', 3, 3, 1150.00, 5, 4, 2020),
(6, '978-9389328523', 'Programming in ANSI C (8th Edition)', 1, 1, 475.00, 6, 5, 2019),
(7, '978-0262033848', 'Introduction to Algorithms (CLRS)', 4, 6, 1299.00, 5, 4, 2015),
(8, '978-0133594140', 'Operating Systems: Design and Implementation', 3, 8, 825.00, 4, 3, 2015),
(9, '978-9332901537', 'Data Communications and Networking', 1, 8, 795.00, 5, 4, 2017),
(10, '978-0143422976', 'The Argumentative Indian', 9, 10, 499.00, 4, 3, 2005),
(11, '978-0143028574', 'Malgudi Days', 7, 9, 299.00, 5, 5, 1982),
(12, '978-0143454793', 'The God of Small Things', 9, 9, 399.00, 4, 4, 1997),
(13, '978-9387471207', 'Object-Oriented Programming with C++', 1, 1, 525.00, 6, 6, 2020),
(14, '978-8120340077', 'Discrete Mathematics (Schaum\'s Outlines)', 4, 5, 450.00, 5, 5, 2017),
(15, '978-9386758651', 'Ignited Minds: Unleashing the Power Within India', 9, 9, 275.00, 6, 6, 2002),
(16, '978-9351343202', 'Cryptography and Network Security: Principles and Practice', 1, 7, 725.00, 4, 4, 2018),
(17, '978-9332518773', 'Computer Networks (5th Indian Edition)', 3, 8, 860.00, 5, 5, 2013),
(18, '978-8126568284', 'Software Engineering: A Practitioner\'s Approach', 10, 4, 920.00, 4, 4, 2019),
(19, '978-9352865215', 'India Positive: New Essays and Selected Columns', 7, 9, 250.00, 4, 4, 2019),
(20, '978-8179921623', 'The Monk Who Sold His Ferrari (Indian Edition)', 8, 10, 320.00, 5, 5, 2003),
(21, '978-0198083849', 'An Uncertain Glory: India and its Contradictions', 2, 10, 575.00, 3, 3, 2013),
(22, '978-9386551870', 'Cloud Computing: Principles and Paradigms', 10, 1, 780.00, 3, 3, 2018),
(23, '978-9353062088', 'Machine Learning Using Python', 5, 3, 620.00, 5, 5, 2021),
(24, '978-8120352865', 'Foundations of Cryptography and Data Security', 4, 7, 850.00, 3, 3, 2016),
(25, '978-9332570498', 'Modern Operating Systems (4th Edition)', 3, 8, 895.00, 4, 4, 2016),
(26, '978-0131103627', 'The Art of Computer Programming, Vol 1', 3, 1, 1499.00, 3, 3, 2011);

-- ---------------------------------------------------------------------
-- 5. Insert BOOK_AUTHOR Records (Many-to-Many Relationships)
-- Demonstrates multi-author textbooks (e.g., Book 2 with 3 authors,
-- Book 5 with 2 authors) for relational join and aggregation tests.
-- ---------------------------------------------------------------------
INSERT INTO BOOK_AUTHOR (Book_ID, Author_ID) VALUES
(1, 1),   -- Wings of Fire -> Dr. A.P.J. Abdul Kalam
(2, 2),   -- Database System Concepts -> S. Sudarshan
(2, 3),   -- Database System Concepts -> Abraham Silberschatz
(2, 4),   -- Database System Concepts -> Henry F. Korth
(3, 14),  -- Data Structures and Algorithms -> Narasimha Karumanchi
(4, 7),   -- Higher Engineering Mathematics -> B.S. Grewal
(5, 11),  -- Artificial Intelligence -> Stuart Russell
(5, 12),  -- Artificial Intelligence -> Peter Norvig
(6, 5),   -- ANSI C -> E. Balagurusamy
(7, 13),  -- Introduction to Algorithms -> Thomas H. Cormen
(8, 15),  -- Operating Systems -> Andrew S. Tanenbaum
(9, 16),  -- Data Communications -> Behrouz A. Forouzan
(10, 8),  -- The Argumentative Indian -> Amartya Sen
(11, 10), -- Malgudi Days -> R.K. Narayan
(12, 9),  -- The God of Small Things -> Arundhati Roy
(13, 5),  -- OOP with C++ -> E. Balagurusamy
(14, 6),  -- Discrete Mathematics -> Seymour Lipschutz
(15, 1),  -- Ignited Minds -> Dr. A.P.J. Abdul Kalam
(16, 16), -- Cryptography and Network Security -> Behrouz A. Forouzan
(17, 15), -- Computer Networks -> Andrew S. Tanenbaum
(18, 2),  -- Software Engineering -> S. Sudarshan
(19, 10), -- India Positive -> R.K. Narayan
(20, 8),  -- The Monk Who Sold His Ferrari -> Amartya Sen
(21, 8),  -- An Uncertain Glory -> Amartya Sen
(22, 2),  -- Cloud Computing -> S. Sudarshan
(23, 5),  -- Machine Learning Using Python -> E. Balagurusamy
(24, 6),  -- Foundations of Cryptography -> Seymour Lipschutz
(25, 15), -- Modern Operating Systems -> Andrew S. Tanenbaum
(26, 13); -- The Art of Computer Programming -> Thomas H. Cormen

-- ---------------------------------------------------------------------
-- 6. Insert MEMBER Records (16 Members)
-- Mix of Active and Inactive members with realistic Indian names.
-- Members 14, 15, and 16 have never borrowed books (for demonstration of NOT EXISTS).
-- ---------------------------------------------------------------------
INSERT INTO MEMBER (Member_ID, Name, Email, Phone, Join_Date, Status) VALUES
(1, 'Aarav Sharma', 'aarav.sharma@college.edu', '98201-11223', '2023-01-10', 'Active'),
(2, 'Priya Patel', 'priya.patel@college.edu', '98202-22334', '2023-01-15', 'Active'),
(3, 'Rohan Verma', 'rohan.verma@college.edu', '98203-33445', '2023-02-01', 'Active'),
(4, 'Ananya Iyer', 'ananya.iyer@college.edu', '98204-44556', '2023-02-12', 'Active'),
(5, 'Vikram Malhotra', 'vikram.m@college.edu', '98205-55667', '2023-03-05', 'Active'),
(6, 'Sneha Kulkarni', 'sneha.k@college.edu', '98206-66778', '2023-03-20', 'Active'),
(7, 'Arjun Nair', 'arjun.nair@college.edu', '98207-77889', '2023-04-10', 'Active'),
(8, 'Diya Sengupta', 'diya.s@college.edu', '98208-88990', '2023-04-25', 'Active'),
(9, 'Kavita Joshi', 'kavita.joshi@college.edu', '98209-99001', '2023-05-15', 'Active'),
(10, 'Aditya Deshmukh', 'aditya.d@college.edu', '98210-10112', '2023-06-01', 'Active'),
(11, 'Meera Nambiar', 'meera.n@college.edu', '98211-12123', '2023-06-18', 'Active'),
(12, 'Rahul Banerjee', 'rahul.b@college.edu', '98212-23234', '2023-07-05', 'Inactive'),
(13, 'Pooja Reddy', 'pooja.reddy@college.edu', '98213-34345', '2023-08-14', 'Inactive'),
(14, 'Siddharth Jain', 'siddharth.j@college.edu', '98214-45456', '2023-09-01', 'Active'),
(15, 'Tanvi Chawla', 'tanvi.c@college.edu', '98215-56567', '2023-10-01', 'Active'),
(16, 'Rajesh Gupta', 'rajesh.gupta@college.edu', '98216-67678', '2023-11-01', 'Inactive');

-- ---------------------------------------------------------------------
-- 7. Insert LIBRARIAN Records (2 Staff Accounts)
-- Default login password for staff is 'Admin@123'
-- ---------------------------------------------------------------------
INSERT INTO LIBRARIAN (Librarian_ID, Name, Email, Password_Hash) VALUES
(1, 'Admin Librarian', 'admin@library.com', 'scrypt:32768:8:1$yoq0KrQzaIUXlM0n$95ffc646d14ce83bf64640126e9f132fcf4baf711e30159d8b5956c2d1790aba1ed5d4b3d9a98faf2a70850671745c2829a17da2b02785b3a8b4bcdbb148b5b9'),
(2, 'Sunita Rao', 'sunita.rao@library.com', 'scrypt:32768:8:1$yoq0KrQzaIUXlM0n$95ffc646d14ce83bf64640126e9f132fcf4baf711e30159d8b5956c2d1790aba1ed5d4b3d9a98faf2a70850671745c2829a17da2b02785b3a8b4bcdbb148b5b9');

-- ---------------------------------------------------------------------
-- 8. Insert BOOK_LOAN Records (24 Borrowing Records)
-- Divided into 4 realistic operational cohorts:
-- A. Past loans returned on time (Fine = 0.00)
-- B. Past loans returned late with paid fines (Fine rate ₹5.00/day)
-- C. Active loans currently on schedule (Return_Date IS NULL, Due_Date in future)
-- D. Active loans currently OVERDUE (Return_Date IS NULL, Due_Date in past)
-- ---------------------------------------------------------------------
INSERT INTO BOOK_LOAN (Loan_ID, Book_ID, Member_ID, Issued_By, Issue_Date, Due_Date, Return_Date, Fine_Amount) VALUES
-- Cohort A: Past loans returned on time (No fines)
(1, 11, 1, 1, '2024-01-10', '2024-01-24', '2024-01-22', 0.00),
(2, 12, 2, 1, '2024-01-15', '2024-01-29', '2024-01-28', 0.00),
(3, 13, 3, 2, '2024-02-01', '2024-02-15', '2024-02-14', 0.00),
(4, 14, 4, 1, '2024-02-05', '2024-02-19', '2024-02-17', 0.00),
(5, 15, 5, 2, '2024-02-10', '2024-02-24', '2024-02-23', 0.00),
(6, 16, 6, 1, '2024-03-01', '2024-03-15', '2024-03-15', 0.00),

-- Cohort B: Past loans returned late with recorded penalties (Days Late * ₹5.00)
(7, 17, 7, 2, '2024-03-05', '2024-03-19', '2024-03-24', 25.00),  -- 5 days late
(8, 18, 8, 1, '2024-03-10', '2024-03-24', '2024-03-30', 30.00),  -- 6 days late
(9, 19, 9, 2, '2024-04-01', '2024-04-15', '2024-04-23', 40.00),  -- 8 days late
(10, 20, 10, 1, '2024-04-05', '2024-04-19', '2024-04-23', 20.00), -- 4 days late
(11, 21, 11, 2, '2024-04-10', '2024-04-24', '2024-05-01', 35.00), -- 7 days late
(12, 22, 12, 1, '2024-05-01', '2024-05-15', '2024-05-20', 25.00), -- 5 days late

-- Cohort C: Active loans currently within schedule (Return_Date IS NULL)
(13, 1, 1, 1, '2026-10-05', '2026-10-19', NULL, 0.00),
(14, 2, 2, 1, '2026-10-06', '2026-10-20', NULL, 0.00),
(15, 3, 3, 2, '2026-10-08', '2026-10-22', NULL, 0.00),
(16, 4, 4, 1, '2026-10-09', '2026-10-23', NULL, 0.00),
(17, 5, 5, 2, '2026-10-10', '2026-10-24', NULL, 0.00),
(18, 6, 6, 1, '2026-10-11', '2026-10-25', NULL, 0.00),

-- Cohort D: Active loans currently OVERDUE (Return_Date IS NULL, Due_Date < CURRENT_DATE)
(19, 2, 7, 2, '2026-09-01', '2026-09-15', NULL, 0.00),  -- Overdue
(20, 3, 8, 1, '2026-09-05', '2026-09-19', NULL, 0.00),  -- Overdue
(21, 7, 9, 2, '2026-09-10', '2026-09-24', NULL, 0.00),  -- Overdue
(22, 8, 10, 1, '2026-09-15', '2026-09-29', NULL, 0.00), -- Overdue
(23, 9, 11, 2, '2026-09-20', '2026-10-04', NULL, 0.00), -- Overdue
(24, 10, 12, 1, '2026-09-25', '2026-10-09', NULL, 0.00); -- Overdue
