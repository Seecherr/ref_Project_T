"""Unit tests for InMemoryLoanRepository."""

import pytest
from datetime import date, timedelta

from src.models.loan import Loan
from src.storage.in_memory_loan_repository import InMemoryLoanRepository


class TestInMemoryLoanRepository:
    """Tests for InMemoryLoanRepository."""

    def test_add_and_get_by_id(self, loan_repo):
        loan = Loan(loan_id="L001", member_id="M1", book_item_barcode="BC001")
        loan_repo.add(loan)
        assert loan_repo.get_by_id("L001") is loan

    def test_get_by_id_nonexistent(self, loan_repo):
        assert loan_repo.get_by_id("nonexistent") is None

    def test_get_active_by_member(self, loan_repo):
        loan_repo.add(Loan(loan_id="L001", member_id="M1", book_item_barcode="BC001"))
        loan_repo.add(Loan(loan_id="L002", member_id="M1", book_item_barcode="BC002"))
        returned = Loan(loan_id="L003", member_id="M1", book_item_barcode="BC003")
        returned.complete_return()
        loan_repo.add(returned)
        active = loan_repo.get_active_by_member("M1")
        assert len(active) == 2

    def test_get_active_by_member_none(self, loan_repo):
        assert loan_repo.get_active_by_member("M1") == []

    def test_get_by_book_item(self, loan_repo):
        loan_repo.add(Loan(loan_id="L001", member_id="M1", book_item_barcode="BC001"))
        loan_repo.add(Loan(loan_id="L002", member_id="M2", book_item_barcode="BC001"))
        results = loan_repo.get_by_book_item("BC001")
        assert len(results) == 2

    def test_get_active_by_book_item(self, loan_repo):
        loan_repo.add(Loan(loan_id="L001", member_id="M1", book_item_barcode="BC001"))
        result = loan_repo.get_active_by_book_item("BC001")
        assert result is not None
        assert result.loan_id == "L001"

    def test_get_active_by_book_item_none(self, loan_repo):
        returned = Loan(loan_id="L001", member_id="M1", book_item_barcode="BC001")
        returned.complete_return()
        loan_repo.add(returned)
        assert loan_repo.get_active_by_book_item("BC001") is None

    def test_get_all(self, loan_repo):
        loan_repo.add(Loan(loan_id="L001", member_id="M1", book_item_barcode="BC001"))
        loan_repo.add(Loan(loan_id="L002", member_id="M2", book_item_barcode="BC002"))
        assert len(loan_repo.get_all()) == 2

    def test_get_all_empty(self, loan_repo):
        assert loan_repo.get_all() == []

    def test_update(self, loan_repo):
        loan = Loan(loan_id="L001", member_id="M1", book_item_barcode="BC001")
        loan_repo.add(loan)
        loan.complete_return()
        loan_repo.update(loan)
        result = loan_repo.get_by_id("L001")
        assert result.return_date is not None

    def test_get_active_different_members(self, loan_repo):
        loan_repo.add(Loan(loan_id="L001", member_id="M1", book_item_barcode="BC001"))
        loan_repo.add(Loan(loan_id="L002", member_id="M2", book_item_barcode="BC002"))
        assert len(loan_repo.get_active_by_member("M1")) == 1
        assert len(loan_repo.get_active_by_member("M2")) == 1

    def test_get_by_book_item_empty(self, loan_repo):
        assert loan_repo.get_by_book_item("BC001") == []
