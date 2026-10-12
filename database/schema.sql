-- =====================================================================
-- DATABASE SCHEMA DEFINITION FOR LIBRARY MANAGEMENT SYSTEM
-- Target RDBMS: MySQL 8.x
-- Database Name: LibraryDB
-- =====================================================================

DROP DATABASE IF EXISTS LibraryDB;
CREATE DATABASE LibraryDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE LibraryDB;

-- Disable foreign key checks while constructing tables
SET FOREIGN_KEY_CHECKS = 0;

-- ---------------------------------------------------------------------
-- Table 1: PUBLISHER
-- Stores information about book publishing houses.
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS PUBLISHER;
CREATE TABLE PUBLISHER (
    Publisher_ID INT AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Address VARCHAR(200),
    CONSTRAINT pk_publisher PRIMARY KEY (Publisher_ID)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table 2: CATEGORY
-- Classifies books into genres/subjects. Unique category names.
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS CATEGORY;
CREATE TABLE CATEGORY (
    Category_ID INT AUTO_INCREMENT,
    Category_Name VARCHAR(60) NOT NULL,
    CONSTRAINT pk_category PRIMARY KEY (Category_ID),
    CONSTRAINT uq_category_name UNIQUE (Category_Name)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table 3: AUTHOR
-- Stores details about book authors.
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS AUTHOR;
CREATE TABLE AUTHOR (
    Author_ID INT AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Country VARCHAR(60),
    CONSTRAINT pk_author PRIMARY KEY (Author_ID)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table 4: BOOK
-- Central book catalog entity with stock and pricing constraints.
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS BOOK;
CREATE TABLE BOOK (
    Book_ID INT AUTO_INCREMENT,
    ISBN VARCHAR(20) NOT NULL,
    Title VARCHAR(200) NOT NULL,
    Publisher_ID INT,
    Category_ID INT,
    Price DECIMAL(10,2) NOT NULL,
    Total_Copies INT NOT NULL,
    Available_Copies INT NOT NULL,
    Publication_Year INT,
    CONSTRAINT pk_book PRIMARY KEY (Book_ID),
    CONSTRAINT uq_book_isbn UNIQUE (ISBN),
    CONSTRAINT fk_book_publisher FOREIGN KEY (Publisher_ID) 
        REFERENCES PUBLISHER(Publisher_ID) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT fk_book_category FOREIGN KEY (Category_ID) 
        REFERENCES CATEGORY(Category_ID) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT chk_book_price CHECK (Price >= 0),
    CONSTRAINT chk_book_total_copies CHECK (Total_Copies >= 0),
    CONSTRAINT chk_book_available_copies CHECK (Available_Copies >= 0 AND Available_Copies <= Total_Copies)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table 5: BOOK_AUTHOR (Junction / Bridge Table)
-- Resolves the Many-to-Many relationship between BOOK and AUTHOR.
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS BOOK_AUTHOR;
CREATE TABLE BOOK_AUTHOR (
    Book_ID INT NOT NULL,
    Author_ID INT NOT NULL,
    CONSTRAINT pk_book_author PRIMARY KEY (Book_ID, Author_ID),
    CONSTRAINT fk_ba_book FOREIGN KEY (Book_ID) 
        REFERENCES BOOK(Book_ID) 
        ON UPDATE CASCADE 
        ON DELETE CASCADE,
    CONSTRAINT fk_ba_author FOREIGN KEY (Author_ID) 
        REFERENCES AUTHOR(Author_ID) 
        ON UPDATE CASCADE 
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table 6: MEMBER
-- Library registered patrons / students / faculty.
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS MEMBER;
CREATE TABLE MEMBER (
    Member_ID INT AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(120) NOT NULL,
    Phone VARCHAR(15),
    Join_Date DATE NOT NULL,
    Status VARCHAR(20) NOT NULL DEFAULT 'Active',
    CONSTRAINT pk_member PRIMARY KEY (Member_ID),
    CONSTRAINT uq_member_email UNIQUE (Email),
    CONSTRAINT chk_member_status CHECK (Status IN ('Active', 'Inactive'))
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table 7: LIBRARIAN
-- Staff accounts authorized to access the system and manage transactions.
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS LIBRARIAN;
CREATE TABLE LIBRARIAN (
    Librarian_ID INT AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(120) NOT NULL,
    Password_Hash VARCHAR(255) NOT NULL,
    CONSTRAINT pk_librarian PRIMARY KEY (Librarian_ID),
    CONSTRAINT uq_librarian_email UNIQUE (Email)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table 8: BOOK_LOAN
-- Tracks book borrowing transactions, due dates, returns, and fines.
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS BOOK_LOAN;
CREATE TABLE BOOK_LOAN (
    Loan_ID INT AUTO_INCREMENT,
    Book_ID INT NOT NULL,
    Member_ID INT NOT NULL,
    Issued_By INT,
    Issue_Date DATE NOT NULL,
    Due_Date DATE NOT NULL,
    Return_Date DATE NULL,
    Fine_Amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    CONSTRAINT pk_book_loan PRIMARY KEY (Loan_ID),
    CONSTRAINT fk_loan_book FOREIGN KEY (Book_ID) 
        REFERENCES BOOK(Book_ID) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT fk_loan_member FOREIGN KEY (Member_ID) 
        REFERENCES MEMBER(Member_ID) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT fk_loan_librarian FOREIGN KEY (Issued_By) 
        REFERENCES LIBRARIAN(Librarian_ID) 
        ON UPDATE CASCADE 
        ON DELETE SET NULL,
    CONSTRAINT chk_loan_due_date CHECK (Due_Date >= Issue_Date),
    CONSTRAINT chk_loan_fine CHECK (Fine_Amount >= 0)
) ENGINE=InnoDB;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- Create useful indexes for query performance
CREATE INDEX idx_book_title ON BOOK(Title);
CREATE INDEX idx_book_category ON BOOK(Category_ID);
CREATE INDEX idx_loan_active ON BOOK_LOAN(Return_Date);
CREATE INDEX idx_loan_due_date ON BOOK_LOAN(Due_Date);
