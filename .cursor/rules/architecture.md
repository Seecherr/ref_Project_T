# Architecture — Library Management System

## Overview

This project implements an **In-Memory Library Management System** using a layered architecture with no external databases or APIs.

## Layered Architecture

```
┌─────────────────────────────────┐
│         Services Layer          │  ← Business logic (CatalogService, LoanService, etc.)
│   Uses Strategy & Observer      │
├─────────────────────────────────┤
│         Storage Layer           │  ← Abstract repositories + In-Memory implementations
│   (Dependency Inversion)        │
├─────────────────────────────────┤
│         Models Layer            │  ← Domain entities (Book, Member, Loan, Fine, etc.)
│   (Dataclasses + Enums)         │
└─────────────────────────────────┘
```

## Key Design Decisions

### In-Memory Storage
- All data is stored in Python dictionaries keyed by entity IDs
- Repository interfaces (ABCs) define the contract
- Concrete implementations (`InMemory*Repository`) fulfill the contract
- This enables easy replacement with real databases in the future

### Dependency Injection
- Services receive their dependencies (repositories, strategies, event managers) through constructor injection
- No hardcoded dependencies on concrete implementations
- This follows the Dependency Inversion Principle (DIP)

### GoF Design Patterns

#### Strategy Pattern (Fine Calculation)
- `FineCalculationStrategy` — abstract interface
- `StandardFineStrategy` — fixed daily rate ($0.50/day)
- `ProgressiveFineStrategy` — tiered rates increasing with duration
- `NoFineStrategy` — zero fines for special items
- Injected into `FineService` via constructor, swappable at runtime

#### Observer Pattern (Event Notifications)
- `EventManager` — central event bus
- `EventListener` — abstract listener interface
- `BookAvailabilityListener` — notifies members about book availability
- Events: BOOK_RETURNED, MEMBER_BLOCKED, RESERVATION_FULFILLED, etc.
- Used by `LoanService` (publisher) and `NotificationService` (subscriber)

## SOLID Principles

| Principle | Implementation |
|---|---|
| **S**ingle Responsibility | Each service handles one domain area |
| **O**pen/Closed | New fine strategies without modifying existing code |
| **L**iskov Substitution | Reader/Librarian are substitutable for Member |
| **I**nterface Segregation | Small focused repository interfaces |
| **D**ependency Inversion | Services depend on abstract repositories |
