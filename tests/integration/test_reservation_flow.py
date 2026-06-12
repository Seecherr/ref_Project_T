"""Integration tests for reservation → notification flow."""

from src.models.book import BookItem
from src.models.member import Reader
from src.services.catalog_service import CatalogService
from src.services.loan_service import LoanService
from src.services.notification_service import BookAvailabilityListener, NotificationService
from src.services.reservation_service import ReservationService
from src.storage.in_memory_book_repository import InMemoryBookItemRepository, InMemoryBookRepository
from src.storage.in_memory_loan_repository import InMemoryLoanRepository
from src.storage.in_memory_member_repository import InMemoryMemberRepository
from src.storage.in_memory_notification_repository import InMemoryNotificationRepository
from src.storage.in_memory_reservation_repository import InMemoryReservationRepository
from src.utils.event_manager import Event, EventManager


class TestReservationFlow:
    """Integration tests for reservation-notification workflow."""

    def _setup_services(self):
        book_repo = InMemoryBookRepository()
        book_item_repo = InMemoryBookItemRepository()
        member_repo = InMemoryMemberRepository()
        loan_repo = InMemoryLoanRepository()
        reservation_repo = InMemoryReservationRepository()
        notification_repo = InMemoryNotificationRepository()
        em = EventManager()

        catalog_service = CatalogService(book_repo, book_item_repo)
        loan_service = LoanService(loan_repo, book_item_repo, member_repo, em)
        reservation_service = ReservationService(reservation_repo, book_item_repo, member_repo, em)
        notification_service = NotificationService(notification_repo)

        listener = BookAvailabilityListener(notification_service, reservation_repo)
        em.subscribe(Event.BOOK_RETURNED, listener)
        em.subscribe(Event.RESERVATION_FULFILLED, listener)

        return catalog_service, loan_service, reservation_service, notification_service, member_repo, book_item_repo

    def test_reserve_then_return_notifies(self):
        _catalog, loans, reservations, notifications, member_repo, book_item_repo = self._setup_services()

        member_repo.add(Reader(member_id="R1", name="John", email="j@t.com"))
        member_repo.add(Reader(member_id="R2", name="Jane", email="ja@t.com"))
        book_item_repo.add(BookItem(barcode="BC1", book_isbn="978-1"))

        # R1 borrows the book
        loans.borrow_book("R1", "BC1")

        # R2 reserves it
        reservations.place_reservation("R2", "978-1")

        # R1 returns it — should notify R2
        loans.return_book("BC1")

        member_notifications = notifications.get_notifications("R2")
        assert len(member_notifications) == 1
        assert "978-1" in member_notifications[0].message

    def test_fulfill_reservation_notifies(self):
        _catalog, _loans, reservations, notifications, member_repo, _book_item_repo = self._setup_services()

        member_repo.add(Reader(member_id="R1", name="John", email="j@t.com"))
        reservations.place_reservation("R1", "978-1")
        reservations.fulfill_next_reservation("978-1")

        member_notifications = notifications.get_notifications("R1")
        assert len(member_notifications) == 1
        assert "fulfilled" in member_notifications[0].message.lower()

    def test_multiple_reservations_fifo(self):
        _catalog, _loans, reservations, _notifications, member_repo, _book_item_repo = self._setup_services()

        member_repo.add(Reader(member_id="R1", name="Alice", email="a@t.com"))
        member_repo.add(Reader(member_id="R2", name="Bob", email="b@t.com"))
        member_repo.add(Reader(member_id="R3", name="Charlie", email="c@t.com"))

        reservations.place_reservation("R1", "978-1")
        reservations.place_reservation("R2", "978-1")
        reservations.place_reservation("R3", "978-1")

        # Fulfill first
        fulfilled = reservations.fulfill_next_reservation("978-1")
        assert fulfilled.member_id == "R1"

        # Fulfill second
        fulfilled = reservations.fulfill_next_reservation("978-1")
        assert fulfilled.member_id == "R2"

    def test_cancel_reservation_not_fulfilled(self):
        _catalog, _loans, reservations, _notifications, member_repo, _book_item_repo = self._setup_services()

        member_repo.add(Reader(member_id="R1", name="John", email="j@t.com"))
        member_repo.add(Reader(member_id="R2", name="Jane", email="ja@t.com"))

        r1 = reservations.place_reservation("R1", "978-1")
        reservations.place_reservation("R2", "978-1")

        # Cancel R1's reservation
        reservations.cancel_reservation(r1.reservation_id)

        # Fulfill should give to R2
        fulfilled = reservations.fulfill_next_reservation("978-1")
        assert fulfilled.member_id == "R2"

    def test_return_with_no_reservations(self):
        _catalog, loans, _reservations, notifications, member_repo, book_item_repo = self._setup_services()

        member_repo.add(Reader(member_id="R1", name="John", email="j@t.com"))
        book_item_repo.add(BookItem(barcode="BC1", book_isbn="978-1"))

        loans.borrow_book("R1", "BC1")
        loans.return_book("BC1")

        # No notifications since no reservations
        assert len(notifications.get_all_notifications()) == 0

    def test_full_cycle_reserve_return_fulfill(self):
        _catalog, loans, reservations, notifications, member_repo, book_item_repo = self._setup_services()

        member_repo.add(Reader(member_id="R1", name="John", email="j@t.com"))
        member_repo.add(Reader(member_id="R2", name="Jane", email="ja@t.com"))
        book_item_repo.add(BookItem(barcode="BC1", book_isbn="978-1"))

        # R1 borrows, R2 reserves
        loans.borrow_book("R1", "BC1")
        reservations.place_reservation("R2", "978-1")

        # Return triggers notification
        loans.return_book("BC1")

        # Fulfill reservation
        fulfilled = reservations.fulfill_next_reservation("978-1")
        assert fulfilled.member_id == "R2"

        # R2 should have 2 notifications: book returned + reservation fulfilled
        member_notifications = notifications.get_notifications("R2")
        assert len(member_notifications) == 2

    def test_reservation_after_cancel_allows_new_one(self):
        _catalog, _loans, reservations, _notifications, member_repo, _book_item_repo = self._setup_services()

        member_repo.add(Reader(member_id="R1", name="John", email="j@t.com"))
        r = reservations.place_reservation("R1", "978-1")
        reservations.cancel_reservation(r.reservation_id)
        r2 = reservations.place_reservation("R1", "978-1")
        assert r2.member_id == "R1"

    def test_multiple_books_reservations(self):
        _catalog, _loans, reservations, _notifications, member_repo, _book_item_repo = self._setup_services()

        member_repo.add(Reader(member_id="R1", name="John", email="j@t.com"))
        reservations.place_reservation("R1", "978-1")
        reservations.place_reservation("R1", "978-2")
        results = reservations.get_member_reservations("R1")
        assert len(results) == 2
