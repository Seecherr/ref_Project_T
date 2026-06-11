"""In-memory implementation of Reservation repository."""

from __future__ import annotations

from typing import Optional

from src.models.reservation import Reservation, ReservationStatus
from src.storage.interfaces import ReservationRepository


class InMemoryReservationRepository(ReservationRepository):
    """Dictionary-based in-memory storage for Reservation entities.

    Waiting reservations are returned sorted by creation date (FIFO)
    to implement priority queue semantics.
    """

    def __init__(self) -> None:
        self._reservations: dict[str, Reservation] = {}

    def add(self, reservation: Reservation) -> None:
        """Add a reservation."""
        self._reservations[reservation.reservation_id] = reservation

    def get_by_id(self, reservation_id: str) -> Optional[Reservation]:
        """Get a reservation by ID."""
        return self._reservations.get(reservation_id)

    def get_waiting_by_isbn(self, book_isbn: str) -> list[Reservation]:
        """Get waiting reservations for a book, ordered by creation date (FIFO)."""
        waiting = [
            r for r in self._reservations.values()
            if r.book_isbn == book_isbn and r.status == ReservationStatus.WAITING
        ]
        return sorted(waiting, key=lambda r: r.created_at)

    def get_by_member(self, member_id: str) -> list[Reservation]:
        """Get all reservations for a member."""
        return [
            r for r in self._reservations.values()
            if r.member_id == member_id
        ]

    def get_all(self) -> list[Reservation]:
        """Get all reservations."""
        return list(self._reservations.values())

    def update(self, reservation: Reservation) -> None:
        """Update a reservation."""
        self._reservations[reservation.reservation_id] = reservation
