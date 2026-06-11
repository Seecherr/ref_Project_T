"""In-memory implementation of Fine repository."""

from __future__ import annotations

from typing import Optional

from src.models.fine import Fine
from src.storage.interfaces import FineRepository


class InMemoryFineRepository(FineRepository):
    """Dictionary-based in-memory storage for Fine entities."""

    def __init__(self) -> None:
        self._fines: dict[str, Fine] = {}

    def add(self, fine: Fine) -> None:
        """Add a fine."""
        self._fines[fine.fine_id] = fine

    def get_by_id(self, fine_id: str) -> Optional[Fine]:
        """Get a fine by ID."""
        return self._fines.get(fine_id)

    def get_unpaid_by_member(self, member_id: str) -> list[Fine]:
        """Get all unpaid fines for a member."""
        return [
            fine for fine in self._fines.values()
            if fine.member_id == member_id and not fine.is_fully_paid()
        ]

    def get_by_loan(self, loan_id: str) -> Optional[Fine]:
        """Get the fine associated with a specific loan."""
        for fine in self._fines.values():
            if fine.loan_id == loan_id:
                return fine
        return None

    def get_all(self) -> list[Fine]:
        """Get all fines."""
        return list(self._fines.values())

    def update(self, fine: Fine) -> None:
        """Update a fine."""
        self._fines[fine.fine_id] = fine
