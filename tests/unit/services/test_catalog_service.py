"""Unit tests for CatalogService."""

import pytest

from src.models.book import Book, BookItem, BookStatus
from src.utils.exceptions import BookNotFoundError, DuplicateError, InvalidISBNError


class TestCatalogService:
    """Tests for CatalogService."""

    def test_add_book(self, catalog_service):
        book = catalog_service.add_book("9780134685991", "Effective Java", "Joshua Bloch")
        assert book.isbn == "9780134685991"
        assert book.title == "Effective Java"

    def test_add_book_with_all_fields(self, catalog_service):
        book = catalog_service.add_book("9780134685991", "Effective Java", "Joshua Bloch", "Programming", 2018)
        assert book.subject == "Programming"
        assert book.year == 2018

    def test_add_book_invalid_isbn(self, catalog_service):
        with pytest.raises(InvalidISBNError):
            catalog_service.add_book("123", "Title", "Author")

    def test_add_book_duplicate(self, catalog_service):
        catalog_service.add_book("9780134685991", "Book 1", "Author 1")
        with pytest.raises(DuplicateError):
            catalog_service.add_book("9780134685991", "Book 2", "Author 2")

    def test_add_book_empty_title(self, catalog_service):
        with pytest.raises(ValueError):
            catalog_service.add_book("9780134685991", "", "Author")

    def test_add_book_empty_author(self, catalog_service):
        with pytest.raises(ValueError):
            catalog_service.add_book("9780134685991", "Title", "")

    def test_add_book_item(self, catalog_service):
        catalog_service.add_book("9780134685991", "Book", "Author")
        item = catalog_service.add_book_item("9780134685991", "BC001")
        assert item.barcode == "BC001"
        assert item.book_isbn == "9780134685991"

    def test_add_book_item_auto_barcode(self, catalog_service):
        catalog_service.add_book("9780134685991", "Book", "Author")
        item = catalog_service.add_book_item("9780134685991")
        assert item.barcode is not None
        assert len(item.barcode) > 0

    def test_add_book_item_nonexistent_book(self, catalog_service):
        with pytest.raises(BookNotFoundError):
            catalog_service.add_book_item("nonexistent", "BC001")

    def test_add_book_item_duplicate_barcode(self, catalog_service):
        catalog_service.add_book("9780134685991", "Book", "Author")
        catalog_service.add_book_item("9780134685991", "BC001")
        with pytest.raises(DuplicateError):
            catalog_service.add_book_item("9780134685991", "BC001")

    def test_get_book(self, catalog_service):
        catalog_service.add_book("9780134685991", "Book", "Author")
        book = catalog_service.get_book("9780134685991")
        assert book.isbn == "9780134685991"

    def test_get_book_not_found(self, catalog_service):
        with pytest.raises(BookNotFoundError):
            catalog_service.get_book("nonexistent")

    def test_get_book_item(self, catalog_service):
        catalog_service.add_book("9780134685991", "Book", "Author")
        catalog_service.add_book_item("9780134685991", "BC001")
        item = catalog_service.get_book_item("BC001")
        assert item.barcode == "BC001"

    def test_get_book_item_not_found(self, catalog_service):
        with pytest.raises(BookNotFoundError):
            catalog_service.get_book_item("nonexistent")

    def test_search_books(self, catalog_service):
        catalog_service.add_book("9780134685991", "Python Programming", "Author")
        catalog_service.add_book("9780132350884", "Java Guide", "Author2")
        results = catalog_service.search_books("python")
        assert len(results) == 1

    def test_search_books_empty_query(self, catalog_service):
        catalog_service.add_book("9780134685991", "Book", "Author")
        assert catalog_service.search_books("") == []

    def test_search_books_no_results(self, catalog_service):
        catalog_service.add_book("9780134685991", "Book", "Author")
        assert catalog_service.search_books("nonexistent") == []

    def test_get_all_books(self, catalog_service):
        catalog_service.add_book("9780134685991", "Book 1", "Author")
        catalog_service.add_book("9780132350884", "Book 2", "Author")
        assert len(catalog_service.get_all_books()) == 2

    def test_update_book(self, catalog_service):
        catalog_service.add_book("9780134685991", "Old Title", "Old Author")
        book = catalog_service.update_book("9780134685991", title="New Title")
        assert book.title == "New Title"
        assert book.author == "Old Author"  # Unchanged

    def test_update_book_all_fields(self, catalog_service):
        catalog_service.add_book("9780134685991", "Old", "Old")
        book = catalog_service.update_book("9780134685991", title="New", author="New Author", subject="New Subject", year=2025)
        assert book.title == "New"
        assert book.author == "New Author"
        assert book.subject == "New Subject"
        assert book.year == 2025

    def test_update_book_not_found(self, catalog_service):
        with pytest.raises(BookNotFoundError):
            catalog_service.update_book("nonexistent", title="New")

    def test_remove_book(self, catalog_service):
        catalog_service.add_book("9780134685991", "Book", "Author")
        assert catalog_service.remove_book("9780134685991") is True

    def test_remove_book_with_items(self, catalog_service):
        catalog_service.add_book("9780134685991", "Book", "Author")
        catalog_service.add_book_item("9780134685991", "BC001")
        catalog_service.add_book_item("9780134685991", "BC002")
        catalog_service.remove_book("9780134685991")
        with pytest.raises(BookNotFoundError):
            catalog_service.get_book("9780134685991")

    def test_remove_book_not_found(self, catalog_service):
        with pytest.raises(BookNotFoundError):
            catalog_service.remove_book("nonexistent")

    def test_remove_book_item(self, catalog_service):
        catalog_service.add_book("9780134685991", "Book", "Author")
        catalog_service.add_book_item("9780134685991", "BC001")
        assert catalog_service.remove_book_item("BC001") is True

    def test_remove_book_item_not_found(self, catalog_service):
        with pytest.raises(BookNotFoundError):
            catalog_service.remove_book_item("nonexistent")

    def test_check_availability_true(self, catalog_service):
        catalog_service.add_book("9780134685991", "Book", "Author")
        catalog_service.add_book_item("9780134685991", "BC001")
        assert catalog_service.check_availability("9780134685991") is True

    def test_check_availability_false(self, catalog_service):
        assert catalog_service.check_availability("9780134685991") is False

    def test_get_available_items(self, catalog_service):
        catalog_service.add_book("9780134685991", "Book", "Author")
        catalog_service.add_book_item("9780134685991", "BC001")
        catalog_service.add_book_item("9780134685991", "BC002")
        items = catalog_service.get_available_items("9780134685991")
        assert len(items) == 2
