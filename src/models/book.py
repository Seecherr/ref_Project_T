"""Book and BookItem domain models for the Library Management System."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


class BookStatus(enum.Enum):
    """Status of a physical book item in the library."""

    AVAILABLE = "available"
    LOANED = "loaned"
    RESERVED = "reserved"
    LOST = "lost"


@dataclass
class BookItem:
    """Represents a physical copy of a book in the library.

    Each Book can have multiple BookItems, each identified by a unique barcode.
    """

    barcode: str
    book_isbn: str
    status: BookStatus = BookStatus.AVAILABLE
    rack_number: str = ""
    due_date: Optional[date] = None

    def is_available(self) -> bool:
        """Check if this book item is available for borrowing."""
        return self.status == BookStatus.AVAILABLE

    def mark_loaned(self, due: date) -> None:
        """Mark this book item as loaned with a due date."""
        self.status = BookStatus.LOANED
        self.due_date = due

    def mark_available(self) -> None:
        """Mark this book item as available."""
        self.status = BookStatus.AVAILABLE
        self.due_date = None

    def mark_reserved(self) -> None:
        """Mark this book item as reserved."""
        self.status = BookStatus.RESERVED

    def mark_lost(self) -> None:
        """Mark this book item as lost."""
        self.status = BookStatus.LOST
        self.due_date = None


@dataclass
class Book:
    """Represents a book in the library catalog.

    A Book is a bibliographic record identified by ISBN.
    Physical copies are represented by BookItem instances.
    """

    isbn: str
    title: str
    author: str
    subject: str = ""
    year: int = 0
    items: list[BookItem] = field(default_factory=list)

    def add_item(self, item: BookItem) -> None:
        """Add a physical copy to this book."""
        self.items.append(item)

    def remove_item(self, barcode: str) -> Optional[BookItem]:
        """Remove a physical copy by barcode. Returns the removed item or None."""
        for i, item in enumerate(self.items):
            if item.barcode == barcode:
                return self.items.pop(i)
        return None

    def get_available_items(self) -> list[BookItem]:
        """Return all available copies of this book."""
        return [item for item in self.items if item.is_available()]

    def has_available_copy(self) -> bool:
        """Check if at least one copy is available."""
        return any(item.is_available() for item in self.items)

    def total_copies(self) -> int:
        """Return total number of physical copies."""
        return len(self.items)
