# Relational Schema & Normalization Analysis

## 1. Formal Relational Schema Notation

The relational schema for **LibraryDB** is defined below. Primary keys are marked with `(PK)`, foreign keys are marked with `(FK)`, and unique candidate keys are marked with `(UK)`.

```
PUBLISHER (
    Publisher_ID (PK),
    Name,
    Address
)

CATEGORY (
    Category_ID (PK),
    Category_Name (UK)
)

AUTHOR (
    Author_ID (PK),
    Name,
    Country
)

BOOK (
    Book_ID (PK),
    ISBN (UK),
    Title,
    Publisher_ID (FK -> PUBLISHER.Publisher_ID),
    Category_ID (FK -> CATEGORY.Category_ID),
    Price,
    Total_Copies,
    Available_Copies,
    Publication_Year
)

BOOK_AUTHOR (
    Book_ID (PK, FK -> BOOK.Book_ID),
    Author_ID (PK, FK -> AUTHOR.Author_ID)
)

MEMBER (
    Member_ID (PK),
    Name,
    Email (UK),
    Phone,
    Join_Date,
    Status
)

LIBRARIAN (
    Librarian_ID (PK),
    Name,
    Email (UK),
    Password_Hash
)

BOOK_LOAN (
    Loan_ID (PK),
    Book_ID (FK -> BOOK.Book_ID),
    Member_ID (FK -> MEMBER.Member_ID),
    Issued_By (FK -> LIBRARIAN.Librarian_ID),
    Issue_Date,
    Due_Date,
    Return_Date,
    Fine_Amount
)
```

---

## 2. Functional Dependencies (FDs)

### 2.1 PUBLISHER
- $Publisher\_ID \rightarrow Name, Address$
- Candidate Key: $\{Publisher\_ID\}$

### 2.2 CATEGORY
- $Category\_ID \rightarrow Category\_Name$
- $Category\_Name \rightarrow Category\_ID$
- Candidate Keys: $\{Category\_ID\}$, $\{Category\_Name\}$

### 2.3 AUTHOR
- $Author\_ID \rightarrow Name, Country$
- Candidate Key: $\{Author\_ID\}$

### 2.4 BOOK
- $Book\_ID \rightarrow ISBN, Title, Publisher\_ID, Category\_ID, Price, Total\_Copies, Available\_Copies, Publication\_Year$
- $ISBN \rightarrow Book\_ID, Title, Publisher\_ID, Category\_ID, Price, Total\_Copies, Available\_Copies, Publication\_Year$
- Candidate Keys: $\{Book\_ID\}$, $\{ISBN\}$

### 2.5 BOOK_AUTHOR
- $\{Book\_ID, Author\_ID\}$ is all-key (no non-prime attributes).
- Candidate Key: $\{Book\_ID, Author\_ID\}$

### 2.6 MEMBER
- $Member\_ID \rightarrow Name, Email, Phone, Join_Date, Status$
- $Email \rightarrow Member\_ID, Name, Phone, Join_Date, Status$
- Candidate Keys: $\{Member\_ID\}$, $\{Email\}$

### 2.7 LIBRARIAN
- $Librarian\_ID \rightarrow Name, Email, Password\_Hash$
- $Email \rightarrow Librarian\_ID, Name, Password\_Hash$
- Candidate Keys: $\{Librarian\_ID\}$, $\{Email\}$

### 2.8 BOOK_LOAN
- $Loan\_ID \rightarrow Book\_ID, Member\_ID, Issued\_By, Issue\_Date, Due\_Date, Return\_Date, Fine\_Amount$
- Candidate Key: $\{Loan\_ID\}$

---

## 3. Normalization Analysis (1NF, 2NF, 3NF)

### 3.1 First Normal Form (1NF)
**Definition**: A relation is in 1NF if and only if all attribute values are atomic (indivisible) and there are no repeating groups or multivalued columns.

**Compliance in LibraryDB**:
- In naive designs, book authors are often stored as a comma-separated string (e.g., `"Knuth, Cormen"`), or loans store multiple book IDs in one row.
- In `LibraryDB`, multi-valued authors are decomposed into a separate junction relation `BOOK_AUTHOR`. Every cell contains exactly one scalar value (e.g. single integer, string, or date).
- Every table has an explicitly defined primary key.
- $\therefore$ **All tables satisfy 1NF.**

### 3.2 Second Normal Form (2NF)
**Definition**: A relation is in 2NF if and only if it is in 1NF and no non-prime attribute is partially dependent on any candidate key (i.e. no partial functional dependencies $X \rightarrow Y$ where $X$ is a strict subset of a composite candidate key).

**Compliance in LibraryDB**:
- The only table with a composite primary key is `BOOK_AUTHOR` $(\{Book\_ID, Author\_ID\})$.
- `BOOK_AUTHOR` has no non-prime attributes; all its attributes are prime. Hence, no partial functional dependency can exist.
- All other tables (`BOOK`, `MEMBER`, `BOOK_LOAN`, etc.) have single-attribute primary keys (`Book_ID`, `Member_ID`, `Loan_ID`).
- By mathematical definition, partial dependency is impossible when the candidate key consists of a single attribute.
- $\therefore$ **All tables satisfy 2NF.**

### 3.3 Third Normal Form (3NF)
**Definition**: A relation is in 3NF if and only if it is in 2NF and there are no transitive functional dependencies of non-prime attributes on the primary key (i.e. for every non-trivial functional dependency $X \rightarrow Y$, either $X$ is a superkey, or $Y$ is a prime attribute).

**Compliance in LibraryDB**:
- **Publisher & Category separation**: If publisher address or category details were stored in the `BOOK` table:
  $Book\_ID \rightarrow Publisher\_ID$ and $Publisher\_ID \rightarrow Address$, leading to a transitive dependency $Book\_ID \rightarrow Address$.
  In `LibraryDB`, `PUBLISHER` and `CATEGORY` are distinct relations, eliminating transitive dependencies in `BOOK`.
- **Borrower separation**: If member name or email were stored in `BOOK_LOAN`:
  $Loan\_ID \rightarrow Member\_ID$ and $Member\_ID \rightarrow Email$, leading to a transitive dependency $Loan\_ID \rightarrow Email$.
  In `LibraryDB`, member attributes reside exclusively in `MEMBER`, with only the surrogate key `Member_ID` stored in `BOOK_LOAN`.
- In every relation, all determinants ($Publisher\_ID$, $Category\_ID$, $Author\_ID$, $Book\_ID$, $Member\_ID$, $Librarian\_ID$, $Loan\_ID$) are candidate keys (superkeys).
- $\therefore$ **All tables satisfy 3NF (and BCNF).**

---

## 4. Elimination of Modification Anomalies

| Anomaly Type | Unnormalized Risk | Resolved In LibraryDB Schema |
| :--- | :--- | :--- |
| **Insertion Anomaly** | Cannot add a new author or publisher until they have published a book. | `AUTHOR` and `PUBLISHER` exist independently of `BOOK`. |
| **Deletion Anomaly** | Deleting the last copy of a book removes the author's and publisher's existence. | Deleting a record in `BOOK` removes `BOOK_AUTHOR` entries but preserves `AUTHOR` and `PUBLISHER`. |
| **Update Anomaly** | Updating a publisher's address requires updating thousands of book rows. | Address is updated in a single row in `PUBLISHER`. |
