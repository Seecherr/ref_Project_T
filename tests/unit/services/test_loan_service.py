"""Unit tests for LoanService."""

from datetime import date, timedelta

import pytest

from src.models.book import BookItem, BookStatus
from src.models.loan import Loan
from src.models.member import MemberStatus, Reader
from src.utils.exceptions import (
    BookNotAvailableError,
    BookNotFoundError,
    LoanLimitExceededError,
    LoanNotFoundError,
    MemberBlockedError,
    MemberNotFoundError,
)


class TestLoanServiceBorrow:
    """Tests for LoanService.borrow_book."""

    def test_borrow_success(self, loan_service, member_repo, book_item_repo):
        reader = Reader(member_id="R001", name="John", email="j@t.com")
        member_repo.add(reader)
        book_item_repo.add(BookItem(barcode="BC001", book_isbn="978-1"))

        loan = loan_service.borrow_book("R001", "BC001")
        assert loan.member_id == "R001"
        assert loan.book_item_barcode == "BC001"
        assert loan.is_active()

    def test_borrow_updates_item_status(self, loan_service, member_repo, book_item_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        item = BookItem(barcode="BC001", book_isbn="978-1")
        book_item_repo.add(item)
        loan_service.borrow_book("R001", "BC001")
        assert item.status == BookStatus.LOANED

    def test_borrow_increments_count(self, loan_service, member_repo, book_item_repo):
        reader = Reader(member_id="R001", name="John", email="j@t.com")
        member_repo.add(reader)
        book_item_repo.add(BookItem(barcode="BC001", book_isbn="978-1"))
        loan_service.borrow_book("R001", "BC001")
        assert reader.total_books_checked_out == 1

    def test_borrow_member_not_found(self, loan_service):
        with pytest.raises(MemberNotFoundError):
            loan_service.borrow_book("nonexistent", "BC001")

    def test_borrow_member_blocked(self, loan_service, member_repo):
        reader = Reader(member_id="R001", name="John", email="j@t.com", status=MemberStatus.BLOCKED)
        member_repo.add(reader)
        with pytest.raises(MemberBlockedError):
            loan_service.borrow_book("R001", "BC001")

    def test_borrow_at_limit(self, loan_service, member_repo, book_item_repo):
        reader = Reader(member_id="R001", name="John", email="j@t.com", total_books_checked_out=5)
        member_repo.add(reader)
        book_item_repo.add(BookItem(barcode="BC001", book_isbn="978-1"))
        with pytest.raises(LoanLimitExceededError):
            loan_service.borrow_book("R001", "BC001")

    def test_borrow_book_not_found(self, loan_service, member_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        with pytest.raises(BookNotFoundError):
            loan_service.borrow_book("R001", "nonexistent")

    def test_borrow_book_not_available(self, loan_service, member_repo, book_item_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        book_item_repo.add(BookItem(barcode="BC001", book_isbn="978-1", status=BookStatus.LOANED))
        with pytest.raises(BookNotAvailableError):
            loan_service.borrow_book("R001", "BC001")

    def test_borrow_custom_period(self, loan_service, member_repo, book_item_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        book_item_repo.add(BookItem(barcode="BC001", book_isbn="978-1"))
        loan = loan_service.borrow_book("R001", "BC001", loan_period_days=7)
        assert loan.due_date == date.today() + timedelta(days=7)

    def test_borrow_multiple_books(self, loan_service, member_repo, book_item_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        for i in range(3):
            book_item_repo.add(BookItem(barcode=f"BC{i:03d}", book_isbn="978-1"))
            loan_service.borrow_book("R001", f"BC{i:03d}")
        assert len(loan_service.get_active_loans_by_member("R001")) == 3


class TestLoanServiceReturn:
    """Tests for LoanService.return_book."""

    def test_return_success(self, loan_service, member_repo, book_item_repo):
        reader = Reader(member_id="R001", name="John", email="j@t.com")
        member_repo.add(reader)
        book_item_repo.add(BookItem(barcode="BC001", book_isbn="978-1"))
        loan_service.borrow_book("R001", "BC001")
        loan = loan_service.return_book("BC001")
        assert loan.return_date is not None
        assert not loan.is_active()

    def test_return_updates_item_status(self, loan_service, member_repo, book_item_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        item = BookItem(barcode="BC001", book_isbn="978-1")
        book_item_repo.add(item)
        loan_service.borrow_book("R001", "BC001")
        loan_service.return_book("BC001")
        assert item.status == BookStatus.AVAILABLE

    def test_return_decrements_count(self, loan_service, member_repo, book_item_repo):
        reader = Reader(member_id="R001", name="John", email="j@t.com")
        member_repo.add(reader)
        book_item_repo.add(BookItem(barcode="BC001", book_isbn="978-1"))
        loan_service.borrow_book("R001", "BC001")
        loan_service.return_book("BC001")
        assert reader.total_books_checked_out == 0

    def test_return_not_found(self, loan_service, book_item_repo):
        with pytest.raises(BookNotFoundError):
            loan_service.return_book("nonexistent")

    def test_return_no_active_loan(self, loan_service, book_item_repo):
        book_item_repo.add(BookItem(barcode="BC001", book_isbn="978-1"))
        with pytest.raises(LoanNotFoundError):
            loan_service.return_book("BC001")

    def test_return_specific_date(self, loan_service, member_repo, book_item_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        book_item_repo.add(BookItem(barcode="BC001", book_isbn="978-1"))
        loan_service.borrow_book("R001", "BC001")
        loan = loan_service.return_book("BC001", date(2025, 12, 25))
        assert loan.return_date == date(2025, 12, 25)


class TestLoanServiceQueries:
    """Tests for LoanService query methods."""

    def test_get_loan(self, loan_service, member_repo, book_item_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        book_item_repo.add(BookItem(barcode="BC001", book_isbn="978-1"))
        loan = loan_service.borrow_book("R001", "BC001")
        result = loan_service.get_loan(loan.loan_id)
        assert result.loan_id == loan.loan_id

    def test_get_loan_not_found(self, loan_service):
        with pytest.raises(LoanNotFoundError):
            loan_service.get_loan("nonexistent")

    def test_get_all_loans(self, loan_service, member_repo, book_item_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        book_item_repo.add(BookItem(barcode="BC001", book_isbn="978-1"))
        book_item_repo.add(BookItem(barcode="BC002", book_isbn="978-1"))
        loan_service.borrow_book("R001", "BC001")
        loan_service.borrow_book("R001", "BC002")
        assert len(loan_service.get_all_loans()) == 2

    def test_get_overdue_loans(self, loan_service, loan_repo):
        overdue = Loan(
            loan_id="L1",
            member_id="R001",
            book_item_barcode="BC001",
            issue_date=date.today() - timedelta(days=30),
            due_date=date.today() - timedelta(days=16),
        )
        loan_repo.add(overdue)
        result = loan_service.get_overdue_loans()
        assert len(result) == 1

    def test_get_loan_history(self, loan_service, member_repo, book_item_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        book_item_repo.add(BookItem(barcode="BC001", book_isbn="978-1"))
        loan_service.borrow_book("R001", "BC001")
        loan_service.return_book("BC001")
        history = loan_service.get_loan_history_by_member("R001")
        assert len(history) == 1
