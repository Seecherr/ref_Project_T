# Domain Model — Library Management System

```mermaid
erDiagram
    BOOK ||--o{ BOOK_ITEM : "has copies"
    MEMBER ||--o{ LOAN : "borrows"
    BOOK_ITEM ||--o{ LOAN : "is loaned via"
    LOAN ||--o| FINE : "may have"
    MEMBER ||--o{ FINE : "owes"
    MEMBER ||--o{ RESERVATION : "places"
    BOOK ||--o{ RESERVATION : "reserved for"
    MEMBER ||--o{ NOTIFICATION : "receives"

    BOOK {
        string isbn PK
        string title
        string author
        string subject
        int year
    }

    BOOK_ITEM {
        string barcode PK
        string book_isbn FK
        enum status
        string rack_number
        date due_date
    }

    MEMBER {
        string member_id PK
        string name
        string email
        enum status
        datetime created_at
    }

    LOAN {
        string loan_id PK
        string member_id FK
        string book_item_barcode FK
        date issue_date
        date due_date
        date return_date
    }

    FINE {
        string fine_id PK
        string loan_id FK
        string member_id FK
        decimal amount
        decimal paid
        datetime created_at
    }

    RESERVATION {
        string reservation_id PK
        string member_id FK
        string book_isbn FK
        datetime created_at
        enum status
    }

    NOTIFICATION {
        string notification_id PK
        string member_id FK
        string message
        datetime created_at
        boolean is_read
    }
```

## Entity Relationships

| Relationship | Type | Description |
|---|---|---|
| Book → BookItem | 1:N | One catalog record has multiple physical copies |
| Member → Loan | 1:N | A member can have multiple active loans (max 5) |
| BookItem → Loan | 1:N | A book item can be loaned multiple times over its lifetime |
| Loan → Fine | 1:0..1 | An overdue loan may generate one fine |
| Member → Reservation | 1:N | A member can have multiple reservations (max 5) |
| Member → Notification | 1:N | A member receives notifications about events |
