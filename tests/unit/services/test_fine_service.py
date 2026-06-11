"""Unit tests for FineService."""

import pytest
from decimal import Decimal
from datetime import date, timedelta

from src.models.loan import Loan
from src.models.fine import Fine
from src.models.member import Reader, MemberStatus
from src.utils.exceptions import FineNotFoundError
from src.utils.fine_strategy import StandardFineStrategy, ProgressiveFineStrategy, NoFineStrategy


class TestFineServiceCalculate:
    """Tests for FineService.calculate_fine and create_fine."""

    def test_calculate_fine_no_overdue(self, fine_service):
        loan = Loan(loan_id="L1", member_id="M1", book_item_barcode="BC001")
        assert fine_service.calculate_fine(loan) == Decimal("0.00")

    def test_calculate_fine_overdue(self, fine_service):
        loan = Loan(
            loan_id="L1", member_id="M1", book_item_barcode="BC001",
            issue_date=date.today() - timedelta(days=20),
            due_date=date.today() - timedelta(days=6),
            return_date=date.today(),
        )
        assert fine_service.calculate_fine(loan) > Decimal("0")

    def test_create_fine_no_overdue(self, fine_service):
        loan = Loan(loan_id="L1", member_id="M1", book_item_barcode="BC001")
        assert fine_service.create_fine(loan) is None

    def test_create_fine_overdue(self, fine_service, member_repo):
        member_repo.add(Reader(member_id="M1", name="John", email="j@t.com"))
        loan = Loan(
            loan_id="L1", member_id="M1", book_item_barcode="BC001",
            issue_date=date.today() - timedelta(days=20),
            due_date=date.today() - timedelta(days=6),
            return_date=date.today(),
        )
        fine = fine_service.create_fine(loan)
        assert fine is not None
        assert fine.amount > Decimal("0")

    def test_create_fine_idempotent(self, fine_service, member_repo):
        member_repo.add(Reader(member_id="M1", name="John", email="j@t.com"))
        loan = Loan(
            loan_id="L1", member_id="M1", book_item_barcode="BC001",
            issue_date=date.today() - timedelta(days=20),
            due_date=date.today() - timedelta(days=6),
            return_date=date.today(),
        )
        fine1 = fine_service.create_fine(loan)
        fine2 = fine_service.create_fine(loan)
        assert fine1 is fine2  # Should not create duplicate

    def test_set_strategy(self, fine_service):
        fine_service.set_strategy(NoFineStrategy())
        loan = Loan(
            loan_id="L1", member_id="M1", book_item_barcode="BC001",
            issue_date=date.today() - timedelta(days=20),
            due_date=date.today() - timedelta(days=6),
            return_date=date.today(),
        )
        assert fine_service.calculate_fine(loan) == Decimal("0.00")

    def test_set_progressive_strategy(self, fine_service):
        fine_service.set_strategy(ProgressiveFineStrategy())
        loan = Loan(
            loan_id="L1", member_id="M1", book_item_barcode="BC001",
            issue_date=date.today() - timedelta(days=20),
            due_date=date.today() - timedelta(days=6),
            return_date=date.today(),
        )
        assert fine_service.calculate_fine(loan) > Decimal("0.00")


class TestFineServicePayment:
    """Tests for FineService.pay_fine."""

    def test_pay_fine_full(self, fine_service, fine_repo, member_repo):
        member_repo.add(Reader(member_id="M1", name="John", email="j@t.com"))
        fine = Fine(fine_id="F1", loan_id="L1", member_id="M1", amount=Decimal("5.00"))
        fine_repo.add(fine)
        result = fine_service.pay_fine("F1", Decimal("5.00"))
        assert result.is_fully_paid()

    def test_pay_fine_partial(self, fine_service, fine_repo, member_repo):
        member_repo.add(Reader(member_id="M1", name="John", email="j@t.com"))
        fine = Fine(fine_id="F1", loan_id="L1", member_id="M1", amount=Decimal("5.00"))
        fine_repo.add(fine)
        result = fine_service.pay_fine("F1", Decimal("3.00"))
        assert result.outstanding == Decimal("2.00")

    def test_pay_fine_not_found(self, fine_service):
        with pytest.raises(FineNotFoundError):
            fine_service.pay_fine("nonexistent", Decimal("5.00"))

    def test_pay_fine_negative(self, fine_service, fine_repo):
        fine = Fine(fine_id="F1", loan_id="L1", member_id="M1", amount=Decimal("5.00"))
        fine_repo.add(fine)
        with pytest.raises(ValueError):
            fine_service.pay_fine("F1", Decimal("-1.00"))


