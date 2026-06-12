"""Unit tests for Fine model."""

from datetime import datetime
from decimal import Decimal

import pytest

from src.models.fine import Fine


class TestFine:
    """Tests for Fine dataclass."""

    def test_creation_defaults(self, sample_fine):
        assert sample_fine.fine_id == "FINE001"
        assert sample_fine.loan_id == "LOAN001"
        assert sample_fine.member_id == "R001"
        assert sample_fine.amount == Decimal("5.00")
        assert sample_fine.paid == Decimal("0.00")
        assert isinstance(sample_fine.created_at, datetime)

    def test_outstanding_initial(self, sample_fine):
        assert sample_fine.outstanding == Decimal("5.00")

    def test_outstanding_after_partial_payment(self, sample_fine):
        sample_fine.pay(Decimal("2.00"))
        assert sample_fine.outstanding == Decimal("3.00")

    def test_is_fully_paid_false(self, sample_fine):
        assert sample_fine.is_fully_paid() is False

    def test_is_fully_paid_true(self, sample_fine):
        sample_fine.pay(Decimal("5.00"))
        assert sample_fine.is_fully_paid() is True

    def test_pay_full_amount(self, sample_fine):
        remaining = sample_fine.pay(Decimal("5.00"))
        assert remaining == Decimal("0.00")
        assert sample_fine.paid == Decimal("5.00")

    def test_pay_partial_amount(self, sample_fine):
        remaining = sample_fine.pay(Decimal("3.00"))
        assert remaining == Decimal("2.00")
        assert sample_fine.paid == Decimal("3.00")

    def test_pay_overpayment(self, sample_fine):
        remaining = sample_fine.pay(Decimal("10.00"))
        assert remaining == Decimal("0.00")
        assert sample_fine.paid == Decimal("5.00")  # Capped at amount

    def test_pay_negative_raises(self, sample_fine):
        with pytest.raises(ValueError, match="negative"):
            sample_fine.pay(Decimal("-1.00"))

    def test_pay_zero(self, sample_fine):
        remaining = sample_fine.pay(Decimal("0.00"))
        assert remaining == Decimal("5.00")

    def test_multiple_payments(self):
        fine = Fine(fine_id="F1", loan_id="L1", member_id="M1", amount=Decimal("10.00"))
        fine.pay(Decimal("3.00"))
        fine.pay(Decimal("3.00"))
        fine.pay(Decimal("3.00"))
        assert fine.paid == Decimal("9.00")
        assert fine.outstanding == Decimal("1.00")
        assert fine.is_fully_paid() is False

    def test_fully_paid_after_multiple_payments(self):
        fine = Fine(fine_id="F1", loan_id="L1", member_id="M1", amount=Decimal("10.00"))
        fine.pay(Decimal("5.00"))
        fine.pay(Decimal("5.00"))
        assert fine.is_fully_paid() is True
