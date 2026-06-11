"""Catalog management service for the Library Management System.

Handles book and book item CRUD operations, catalog searches,
and availability checks.
"""

from __future__ import annotations

from typing import Optional

from src.models.book import Book, BookItem, BookStatus
from src.storage.interfaces import BookRepository, BookItemRepository
from src.utils.exceptions import (
    BookNotFoundError,
    DuplicateError,
    InvalidISBNError,
)
from src.utils.id_generator import generate_id
from src.utils.validators import validate_isbn, validate_non_empty_string


class CatalogService:
    """Service for managing the library catalog.

    Provides operations for adding, searching, updating, and removing
    books and their physical copies (BookItems).
    """

    def __init__(
        self,
        book_repo: BookRepository,
        book_item_repo: BookItemRepository,
    ) -> None:
        """Initialize with repository dependencies.

        Args:
            book_repo: Repository for Book entities.
            book_item_repo: Repository for BookItem entities.
        """
        self._book_repo = book_repo
        self._book_item_repo = book_item_repo

    def add_book(
        self,
        isbn: str,
        title: str,
        author: str,
        subject: str = "",
        year: int = 0,
    ) -> Book:
        """Add a new book to the catalog.

        Args:
            isbn: Book ISBN (validated).
            title: Book title.
            author: Book author.
            subject: Book subject/category.
            year: Publication year.

        Returns:
            The created Book.

        Raises:
            InvalidISBNError: If ISBN format is invalid.
            DuplicateError: If a book with this ISBN already exists.
        """
        validate_isbn(isbn)
        validate_non_empty_string(title, "title")
        validate_non_empty_string(author, "author")

        if self._book_repo.get_by_isbn(isbn):
            raise DuplicateError("Book", isbn)

        book = Book(isbn=isbn, title=title, author=author, subject=subject, year=year)
        self._book_repo.add(book)
        return book

    def add_book_item(
        self,
        isbn: str,
        barcode: Optional[str] = None,
        rack_number: str = "",
    ) -> BookItem:
        """Add a physical copy to an existing book.

        Args:
            isbn: The ISBN of the book to add a copy to.
            barcode: Optional barcode. Generated if not provided.
            rack_number: Physical location in the library.

        Returns:
            The created BookItem.

        Raises:
            BookNotFoundError: If no book with this ISBN exists.
            DuplicateError: If a book item with this barcode already exists.
        """
        book = self._book_repo.get_by_isbn(isbn)
        if not book:
            raise BookNotFoundError(isbn)

        if barcode is None:
            barcode = generate_id()

        if self._book_item_repo.get_by_barcode(barcode):
            raise DuplicateError("BookItem", barcode)

        item = BookItem(barcode=barcode, book_isbn=isbn, rack_number=rack_number)
        self._book_item_repo.add(item)
        book.add_item(item)
        self._book_repo.update(book)
        return item

    def get_book(self, isbn: str) -> Book:
        """Get a book by ISBN.

        Args:
            isbn: The ISBN to look up.

        Returns:
            The Book.

        Raises:
            BookNotFoundError: If no book with this ISBN exists.
        """
        book = self._book_repo.get_by_isbn(isbn)
        if not book:
            raise BookNotFoundError(isbn)
        return book

    def get_book_item(self, barcode: str) -> BookItem:
        """Get a book item by barcode.

        Args:
            barcode: The barcode to look up.

        Returns:
            The BookItem.

        Raises:
            BookNotFoundError: If no book item with this barcode exists.
        """
        item = self._book_item_repo.get_by_barcode(barcode)
        if not item:
            raise BookNotFoundError(barcode)
        return item

    def search_books(self, query: str) -> list[Book]:
        """Search the catalog by title, author, ISBN, or subject.

        Args:
            query: The search query string.

        Returns:
            List of matching books.
        """
        if not query or not query.strip():
            return []
        return self._book_repo.search(query)

    def get_all_books(self) -> list[Book]:
        """Get all books in the catalog.

        Returns:
            List of all books.
        """
        return self._book_repo.get_all()

    def update_book(
        self,
        isbn: str,
        title: Optional[str] = None,
        author: Optional[str] = None,
        subject: Optional[str] = None,
        year: Optional[int] = None,
    ) -> Book:
        """Update a book's information.

        Args:
            isbn: The ISBN of the book to update.
            title: New title (or None to keep current).
            author: New author (or None to keep current).
            subject: New subject (or None to keep current).
            year: New year (or None to keep current).

        Returns:
            The updated Book.

        Raises:
            BookNotFoundError: If no book with this ISBN exists.
        """
        book = self.get_book(isbn)

        if title is not None:
            validate_non_empty_string(title, "title")
            book.title = title
        if author is not None:
            validate_non_empty_string(author, "author")
            book.author = author
        if subject is not None:
            book.subject = subject
        if year is not None:
            book.year = year

        self._book_repo.update(book)
        return book

    def remove_book(self, isbn: str) -> bool:
        """Remove a book and all its items from the catalog.

        Args:
            isbn: The ISBN of the book to remove.

        Returns:
            True if the book was removed.

        Raises:
            BookNotFoundError: If no book with this ISBN exists.
        """
        book = self.get_book(isbn)

        # Remove all associated book items
        for item in list(book.items):
            self._book_item_repo.delete(item.barcode)

        return self._book_repo.delete(isbn)

    def remove_book_item(self, barcode: str) -> bool:
        """Remove a specific book item.

        Args:
            barcode: The barcode of the item to remove.

        Returns:
            True if the item was removed.

        Raises:
            BookNotFoundError: If no book item with this barcode exists.
        """
        item = self.get_book_item(barcode)
        book = self._book_repo.get_by_isbn(item.book_isbn)
        if book:
            book.remove_item(barcode)
            self._book_repo.update(book)

        return self._book_item_repo.delete(barcode)

    def check_availability(self, isbn: str) -> bool:
        """Check if any copy of a book is available.

        Args:
            isbn: The ISBN to check.

        Returns:
            True if at least one copy is available.
        """
        items = self._book_item_repo.get_available_by_isbn(isbn)
        return len(items) > 0

    def get_available_items(self, isbn: str) -> list[BookItem]:
        """Get all available copies of a book.

        Args:
            isbn: The ISBN to look up.

        Returns:
            List of available BookItems.
        """
        return self._book_item_repo.get_available_by_isbn(isbn)
