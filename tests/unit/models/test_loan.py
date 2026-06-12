"""Unit tests for Loan model."""

from datetime import date, timedelta

from src.models.loan import DEFAULT_LOAN_PERIOD_DAYS, Loan


class TestLoan:
    """Tests for Loan dataclass."""

    def test_creation_defaults(self, sample_loan):
        assert sample_loan.loan_id == "LOAN001"
        assert sample_loan.member_id == "R001"
        assert sample_loan.book_item_barcode == "BC001"
        assert sample_loan.issue_date == date.today()
        assert sample_loan.due_date == date.today() + timedelta(days=DEFAULT_LOAN_PERIOD_DAYS)
        assert sample_loan.return_date is None

    def test_custom_due_date(self):
        due = date(2025, 12, 31)
        loan = Loan(loan_id="L1", member_id="M1", book_item_barcode="B1", due_date=due)
        assert loan.due_date == due

    def test_is_active_default(self, sample_loan):
        assert sample_loan.is_active() is True

    def test_is_active_after_return(self, sample_loan):
        sample_loan.complete_return()
        assert sample_loan.is_active() is False

    def test_is_overdue_not_overdue(self, sample_loan):
        assert sample_loan.is_overdue() is False

    def test_is_overdue_when_overdue(self, overdue_loan):
        assert overdue_loan.is_overdue() is True

    def test_is_overdue_on_due_date(self):
        loan = Loan(
            loan_id="L1",
            member_id="M1",
            book_item_barcode="B1",
            due_date=date.today(),
        )
        assert loan.is_overdue() is False

    def test_is_overdue_returned_late(self):
        loan = Loan(
            loan_id="L1",
            member_id="M1",
            book_item_barcode="B1",
            issue_date=date(2025, 1, 1),
            due_date=date(2025, 1, 15),
            return_date=date(2025, 1, 20),
        )
        assert loan.is_overdue() is True

    def test_is_overdue_returned_on_time(self):
        loan = Loan(
            loan_id="L1",
            member_id="M1",
            book_item_barcode="B1",
            issue_date=date(2025, 1, 1),
            due_date=date(2025, 1, 15),
            return_date=date(2025, 1, 14),
        )
        assert loan.is_overdue() is False

    def test_days_overdue_not_overdue(self, sample_loan):
        assert sample_loan.days_overdue() == 0

    def test_days_overdue_when_overdue(self, overdue_loan):
        assert overdue_loan.days_overdue() > 0

    def test_days_overdue_specific_date(self):
        loan = Loan(
            loan_id="L1",
            member_id="M1",
            book_item_barcode="B1",
            issue_date=date(2025, 1, 1),
            due_date=date(2025, 1, 15),
        )
        assert loan.days_overdue(date(2025, 1, 20)) == 5

    def test_days_overdue_returned_late(self):
        loan = Loan(
            loan_id="L1",
            member_id="M1",
            book_item_barcode="B1",
            issue_date=date(2025, 1, 1),
            due_date=date(2025, 1, 15),
            return_date=date(2025, 1, 25),
        )
        assert loan.days_overdue() == 10

    def test_complete_return_default_date(self, sample_loan):
        sample_loan.complete_return()
        assert sample_loan.return_date == date.today()
        assert sample_loan.is_active() is False

    def test_complete_return_specific_date(self, sample_loan):
        return_on = date(2025, 6, 15)
        sample_loan.complete_return(return_on)
        assert sample_loan.return_date == return_on

    def test_default_loan_period(self):
        assert DEFAULT_LOAN_PERIOD_DAYS == 14

    def test_is_overdue_with_as_of(self):
        loan = Loan(
            loan_id="L1",
            member_id="M1",
            book_item_barcode="B1",
            issue_date=date(2025, 1, 1),
            due_date=date(2025, 1, 15),
        )
        assert loan.is_overdue(date(2025, 1, 14)) is False
        assert loan.is_overdue(date(2025, 1, 16)) is True
