"""Integration tests for blocking → fine → payment → unblock flow."""

from datetime import timedelta
from decimal import Decimal

import pytest

from src.models.book import BookItem
from src.models.member import MemberStatus, Reader
from src.services.fine_service import FineService
from src.services.loan_service import LoanService
from src.services.notification_service import BookAvailabilityListener, NotificationService
from src.storage.in_memory_book_repository import InMemoryBookItemRepository
from src.storage.in_memory_fine_repository import InMemoryFineRepository
from src.storage.in_memory_loan_repository import InMemoryLoanRepository
from src.storage.in_memory_member_repository import InMemoryMemberRepository
from src.storage.in_memory_notification_repository import InMemoryNotificationRepository
from src.utils.event_manager import Event, EventManager
from src.utils.exceptions import MemberBlockedError


class TestBlockingFlow:
    """Integration tests for the overdue → fine → block → pay → unblock cycle."""

    def _setup_services(self):
        book_item_repo = InMemoryBookItemRepository()
        member_repo = InMemoryMemberRepository()
        loan_repo = InMemoryLoanRepository()
        fine_repo = InMemoryFineRepository()
        notification_repo = InMemoryNotificationRepository()
        em = EventManager()

        loan_service = LoanService(loan_repo, book_item_repo, member_repo, em)
        fine_service = FineService(fine_repo, member_repo, event_manager=em, block_threshold=Decimal("10.00"))
        notification_service = NotificationService(notification_repo)

        listener = BookAvailabilityListener(notification_service)
        em.subscribe(Event.MEMBER_BLOCKED, listener)
        em.subscribe(Event.MEMBER_UNBLOCKED, listener)

        return book_item_repo, member_repo, loan_service, fine_service, notification_service

    def test_auto_block_on_high_fines(self):
        book_item_repo, member_repo, loan_service, fine_service, _notification_service = self._setup_services()
        reader = Reader(member_id="R1", name="John", email="j@t.com")
        member_repo.add(reader)
        book_item_repo.add(BookItem(barcode="BC1", book_isbn="978-1"))

        loan = loan_service.borrow_book("R1", "BC1")
        late_return = loan.due_date + timedelta(days=25)
        returned_loan = loan_service.return_book("BC1", late_return)
        fine = fine_service.create_fine(returned_loan)

        # Fine = 25 x $0.50 = $12.50 > $10 threshold
        assert fine.amount == Decimal("12.50")
        assert reader.status == MemberStatus.BLOCKED

    def test_blocked_member_cannot_borrow(self):
        book_item_repo, member_repo, loan_service, fine_service, _notification_service = self._setup_services()
        reader = Reader(member_id="R1", name="John", email="j@t.com")
        member_repo.add(reader)
        book_item_repo.add(BookItem(barcode="BC1", book_isbn="978-1"))
        book_item_repo.add(BookItem(barcode="BC2", book_isbn="978-2"))

        # Create overdue fine that triggers block
        loan = loan_service.borrow_book("R1", "BC1")
        late_return = loan.due_date + timedelta(days=25)
        returned_loan = loan_service.return_book("BC1", late_return)
        fine_service.create_fine(returned_loan)

        # Try to borrow — should fail
        with pytest.raises(MemberBlockedError):
            loan_service.borrow_book("R1", "BC2")

    def test_pay_fine_unblocks_member(self):
        book_item_repo, member_repo, loan_service, fine_service, _notification_service = self._setup_services()
        reader = Reader(member_id="R1", name="John", email="j@t.com")
        member_repo.add(reader)
        book_item_repo.add(BookItem(barcode="BC1", book_isbn="978-1"))

        loan = loan_service.borrow_book("R1", "BC1")
        late_return = loan.due_date + timedelta(days=25)
        returned_loan = loan_service.return_book("BC1", late_return)
        fine = fine_service.create_fine(returned_loan)

        assert reader.status == MemberStatus.BLOCKED

        # Pay the fine
        fine_service.pay_fine(fine.fine_id, fine.amount)
        assert reader.status == MemberStatus.ACTIVE

    def test_partial_payment_keeps_blocked(self):
        book_item_repo, member_repo, loan_service, fine_service, _notification_service = self._setup_services()
        reader = Reader(member_id="R1", name="John", email="j@t.com")
        member_repo.add(reader)
        book_item_repo.add(BookItem(barcode="BC1", book_isbn="978-1"))

        loan = loan_service.borrow_book("R1", "BC1")
        late_return = loan.due_date + timedelta(days=25)
        returned_loan = loan_service.return_book("BC1", late_return)
        fine = fine_service.create_fine(returned_loan)

        # Partial payment — still over threshold
        fine_service.pay_fine(fine.fine_id, Decimal("1.00"))
        assert reader.status == MemberStatus.BLOCKED

    def test_block_notification_sent(self):
        book_item_repo, member_repo, loan_service, fine_service, notification_service = self._setup_services()
        reader = Reader(member_id="R1", name="John", email="j@t.com")
        member_repo.add(reader)
        book_item_repo.add(BookItem(barcode="BC1", book_isbn="978-1"))

        loan = loan_service.borrow_book("R1", "BC1")
        late_return = loan.due_date + timedelta(days=25)
        returned_loan = loan_service.return_book("BC1", late_return)
        fine_service.create_fine(returned_loan)

        notifications = notification_service.get_notifications("R1")
        assert any("blocked" in n.message.lower() for n in notifications)

    def test_unblock_notification_sent(self):
        book_item_repo, member_repo, loan_service, fine_service, notification_service = self._setup_services()
        reader = Reader(member_id="R1", name="John", email="j@t.com")
        member_repo.add(reader)
        book_item_repo.add(BookItem(barcode="BC1", book_isbn="978-1"))

        loan = loan_service.borrow_book("R1", "BC1")
        late_return = loan.due_date + timedelta(days=25)
        returned_loan = loan_service.return_book("BC1", late_return)
        fine = fine_service.create_fine(returned_loan)
        fine_service.pay_fine(fine.fine_id, fine.amount)

        notifications = notification_service.get_notifications("R1")
        assert any("unblocked" in n.message.lower() for n in notifications)

    def test_full_cycle_block_pay_borrow_again(self):
        book_item_repo, member_repo, loan_service, fine_service, _notification_service = self._setup_services()
        reader = Reader(member_id="R1", name="John", email="j@t.com")
        member_repo.add(reader)
        book_item_repo.add(BookItem(barcode="BC1", book_isbn="978-1"))
        book_item_repo.add(BookItem(barcode="BC2", book_isbn="978-2"))

        # Borrow and return late → blocked
        loan = loan_service.borrow_book("R1", "BC1")
        late_return = loan.due_date + timedelta(days=25)
        returned_loan = loan_service.return_book("BC1", late_return)
        fine = fine_service.create_fine(returned_loan)
        assert reader.status == MemberStatus.BLOCKED

        # Pay → unblocked
        fine_service.pay_fine(fine.fine_id, fine.amount)
        assert reader.status == MemberStatus.ACTIVE

        # Can borrow again
        loan2 = loan_service.borrow_book("R1", "BC2")
        assert loan2.is_active()
