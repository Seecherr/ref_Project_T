"""Integration tests for catalog search flow."""

from src.services.catalog_service import CatalogService
from src.storage.in_memory_book_repository import InMemoryBookItemRepository, InMemoryBookRepository


class TestSearchFlow:
    """Integration tests for catalog management and search."""

    def _setup(self):
        book_repo = InMemoryBookRepository()
        book_item_repo = InMemoryBookItemRepository()
        service = CatalogService(book_repo, book_item_repo)
        return service

    def test_add_books_and_search_by_title(self):
        service = self._setup()
        service.add_book("9780134685991", "Effective Java", "Joshua Bloch", "Programming")
        service.add_book("9780132350884", "Clean Code", "Robert Martin", "Programming")
        service.add_book("9780596007126", "Head First Design Patterns", "Eric Freeman", "Design")

        results = service.search_books("code")
        assert len(results) == 1
        assert results[0].title == "Clean Code"

    def test_search_by_author(self):
        service = self._setup()
        service.add_book("9780134685991", "Effective Java", "Joshua Bloch")
        service.add_book("9780132350884", "Clean Code", "Robert Martin")

        results = service.search_books("bloch")
        assert len(results) == 1

    def test_search_by_subject(self):
        service = self._setup()
        service.add_book("9780134685991", "Book A", "Author A", "Science")
        service.add_book("9780132350884", "Book B", "Author B", "Art")
        service.add_book("9780596007126", "Book C", "Author C", "Science")

        results = service.search_books("science")
        assert len(results) == 2

    def test_add_items_and_check_availability(self):
        service = self._setup()
        service.add_book("9780134685991", "Book", "Author")
        service.add_book_item("9780134685991", "BC001")
        service.add_book_item("9780134685991", "BC002")

        assert service.check_availability("9780134685991") is True
        assert len(service.get_available_items("9780134685991")) == 2

    def test_remove_item_updates_availability(self):
        service = self._setup()
        service.add_book("9780134685991", "Book", "Author")
        service.add_book_item("9780134685991", "BC001")
        service.remove_book_item("BC001")

        assert service.check_availability("9780134685991") is False

    def test_update_and_search(self):
        service = self._setup()
        service.add_book("9780134685991", "Old Title", "Old Author")
        service.update_book("9780134685991", title="Python Mastery", author="New Author")

        results = service.search_books("python")
        assert len(results) == 1
        assert results[0].title == "Python Mastery"

    def test_full_catalog_lifecycle(self):
        service = self._setup()

        # Add books
        service.add_book("9780134685991", "Effective Java", "Bloch", "Programming", 2018)
        service.add_book("9780132350884", "Clean Code", "Martin", "Programming", 2008)

        # Add items
        service.add_book_item("9780134685991", "BC001")
        service.add_book_item("9780134685991", "BC002")
        service.add_book_item("9780132350884", "BC003")

        # Search
        assert len(service.search_books("programming")) == 2
        assert len(service.get_all_books()) == 2

        # Remove a book
        service.remove_book("9780132350884")
        assert len(service.get_all_books()) == 1

        # Verify items cleaned up
        assert service.check_availability("9780132350884") is False
