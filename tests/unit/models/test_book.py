"""Unit tests for Book and BookItem models."""

from datetime import date

from src.models.book import Book, BookItem, BookStatus


class TestBookStatus:
    """Tests for BookStatus enum."""

    def test_available_value(self):
        assert BookStatus.AVAILABLE.value == "available"

    def test_loaned_value(self):
        assert BookStatus.LOANED.value == "loaned"

    def test_reserved_value(self):
        assert BookStatus.RESERVED.value == "reserved"

    def test_lost_value(self):
        assert BookStatus.LOST.value == "lost"


class TestBookItem:
    """Tests for BookItem dataclass."""

    def test_creation_defaults(self):
        item = BookItem(barcode="BC001", book_isbn="978-0")
        assert item.barcode == "BC001"
        assert item.book_isbn == "978-0"
        assert item.status == BookStatus.AVAILABLE
        assert item.rack_number == ""
        assert item.due_date is None

    def test_is_available_when_available(self, sample_book_item):
        assert sample_book_item.is_available() is True

    def test_is_available_when_loaned(self, sample_book_item):
        sample_book_item.mark_loaned(date.today())
        assert sample_book_item.is_available() is False

    def test_mark_loaned(self, sample_book_item):
        due = date(2025, 12, 31)
        sample_book_item.mark_loaned(due)
        assert sample_book_item.status == BookStatus.LOANED
        assert sample_book_item.due_date == due

    def test_mark_available(self, sample_book_item):
        sample_book_item.mark_loaned(date.today())
        sample_book_item.mark_available()
        assert sample_book_item.status == BookStatus.AVAILABLE
        assert sample_book_item.due_date is None

    def test_mark_reserved(self, sample_book_item):
        sample_book_item.mark_reserved()
        assert sample_book_item.status == BookStatus.RESERVED

    def test_mark_lost(self, sample_book_item):
        sample_book_item.mark_loaned(date.today())
        sample_book_item.mark_lost()
        assert sample_book_item.status == BookStatus.LOST
        assert sample_book_item.due_date is None

    def test_is_available_when_reserved(self):
        item = BookItem(barcode="BC002", book_isbn="978-0", status=BookStatus.RESERVED)
        assert item.is_available() is False

    def test_is_available_when_lost(self):
        item = BookItem(barcode="BC003", book_isbn="978-0", status=BookStatus.LOST)
        assert item.is_available() is False


class TestBook:
    """Tests for Book dataclass."""

    def test_creation_defaults(self):
        book = Book(isbn="978-0", title="Test", author="Author")
        assert book.isbn == "978-0"
        assert book.title == "Test"
        assert book.author == "Author"
        assert book.subject == ""
        assert book.year == 0
        assert book.items == []

    def test_creation_with_all_fields(self, sample_book):
        assert sample_book.isbn == "9780134685991"
        assert sample_book.title == "Effective Java"
        assert sample_book.author == "Joshua Bloch"
        assert sample_book.subject == "Programming"
        assert sample_book.year == 2018

    def test_add_item(self, sample_book, sample_book_item):
        sample_book.add_item(sample_book_item)
        assert len(sample_book.items) == 1
        assert sample_book.items[0] is sample_book_item

    def test_remove_item_existing(self, sample_book, sample_book_item):
        sample_book.add_item(sample_book_item)
        removed = sample_book.remove_item("BC001")
        assert removed is sample_book_item
        assert len(sample_book.items) == 0

    def test_remove_item_nonexistent(self, sample_book):
        result = sample_book.remove_item("NONEXISTENT")
        assert result is None

    def test_get_available_items(self, sample_book):
        item1 = BookItem(barcode="BC001", book_isbn=sample_book.isbn)
        item2 = BookItem(barcode="BC002", book_isbn=sample_book.isbn, status=BookStatus.LOANED)
        item3 = BookItem(barcode="BC003", book_isbn=sample_book.isbn)
        sample_book.items = [item1, item2, item3]

        available = sample_book.get_available_items()
        assert len(available) == 2
        assert item1 in available
        assert item3 in available

    def test_has_available_copy_true(self, sample_book, sample_book_item):
        sample_book.add_item(sample_book_item)
        assert sample_book.has_available_copy() is True

    def test_has_available_copy_false(self, sample_book):
        item = BookItem(barcode="BC001", book_isbn=sample_book.isbn, status=BookStatus.LOANED)
        sample_book.add_item(item)
        assert sample_book.has_available_copy() is False

    def test_has_available_copy_empty(self, sample_book):
        assert sample_book.has_available_copy() is False

    def test_total_copies(self, sample_book):
        sample_book.add_item(BookItem(barcode="BC001", book_isbn=sample_book.isbn))
        sample_book.add_item(BookItem(barcode="BC002", book_isbn=sample_book.isbn))
        assert sample_book.total_copies() == 2

    def test_total_copies_empty(self, sample_book):
        assert sample_book.total_copies() == 0

    def test_add_multiple_items(self, sample_book):
        for i in range(5):
            sample_book.add_item(BookItem(barcode=f"BC{i:03d}", book_isbn=sample_book.isbn))
        assert sample_book.total_copies() == 5
