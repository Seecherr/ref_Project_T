"""Unit tests for InMemoryBookRepository and InMemoryBookItemRepository."""

import pytest

from src.models.book import Book, BookItem, BookStatus
from src.storage.in_memory_book_repository import InMemoryBookRepository, InMemoryBookItemRepository


class TestInMemoryBookRepository:
    """Tests for InMemoryBookRepository."""

    def test_add_and_get(self, book_repo):
        book = Book(isbn="978-1", title="Test", author="Author")
        book_repo.add(book)
        result = book_repo.get_by_isbn("978-1")
        assert result is book

    def test_get_nonexistent(self, book_repo):
        assert book_repo.get_by_isbn("nonexistent") is None

    def test_get_all_empty(self, book_repo):
        assert book_repo.get_all() == []

    def test_get_all_multiple(self, book_repo):
        book_repo.add(Book(isbn="978-1", title="Book 1", author="A1"))
        book_repo.add(Book(isbn="978-2", title="Book 2", author="A2"))
        assert len(book_repo.get_all()) == 2

    def test_search_by_title(self, book_repo):
        book_repo.add(Book(isbn="978-1", title="Python Programming", author="Author"))
        book_repo.add(Book(isbn="978-2", title="Java Guide", author="Author"))
        results = book_repo.search("python")
        assert len(results) == 1
        assert results[0].title == "Python Programming"

    def test_search_by_author(self, book_repo):
        book_repo.add(Book(isbn="978-1", title="Book", author="John Smith"))
        results = book_repo.search("smith")
        assert len(results) == 1

    def test_search_by_isbn(self, book_repo):
        book_repo.add(Book(isbn="978-123456", title="Book", author="Author"))
        results = book_repo.search("978-123456")
        assert len(results) == 1

    def test_search_by_subject(self, book_repo):
        book_repo.add(Book(isbn="978-1", title="Book", author="Author", subject="Science"))
        results = book_repo.search("science")
        assert len(results) == 1

    def test_search_no_results(self, book_repo):
        book_repo.add(Book(isbn="978-1", title="Book", author="Author"))
        results = book_repo.search("nonexistent")
        assert len(results) == 0

    def test_search_case_insensitive(self, book_repo):
        book_repo.add(Book(isbn="978-1", title="Python", author="Author"))
        assert len(book_repo.search("PYTHON")) == 1
        assert len(book_repo.search("python")) == 1

    def test_update(self, book_repo):
        book = Book(isbn="978-1", title="Old Title", author="Author")
        book_repo.add(book)
        book.title = "New Title"
        book_repo.update(book)
        result = book_repo.get_by_isbn("978-1")
        assert result.title == "New Title"

    def test_delete_existing(self, book_repo):
        book_repo.add(Book(isbn="978-1", title="Book", author="Author"))
        assert book_repo.delete("978-1") is True
        assert book_repo.get_by_isbn("978-1") is None

    def test_delete_nonexistent(self, book_repo):
        assert book_repo.delete("nonexistent") is False

    def test_search_multiple_results(self, book_repo):
        book_repo.add(Book(isbn="978-1", title="Python Basics", author="A1"))
        book_repo.add(Book(isbn="978-2", title="Advanced Python", author="A2"))
        book_repo.add(Book(isbn="978-3", title="Java", author="A3"))
        results = book_repo.search("python")
        assert len(results) == 2


class TestInMemoryBookItemRepository:
    """Tests for InMemoryBookItemRepository."""

    def test_add_and_get(self, book_item_repo):
        item = BookItem(barcode="BC001", book_isbn="978-1")
        book_item_repo.add(item)
        result = book_item_repo.get_by_barcode("BC001")
        assert result is item

    def test_get_nonexistent(self, book_item_repo):
        assert book_item_repo.get_by_barcode("nonexistent") is None

    def test_get_by_isbn(self, book_item_repo):
        book_item_repo.add(BookItem(barcode="BC001", book_isbn="978-1"))
        book_item_repo.add(BookItem(barcode="BC002", book_isbn="978-1"))
        book_item_repo.add(BookItem(barcode="BC003", book_isbn="978-2"))
        results = book_item_repo.get_by_isbn("978-1")
        assert len(results) == 2

    def test_get_available_by_isbn(self, book_item_repo):
        book_item_repo.add(BookItem(barcode="BC001", book_isbn="978-1"))
        book_item_repo.add(BookItem(barcode="BC002", book_isbn="978-1", status=BookStatus.LOANED))
        book_item_repo.add(BookItem(barcode="BC003", book_isbn="978-1"))
        results = book_item_repo.get_available_by_isbn("978-1")
        assert len(results) == 2

    def test_get_available_by_isbn_none_available(self, book_item_repo):
        book_item_repo.add(BookItem(barcode="BC001", book_isbn="978-1", status=BookStatus.LOANED))
        results = book_item_repo.get_available_by_isbn("978-1")
        assert len(results) == 0

    def test_update(self, book_item_repo):
        item = BookItem(barcode="BC001", book_isbn="978-1")
        book_item_repo.add(item)
        item.status = BookStatus.LOANED
        book_item_repo.update(item)
        result = book_item_repo.get_by_barcode("BC001")
        assert result.status == BookStatus.LOANED

    def test_delete_existing(self, book_item_repo):
        book_item_repo.add(BookItem(barcode="BC001", book_isbn="978-1"))
        assert book_item_repo.delete("BC001") is True
        assert book_item_repo.get_by_barcode("BC001") is None

    def test_delete_nonexistent(self, book_item_repo):
        assert book_item_repo.delete("nonexistent") is False

    def test_get_all(self, book_item_repo):
        book_item_repo.add(BookItem(barcode="BC001", book_isbn="978-1"))
        book_item_repo.add(BookItem(barcode="BC002", book_isbn="978-2"))
        assert len(book_item_repo.get_all()) == 2

    def test_get_all_empty(self, book_item_repo):
        assert book_item_repo.get_all() == []

    def test_get_by_isbn_empty(self, book_item_repo):
        assert book_item_repo.get_by_isbn("978-1") == []
