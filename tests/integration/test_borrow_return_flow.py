"""Integration tests for borrow → return → fine flow."""

from datetime import date, timedelta
from decimal import Decimal

from src.models.book import BookItem
from src.models.member import Reader
from src.services.fine_service import FineService
from src.services.loan_service import LoanService
from src.storage.in_memory_book_repository import InMemoryBookItemRepository
from src.storage.in_memory_fine_repository import InMemoryFineRepository
from src.storage.in_memory_loan_repository import InMemoryLoanRepository
from src.storage.in_memory_member_repository import InMemoryMemberRepository
from src.utils.event_manager import EventManager
from src.utils.fine_strategy import ProgressiveFineStrategy


class TestBorrowReturnFlow:
    """Integration tests for the complete borrow-return lifecycle."""

    def _setup_services(self):
        book_item_repo = InMemoryBookItemRepository()
        member_repo = InMemoryMemberRepository()
        loan_repo = InMemoryLoanRepository()
        fine_repo = InMemoryFineRepository()
        em = EventManager()

        loan_service = LoanService(loan_repo, book_item_repo, member_repo, em)
        fine_service = FineService(fine_repo, member_repo, event_manager=em)

        return book_item_repo, member_repo, loan_service, fine_service

    def test_borrow_and_return_on_time(self):
        book_item_repo, member_repo, loan_service, fine_service = self._setup_services()
        member_repo.add(Reader(member_id="R1", name="John", email="j@t.com"))
        book_item_repo.add(BookItem(barcode="BC1", book_isbn="978-1"))

        loan_service.borrow_book("R1", "BC1")
        returned_loan = loan_service.return_book("BC1")
        fine = fine_service.create_fine(returned_loan)

        assert returned_loan.return_date is not None
        assert fine is None  # No fine for on-time return

    def test_borrow_and_return_late(self):
        book_item_repo, member_repo, loan_service, fine_service = self._setup_services()
        member_repo.add(Reader(member_id="R1", name="John", email="j@t.com"))
        book_item_repo.add(BookItem(barcode="BC1", book_isbn="978-1"))

        loan = loan_service.borrow_book("R1", "BC1")
        late_return = loan.due_date + timedelta(days=5)
        returned_loan = loan_service.return_book("BC1", late_return)
        fine = fine_service.create_fine(returned_loan)

        assert fine is not None
        assert fine.amount == Decimal("2.50")  # 5 days x $0.50

    def test_multiple_borrows_and_returns(self):
        book_item_repo, member_repo, loan_service, _fine_service = self._setup_services()
        reader = Reader(member_id="R1", name="John", email="j@t.com")
        member_repo.add(reader)

        for i in range(5):
            book_item_repo.add(BookItem(barcode=f"BC{i}", book_isbn="978-1"))
            loan_service.borrow_book("R1", f"BC{i}")

        assert reader.total_books_checked_out == 5

        for i in range(5):
            loan_service.return_book(f"BC{i}")

        assert reader.total_books_checked_out == 0

    def test_borrow_return_reborrow(self):
        book_item_repo, member_repo, loan_service, _fine_service = self._setup_services()
        member_repo.add(Reader(member_id="R1", name="John", email="j@t.com"))
        book_item_repo.add(BookItem(barcode="BC1", book_isbn="978-1"))

        loan_service.borrow_book("R1", "BC1")
        loan_service.return_book("BC1")
        loan2 = loan_service.borrow_book("R1", "BC1")

        assert loan2.is_active()
        assert len(loan_service.get_all_loans()) == 2

    def test_late_return_with_progressive_fine(self):
        book_item_repo, member_repo, loan_service, fine_service = self._setup_services()
        fine_service.set_strategy(ProgressiveFineStrategy())
        member_repo.add(Reader(member_id="R1", name="John", email="j@t.com"))
        book_item_repo.add(BookItem(barcode="BC1", book_isbn="978-1"))

        loan = loan_service.borrow_book("R1", "BC1")
        late_return = loan.due_date + timedelta(days=10)
        returned_loan = loan_service.return_book("BC1", late_return)
        fine = fine_service.create_fine(returned_loan)

        assert fine is not None
        # 7 x $0.50 + 3 x $1.00 = $6.50
        assert fine.amount == Decimal("6.50")

    def test_fine_payment_clears_amount(self):
        book_item_repo, member_repo, loan_service, fine_service = self._setup_services()
        member_repo.add(Reader(member_id="R1", name="John", email="j@t.com"))
        book_item_repo.add(BookItem(barcode="BC1", book_isbn="978-1"))

        loan = loan_service.borrow_book("R1", "BC1")
        late_return = loan.due_date + timedelta(days=5)
        returned_loan = loan_service.return_book("BC1", late_return)
        fine = fine_service.create_fine(returned_loan)

        fine_service.pay_fine(fine.fine_id, fine.amount)
        assert fine.is_fully_paid()

    def test_overdue_detection(self):
        book_item_repo, member_repo, loan_service, _fine_service = self._setup_services()
        member_repo.add(Reader(member_id="R1", name="John", email="j@t.com"))
        book_item_repo.add(BookItem(barcode="BC1", book_isbn="978-1"))

        loan_service.borrow_book("R1", "BC1", loan_period_days=1)
        overdue = loan_service.get_overdue_loans(date.today() + timedelta(days=2))
        assert len(overdue) == 1

    def test_no_overdue_on_time(self):
        book_item_repo, member_repo, loan_service, _fine_service = self._setup_services()
        member_repo.add(Reader(member_id="R1", name="John", email="j@t.com"))
        book_item_repo.add(BookItem(barcode="BC1", book_isbn="978-1"))

        loan_service.borrow_book("R1", "BC1", loan_period_days=30)
        overdue = loan_service.get_overdue_loans()
        assert len(overdue) == 0
