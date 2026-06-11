"""Root conftest for pytest — shared fixtures."""

import pytest
from decimal import Decimal
from datetime import date, datetime, timedelta

from src.models.book import Book, BookItem, BookStatus
from src.models.member import Reader, Librarian, MemberStatus
from src.models.loan import Loan
from src.models.fine import Fine
from src.models.reservation import Reservation, ReservationStatus
from src.models.notification import Notification

from src.storage.in_memory_book_repository import InMemoryBookRepository, InMemoryBookItemRepository
from src.storage.in_memory_member_repository import InMemoryMemberRepository
from src.storage.in_memory_loan_repository import InMemoryLoanRepository
from src.storage.in_memory_fine_repository import InMemoryFineRepository
from src.storage.in_memory_reservation_repository import InMemoryReservationRepository
from src.storage.in_memory_notification_repository import InMemoryNotificationRepository

from src.utils.event_manager import EventManager
from src.utils.fine_strategy import StandardFineStrategy, ProgressiveFineStrategy, NoFineStrategy

from src.services.catalog_service import CatalogService
from src.services.member_service import MemberService
from src.services.loan_service import LoanService
from src.services.fine_service import FineService
from src.services.reservation_service import ReservationService
from src.services.notification_service import NotificationService


# ── Model Fixtures ──────────────────────────────────────────────────


@pytest.fixture
def sample_book():
    """Create a sample Book."""
    return Book(isbn="9780134685991", title="Effective Java", author="Joshua Bloch", subject="Programming", year=2018)


@pytest.fixture
def sample_book_item():
    """Create a sample BookItem."""
    return BookItem(barcode="BC001", book_isbn="9780134685991")


@pytest.fixture
def sample_reader():
    """Create a sample Reader."""
    return Reader(member_id="R001", name="John Doe", email="john@example.com")


@pytest.fixture
def sample_librarian():
    """Create a sample Librarian."""
    return Librarian(member_id="L001", name="Jane Smith", email="jane@example.com", employee_id="EMP001")


@pytest.fixture
def sample_loan():
    """Create a sample Loan."""
    return Loan(loan_id="LOAN001", member_id="R001", book_item_barcode="BC001")


@pytest.fixture
def overdue_loan():
    """Create an overdue Loan."""
    return Loan(
        loan_id="LOAN002",
        member_id="R001",
        book_item_barcode="BC002",
        issue_date=date.today() - timedelta(days=30),
        due_date=date.today() - timedelta(days=16),
    )


@pytest.fixture
def sample_fine():
    """Create a sample Fine."""
    return Fine(fine_id="FINE001", loan_id="LOAN001", member_id="R001", amount=Decimal("5.00"))


@pytest.fixture
def sample_reservation():
    """Create a sample Reservation."""
    return Reservation(reservation_id="RES001", member_id="R001", book_isbn="9780134685991")


@pytest.fixture
def sample_notification():
    """Create a sample Notification."""
    return Notification(notification_id="NOT001", member_id="R001", message="Test notification")


# ── Repository Fixtures ─────────────────────────────────────────────


@pytest.fixture
def book_repo():
    """Create an empty InMemoryBookRepository."""
    return InMemoryBookRepository()


@pytest.fixture
def book_item_repo():
    """Create an empty InMemoryBookItemRepository."""
    return InMemoryBookItemRepository()


@pytest.fixture
def member_repo():
    """Create an empty InMemoryMemberRepository."""
    return InMemoryMemberRepository()


@pytest.fixture
def loan_repo():
    """Create an empty InMemoryLoanRepository."""
    return InMemoryLoanRepository()


@pytest.fixture
def fine_repo():
    """Create an empty InMemoryFineRepository."""
    return InMemoryFineRepository()


@pytest.fixture
def reservation_repo():
    """Create an empty InMemoryReservationRepository."""
    return InMemoryReservationRepository()


@pytest.fixture
def notification_repo():
    """Create an empty InMemoryNotificationRepository."""
    return InMemoryNotificationRepository()


# ── Service Fixtures ────────────────────────────────────────────────


@pytest.fixture
def event_manager():
    """Create an EventManager."""
    return EventManager()


@pytest.fixture
def catalog_service(book_repo, book_item_repo):
    """Create a CatalogService with in-memory repos."""
    return CatalogService(book_repo, book_item_repo)


@pytest.fixture
def member_service(member_repo):
    """Create a MemberService with in-memory repo."""
    return MemberService(member_repo)


@pytest.fixture
def loan_service(loan_repo, book_item_repo, member_repo, event_manager):
    """Create a LoanService with in-memory repos."""
    return LoanService(loan_repo, book_item_repo, member_repo, event_manager)


@pytest.fixture
def fine_service(fine_repo, member_repo, event_manager):
    """Create a FineService with in-memory repos."""
    return FineService(fine_repo, member_repo, event_manager=event_manager)


@pytest.fixture
def reservation_service(reservation_repo, book_item_repo, member_repo, event_manager):
    """Create a ReservationService with in-memory repos."""
    return ReservationService(reservation_repo, book_item_repo, member_repo, event_manager)


@pytest.fixture
def notification_service(notification_repo):
    """Create a NotificationService with in-memory repo."""
    return NotificationService(notification_repo)
