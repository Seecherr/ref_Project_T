# Use Case Diagram — Library Management System

```mermaid
graph LR
    subgraph Actors
        R["📖 Reader"]
        L["👤 Librarian"]
    end

    subgraph "Library Management System"
        UC1["Borrow Book"]
        UC2["Return Book"]
        UC3["Search Catalog"]
        UC4["Reserve Book"]
        UC5["Pay Fine"]
        UC6["Receive Notification"]
        UC7["Block/Unblock Reader"]
        UC8["Manage Catalog"]
        UC9["View Loan History"]
    end

    R --> UC1
    R --> UC2
    R --> UC3
    R --> UC4
    R --> UC5
    R --> UC6
    R --> UC9

    L --> UC1
    L --> UC2
    L --> UC3
    L --> UC7
    L --> UC8
    L --> UC9

    UC1 -.->|"includes"| UC3
    UC2 -.->|"extends"| UC5
    UC4 -.->|"extends"| UC6
```

## Use Case Descriptions

| # | Use Case | Primary Actor | Description |
|---|----------|--------------|-------------|
| UC1 | Borrow Book | Reader/Librarian | Reader requests a book; system validates membership, limits, availability |
| UC2 | Return Book | Reader/Librarian | Book is returned; system calculates fine if overdue |
| UC3 | Search Catalog | Reader/Librarian | Search by title, author, ISBN, or subject |
| UC4 | Reserve Book | Reader | Place reservation on unavailable book (FIFO priority queue) |
| UC5 | Pay Fine | Reader | Pay outstanding fine; auto-unblock if balance cleared |
| UC6 | Receive Notification | Reader | Get notified when reserved book becomes available |
| UC7 | Block/Unblock Reader | Librarian | Block reader with high unpaid fines; unblock after payment |
| UC8 | Manage Catalog | Librarian | Add/update/remove books and physical copies |
| UC9 | View Loan History | Reader/Librarian | View active and past loans |
