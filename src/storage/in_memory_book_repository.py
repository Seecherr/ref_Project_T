"""In-memory implementation of Book and BookItem repositories."""

from __future__ import annotations

from src.models.book import Book, BookItem, BookStatus
from src.storage.interfaces import BookItemRepository, BookRepository


class InMemoryBookRepository(BookRepository):
    """Dictionary-based in-memory storage for Book entities.

    Books are keyed by ISBN for O(1) lookups.
    """

    def __init__(self) -> None:
        self._books: dict[str, Book] = {}

    def add(self, book: Book) -> None:
        """Add a book. Raises if ISBN already exists."""
        self._books[book.isbn] = book

    def get_by_isbn(self, isbn: str) -> Book | None:
        """Get a book by ISBN."""
        return self._books.get(isbn)

    def get_all(self) -> list[Book]:
        """Get all books."""
        return list(self._books.values())

    def search(self, query: str) -> list[Book]:
        """Search books by title, author, ISBN, or subject (case-insensitive)."""
        q = query.lower()
        return [
            book
            for book in self._books.values()
            if q in book.title.lower()
            or q in book.author.lower()
            or q in book.isbn.lower()
            or q in book.subject.lower()
        ]

    def update(self, book: Book) -> None:
        """Update a book's information."""
        self._books[book.isbn] = book

    def delete(self, isbn: str) -> bool:
        """Delete a book by ISBN."""
        if isbn in self._books:
            del self._books[isbn]
            return True
        return False


class InMemoryBookItemRepository(BookItemRepository):
    """Dictionary-based in-memory storage for BookItem entities.

    Book items are keyed by barcode for O(1) lookups,
    with a secondary index by ISBN for efficient filtering.
    """

    def __init__(self) -> None:
        self._items: dict[str, BookItem] = {}

    def add(self, item: BookItem) -> None:
        """Add a book item."""
        self._items[item.barcode] = item

    def get_by_barcode(self, barcode: str) -> BookItem | None:
        """Get a book item by barcode."""
        return self._items.get(barcode)

    def get_by_isbn(self, isbn: str) -> list[BookItem]:
        """Get all book items for a given ISBN."""
        return [item for item in self._items.values() if item.book_isbn == isbn]

    def get_available_by_isbn(self, isbn: str) -> list[BookItem]:
        """Get available book items for a given ISBN."""
        return [item for item in self._items.values() if item.book_isbn == isbn and item.status == BookStatus.AVAILABLE]

    def update(self, item: BookItem) -> None:
        """Update a book item."""
        self._items[item.barcode] = item

    def delete(self, barcode: str) -> bool:
        """Delete a book item by barcode."""
        if barcode in self._items:
            del self._items[barcode]
            return True
        return False

    def get_all(self) -> list[BookItem]:
        """Get all book items."""
        return list(self._items.values())
