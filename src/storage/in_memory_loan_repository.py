"""In-memory implementation of Loan repository."""

from __future__ import annotations

from typing import Optional

from src.models.loan import Loan
from src.storage.interfaces import LoanRepository


class InMemoryLoanRepository(LoanRepository):
    """Dictionary-based in-memory storage for Loan entities."""

    def __init__(self) -> None:
        self._loans: dict[str, Loan] = {}

    def add(self, loan: Loan) -> None:
        """Add a loan."""
        self._loans[loan.loan_id] = loan

    def get_by_id(self, loan_id: str) -> Optional[Loan]:
        """Get a loan by ID."""
        return self._loans.get(loan_id)

    def get_active_by_member(self, member_id: str) -> list[Loan]:
        """Get all active loans for a member."""
        return [
            loan for loan in self._loans.values()
            if loan.member_id == member_id and loan.is_active()
        ]

    def get_by_book_item(self, barcode: str) -> list[Loan]:
        """Get all loans for a specific book item."""
        return [
            loan for loan in self._loans.values()
            if loan.book_item_barcode == barcode
        ]

    def get_active_by_book_item(self, barcode: str) -> Optional[Loan]:
        """Get the active loan for a specific book item."""
        for loan in self._loans.values():
            if loan.book_item_barcode == barcode and loan.is_active():
                return loan
        return None

    def get_all(self) -> list[Loan]:
        """Get all loans."""
        return list(self._loans.values())

    def update(self, loan: Loan) -> None:
        """Update a loan."""
        self._loans[loan.loan_id] = loan
