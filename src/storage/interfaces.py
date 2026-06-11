"""Abstract repository interfaces for the Library Management System.

These ABCs define the contract for data access operations.
Concrete implementations (e.g., in-memory) must fulfill these
interfaces, enabling the Dependency Inversion Principle (DIP).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from src.models.book import Book, BookItem
from src.models.fine import Fine
from src.models.loan import Loan
from src.models.member import Member
from src.models.notification import Notification
from src.models.reservation import Reservation


class BookRepository(ABC):
    """Abstract repository for Book entities."""

    @abstractmethod
    def add(self, book: Book) -> None:
        """Add a book to the repository."""
        ...  # pragma: no cover

    @abstractmethod
    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        """Get a book by its ISBN."""
        ...  # pragma: no cover

    @abstractmethod
    def get_all(self) -> list[Book]:
        """Get all books."""
        ...  # pragma: no cover

    @abstractmethod
    def search(self, query: str) -> list[Book]:
        """Search books by title, author, or subject."""
        ...  # pragma: no cover

    @abstractmethod
    def update(self, book: Book) -> None:
        """Update a book's information."""
        ...  # pragma: no cover

    @abstractmethod
    def delete(self, isbn: str) -> bool:
        """Delete a book by ISBN. Returns True if deleted."""
        ...  # pragma: no cover


class BookItemRepository(ABC):
    """Abstract repository for BookItem entities."""

    @abstractmethod
    def add(self, item: BookItem) -> None:
        """Add a book item to the repository."""
        ...  # pragma: no cover

    @abstractmethod
    def get_by_barcode(self, barcode: str) -> Optional[BookItem]:
        """Get a book item by its barcode."""
        ...  # pragma: no cover

    @abstractmethod
    def get_by_isbn(self, isbn: str) -> list[BookItem]:
        """Get all book items for a given ISBN."""
        ...  # pragma: no cover

    @abstractmethod
    def get_available_by_isbn(self, isbn: str) -> list[BookItem]:
        """Get available book items for a given ISBN."""
        ...  # pragma: no cover

    @abstractmethod
    def update(self, item: BookItem) -> None:
        """Update a book item."""
        ...  # pragma: no cover

    @abstractmethod
    def delete(self, barcode: str) -> bool:
        """Delete a book item by barcode. Returns True if deleted."""
        ...  # pragma: no cover

    @abstractmethod
    def get_all(self) -> list[BookItem]:
        """Get all book items."""
        ...  # pragma: no cover


class MemberRepository(ABC):
    """Abstract repository for Member entities."""

    @abstractmethod
    def add(self, member: Member) -> None:
        """Add a member to the repository."""
        ...  # pragma: no cover

    @abstractmethod
    def get_by_id(self, member_id: str) -> Optional[Member]:
        """Get a member by ID."""
        ...  # pragma: no cover

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Member]:
        """Get a member by email."""
        ...  # pragma: no cover

    @abstractmethod
    def get_all(self) -> list[Member]:
        """Get all members."""
        ...  # pragma: no cover

    @abstractmethod
    def update(self, member: Member) -> None:
        """Update a member's information."""
        ...  # pragma: no cover

    @abstractmethod
    def delete(self, member_id: str) -> bool:
        """Delete a member by ID. Returns True if deleted."""
        ...  # pragma: no cover


class LoanRepository(ABC):
    """Abstract repository for Loan entities."""

    @abstractmethod
    def add(self, loan: Loan) -> None:
        """Add a loan to the repository."""
        ...  # pragma: no cover

    @abstractmethod
    def get_by_id(self, loan_id: str) -> Optional[Loan]:
        """Get a loan by ID."""
        ...  # pragma: no cover

    @abstractmethod
    def get_active_by_member(self, member_id: str) -> list[Loan]:
        """Get all active (not returned) loans for a member."""
        ...  # pragma: no cover

    @abstractmethod
    def get_by_book_item(self, barcode: str) -> list[Loan]:
        """Get all loans for a specific book item."""
        ...  # pragma: no cover

    @abstractmethod
    def get_active_by_book_item(self, barcode: str) -> Optional[Loan]:
        """Get the active loan for a specific book item, if any."""
        ...  # pragma: no cover

    @abstractmethod
    def get_all(self) -> list[Loan]:
        """Get all loans."""
        ...  # pragma: no cover

    @abstractmethod
    def update(self, loan: Loan) -> None:
        """Update a loan."""
        ...  # pragma: no cover


class FineRepository(ABC):
    """Abstract repository for Fine entities."""

    @abstractmethod
    def add(self, fine: Fine) -> None:
        """Add a fine to the repository."""
        ...  # pragma: no cover

    @abstractmethod
    def get_by_id(self, fine_id: str) -> Optional[Fine]:
        """Get a fine by ID."""
        ...  # pragma: no cover

    @abstractmethod
    def get_unpaid_by_member(self, member_id: str) -> list[Fine]:
        """Get all unpaid fines for a member."""
        ...  # pragma: no cover

    @abstractmethod
    def get_by_loan(self, loan_id: str) -> Optional[Fine]:
        """Get the fine associated with a specific loan."""
        ...  # pragma: no cover

    @abstractmethod
    def get_all(self) -> list[Fine]:
        """Get all fines."""
        ...  # pragma: no cover

    @abstractmethod
    def update(self, fine: Fine) -> None:
        """Update a fine."""
        ...  # pragma: no cover


class ReservationRepository(ABC):
    """Abstract repository for Reservation entities."""

    @abstractmethod
    def add(self, reservation: Reservation) -> None:
        """Add a reservation to the repository."""
        ...  # pragma: no cover

    @abstractmethod
    def get_by_id(self, reservation_id: str) -> Optional[Reservation]:
        """Get a reservation by ID."""
        ...  # pragma: no cover

    @abstractmethod
    def get_waiting_by_isbn(self, book_isbn: str) -> list[Reservation]:
        """Get all waiting reservations for a book, ordered by creation date."""
        ...  # pragma: no cover

    @abstractmethod
    def get_by_member(self, member_id: str) -> list[Reservation]:
        """Get all reservations for a member."""
        ...  # pragma: no cover

    @abstractmethod
    def get_all(self) -> list[Reservation]:
        """Get all reservations."""
        ...  # pragma: no cover

    @abstractmethod
    def update(self, reservation: Reservation) -> None:
        """Update a reservation."""
        ...  # pragma: no cover


class NotificationRepository(ABC):
    """Abstract repository for Notification entities."""

    @abstractmethod
    def add(self, notification: Notification) -> None:
        """Add a notification to the repository."""
        ...  # pragma: no cover

    @abstractmethod
    def get_by_member(self, member_id: str) -> list[Notification]:
        """Get all notifications for a member."""
        ...  # pragma: no cover

    @abstractmethod
    def get_unread_by_member(self, member_id: str) -> list[Notification]:
        """Get all unread notifications for a member."""
        ...  # pragma: no cover

    @abstractmethod
    def get_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get a notification by ID."""
        ...  # pragma: no cover

    @abstractmethod
    def update(self, notification: Notification) -> None:
        """Update a notification."""
        ...  # pragma: no cover

    @abstractmethod
    def get_all(self) -> list[Notification]:
        """Get all notifications."""
        ...  # pragma: no cover