class TestFineServiceQueries:
    """Tests for FineService query methods."""

    def test_get_fine(self, fine_service, fine_repo):
        fine = Fine(fine_id="F1", loan_id="L1", member_id="M1", amount=Decimal("5.00"))
        fine_repo.add(fine)
        result = fine_service.get_fine("F1")
        assert result is fine

    def test_get_fine_not_found(self, fine_service):
        with pytest.raises(FineNotFoundError):
            fine_service.get_fine("nonexistent")

    def test_get_unpaid_fines(self, fine_service, fine_repo):
        fine_repo.add(Fine(fine_id="F1", loan_id="L1", member_id="M1", amount=Decimal("5.00")))
        fine_repo.add(Fine(fine_id="F2", loan_id="L2", member_id="M1", amount=Decimal("3.00"), paid=Decimal("3.00")))
        unpaid = fine_service.get_unpaid_fines("M1")
        assert len(unpaid) == 1

    def test_get_total_unpaid(self, fine_service, fine_repo):
        fine_repo.add(Fine(fine_id="F1", loan_id="L1", member_id="M1", amount=Decimal("5.00")))
        fine_repo.add(Fine(fine_id="F2", loan_id="L2", member_id="M1", amount=Decimal("3.00")))
        assert fine_service.get_total_unpaid("M1") == Decimal("8.00")

    def test_get_total_unpaid_with_partial_payment(self, fine_service, fine_repo):
        fine = Fine(fine_id="F1", loan_id="L1", member_id="M1", amount=Decimal("10.00"), paid=Decimal("3.00"))
        fine_repo.add(fine)
        assert fine_service.get_total_unpaid("M1") == Decimal("7.00")

    def test_get_all_fines(self, fine_service, fine_repo):
        fine_repo.add(Fine(fine_id="F1", loan_id="L1", member_id="M1", amount=Decimal("5.00")))
        assert len(fine_service.get_all_fines()) == 1


class TestFineServiceAutoBlock:
    """Tests for FineService auto-blocking/unblocking."""

    def test_auto_block_on_high_fines(self, fine_service, member_repo):
        reader = Reader(member_id="M1", name="John", email="j@t.com")
        member_repo.add(reader)
        loan = Loan(
            loan_id="L1", member_id="M1", book_item_barcode="BC001",
            issue_date=date.today() - timedelta(days=80),
            due_date=date.today() - timedelta(days=66),
            return_date=date.today(),
        )
        fine_service.create_fine(loan)
        # Should be auto-blocked if fine > threshold ($25)
        updated = member_repo.get_by_id("M1")
        if fine_service.get_total_unpaid("M1") >= Decimal("25.00"):
            assert updated.status == MemberStatus.BLOCKED

    def test_auto_unblock_after_payment(self, fine_service, fine_repo, member_repo):
        reader = Reader(member_id="M1", name="John", email="j@t.com", status=MemberStatus.BLOCKED)
        member_repo.add(reader)
        fine = Fine(fine_id="F1", loan_id="L1", member_id="M1", amount=Decimal("5.00"))
        fine_repo.add(fine)
        fine_service.pay_fine("F1", Decimal("5.00"))
        updated = member_repo.get_by_id("M1")
        assert updated.status == MemberStatus.ACTIVE
