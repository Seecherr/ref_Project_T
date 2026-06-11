"""Unit tests for InMemoryFineRepository."""

import pytest
from decimal import Decimal

from src.models.fine import Fine
from src.storage.in_memory_fine_repository import InMemoryFineRepository


class TestInMemoryFineRepository:
    """Tests for InMemoryFineRepository."""

    def test_add_and_get(self, fine_repo):
        fine = Fine(fine_id="F1", loan_id="L1", member_id="M1", amount=Decimal("5.00"))
        fine_repo.add(fine)
        assert fine_repo.get_by_id("F1") is fine

    def test_get_nonexistent(self, fine_repo):
        assert fine_repo.get_by_id("nonexistent") is None

    def test_get_unpaid_by_member(self, fine_repo):
        fine_repo.add(Fine(fine_id="F1", loan_id="L1", member_id="M1", amount=Decimal("5.00")))
        fine_repo.add(Fine(fine_id="F2", loan_id="L2", member_id="M1", amount=Decimal("3.00")))
        paid = Fine(fine_id="F3", loan_id="L3", member_id="M1", amount=Decimal("2.00"), paid=Decimal("2.00"))
        fine_repo.add(paid)
        unpaid = fine_repo.get_unpaid_by_member("M1")
        assert len(unpaid) == 2

    def test_get_unpaid_by_member_none(self, fine_repo):
        assert fine_repo.get_unpaid_by_member("M1") == []

    def test_get_by_loan(self, fine_repo):
        fine = Fine(fine_id="F1", loan_id="L1", member_id="M1", amount=Decimal("5.00"))
        fine_repo.add(fine)
        result = fine_repo.get_by_loan("L1")
        assert result is fine

    def test_get_by_loan_nonexistent(self, fine_repo):
        assert fine_repo.get_by_loan("nonexistent") is None

    def test_get_all(self, fine_repo):
        fine_repo.add(Fine(fine_id="F1", loan_id="L1", member_id="M1", amount=Decimal("5.00")))
        fine_repo.add(Fine(fine_id="F2", loan_id="L2", member_id="M2", amount=Decimal("3.00")))
        assert len(fine_repo.get_all()) == 2

    def test_get_all_empty(self, fine_repo):
        assert fine_repo.get_all() == []

    def test_update(self, fine_repo):
        fine = Fine(fine_id="F1", loan_id="L1", member_id="M1", amount=Decimal("5.00"))
        fine_repo.add(fine)
        fine.pay(Decimal("3.00"))
        fine_repo.update(fine)
        result = fine_repo.get_by_id("F1")
        assert result.paid == Decimal("3.00")

    def test_get_unpaid_different_members(self, fine_repo):
        fine_repo.add(Fine(fine_id="F1", loan_id="L1", member_id="M1", amount=Decimal("5.00")))
        fine_repo.add(Fine(fine_id="F2", loan_id="L2", member_id="M2", amount=Decimal("3.00")))
        assert len(fine_repo.get_unpaid_by_member("M1")) == 1
        assert len(fine_repo.get_unpaid_by_member("M2")) == 1
